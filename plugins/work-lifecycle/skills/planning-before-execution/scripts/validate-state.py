#!/usr/bin/env python3
"""Validate a work-lifecycle plan state file before execution starts, and after each edit.

Claude runs it as `validate-state.py <state file>`. It prints every problem it finds and exits 1,
or prints that the file is valid and exits 0. Standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable

STATUSES = ("planning", "executing", "awaiting-authorization", "done")
RUNS = ("evidence", "red", "green")
ARGC = 1


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


def main(argv: list[str]) -> int:
    """Report whether one state file is valid."""
    if len(argv) != ARGC:
        _ = sys.stderr.write("usage: validate-state.py <state file>\n")
        return 2
    path = Path(argv[0])
    _, found = load(path)
    if found:
        _ = sys.stdout.write("".join(f"{path}: {problem}\n" for problem in found))
        return 1
    _ = sys.stdout.write(f"{path}: valid\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
