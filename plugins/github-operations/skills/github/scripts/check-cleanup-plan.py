#!/usr/bin/env python3
"""Check a cleanup plan before it is shown for Gate 2.

Usage: check-cleanup-plan.py PLAN_PATH

Each action is a `### A-NN <title>` heading followed by these list items:
`- **Class**: <class>`, `- **Affected items**: ...`, `- **Containment check**: <command or n/a>`,
`- **Force**: none | approved by name: <flag>[, <flag>...]` and `- **Commands**:` with a fenced
block. Checks: A-01 is the backup and comes first; every field is present and every class known;
classes keep their order; every deletion has a containment check; every SHA in Affected items has
40 characters; every force flag in the commands is approved by name.
Exit 0 = pass, 1 = at least one finding (one line each on stderr), 2 = usage error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import shlex
import sys

CLASSES = (
    "prep",
    "investigate",
    "fix",
    "integrate",
    "publish",
    "local-delete",
    "remote-delete",
    "github-close",
    "external-unlink",
    "files",
    "maintenance",
    "history-rewrite",
)
DELETIONS = ("local-delete", "remote-delete")
FIELDS = ("Class", "Affected items", "Containment check", "Force")
FULL_SHA = 40
HEADING = re.compile(r"^### (A-\d{2,})\b(.*)$")
FIELD = re.compile(r"^- \*\*([A-Za-z ]+)\*\*:\s*(.*)$")
SHA_LIKE = re.compile(r"\b[0-9a-f]{7,40}\b")
APPROVED = "approved by name:"
FORCE_FLAGS = ("--force", "-f", "--force-with-lease", "-D", "--no-verify")


@dataclass
class Action:
    """One action of the plan: its ID, title, fields and command lines."""

    ident: str
    title: str
    fields: dict[str, str] = field(default_factory=dict[str, str])
    commands: list[str] = field(default_factory=list[str])


def parse(text: str) -> list[Action]:
    """Return the plan's actions in order."""
    actions: list[Action] = []
    fenced = False
    for line in text.splitlines():
        heading = HEADING.match(line)
        if heading:
            actions.append(Action(heading.group(1), heading.group(2).strip()))
            fenced = False
        elif not actions:
            continue
        elif line.startswith("```"):
            fenced = not fenced
        elif fenced:
            actions[-1].commands.append(line)
        elif item := FIELD.match(line):
            actions[-1].fields[item.group(1)] = item.group(2).strip()
    return actions


def force_flags(line: str) -> list[str]:
    """Return the force flags one command line uses."""
    try:
        words = shlex.split(line, comments=True)
    except ValueError:
        words = line.split()
    used = [w for w in words if w in FORCE_FLAGS or w.startswith("--force-with-lease=")]
    if "reset" in words and "--hard" in words:
        used.append("reset --hard")
    if "push" in words:
        used.extend(w for w in words if w.startswith("+"))
    return used


def approved_flags(force: str) -> list[str]:
    """Return the flags a Force field approves by name."""
    names = force.removeprefix(APPROVED)
    return [flag.strip() for flag in names.split(",")] if names != force else []


def check_action(action: Action) -> list[str]:
    """Return the findings of one action on its own."""
    found = [
        f"{action.ident}: missing field {name}" for name in FIELDS if name not in action.fields
    ]
    cls = action.fields.get("Class", "")
    if cls and cls not in CLASSES:
        found.append(f"{action.ident}: unknown class {cls}; classes: {', '.join(CLASSES)}")
    containment = action.fields.get("Containment check", "").lower()
    if cls in DELETIONS and containment in {"", "n/a", "none"}:
        found.append(f"{action.ident}: {cls} action has no containment check")
    shas = [m.group(0) for m in SHA_LIKE.finditer(action.fields.get("Affected items", ""))]
    found.extend(
        f"{action.ident}: SHA {sha} has {len(sha)} characters; write all 40"
        for sha in shas
        if len(sha) != FULL_SHA
    )
    approved = approved_flags(action.fields.get("Force", "none"))
    for line in action.commands:
        found.extend(
            f"{action.ident}: command uses {flag} but Force does not approve it by name"
            for flag in force_flags(line)
            if flag not in approved
        )
    return found


def check_plan(actions: list[Action]) -> list[str]:
    """Return the findings of the whole plan."""
    if not actions:
        return ["the plan has no action: write each one as ### A-NN <title>"]
    found: list[str] = []
    first = actions[0]
    is_backup = first.fields.get("Class") == "prep" and "backup" in first.title.lower()
    if first.ident != "A-01" or not is_backup:
        found.append(
            f"A-01 must be the backup and the first action; found {first.ident} {first.title}"
        )
    last = 0
    for action in actions:
        found.extend(check_action(action))
        cls = action.fields.get("Class", "")
        if cls in CLASSES:
            index = CLASSES.index(cls)
            if index < last:
                order = ", ".join(CLASSES)
                message = f"class {cls} is out of order after {CLASSES[last]}; order: {order}"
                found.append(f"{action.ident}: {message}")
            last = max(last, index)
    return found


def main() -> int:
    """Read the plan, run the checks and report."""
    paths = sys.argv[1:]
    if len(paths) != 1:
        _ = sys.stderr.write("usage: check-cleanup-plan.py PLAN_PATH\n")
        return 2
    try:
        text = Path(paths[0]).read_text(encoding="utf-8")
    except OSError as error:
        _ = sys.stderr.write(f"check-cleanup-plan: cannot read the plan: {error}\n")
        return 2
    found = check_plan(parse(text))
    for message in found:
        _ = sys.stderr.write(message + "\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
