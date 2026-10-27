#!/usr/bin/env python3
"""Plugin name: a new plugin's name is free and unlike every name this marketplace uses.

<name> is taken when `plugins` of .claude-plugin/marketplace.json lists it, its `renames` map
has it as a key (a retired name is never reused), or plugins/<name> exists. It is similar to a
listed name or a plugins/ directory when the two are at most 2 edits apart, hold the same words
in another order, or the words of one are all words of the other. Run it before design, when
the name is chosen: a taken name is refused, and a similar one needs Nery's OK.

It reads marketplace.json and lists plugins/: it never writes, starts a process or uses the
network.
Exit 0 = free and unlike every name, 1 = taken or similar, 2 = wrong arguments (it takes one
kebab-case name).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import re
import sys
from typing import cast

MARKETPLACE = ".claude-plugin/marketplace.json"
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_EDITS = 2
USAGE = "usage: .claude/skills/building-plugins/scripts/check-plugin-name.py <name>\n"
_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def marketplace_names(root: Path) -> tuple[set[str], set[str], str | None]:
    """The listed names, the `renames` keys, and why marketplace.json cannot be read."""
    try:
        data = _decode((root / MARKETPLACE).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return set(), set(), f"cannot be read as JSON: {e}"
    if not isinstance(data, dict):
        return set(), set(), "must be a JSON object"
    marketplace = cast("dict[str, object]", data)
    listed: set[str] = set()
    plugins = marketplace.get("plugins")
    if isinstance(plugins, list):
        for entry in cast("list[object]", plugins):
            name = cast("dict[str, object]", entry).get("name") if isinstance(entry, dict) else None
            if isinstance(name, str):
                listed.add(name)
    renames = marketplace.get("renames")
    retired = set(cast("dict[str, object]", renames)) if isinstance(renames, dict) else set[str]()
    return listed, retired, None


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance between a and b."""
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (char_a != char_b))
            )
        previous = current
    return previous[-1]


def similarity(name: str, other: str) -> str | None:
    """Why name looks like other, or None when it does not."""
    words, other_words = set(name.split("-")), set(other.split("-"))
    if words == other_words:
        return "the same words in another order"
    if words < other_words or other_words < words:
        return "all the words of one are words of the other"
    if edit_distance(name, other) <= MAX_EDITS:
        return f"at most {MAX_EDITS} edits apart"
    return None


def check(root: Path, name: str) -> list[str]:
    """Every reason name is taken or similar to a name in use."""
    listed, retired, problem = marketplace_names(root)
    if problem is not None:
        return [f"[{MARKETPLACE}] {problem}"]
    plugins_dir = root / "plugins"
    folders = (
        {p.name for p in plugins_dir.iterdir() if p.is_dir()}
        if plugins_dir.is_dir()
        else set[str]()
    )
    errors: list[str] = []
    if name in listed:
        errors.append(f'taken: "{name}" is already listed in plugins of {MARKETPLACE}')
    if name in retired:
        errors.append(
            f'taken: "{name}" is a key of renames in {MARKETPLACE}: a retired name is never reused'
        )
    if name in folders:
        errors.append(f"taken: plugins/{name} already exists")
    if errors:
        return errors
    for other in sorted(listed | folders):
        reason = similarity(name, other)
        if reason is not None:
            errors.append(f'similar: "{other}" ({reason})')
    return errors


def main(argv: list[str]) -> int:
    """Print every reason the name is taken or similar and return the exit code."""
    if len(argv) != 1 or not KEBAB.fullmatch(argv[0]):
        _ = sys.stderr.write(
            USAGE + "The name is kebab-case: lowercase letters, digits and single hyphens.\n"
        )
        return 2
    errors = check(repo_root(), argv[0])
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    _ = sys.stdout.write(f'✔ "{argv[0]}" is free and unlike every name of this marketplace\n')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
