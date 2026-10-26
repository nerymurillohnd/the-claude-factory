#!/usr/bin/env python3
"""Marketplace unversioned: .claude-plugin/marketplace.json carries no version anywhere.

Plugins are versioned in their own plugin.json; the marketplace is never versioned. This fails
when marketplace.json has a top-level `version`, a `metadata.version`, or a `version` on any
entry of `plugins`. Each error names the field that holds it.

It reads marketplace.json only: it never writes, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
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
_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def check(root: Path) -> list[str]:
    """Every field of marketplace.json that holds a version."""
    path = root / MARKETPLACE
    try:
        data = _decode(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"[{MARKETPLACE}] cannot be read as JSON: {e}"]
    if not isinstance(data, dict):
        return [f"[{MARKETPLACE}] must be a JSON object"]
    marketplace = cast("dict[str, object]", data)
    errors: list[str] = []
    remove = "remove it: plugins are versioned in their plugin.json"
    if "version" in marketplace:
        errors.append(f"[{MARKETPLACE}] has a top-level version; {remove}")
    metadata = marketplace.get("metadata")
    if isinstance(metadata, dict) and "version" in metadata:
        errors.append(f"[{MARKETPLACE}] has metadata.version; {remove}")
    plugins = marketplace.get("plugins")
    if isinstance(plugins, list):
        for index, entry in enumerate(cast("list[object]", plugins)):
            if isinstance(entry, dict) and "version" in entry:
                name = cast("dict[str, object]", entry).get("name", index)
                errors.append(f"[{MARKETPLACE}] plugins entry {name} has a version; {remove}")
    return errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: check-marketplace-unversioned.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Marketplace version check failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {MARKETPLACE} carries no version\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
