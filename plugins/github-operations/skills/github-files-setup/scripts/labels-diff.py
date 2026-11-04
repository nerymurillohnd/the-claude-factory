#!/usr/bin/env python3
"""Compare a repository's labels with a labels file.

Usage: labels-diff.py --repo OWNER/REPO --labels PATH

Reads the repository's labels with `gh label list` and prints one JSON object on stdout:
`missing` (names in the file the repository lacks), `extra` (names the repository has and the
file does not) and `different` (same name, another color or description, as `want` and `have`).
Colors compare without case.
Exit 0 = nothing missing or different, 1 = something missing or different, 2 = usage error or
`gh` failed (its stderr is passed on).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TypeIs


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_array(value: object) -> TypeIs[list[object]]:
    """Report whether a decoded JSON value is an array."""
    return isinstance(value, list)


class Label:
    """One label: its name, its color in upper case and its description."""

    def __init__(self, item: object) -> None:
        """Read one label from a decoded JSON object."""
        if not isinstance(item, JsonObject):
            msg = f"a label is not a JSON object: {item!r}"
            raise TypeError(msg)
        name, color, description = item.get("name"), item.get("color", ""), item.get("description")
        if not isinstance(name, str) or not isinstance(color, str):
            msg = f"a label has no name or color string: {dict(item)!r}"
            raise TypeError(msg)
        self.name: str = name
        self.color: str = color.upper()
        self.description: str = description if isinstance(description, str) else ""

    def fields(self) -> dict[str, str]:
        """Return the fields that can differ."""
        return {"color": self.color, "description": self.description}


def labels(text: str) -> dict[str, Label]:
    """Return the labels of a JSON list, by name."""
    items = _decode(text)
    if not is_array(items):
        msg = "the labels are not a JSON list"
        raise TypeError(msg)
    found = [Label(item) for item in items]
    return {label.name: label for label in found}


def diff(want: dict[str, Label], have: dict[str, Label]) -> dict[str, list[object]]:
    """Return the missing, extra and different labels."""
    different: list[object] = [
        {"name": name, "want": label.fields(), "have": have[name].fields()}
        for name, label in want.items()
        if name in have and label.fields() != have[name].fields()
    ]
    return {
        "missing": [name for name in want if name not in have],
        "extra": [name for name in have if name not in want],
        "different": different,
    }


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    repo: str = ""
    labels: Path = Path()


def main() -> int:
    """Read both label sets, compare them and report."""
    parser = argparse.ArgumentParser(description="Compare a repository's labels with a file.")
    _ = parser.add_argument("--repo", required=True)
    _ = parser.add_argument("--labels", required=True, type=Path)
    args = parser.parse_args(namespace=Args())
    command = ["gh", "label", "list", "-R", args.repo, "--limit", "500"]
    command += ["--json", "name,color,description"]
    try:
        want = labels(args.labels.read_text(encoding="utf-8"))
        listed = subprocess.run(command, capture_output=True, text=True, check=False)
    except (OSError, ValueError, TypeError) as error:
        _ = sys.stderr.write(f"labels-diff: {error}\n")
        return 2
    if listed.returncode != 0:
        _ = sys.stderr.write(f"labels-diff: gh exited {listed.returncode}\n{listed.stderr}")
        return 2
    try:
        have = labels(listed.stdout)
    except (ValueError, TypeError) as error:
        _ = sys.stderr.write(f"labels-diff: cannot read gh's output: {error}\n")
        return 2
    report = diff(want, have)
    _ = sys.stdout.write(json.dumps(report, indent=2) + "\n")
    return 1 if report["missing"] or report["different"] else 0


if __name__ == "__main__":
    sys.exit(main())
