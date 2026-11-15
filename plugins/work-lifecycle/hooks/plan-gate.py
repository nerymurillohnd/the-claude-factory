#!/usr/bin/env python3
"""Plan gate for work-lifecycle: a Stop hook and the validator of its state file.

Gate mode, with no arguments: Claude Code runs it as a Stop hook registered by a skill and
writes the hook input on stdin. While the session's plan is executing, it blocks Claude from
ending its turn as long as any task lacks recorded evidence.

Validate mode, `plan-gate.py --validate <state file>`: Claude runs it after writing or
editing the state file. It prints each problem and exits 1, or prints that the file is valid.

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
SCRIPT = Path(__file__).resolve()
VALIDATE_ARGC = 2


class JsonObject(dict[str, object]):
    """A decoded JSON object, typed so isinstance narrows it."""


def _pairs(items: list[tuple[str, object]]) -> JsonObject:
    """Build each decoded object as a JsonObject."""
    return JsonObject(items)


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_pairs).decode


def _is_list(value: object) -> TypeGuard[list[object]]:
    """Whether a decoded value is a JSON array; its items are typed as plain objects."""
    return isinstance(value, list)


def _text(value: object) -> bool:
    """Whether a value is a non-empty string."""
    return isinstance(value, str) and value.strip() != ""


def _run_problems(name: str, label: str, value: object) -> list[str]:
    """Problems of one recorded run: absent, or a command with its real output."""
    if value is None:
        return []
    if not isinstance(value, JsonObject):
        return [f"{label}: {name} must be null or an object with command and output"]
    return [
        f"{label}: {name}.{field} must be a non-empty string"
        for field in ("command", "output")
        if not _text(value.get(field))
    ]


def _task_problems(index: int, item: object, seen: set[str]) -> list[str]:
    """Problems of one task."""
    if not isinstance(item, JsonObject):
        return [f"task at position {index}: must be an object"]
    task_id = item.get("id")
    label = f"task {task_id}" if _text(task_id) else f"task at position {index}"
    found: list[str] = []
    if not isinstance(task_id, str) or not _text(task_id):
        found.append(f"{label}: id must be a non-empty string")
    elif task_id in seen:
        found.append(f"{label}: duplicate id")
    else:
        seen.add(task_id)
    found.extend(
        f"{label}: {field} is missing or empty"
        for field in ("title", "check")
        if not _text(item.get(field))
    )
    if not isinstance(item.get("test_first"), bool):
        found.append(f"{label}: test_first must be true or false")
    for name in RUNS:
        found.extend(_run_problems(name, label, item.get(name)))
    return found


def problems(data: object) -> list[str]:
    """Every way a decoded state file breaks the schema; empty when it is valid."""
    if not isinstance(data, JsonObject):
        return ["the state file must hold one JSON object"]
    found: list[str] = []
    if data.get("schema") != 1:
        found.append("schema must be 1")
    if not _text(data.get("plan")):
        found.append("plan must name the plan file's path, or reply when the plan is in the reply")
    status = data.get("status")
    if status not in STATUSES:
        found.append(f"status {status!r} is not one of {', '.join(STATUSES)}")
    tasks = data.get("tasks")
    if not _is_list(tasks) or not tasks:
        found.append("tasks must be a non-empty list")
        return found
    seen: set[str] = set()
    for index, item in enumerate(tasks, start=1):
        found.extend(_task_problems(index, item, seen))
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
                    f"Claude stop. Fix the file, then run python3 {SCRIPT} --validate {event.path}"
                )
            }
        )
    return emit(
        {
            "decision": "block",
            "reason": (
                f"The plan state file {event.path} is not valid: {detail}. Fix it, run "
                f"`python3 {SCRIPT} --validate {event.path}` until it reports the file valid, "
                "then continue the plan."
            ),
        }
    )


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
    if event.continuing and memo.exists() and memo.read_text(encoding="utf-8") == signature:
        forget(memo)
        return emit(
            {
                "systemMessage": (
                    "work-lifecycle plan gate stopped blocking: no task gained evidence since its "
                    f"last block. Still pending: {'; '.join(lines)}"
                )
            }
        )
    _ = memo.write_text(signature, encoding="utf-8")
    listing = "\n".join(f"- {line}" for line in lines)
    return emit(
        {
            "decision": "block",
            "reason": (
                f"The plan is executing and these tasks have no recorded evidence:\n{listing}\n"
                f"Run each task's check, record its command and real output in {event.path}, and "
                "validate the file. If you must wait for the user's authorization, set status to "
                "awaiting-authorization first; every task needs its evidence before status "
                "becomes done."
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


def validate(target: str) -> int:
    """Report whether one state file is valid."""
    path = Path(target)
    _, found = load(path)
    if found:
        _ = sys.stdout.write("".join(f"{path}: {problem}\n" for problem in found))
        return 1
    _ = sys.stdout.write(f"{path}: valid\n")
    return 0


def main(argv: list[str]) -> int:
    """Run the gate, or the validator with --validate."""
    if len(argv) == VALIDATE_ARGC and argv[0] == "--validate":
        return validate(argv[1])
    if argv:
        return fail("usage: plan-gate.py [--validate <state file>]")
    return gate(sys.stdin.read())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
