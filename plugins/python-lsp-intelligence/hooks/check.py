#!/usr/bin/env python3
"""Post-edit hook of python-lsp-intelligence: ruff check --fix, ruff format, basedpyright.

Reads one PostToolUse or PostToolUseFailure event on stdin, finds the Python files the
tool call changed, runs the tools on each one with the user's own configuration (the
plugin's defaults in hooks/defaults/ only when ruff or basedpyright would find none) and
reports: exit 0 with a systemMessage when everything passed, stderr and exit 2 when there
are findings or a tool could not run. Files of other languages are ignored in silence.
Python 3.9 or later, standard library only.
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
import time
from typing import TYPE_CHECKING, NamedTuple, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

PLUGIN = "python-lsp-intelligence"
PYTHON_SUFFIXES = frozenset({".py", ".pyi", ".pyw"})
NOTEBOOK_SUFFIX = ".ipynb"
SHEBANG = re.compile(r"^#!.*\b(python[0-9.]*|uv\s+run)\b")
SKIPPED_DIRS = frozenset({"node_modules", ".venv", "venv", "site-packages"})
PRUNED_DIRS = SKIPPED_DIRS | frozenset(
    {".git", "dist", "build", "__pycache__", ".ruff_cache", ".mypy_cache", ".cache"},
)
# A Bash command that rewrites more files than this gets the rest reported, not checked.
MAX_FILES = 20
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


def changed_since(project: Path, since_s: float) -> list[Path]:
    """Files under project modified after since_s: git's view in a work tree, else a pruned walk."""
    git = shutil.which("git")
    if git is not None:
        inside = run([git, "-C", str(project), "rev-parse", "--is-inside-work-tree"])
        if inside.code == 0:
            listed = run(
                [
                    git,
                    "-C",
                    str(project),
                    "ls-files",
                    "-z",
                    "--modified",
                    "--others",
                    "--exclude-standard",
                ],
            )
            paths = (project / rel for rel in listed.output.split("\0") if rel)
            return [path for path in paths if newer_than(path, since_s)]
    found: list[Path] = []
    for directory, subdirs, files in os.walk(project):
        subdirs[:] = [name for name in subdirs if name not in PRUNED_DIRS]
        paths = (Path(directory) / name for name in files)
        found.extend(path for path in paths if newer_than(path, since_s))
    return found


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


def candidates(event: JsonObject, now_ms: int) -> list[Path]:
    """The files the tool call may have changed, by tool name."""
    tool = text_at(event, "tool_name")
    if tool in {"Edit", "Write"}:
        return as_files([text_at(event, "tool_input", "file_path")])
    if tool == "NotebookEdit":
        return as_files([text_at(event, "tool_input", "notebook_path")])
    if tool != "Bash":
        return []
    changed = strings_at(event, "tool_response", "bashEditDiff", "changedFiles")
    if changed is not None:
        return as_files(changed)
    project = project_dir(event)
    if project is None:
        return []
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


def run(argv: list[str]) -> Run:
    """Run one command, capturing stdout and stderr together; never raises."""
    try:
        done = subprocess.run(
            argv,
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


def pyright_config(path: Path) -> Path:
    """The nearest pyrightconfig.json or pyproject.toml with a pyright table above path.

    The plugin's default config when there is none.
    """
    for directory in path.parents:
        config = directory / "pyrightconfig.json"
        if config.is_file():
            return config
        pyproject = directory / "pyproject.toml"
        if pyproject.is_file() and has_pyright_table(pyproject):
            return pyproject
    return DEFAULTS_DIR / "pyrightconfig.json"


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
        pyright = run([tools.basedpyright, "-p", str(pyright_config(path)), str(path)])
        record(pyright, "basedpyright", path, out)
    return FileResult(out.findings, out.failures, rewrote)


def find_tools() -> Tools | str:
    """Absolute executable paths, or the stderr message for the first missing one."""
    found: dict[str, str] = {}
    for name, hint in INSTALL_HINTS.items():
        executable = shutil.which(name)
        if executable is None:
            missing = f"{PLUGIN}: {name} is not installed, so no Python file was checked."
            return f"{missing} Install it: {hint}\n"
        found[name] = executable
    return Tools(found["ruff"], found["basedpyright"])


def bounded(text: str) -> str:
    """Cut text at MAX_REPORT_CHARS on a line boundary, saying how many lines were dropped."""
    if len(text) <= MAX_REPORT_CHARS:
        return text
    kept: list[str] = []
    size = 0
    lines = text.splitlines()
    for line in lines:
        if size + len(line) + 1 > MAX_REPORT_CHARS:
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


def report(
    checked: list[Path],
    results: list[FileResult],
    unchecked: list[Path],
    base: Path | None,
) -> str:
    """The stderr text for findings, failures and unchecked files; "" when all is clean."""
    parts = [text for result in results for text in (*result.findings, *result.failures)]
    if unchecked:
        names = "\n".join(f"  {display(path, base)}" for path in unchecked)
        summary = f"{len(unchecked)} more Python files changed and were not checked"
        parts.append(f"{summary}; run the toolchain on them:\n{names}")
    if not parts:
        return ""
    names = ", ".join(display(path, base) for path in checked)
    parts.append(f"Fix these findings in {names} before continuing; do not suppress them.")
    return "\n".join(parts) + "\n"


def success(
    event: JsonObject,
    checked: list[Path],
    results: list[FileResult],
    base: Path | None,
) -> str:
    """The JSON stdout for a clean run: a systemMessage, plus a re-read note after a rewrite."""
    names = ", ".join(display(path, base) for path in checked)
    notebooks_only = all(path.suffix == NOTEBOOK_SUFFIX for path in checked)
    tools = "ruff check, ruff format" if notebooks_only else "ruff check, ruff format, basedpyright"
    payload: dict[str, object] = {"systemMessage": f"{PLUGIN}: {tools} passed · {names}"}
    rewritten = [
        display(path, base) for index, path in enumerate(checked) if results[index].rewrote
    ]
    if rewritten:
        note = f"ruff reformatted {', '.join(rewritten)}; re-read before the next edit."
        payload["hookSpecificOutput"] = {
            "hookEventName": text_at(event, "hook_event_name") or "PostToolUse",
            "additionalContext": note,
        }
    return json.dumps(payload)


def main() -> int:
    """Entry point: exit 0 when clean or not applicable, 2 with findings or failures."""
    event = read_event()
    if event is None:
        return 0
    now_ms = int(time.time() * MS_PER_S)
    files = [path for path in candidates(event, now_ms) if not skipped(path) and is_python(path)]
    if not files:
        return 0
    tools = find_tools()
    if isinstance(tools, str):
        _ = sys.stderr.write(tools)
        return 2
    checked, unchecked = files[:MAX_FILES], files[MAX_FILES:]
    results = [check_file(path, tools) for path in checked]
    base = project_dir(event)
    text = report(checked, results, unchecked, base)
    if text:
        _ = sys.stderr.write(bounded(text))
        return 2
    _ = sys.stdout.write(success(event, checked, results, base))
    return 0


if __name__ == "__main__":
    sys.exit(main())
