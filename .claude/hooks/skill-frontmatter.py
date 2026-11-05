#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["ruamel.yaml>=0.19.1"]
# ///
"""PreToolUse and PostToolUse hook: keep every SKILL.md frontmatter strict, portable YAML.

Claude Code reads a skill's frontmatter leniently (an unquoted ": " inside a description loads),
but other Agent Skills clients do not: the `skills` CLI parses it with the strict `yaml` package
and silently drops a skill whose frontmatter fails (https://github.com/mintlify/docs/issues/6061).
So every SKILL.md this repository writes must parse as strict YAML 1.2.

- PreToolUse on Write or Edit: builds the file as the call would leave it (the Write content, or
  the current file with the Edit applied) and denies the call when its frontmatter fails, with
  the errors and the frontmatter as written, so Claude fixes the call before anything is saved.
- PostToolUse on Write or Edit: reads the file as saved and, when its frontmatter fails, adds the
  errors and the frontmatter to the tool result (decision "block"), so Claude reads them and fixes
  the file. It is the safety net for what PreToolUse could not rebuild.

Checks, from https://agentskills.io/specification and
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices:
the file opens with a `---` line and a closing `---` line; the block parses as strict YAML 1.2
into one mapping with no duplicate key; `name` and `description` are present and are text, not a
number, boolean, date or null; `name` has at most 64 characters of a-z, 0-9 and single hyphens,
neither first nor last, and equals its directory; `description` is not empty, has at most 1024
characters and holds no XML tag.

Any other file, and any input it cannot read, goes ahead untouched: the hook only ever speaks
about a SKILL.md. Exit 0 always; the decision is in the JSON on stdout.
Maintainer tooling: uv runs it from its inline metadata, as the validators run.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

from ruamel.yaml import YAML
from ruamel.yaml.error import MarkedYAMLError, YAMLError

SKILL_FILE = "SKILL.md"
FENCE = "---"
MAX_NAME = 64
MAX_DESCRIPTION = 1024
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
XML_TAG = re.compile(r"</?[A-Za-z][^<>]*>")
FIX_HINT = (
    "Quote a value that holds ': ' or ' #', or write it without them; keep `name` and "
    "`description` as plain text; remove the duplicate key."
)


def frontmatter(text: str) -> tuple[str, int] | None:
    """The YAML between the opening and closing `---` lines and its first line number, or None."""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != FENCE:
        return None
    for end in range(1, len(lines)):
        if lines[end].rstrip() == FENCE:
            return "\n".join(lines[1:end]) + "\n", 2
    return None


def parse(text: str) -> dict[object, object] | str:
    """The frontmatter as a mapping, or why it is missing or not strict YAML 1.2."""
    block = frontmatter(text)
    if block is None:
        return 'no frontmatter: the file must open with a "---" line and close it with another'
    source, first_line = block
    reader = YAML(typ="safe", pure=True)
    reader.version = (1, 2)
    try:
        data: object = reader.load(source)
    except MarkedYAMLError as e:
        mark = e.problem_mark
        where = f"line {mark.line + first_line}, column {mark.column + 1}: " if mark else ""
        return f"not strict YAML: {where}{' '.join(str(e.problem or e).split())}"
    except YAMLError as e:
        return f"not strict YAML: {' '.join(str(e).split())}"
    if not isinstance(data, dict):
        return "the frontmatter must be a mapping of keys to values"
    return data


def name_problems(name: object, skill_dir: str) -> list[str]:
    """Why `name` is not a short, plain name equal to its directory."""
    if not isinstance(name, str):
        return [f'"name" must be text, not {type(name).__name__}']
    found: list[str] = []
    if len(name) > MAX_NAME:
        found.append(f'"name" has {len(name)} characters; the limit is {MAX_NAME}')
    if not NAME_PATTERN.fullmatch(name):
        found.append('"name" may hold only a-z, 0-9 and single hyphens, neither first nor last')
    if name != skill_dir:
        found.append(f'"name" "{name}" must equal its directory "{skill_dir}"')
    return found


def description_problems(description: object) -> list[str]:
    """Why `description` is not non-empty text within the limit and free of XML tags."""
    if not isinstance(description, str):
        return [f'"description" must be text, not {type(description).__name__}']
    found: list[str] = []
    if not description.strip():
        found.append('"description" is empty')
    if len(description) > MAX_DESCRIPTION:
        found.append(
            f'"description" has {len(description)} characters; the limit is {MAX_DESCRIPTION}'
        )
    if XML_TAG.search(description):
        found.append('"description" holds an XML tag')
    return found


def problems(text: str, skill_dir: str) -> list[str]:
    """Why this SKILL.md text fails, each as one line; empty when it passes."""
    data = parse(text)
    if isinstance(data, str):
        return [data]
    return name_problems(data.get("name"), skill_dir) + description_problems(
        data.get("description")
    )


def numbered_frontmatter(text: str) -> str:
    """The frontmatter lines with their line numbers, as `head` would show them."""
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == FENCE), min(len(lines), 20))
    return "\n".join(f"{i + 1:>4}  {lines[i]}" for i in range(min(end + 1, len(lines))))


def edited_text(path: Path, tool_input: dict[str, object]) -> str | None:
    """The file as an Edit call would leave it, or None when it cannot be rebuilt here."""
    old, new = tool_input.get("old_string"), tool_input.get("new_string")
    if not isinstance(old, str) or not isinstance(new, str) or not old:
        return None
    try:
        current = path.read_text(encoding="utf-8")
    except OSError, ValueError:
        return None
    if tool_input.get("replace_all") is True:
        return current.replace(old, new) if old in current else None
    return current.replace(old, new, 1) if current.count(old) == 1 else None


def report(path: Path, text: str, found: list[str]) -> str:
    """The message Claude reads: the file, each problem, the frontmatter and the fix."""
    listed = "\n".join(f"- {p}" for p in found)
    return (
        f"{path} frontmatter fails strict YAML checks:\n{listed}\n\n"
        f"Frontmatter as written:\n{numbered_frontmatter(text)}\n\n{FIX_HINT}"
    )


def planned_text(tool: object, path: Path, tool_input: dict[str, object]) -> str | None:
    """The file as a Write or Edit call would leave it, or None when it cannot be rebuilt."""
    content = tool_input.get("content")
    if tool == "Write":
        return content if isinstance(content, str) else None
    if tool == "Edit":
        return edited_text(path, tool_input)
    return None


def saved_text(path: Path) -> str | None:
    """The file as saved, or None when it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError, ValueError:
        return None


def before(event: dict[str, object], path: Path, tool_input: dict[str, object]) -> object:
    """PreToolUse: deny the call when the file it would leave fails."""
    text = planned_text(event.get("tool_name"), path, tool_input)
    found = problems(text, path.parent.name) if text is not None else []
    if text is None or not found:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Not saved. " + report(path, text, found),
        }
    }


def after(path: Path) -> object:
    """PostToolUse: add the problems of the saved file to the tool result."""
    text = saved_text(path)
    found = problems(text, path.parent.name) if text is not None else []
    if text is None or not found:
        return None
    return {
        "decision": "block",
        "reason": "Saved with defects: fix them now. " + report(path, text, found),
    }


def decide(event: dict[str, object]) -> object:
    """The hook's JSON answer for one event, or None to let it go ahead silently."""
    tool_input = event.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(tool_input, dict) or not isinstance(file_path, str):
        return None
    path = Path(file_path)
    if path.name != SKILL_FILE:
        return None
    match event.get("hook_event_name"):
        case "PreToolUse":
            return before(event, path, tool_input)
        case "PostToolUse":
            return after(path)
        case _:
            return None


def main() -> int:
    """Read the hook event on stdin and print the decision, if any."""
    try:
        event = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    answer = decide(event) if isinstance(event, dict) else None
    if answer is not None:
        _ = sys.stdout.write(json.dumps(answer) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
