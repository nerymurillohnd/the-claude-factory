#!/usr/bin/env python3
"""New name: a plugin's new name is free to take before it is renamed to it.

A published name is permanent and a retired one is never reused, so <name> must be kebab-case,
must not be listed in `plugins` of .claude-plugin/marketplace.json, must not be a key of its
`renames` map, and plugins/<name> must not exist. Run it before `git mv plugins/<old>
plugins/<name>`: afterwards the folder exists and the check fails.

It reads marketplace.json and checks whether one folder exists: it never writes, starts a
process or uses the network.
Exit 0 = the name is free, 1 = it is not, 2 = wrong arguments (it takes one: the new name).
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
    plugins = marketplace.get("plugins")
    listed: set[str] = set()
    if isinstance(plugins, list):
        for entry in cast("list[object]", plugins):
            name = cast("dict[str, object]", entry).get("name") if isinstance(entry, dict) else None
            if isinstance(name, str):
                listed.add(name)
    renames = marketplace.get("renames")
    retired: set[str] = set()
    if isinstance(renames, dict):
        retired = set(cast("dict[str, object]", renames))
    return listed, retired, None


def check(root: Path, name: str) -> list[str]:
    """Every reason `name` cannot be the plugin's new name."""
    errors: list[str] = []
    if not KEBAB.fullmatch(name):
        errors.append(f'"{name}" is not kebab-case (lowercase letters, digits and single hyphens)')
    listed, retired, problem = marketplace_names(root)
    if problem is not None:
        return [*errors, f"[{MARKETPLACE}] {problem}"]
    if name in listed:
        errors.append(f'[{MARKETPLACE}] "{name}" is already listed in plugins')
    if name in retired:
        errors.append(
            f'[{MARKETPLACE}] "{name}" is a key of renames: a retired name is never reused'
        )
    if (root / "plugins" / name).exists():
        errors.append(f"[plugins/{name}] already exists")
    return errors


def main(argv: list[str]) -> int:
    """Print every reason the name is taken and return the exit code."""
    if len(argv) != 1:
        _ = sys.stderr.write("usage: check-new-name.py <new-name>\n")
        return 2
    errors = check(repo_root(), argv[0])
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    _ = sys.stdout.write(f'✔ "{argv[0]}" is free to take as a plugin name\n')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
