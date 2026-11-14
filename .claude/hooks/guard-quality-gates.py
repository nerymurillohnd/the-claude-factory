#!/usr/bin/env python3
"""PreToolUse guard: Nery decides every edit that could loosen a quality gate.

It answers "ask" (a permission prompt for Nery, with the reason) when an Edit,
Write or NotebookEdit call:
- touches a protected file: lint, format, type-check and workflow-audit
  configuration, the project instructions and settings, the CI workflows, or
  this guard itself;
- adds an inline suppression (noqa, type: ignore, biome-ignore, ts-ignore,
  shellcheck disable and similar) beyond what the file already had.

It stays silent otherwise, so the normal permission flow decides. Input it
cannot read blocks the call (exit 2), because a guard must fail closed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import sys

PROTECTED = (
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
PROTECTED_DIRS = (
    ".github/workflows/",
    ".claude/hooks/",
)
SUPPRESSION = re.compile(
    r"#\s*noqa\b|#\s*ruff\s*:\s*noqa|#\s*type\s*:\s*ignore|#\s*pyright\s*:\s*(ignore|basic)"
    r"|#\s*mypy\s*:\s*ignore|#\s*nosec\b|#\s*pragma\s*:\s*no\s*cover|#\s*fmt\s*:\s*(off|skip)"
    r"|biome-ignore|@ts-ignore|@ts-expect-error|@ts-nocheck|eslint-disable|prettier-ignore"
    r"|shellcheck\s+disable\s*=",
    re.IGNORECASE,
)


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


def count(text: object) -> int:
    """Count suppression markers in a string."""
    return len(SUPPRESSION.findall(text)) if isinstance(text, str) else 0


def added_suppressions(tool: str, tool_input: dict[str, object], path: str) -> int:
    """Return how many suppression markers the call adds."""
    if tool == "Edit":
        return count(tool_input.get("new_string")) - count(tool_input.get("old_string"))
    if tool == "Write":
        before = ""
        try:
            before = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            before = ""
        return count(tool_input.get("content")) - count(before)
    if tool == "NotebookEdit":
        return count(tool_input.get("new_source"))
    return 0


def main() -> None:
    """Read the hook input and decide."""
    try:
        data = json.load(sys.stdin)
    except ValueError, OSError:
        block("could not read the hook input as JSON, so the edit is blocked.")
    if not isinstance(data, dict):
        block("the hook input is not a JSON object, so the edit is blocked.")
    tool = data.get("tool_name")
    tool_input = data.get("tool_input")
    if not isinstance(tool, str) or not isinstance(tool_input, dict):
        block("the hook input has no tool_name or tool_input, so the edit is blocked.")
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        block(f"{tool} input has no file path, so the edit is blocked.")
    root = os.environ.get("CLAUDE_PROJECT_DIR") or str(data.get("cwd") or "")
    rel = relative(path, root) if root else None

    if rel is not None and (rel in PROTECTED or rel.startswith(PROTECTED_DIRS)):
        ask(
            f"{rel} is a protected file (quality gates, instructions, settings, CI or this guard). "
            "Nery decides every change to it."
        )
    added = added_suppressions(tool, tool_input, path)
    if added > 0:
        ask(
            f"This edit adds {added} inline suppression(s) (noqa, type: ignore, biome-ignore, "
            f"ts-ignore, shellcheck disable or similar) to {rel or path}. "
            "Nery decides every suppression."
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
