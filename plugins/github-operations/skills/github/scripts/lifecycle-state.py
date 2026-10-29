#!/usr/bin/env python3
"""Keep the PR lifecycle or cleanup state of one session in a file.

Usage:
  lifecycle-state.py write --data-dir DIR --session ID --set KEY=VALUE [--set KEY=VALUE ...]
  lifecycle-state.py read  --data-dir DIR --session ID
  lifecycle-state.py clear --data-dir DIR --session ID

The record is DIR/state/<ID>.json. `write` merges the pairs into it and stamps `updated` (UTC);
`read` prints it as JSON, or exits 1 when there is none; `clear` removes it.
Keys: kind (pr or cleanup), repository, pr, base, head, phase, approval, next_reference,
scratch, backup. Exit 2 on an unknown key, a bad value or a session ID that is not a plain name.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

KEYS = (
    "kind",
    "repository",
    "pr",
    "base",
    "head",
    "phase",
    "approval",
    "next_reference",
    "scratch",
    "backup",
)
KINDS = ("pr", "cleanup")
SESSION = re.compile(r"[A-Za-z0-9_-]+")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


class UsageError(Exception):
    """A bad argument or record: reported on stderr with exit 2."""


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    command: str = ""
    data_dir: Path = Path()
    session: str = ""
    pairs: list[str] | None = None


def parse_pairs(pairs: list[str]) -> dict[str, str]:
    """Return the KEY=VALUE pairs as a mapping, rejecting unknown keys and bad kinds."""
    if not pairs:
        msg = "write needs at least one --set KEY=VALUE"
        raise UsageError(msg)
    values: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            msg = f"not KEY=VALUE: {pair}"
            raise UsageError(msg)
        if key not in KEYS:
            msg = f"unknown key {key}; allowed: {', '.join(KEYS)}"
            raise UsageError(msg)
        if key == "kind" and value not in KINDS:
            msg = f"kind must be one of {', '.join(KINDS)}, not {value}"
            raise UsageError(msg)
        values[key] = value
    return values


def record_path(data_dir: Path, session: str) -> Path:
    """Return the record file of a session, rejecting an ID that is not a plain name."""
    if not SESSION.fullmatch(session):
        msg = f"session ID must be letters, digits, - or _, not {session}"
        raise UsageError(msg)
    return data_dir / "state" / f"{session}.json"


def load(path: Path) -> JsonObject:
    """Return the stored record, or an empty one when the file is absent."""
    if not path.exists():
        return JsonObject()
    value = _decode(path.read_text(encoding="utf-8"))
    if not isinstance(value, JsonObject):
        msg = f"{path} does not hold a JSON object"
        raise UsageError(msg)
    return value


def save(path: Path, record: JsonObject) -> None:
    """Write the record atomically, so a reader never sees half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".state-")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        _ = handle.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    _ = Path(tmp).replace(path)


def run(args: Args) -> int:
    """Run one command and return its exit code."""
    path = record_path(args.data_dir, args.session)
    if args.command == "read":
        if not path.exists():
            _ = sys.stderr.write(f"lifecycle-state: no record for session {args.session}\n")
            return 1
        _ = sys.stdout.write(json.dumps(load(path), indent=2, sort_keys=True) + "\n")
    elif args.command == "clear":
        path.unlink(missing_ok=True)
    else:
        values = parse_pairs(args.pairs or [])
        record = load(path)
        record.update(values)
        record["updated"] = datetime.now(UTC).isoformat(timespec="seconds")
        save(path, record)
    return 0


def main() -> int:
    """Parse the arguments and run the command."""
    parser = argparse.ArgumentParser(description="Keep one session's lifecycle state.")
    _ = parser.add_argument("command", choices=("write", "read", "clear"))
    _ = parser.add_argument("--data-dir", required=True, type=Path)
    _ = parser.add_argument("--session", required=True)
    _ = parser.add_argument("--set", action="append", dest="pairs")
    try:
        return run(parser.parse_args(namespace=Args()))
    except (UsageError, OSError, ValueError) as error:
        _ = sys.stderr.write(f"lifecycle-state: {error}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
