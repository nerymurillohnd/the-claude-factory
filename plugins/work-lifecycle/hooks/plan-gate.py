#!/usr/bin/env python3
"""Plan gate for work-lifecycle: the Stop hook that holds an executing plan open.

Claude Code runs it as a Stop hook registered by a skill's frontmatter, with the hook input on
stdin; Claude never runs it. While the session's plan is executing, it blocks Claude from ending
its turn as long as any task lacks recorded evidence. It checks only what it reads; the planning
skill's validate-state.py checks the whole schema.

The state file lives at `<project>/.work-lifecycle/<session_id>.json`. Standard library only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, NamedTuple, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable

FOLDER = ".work-lifecycle"
STATUSES = ("planning", "executing", "awaiting-authorization", "done")
RUNS = ("evidence", "red", "green")
SESSION_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
RELEASE_AFTER = 3
VALIDATE = "the validate-state.py command of the planning-before-execution skill"


class JsonObject(dict[str, object]):
    """A decoded JSON object, typed so isinstance narrows it."""


def _pairs(items: list[tuple[str, object]]) -> JsonObject:
    """Build each decoded object as a JsonObject."""
    return JsonObject(items)


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_pairs).decode


def _is_list(value: object) -> TypeGuard[list[object]]:
    """Whether a decoded value is a JSON array; its items are typed as plain objects."""
    return isinstance(value, list)


def problems(data: object) -> list[str]:
    """What keeps the gate from reading a state file; the skill's validator checks the rest."""
    if not isinstance(data, JsonObject):
        return ["the state file must hold one JSON object"]
    found: list[str] = []
    status = data.get("status")
    if status not in STATUSES:
        found.append(f"status {status!r} is not one of {', '.join(STATUSES)}")
    tasks = data.get("tasks")
    if not _is_list(tasks) or not tasks:
        found.append("tasks must be a non-empty list")
        return found
    for index, item in enumerate(tasks, start=1):
        if not isinstance(item, JsonObject):
            found.append(f"task at position {index}: must be an object")
            continue
        found.extend(
            f"task at position {index}: {name} must be null or an object"
            for name in RUNS
            if item.get(name) is not None and not isinstance(item.get(name), JsonObject)
        )
    return found


def pending(data: JsonObject) -> list[str]:
    """One line per task that still lacks evidence, in plan order."""
    lines: list[str] = []
    tasks = data.get("tasks")
    if not _is_list(tasks):
        return lines
    for item in tasks:
        if not isinstance(item, JsonObject):
            continue
        wanted = ["evidence", "red", "green"] if item.get("test_first") is True else ["evidence"]
        missing = [name for name in wanted if item.get(name) is None]
        if missing:
            lines.append(f"task {item.get('id')} ({item.get('title')}): no {', '.join(missing)}")
    return lines


def load(path: Path) -> tuple[JsonObject | None, list[str]]:
    """Read and check a state file: the data when valid, otherwise its problems."""
    try:
        data = _decode(path.read_text(encoding="utf-8"))
    except OSError as error:
        return None, [f"cannot read the file: {error.strerror}"]
    except ValueError as error:
        return None, [f"not valid JSON: {error}"]
    found = problems(data)
    if found or not isinstance(data, JsonObject):
        return None, found
    return data, []


def emit(output: dict[str, str]) -> int:
    """Print the hook's JSON output and allow the hook to finish."""
    _ = sys.stdout.write(json.dumps(output))
    return 0


def fail(message: str) -> int:
    """Report a broken hook input: a non-blocking hook error."""
    _ = sys.stderr.write(f"work-lifecycle plan gate: {message}\n")
    return 1


def forget(memo: Path) -> None:
    """Drop the record of the last block."""
    memo.unlink(missing_ok=True)


class StopEvent(NamedTuple):
    """What the gate needs from one Stop hook input."""

    path: Path
    continuing: bool
    busy: bool


def read_event(raw: str) -> StopEvent | str:
    """Parse the hook input into a StopEvent, or say why it can't be used."""
    try:
        payload = _decode(raw)
    except ValueError:
        return "the hook input is not JSON"
    if not isinstance(payload, JsonObject):
        return "the hook input is not a JSON object"
    session = payload.get("session_id")
    if not isinstance(session, str) or SESSION_ID.fullmatch(session) is None:
        return "session_id is missing or holds characters other than letters, digits, - and _"
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd")
    if not isinstance(root, str) or not root:
        return "neither CLAUDE_PROJECT_DIR nor cwd names the project"
    background = payload.get("background_tasks")
    return StopEvent(
        path=Path(root) / FOLDER / f"{session}.json",
        continuing=payload.get("stop_hook_active") is True,
        busy=_is_list(background) and len(background) > 0,
    )


def unreadable(event: StopEvent, found: list[str]) -> int:
    """Block once on a state file the gate can't use; on the continuation, warn and allow."""
    detail = "; ".join(found)
    if event.continuing:
        forget(event.path.with_suffix(".gate"))
        return emit(
            {
                "systemMessage": (
                    f"work-lifecycle plan gate could not read {event.path} ({detail}), so it let "
                    f"Claude stop. Fix the file, then check it with {VALIDATE}."
                )
            }
        )
    return emit(
        {
            "decision": "block",
            "reason": (
                f"The plan state file {event.path} is not valid: {detail}. Fix it, run "
                f"{VALIDATE} until it reports the file valid, then continue the plan."
            ),
        }
    )


def previous_blocks(memo: Path, signature: str) -> int:
    """How many blocks in a row named exactly these pending tasks; 0 when none or unreadable."""
    try:
        count, _, recorded = memo.read_text(encoding="utf-8").partition("\n")
    except OSError:
        return 0
    if recorded != signature or not count.isdigit():
        return 0
    return int(count)


def decide(event: StopEvent, data: JsonObject) -> int:
    """Allow stopping, or block while executing tasks lack evidence."""
    memo = event.path.with_suffix(".gate")
    lines = pending(data) if data.get("status") == "executing" else []
    if not lines:
        forget(memo)
        return 0
    if event.busy:
        return 0
    signature = "\n".join(lines)
    blocks = previous_blocks(memo, signature) if event.continuing else 0
    if blocks >= RELEASE_AFTER:
        forget(memo)
        return emit(
            {
                "systemMessage": (
                    f"work-lifecycle plan gate stopped blocking: no task gained evidence in "
                    f"{RELEASE_AFTER} continuations. Still pending: {'; '.join(lines)}"
                )
            }
        )
    _ = memo.write_text(f"{blocks + 1}\n{signature}", encoding="utf-8")
    listing = "\n".join(f"- {line}" for line in lines)
    return emit(
        {
            "decision": "block",
            "reason": (
                f"The plan is executing and these tasks have no recorded evidence:\n{listing}\n"
                f"Run each task's check, record its command and real output in {event.path}, and "
                "validate the file. If you must stop for the user (a question, a decision or an "
                "authorization), set status to awaiting-authorization first; every task needs its "
                "evidence before status becomes done."
            ),
        }
    )


def gate(raw: str) -> int:
    """Decide one Stop event."""
    event = read_event(raw)
    if isinstance(event, str):
        return fail(event)
    if not event.path.exists():
        return 0
    data, found = load(event.path)
    if data is None:
        return unreadable(event, found)
    return decide(event, data)


def main(argv: list[str]) -> int:
    """Run the gate on the hook input from stdin."""
    if argv:
        return fail("takes no arguments; Claude Code writes the hook input on stdin")
    return gate(sys.stdin.read())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
