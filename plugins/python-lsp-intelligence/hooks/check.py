#!/usr/bin/env python3
"""Post-edit hook of python-lsp-intelligence: ruff check --fix, ruff format, basedpyright.

Reads one PostToolUse or PostToolUseFailure event on stdin, finds the Python files the
tool call changed, runs the tools on each one with the user's own configuration (the
plugin's defaults in hooks/defaults/ only when ruff or basedpyright would find none) and
reports in two places. The user always gets one systemMessage line saying which tools ran on
which files, whether they reformatted any and whether they found errors, or why they did not
run. Claude gets a message only when the tools found errors or failed on a file: the
findings on stderr with exit 2, and the instruction to audit and fix them with the plugin's
skill before continuing. Files of other languages are ignored in silence.

The hook judges only what the tool call changed and never blocks because it cannot check:
- A tool that is not installed is reported to the user on every call, with exit 0.
- Files that a Bash command left under a nested Git work tree count only when Git lists
  them as modified, untracked or staged there, so a clone, a checkout or a pull is never checked.
- More than MAX_FILES files found by modification time alone, outside Git, are an arrival
  (an extracted archive, a generated tree), not an edit: none is checked, and Claude is told.
Python 3.12 or later, standard library only.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import TYPE_CHECKING, NamedTuple, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

PLUGIN = "python-lsp-intelligence"
# Closes the message Claude receives when the tools found errors.
CLAUDE_INSTRUCTION = (
    f'Use the Skill tool to load "{PLUGIN}:{PLUGIN}", audit these errors with it and fix them '
    "before continuing with anything else."
)
PYTHON_SUFFIXES = frozenset({".py", ".pyi", ".pyw"})
NOTEBOOK_SUFFIX = ".ipynb"
SHEBANG = re.compile(r"^#!.*\b(python[0-9.]*|uv\s+run)\b")
SKIPPED_DIRS = frozenset({"node_modules", ".venv", "venv", "site-packages"})
PRUNED_DIRS = SKIPPED_DIRS | frozenset(
    {".git", "dist", "build", "__pycache__", ".ruff_cache", ".mypy_cache", ".cache"},
)
# A Bash command that rewrites more files than this gets the rest reported, not checked.
MAX_FILES = 20
# The modification-time walk gives up after this many files, so a huge tree stays cheap.
MAX_WALK_FILES = 20_000
# A file's project root, where basedpyright resolves first-party imports and the .venv from.
PROJECT_MARKERS = ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", ".git")
# Claude Code saves hook output over 10,000 characters to a file Claude never reads.
MAX_REPORT_CHARS = 9000
# Clock slack added to duration_ms when looking for files a Bash command changed.
BASH_SLACK_MS = 2000
# Window used when the event carries no duration_ms.
FALLBACK_WINDOW_MS = 30_000
MS_PER_S = 1000
# Under the hook's 60 s budget, so a hung tool is reported instead of cancelled in silence.
TOOL_TIMEOUT_S = 50
# ruff exits 2, and basedpyright 2 or more, when they could not do their job at all.
ABNORMAL_EXIT = 2
DEFAULTS_DIR = Path(__file__).resolve().parent / "defaults"
DEFAULTS_PYRIGHT = DEFAULTS_DIR / "pyrightconfig.json"
INSTALL_HINTS = {"ruff": "uv tool install ruff", "basedpyright": "uv tool install basedpyright"}


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


class Run(NamedTuple):
    """One tool invocation: exit code (None when it could not run) and combined output."""

    code: int | None
    output: str


class FileResult(NamedTuple):
    """What the chain found for one file."""

    findings: list[str]
    failures: list[str]
    rewrote: bool


class Tools(NamedTuple):
    """Absolute paths of the executables."""

    ruff: str
    basedpyright: str


class Changed(NamedTuple):
    """The files a tool call changed, and the folder searched by modification time alone.

    walked is None when the list comes from the tool's input, from Claude Code or from Git.
    """

    files: list[Path]
    walked: Path | None


def text_at(value: object, *keys: str) -> str:
    """Return the string under keys in nested JSON objects, or "" when absent or not text."""
    for key in keys:
        if not isinstance(value, JsonObject):
            return ""
        value = value.get(key)
    return value if isinstance(value, str) else ""


def strings_at(value: object, *keys: str) -> list[str] | None:
    """Return the strings in the list under keys, or None when absent or not a list."""
    for key in keys:
        if not isinstance(value, JsonObject):
            return None
        value = value.get(key)
    if not isinstance(value, list):
        return None
    items = cast("list[object]", value)  # a JSON array holds decoded values of any type
    return [item for item in items if isinstance(item, str)]


def integer_at(value: object, key: str) -> int | None:
    """Return the integer under key, or None."""
    if not isinstance(value, JsonObject):
        return None
    number = value.get(key)
    if isinstance(number, bool) or not isinstance(number, int):
        return None
    return number


def read_event() -> JsonObject | None:
    """Decode the hook event from stdin; None when it is not a JSON object."""
    try:
        data = _decode(sys.stdin.read())
    except (OSError, ValueError):
        return None
    return data if isinstance(data, JsonObject) else None


def project_dir(event: JsonObject) -> Path | None:
    """The folder a Bash command may have changed files under: CLAUDE_PROJECT_DIR, else cwd."""
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    for candidate in (env_dir, text_at(event, "cwd"), str(Path.cwd())):
        if candidate and Path(candidate).is_dir():
            # Resolved like the files are, so relative display works with symlinked or 8.3 paths.
            return Path(candidate).resolve()
    return None


def newer_than(path: Path, since_s: float) -> bool:
    """True when path is a regular file modified after since_s."""
    try:
        return path.is_file() and path.stat().st_mtime > since_s
    except OSError:
        return False


def git_changed(git: str, tree: Path) -> list[Path] | None:
    """The files Git lists as modified, untracked or staged in work tree `tree`; None outside one.

    Staged files count too: a command that runs `git add` leaves nothing `--modified`.
    """
    inside = run([git, "-C", str(tree), "rev-parse", "--is-inside-work-tree"])
    if inside.code != 0:
        return None
    listed = run(
        [git, "-C", str(tree), "ls-files", "-z", "--modified", "--others", "--exclude-standard"],
    )
    staged = run([git, "-C", str(tree), "diff", "-z", "--cached", "--name-only", "--relative"])
    names = listed.output.split("\0")
    if staged.code == 0:
        names += staged.output.split("\0")
    return [tree / rel for rel in dict.fromkeys(names) if rel]


def not_ignored(files: list[Path]) -> list[Path]:
    """The files Git does not ignore; a file outside every work tree is kept.

    What a command writes into an ignored place, such as a virtual environment or a build
    folder, is output, not source the project maintains.
    """
    git = shutil.which("git")
    if git is None:
        return files
    by_folder: dict[Path, list[Path]] = {}
    for path in files:
        by_folder.setdefault(path.parent, []).append(path)
    ignored: set[str] = set()
    for folder, group in by_folder.items():
        # Exit 0 lists the ignored paths, 1 means none is, 128 that the folder is in no work tree.
        # NUL-separated both ways, which git accepts only on standard input.
        names = "".join(f"{path}\0" for path in group)
        listed = run([git, "-C", str(folder), "check-ignore", "--stdin", "-z"], stdin=names)
        if listed.code == 0:
            ignored.update(listed.output.split("\0"))
    return [path for path in files if str(path) not in ignored]


def walk(project: Path, since_s: float) -> list[Path]:
    """Files under project modified after since_s, by a pruned walk of at most MAX_WALK_FILES."""
    found: list[Path] = []
    visited = 0
    for directory, subdirs, files in os.walk(project):  # unreadable folders are skipped
        subdirs[:] = [name for name in subdirs if name not in PRUNED_DIRS]
        for name in files:
            visited += 1
            if visited > MAX_WALK_FILES:
                return found
            path = Path(directory) / name
            if newer_than(path, since_s):
                found.append(path)
    return found


def changed_since(project: Path, since_s: float) -> Changed:
    """Files under project modified after since_s: Git's view in a work tree, else a pruned walk."""
    git = shutil.which("git")
    if git is not None:
        listed = git_changed(git, project)
        if listed is not None:
            return Changed([path for path in listed if newer_than(path, since_s)], None)
    if project in (Path.home().resolve(), Path(project.anchor)):
        # A walk of the whole home directory or disk is never worth a hook's budget.
        return Changed([], None)
    return Changed(walk(project, since_s), project)


def nested_tree(path: Path, top: Path, known: dict[Path, Path | None]) -> Path | None:
    """The nearest folder between path and top that holds a .git entry: a nested work tree.

    known remembers the answer for every folder visited, so each folder is examined once.
    """
    trail: list[Path] = []
    tree: Path | None = None
    for directory in path.parents:
        if directory == top or top not in directory.parents:
            break
        if directory in known:
            tree = known[directory]
            break
        trail.append(directory)
        if (directory / ".git").exists():
            tree = directory
            break
    for directory in trail:
        known[directory] = tree
    return tree


def own_changes(files: list[Path], walked: Path) -> tuple[list[Path], list[Path]]:
    """Split the files found by modification time under walked into (verified, loose).

    A clone, a checkout or a pull writes files with a new modification time that nobody
    edited. Inside a nested Git work tree only the files Git lists as modified, untracked or
    staged are a change: those are verified, and the rest are dropped. Files outside every
    work tree are loose: nothing tells an edit from an arrival there.
    """
    git = shutil.which("git")
    if git is None:
        return [], files
    known: dict[Path, Path | None] = {}
    listed: dict[Path, frozenset[Path] | None] = {}
    verified: list[Path] = []
    loose: list[Path] = []
    for path in files:
        tree = nested_tree(path, walked, known)
        if tree is None:
            loose.append(path)
            continue
        if tree not in listed:
            changed = git_changed(git, tree)
            listed[tree] = None if changed is None else frozenset(changed)
        changed_here = listed[tree]
        if changed_here is None:
            loose.append(path)  # a .git entry Git does not accept as a work tree
        elif path in changed_here:
            verified.append(path)
    return verified, loose


def as_files(names: Iterable[str]) -> list[Path]:
    """Existing regular files among names, resolved, without duplicates."""
    seen: dict[Path, None] = {}
    for name in names:
        if not name:
            continue
        path = Path(name).resolve()
        if path.is_file():
            seen.setdefault(path, None)
    return list(seen)


def candidates(event: JsonObject, now_ms: int) -> Changed:
    """The files the tool call may have changed, by tool name."""
    tool = text_at(event, "tool_name")
    if tool in {"Edit", "Write"}:
        return Changed(as_files([text_at(event, "tool_input", "file_path")]), None)
    if tool == "NotebookEdit":
        return Changed(as_files([text_at(event, "tool_input", "notebook_path")]), None)
    if tool != "Bash":
        return Changed([], None)
    changed = strings_at(event, "tool_response", "bashEditDiff", "changedFiles")
    if changed is not None:
        return Changed(not_ignored(as_files(changed)), None)
    project = project_dir(event)
    if project is None:
        return Changed([], None)
    duration = integer_at(event, "duration_ms")
    window_ms = FALLBACK_WINDOW_MS if duration is None else duration + BASH_SLACK_MS
    return changed_since(project, (now_ms - window_ms) / MS_PER_S)


def is_python(path: Path) -> bool:
    """True for .py/.pyi/.pyw/.ipynb files and extensionless scripts with a Python shebang."""
    if path.suffix in PYTHON_SUFFIXES or path.suffix == NOTEBOOK_SUFFIX:
        return True
    if path.suffix:
        return False
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            return SHEBANG.match(handle.readline()) is not None
    except OSError:
        return False


def skipped(path: Path) -> bool:
    """True for third-party code the hook must never touch."""
    return any(part in SKIPPED_DIRS for part in path.parts)


def run(argv: list[str], stdin: str | None = None) -> Run:
    """Run one command, capturing stdout and stderr together; never raises.

    With stdin, the command reads that text as its standard input.
    """
    try:
        done = subprocess.run(
            argv,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=TOOL_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Run(None, f"{argv[0]} timed out after {TOOL_TIMEOUT_S} s")
    except OSError as error:
        return Run(None, f"{argv[0]} could not start: {error}")
    return Run(done.returncode, (done.stdout + done.stderr).strip())


def digest(path: Path) -> str:
    """sha256 of the file's bytes, or "" when unreadable."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def ruff_config_args(ruff: str, path: Path) -> list[str]:
    """Empty when ruff resolves a configuration for path on its own, else the plugin defaults."""
    shown = run([ruff, "check", "--show-settings", str(path)])
    if shown.code != 0 or "Settings path:" in shown.output:
        return []
    return ["--config", str(DEFAULTS_DIR / "ruff.toml")]


def has_pyright_table(pyproject: Path) -> bool:
    """True when the file declares [tool.basedpyright] or [tool.pyright]."""
    try:
        text = pyproject.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return "[tool.basedpyright]" in text or "[tool.pyright]" in text


def user_pyright_config(path: Path) -> Path | None:
    """The nearest pyrightconfig.json or pyproject.toml with a pyright table above path."""
    for directory in path.parents:
        config = directory / "pyrightconfig.json"
        if config.is_file():
            return config
        pyproject = directory / "pyproject.toml"
        if pyproject.is_file() and has_pyright_table(pyproject):
            return pyproject
    return None


def project_root(path: Path) -> Path:
    """The nearest folder above path with a project marker, else the file's own folder."""
    for directory in path.parents:
        if any((directory / marker).exists() for marker in PROJECT_MARKERS):
            return directory
    return path.parent


def default_pyright_config(path: Path, scratch: Path) -> Path:
    """Write the plugin's profile, bound to the file's project, into scratch and return it.

    basedpyright resolves imports and the virtual environment from the config file's folder,
    so the bundled profile is copied next to nothing in the project: the project root (and
    its src/) become search paths and execution root, and a .venv there is used when present.
    """
    root = project_root(path)
    profile = _decode(DEFAULTS_PYRIGHT.read_text(encoding="utf-8"))
    if not isinstance(profile, JsonObject):
        profile = JsonObject()
    search = [str(root), str(root / "src")]
    profile["extraPaths"] = search
    profile["executionEnvironments"] = [{"root": str(root), "extraPaths": search}]
    if (root / ".venv").is_dir():
        profile["venvPath"] = str(root)
        profile["venv"] = ".venv"
    config = scratch / "pyrightconfig.json"
    _ = config.write_text(json.dumps(profile), encoding="utf-8")
    return config


def record(result: Run, label: str, path: Path, out: FileResult) -> None:
    """File a tool result under findings or failures."""
    if result.code is None or result.code >= ABNORMAL_EXIT:
        out.failures.append(f"{label} failed, so {path} was not checked:\n{result.output}")
    elif result.code != 0:
        out.findings.append(f"{label} ({path}):\n{result.output}")


def check_file(path: Path, tools: Tools) -> FileResult:
    """Run ruff check --fix, ruff format and basedpyright on one file."""
    out = FileResult([], [], rewrote=False)
    before = digest(path)
    config = ruff_config_args(tools.ruff, path)
    record(run([tools.ruff, "check", "--fix", *config, str(path)]), "ruff check", path, out)
    record(run([tools.ruff, "format", *config, str(path)]), "ruff format", path, out)
    rewrote = digest(path) != before
    if path.suffix != NOTEBOOK_SUFFIX:
        with tempfile.TemporaryDirectory(prefix="python-lsp-intelligence-") as scratch:
            pyright_cfg = user_pyright_config(path) or default_pyright_config(path, Path(scratch))
            pyright = run([tools.basedpyright, "-p", str(pyright_cfg), str(path)])
        record(pyright, "basedpyright", path, out)
    return FileResult(out.findings, out.failures, rewrote)


def find_tools() -> Tools | str:
    """Absolute executable paths, or the name of the first tool that is not installed."""
    found: dict[str, str] = {}
    for name in INSTALL_HINTS:
        executable = shutil.which(name)
        if executable is None:
            return name
        found[name] = executable
    return Tools(found["ruff"], found["basedpyright"])


def bounded(text: str, reserve: int) -> str:
    """Cut text on a line boundary so it and reserve more characters fit under MAX_REPORT_CHARS.

    Says how many lines were dropped.
    """
    limit = MAX_REPORT_CHARS - reserve
    if len(text) <= limit:
        return text
    kept: list[str] = []
    size = 0
    lines = text.splitlines()
    for line in lines:
        if size + len(line) + 1 > limit:
            break
        kept.append(line)
        size += len(line) + 1
    return "\n".join(kept) + f"\n… {len(lines) - len(kept)} more lines\n"


def display(path: Path, base: Path | None) -> str:
    """Path relative to base when it lies under it, for short messages."""
    if base is not None:
        try:
            return path.relative_to(base).as_posix()
        except ValueError:
            return str(path)
    return str(path)


def names_of(paths: Iterable[Path], base: Path | None) -> str:
    """The paths as a comma-separated list for a message."""
    return ", ".join(display(path, base) for path in paths)


def tools_run(checked: list[Path]) -> str:
    """The tools the hook ran on checked: basedpyright skips notebooks."""
    if all(path.suffix == NOTEBOOK_SUFFIX for path in checked):
        return "ruff check --fix, ruff format"
    return "ruff check --fix, ruff format, basedpyright"


def user_message(parts: list[str]) -> str:
    """The JSON stdout with the one line the user sees."""
    return json.dumps({"systemMessage": f"{PLUGIN}: {' · '.join(parts)}"})


def arrival_note(count: int) -> str:
    """What the user is told when a command left more loose files than the hook checks."""
    return (
        f"not run on {count} Python files this command left outside a Git work tree "
        f"(more than the {MAX_FILES} checked per tool call)"
    )


def outcome_parts(
    checked: list[Path],
    results: list[FileResult],
    unchecked: list[Path],
    base: Path | None,
) -> list[str]:
    """What the user is told after the tools ran: what ran, what was formatted, what was found."""
    pairs = list(zip(checked, results, strict=True))
    rewritten = [path for path, result in pairs if result.rewrote]
    with_errors = [path for path, result in pairs if result.findings or result.failures]
    parts = [
        f"ran {tools_run(checked)} on {names_of(checked, base)}",
        f"reformatted {names_of(rewritten, base)}" if rewritten else "no formatting changes",
        f"errors in {names_of(with_errors, base)}, sent to Claude to fix"
        if with_errors
        else "no errors",
    ]
    if unchecked:
        parts.append(
            f"not run on {names_of(unchecked, base)} "
            f"(more than the {MAX_FILES} checked per tool call)",
        )
    return parts


def claude_report(checked: list[Path], results: list[FileResult], base: Path | None) -> str:
    """The stderr text Claude receives when the tools found errors; "" when there are none."""
    details = [text for result in results for text in (*result.findings, *result.failures)]
    if not details:
        return ""
    head = (
        f"{PLUGIN}'s post-edit hook ran {tools_run(checked)} on {names_of(checked, base)} "
        "and found errors:\n"
    )
    body = bounded(head + "\n".join(details) + "\n", len(CLAUDE_INSTRUCTION) + 1)
    return f"{body}{CLAUDE_INSTRUCTION}\n"


def changed_python(event: JsonObject) -> tuple[list[Path], str]:
    """The Python files to check, and the note about loose files left unchecked ("" for none)."""
    changed = candidates(event, int(time.time() * MS_PER_S))
    files = [path for path in changed.files if not skipped(path) and is_python(path)]
    if changed.walked is None:
        return files, ""
    verified, loose = own_changes(files, changed.walked)
    if len(loose) > MAX_FILES:
        return verified, arrival_note(len(loose))
    return [*verified, *loose], ""


def main() -> int:
    """Entry point: exit 0 when clean or not applicable, 2 when the tools found errors."""
    event = read_event()
    if event is None:
        return 0
    files, arrival = changed_python(event)
    notes = [arrival] if arrival else []
    if not files:
        if notes:
            _ = sys.stdout.write(user_message(notes))
        return 0
    base = project_dir(event)
    tools = find_tools()
    if isinstance(tools, str):
        missing = (
            f"not run on {names_of(files, base)}: {tools} is not installed "
            f"(install it with {INSTALL_HINTS[tools]})"
        )
        _ = sys.stdout.write(user_message([missing, *notes]))
        return 0
    checked, unchecked = files[:MAX_FILES], files[MAX_FILES:]
    results = [check_file(path, tools) for path in checked]
    _ = sys.stdout.write(user_message([*outcome_parts(checked, results, unchecked, base), *notes]))
    text = claude_report(checked, results, base)
    if text:
        _ = sys.stderr.write(text)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
