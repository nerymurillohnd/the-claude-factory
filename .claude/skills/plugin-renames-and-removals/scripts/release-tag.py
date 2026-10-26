#!/usr/bin/env python3
"""Release tag: print the tag release.yml creates for a plugin at its current version.

Prints `<plugin>--v<version>` for the version in plugins/<plugin>/.claude-plugin/plugin.json,
the tag to look up with `gh release view` after the merge.

It reads that plugin.json only: it never writes, starts a process or uses the network.
Exit 0 = printed, 1 = no version found, 2 = wrong arguments (it takes one: the plugin name).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import sys
from typing import cast

_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def plugin_version(root: Path, name: str) -> str | None:
    """The plugin.json version, or None when it cannot be read."""
    path = root / "plugins" / name / ".claude-plugin" / "plugin.json"
    try:
        data = _decode(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    version = cast("dict[str, object]", data).get("version")
    return version if isinstance(version, str) and version else None


def main(argv: list[str]) -> int:
    """Print the tag, or why there is none."""
    if len(argv) != 1:
        _ = sys.stderr.write("usage: release-tag.py <plugin>\n")
        return 2
    version = plugin_version(repo_root(), argv[0])
    if version is None:
        _ = sys.stderr.write(f"✖ No version found for {argv[0]}\n")
        return 1
    _ = sys.stdout.write(f"{argv[0]}--v{version}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
