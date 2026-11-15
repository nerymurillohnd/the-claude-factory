#!/usr/bin/env python3
"""PreToolUse guard: Nery decides every write that could loosen a quality gate.

Protected does not mean forbidden: the guard answers "ask" (a permission prompt
for Nery, with the reason), and the write goes ahead once Nery approves. It asks
when:
- an Edit, Write or NotebookEdit call touches a protected file: lint, format,
  type-check and workflow-audit configuration, the project instructions and
  settings, the CI workflows, or this guard itself;
- an Edit, Write or NotebookEdit call adds an inline suppression (noqa,
  type: ignore, biome-ignore, ts-ignore, shellcheck disable and similar): a line
  holding one that the text it replaces didn't have, so swapping one
  suppression for another counts too;
- a Bash command names a protected file and can write it (a redirect, tee,
  sed -i, cp, mv, rm, an inline script, a git command that rewrites files), or
  can rewrite the whole tree (a formatter's --write or --fix on ".", git stash,
  git reset --hard, git clean).

The Bash check reads the command's words, so a command that reaches a file by
other means (a path built at run time, a script file, an npm script) passes.
It is a barrier for Claude, not a security boundary.

It stays silent otherwise, so the normal permission flow decides. Input it
cannot read blocks the call (exit 2), because a guard must fail closed.
"""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import sys

# relative() folds case, so these are compared folded too.
PROTECTED_NAMES = (
    "ruff.toml",
    ".shellcheckrc",
    "biome.jsonc",
    "pyrightconfig.json",
    "scripts/pyrightconfig.json",
    "tsconfig.json",
    "tsconfig.base.json",
    ".editorconfig",
    ".github/zizmor.yml",
    "package.json",
    "pyproject.toml",
    ".claude/CLAUDE.md",
    ".claude/settings.json",
    ".claude/settings.local.json",
)
PROTECTED = frozenset(name.casefold() for name in PROTECTED_NAMES)
PROTECTED_DIRS = tuple(name.casefold() for name in (".github/workflows/", ".claude/hooks/"))
SUPPRESSION = re.compile(
    r"#\s*noqa\b|#\s*ruff\s*:\s*noqa|#\s*type\s*:\s*ignore|#\s*pyright\s*:\s*(ignore|basic)"
    r"|#\s*mypy\s*:\s*ignore|#\s*nosec\b|#\s*pragma\s*:\s*no\s*cover|#\s*fmt\s*:\s*(off|skip)"
    r"|biome-ignore|@ts-ignore|@ts-expect-error|@ts-nocheck|eslint-disable|prettier-ignore"
    r"|shellcheck\s+disable\s*=",
    re.IGNORECASE,
)

# Bash words that write the files they name.
WRITE_COMMANDS = frozenset(
    {"tee", "cp", "mv", "rm", "truncate", "dd", "install", "ln", "chmod", "chown", "touch"}
    | {"patch", "rsync", "unlink"}
)
# Interpreters run inline code, which can write any file the command names.
INTERPRETERS = frozenset({"python", "python3", "node", "perl", "ruby", "deno", "bash", "sh", "zsh"})
INTERPRETERS |= {"awk", "gawk"}
REDIRECTS = frozenset({">", ">>", ">|", "&>", "&>>"})
GIT_WRITES = frozenset(
    {"checkout", "restore", "apply", "rm", "mv", "reset", "stash", "revert", "merge", "pull"}
    | {"cherry-pick", "am", "rebase", "clean", "switch"}
)
# git subcommands that rewrite the tracked files without naming them.
GIT_TREE_WRITES = frozenset({"stash", "clean"})
WRITE_FLAGS = frozenset({"--write", "--fix", "--fix-only", "--apply", "--apply-unsafe", "-w"})
FORMATTERS = frozenset({"ruff", "biome", "prettier", "dprint", "shfmt"})
WHOLE_TREE = frozenset({".", "./", "*"})
BOUNDARY_BEFORE = r"(?:^|(?<=[\s'\"`=(;|&<>]))"
BOUNDARY_AFTER = r"(?=$|[\s'\"`;|&)<>,])"


def block(reason: str) -> None:
    """Fail closed: exit 2 blocks the call and shows the reason to Claude."""
    _ = sys.stderr.write(f"guard-quality-gates: {reason}\n")
    sys.exit(2)


def ask(reason: str) -> None:
    """Send the call to Nery's permission prompt with the reason."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }
    _ = sys.stdout.write(json.dumps(out))
    sys.exit(0)


def relative(file_path: str, root: str) -> str | None:
    """Return file_path relative to the project root, or None when outside it."""
    # Resolve symlinks and "..", and fold case: macOS file systems ignore case,
    # so RUFF.toml there is ruff.toml.
    norm = os.path.realpath(file_path.replace("\\", "/"))
    root_norm = os.path.realpath(root.replace("\\", "/").rstrip("/"))
    try:
        rel = PurePosixPath(norm).relative_to(root_norm)
    except ValueError:
        return None
    return rel.as_posix().casefold()


def markers(text: object) -> Counter[str]:
    """Return each line that holds a suppression marker, stripped, with how often it occurs."""
    if not isinstance(text, str):
        return Counter()
    return Counter(line.strip() for line in text.splitlines() if SUPPRESSION.search(line))


def added(after: object, before: object) -> int:
    """Count the suppression lines in after that before didn't have."""
    return sum((markers(after) - markers(before)).values())


def cell_source(path: str, cell_id: object) -> str:
    """Return the current source of a notebook cell, or '' when it can't be read."""
    try:
        notebook: object = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    cells = notebook.get("cells") if isinstance(notebook, dict) else None
    for cell in cells if isinstance(cells, list) else []:
        if isinstance(cell, dict) and cell.get("id") == cell_id:
            source = cell.get("source")
            if isinstance(source, list):
                return "".join(part for part in source if isinstance(part, str))
            return source if isinstance(source, str) else ""
    return ""


def added_suppressions(tool: str, tool_input: dict[str, object], path: str) -> int:
    """Return how many suppression lines the call adds."""
    if tool == "Edit":
        return added(tool_input.get("new_string"), tool_input.get("old_string"))
    if tool == "Write":
        before = ""
        try:
            before = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            before = ""
        return added(tool_input.get("content"), before)
    if tool == "NotebookEdit":
        # A new cell has no previous source; an edited cell is compared with its own.
        inserting = tool_input.get("edit_mode") == "insert"
        before = "" if inserting else cell_source(path, tool_input.get("cell_id"))
        return added(tool_input.get("new_source"), before)
    return 0


def words(command: str) -> list[str]:
    """Split a command into its shell words and operators, quotes removed, case folded."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return [word.casefold() for word in lexer]
    except ValueError:
        # Unbalanced quotes: fall back to splitting on blanks and operators.
        return [w for w in re.split(r"[\s;|&()<>]+", command.casefold()) if w]


def protected_named(command: str, root: str) -> str | None:
    """Return the first protected file or folder the command names, or None."""
    prefix = r"(?:\./)?" + (f"(?:{re.escape(root.casefold().rstrip('/'))}/)?" if root else "")
    names = [re.escape(name) + BOUNDARY_AFTER for name in sorted(PROTECTED, key=len)[::-1]]
    dirs = [re.escape(d.rstrip("/")) + r"(?:/|" + BOUNDARY_AFTER + ")" for d in PROTECTED_DIRS]
    pattern = re.compile(BOUNDARY_BEFORE + prefix + "(" + "|".join(names + dirs) + ")")
    for text in (command.casefold(), " ".join(words(command))):
        found = pattern.search(text)
        if found:
            return found[1].rstrip("/")
    return None


def bash_writes(tokens: list[str]) -> bool:
    """Return whether the command's words can write a file they name."""
    for index, token in enumerate(tokens):
        name = token.rsplit("/", 1)[-1]
        following = tokens[index + 1] if index + 1 < len(tokens) else ""
        if token in REDIRECTS and following != "/dev/null":
            return True
        if name in WRITE_COMMANDS or name in INTERPRETERS or name.startswith("python3."):
            return True
        if name in {"sed", "perl"} and any(t.startswith(("-i", "--in-place")) for t in tokens):
            return True
    return "git" in tokens and any(t in GIT_WRITES for t in tokens)


def bash_rewrites_tree(tokens: list[str]) -> bool:
    """Return whether the command can rewrite every file, protected ones included."""
    if "git" in tokens and (
        any(t in GIT_TREE_WRITES for t in tokens) or ("reset" in tokens and "--hard" in tokens)
    ):
        return True
    writes = any(t in WRITE_FLAGS for t in tokens) or (
        "format" in tokens and any(t.rsplit("/", 1)[-1] in FORMATTERS for t in tokens)
    )
    return writes and any(t in WHOLE_TREE for t in tokens)


def check_bash(tool_input: dict[str, object], root: str) -> None:
    """Ask before a Bash command writes a protected file; stay silent otherwise."""
    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        block("Bash input has no command, so the call is blocked.")
    tokens = words(command)
    target = protected_named(command, root)
    if target is not None and bash_writes(tokens):
        ask(
            f"This Bash command can write {target}, a protected file (quality gates, "
            "instructions, settings, CI or this guard). Nery decides every change to it."
        )
    if bash_rewrites_tree(tokens):
        ask(
            "This Bash command can rewrite every file in the tree, protected files included "
            "(quality gates, instructions, settings, CI or this guard). Nery decides."
        )
    sys.exit(0)


def main() -> None:
    """Read the hook input and decide."""
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        block("could not read the hook input as JSON, so the call is blocked.")
    if not isinstance(data, dict):
        block("the hook input is not a JSON object, so the call is blocked.")
    tool = data.get("tool_name")
    tool_input = data.get("tool_input")
    if not isinstance(tool, str) or not isinstance(tool_input, dict):
        block("the hook input has no tool_name or tool_input, so the call is blocked.")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or str(data.get("cwd") or "")
    if tool == "Bash":
        check_bash(tool_input, root)
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        block(f"{tool} input has no file path, so the edit is blocked.")
    rel = relative(path, root) if root else None

    if rel is not None and (rel in PROTECTED or rel.startswith(PROTECTED_DIRS)):
        ask(
            f"{rel} is a protected file (quality gates, instructions, settings, CI or this guard). "
            "Nery decides every change to it."
        )
    count = added_suppressions(tool, tool_input, path)
    if count > 0:
        ask(
            f"This edit adds {count} inline suppression(s) (noqa, type: ignore, biome-ignore, "
            f"ts-ignore, shellcheck disable or similar) to {rel or path}. "
            "Nery decides every suppression."
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
