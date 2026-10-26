#!/usr/bin/env python3
"""Plugin labels: print the `gh label create` command of each plugin's GitHub label.

Each plugin listed in .claude-plugin/marketplace.json has a `plugin: <name>` label. This prints
the command that creates or updates each one, in the form `scripts/sync-labels.mjs` runs it, so
the label a rename needs can be shown to Nery before he orders it written. Labels of retired
plugins stay on GitHub and are not printed.

It reads marketplace.json only: it never runs the commands it prints, never calls GitHub and
never writes.
Exit 0 = printed, 1 = marketplace.json cannot be read, 2 = called with arguments (it takes none).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import sys
from typing import cast

MARKETPLACE = ".claude-plugin/marketplace.json"
REPO_SLUG = "nerymurillohnd/the-claude-factory"
COLOR = "EDEDED"
_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def quoted(arg: str) -> str:
    """`arg` in double quotes when it holds a space, as JSON quotes it."""
    return json.dumps(arg) if " " in arg else arg


def commands(root: Path) -> tuple[list[str], str | None]:
    """One `gh label create` line per listed plugin, or why there are none."""
    try:
        data = _decode((root / MARKETPLACE).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [], f"[{MARKETPLACE}] cannot be read as JSON: {e}"
    plugins = cast("dict[str, object]", data).get("plugins") if isinstance(data, dict) else None
    if not isinstance(plugins, list):
        return [], f"[{MARKETPLACE}] plugins must be an array"
    lines: list[str] = []
    for entry in cast("list[object]", plugins):
        name = cast("dict[str, object]", entry).get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            continue
        args = [
            "label",
            "create",
            f"plugin: {name}",
            "--repo",
            REPO_SLUG,
            "--color",
            COLOR,
            "--description",
            f"Issues about the {name} plugin",
            "--force",
        ]
        lines.append("gh " + " ".join(quoted(a) for a in args))
    return lines, None


def main(argv: list[str]) -> int:
    """Print the commands, or why not."""
    if argv:
        _ = sys.stderr.write("usage: plugin-labels.py\n")
        return 2
    lines, problem = commands(repo_root())
    if problem is not None:
        _ = sys.stderr.write(f"✖ {problem}\n")
        return 1
    _ = sys.stdout.write("\n".join([*lines, f"✔ {len(lines)} plugin labels planned"]) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
