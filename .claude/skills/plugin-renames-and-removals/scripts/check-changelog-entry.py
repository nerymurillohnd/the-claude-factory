#!/usr/bin/env python3
"""Changelog entry: the plugin's CHANGELOG.md has a non-empty section for its current version.

The release notes users read and the GitHub Release body come from the `## [X.Y.Z]` section of
plugins/<plugin>/CHANGELOG.md for the version in its plugin.json. This fails when the manifest
or its version is missing, when the changelog is missing, or when that section is missing or
empty.

It reads the plugin's plugin.json and CHANGELOG.md only: it never writes, starts a process or
uses the network.
Exit 0 = pass, 1 = at least one error, 2 = wrong arguments (it takes one: the plugin name).
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

_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def changelog_section(text: str, version: str) -> str | None:
    """Body of the `## [version]` section, stripped; None when there is no such heading."""
    pattern = rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]:|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


def manifest_version(manifest: Path) -> tuple[str | None, str | None]:
    """The plugin.json version, or None and why it cannot be read."""
    if not manifest.is_file():
        return None, "not found"
    try:
        data = _decode(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"is not valid JSON: {e}"
    if not isinstance(data, dict):
        return None, "is not a JSON object"
    version = cast("dict[str, object]", data).get("version")
    if not isinstance(version, str) or not version:
        return None, "has no version"
    return version, None


def check(root: Path, name: str) -> list[str]:
    """Why the plugin's current version has no usable changelog entry, if it has none."""
    scope = f"plugins/{name}"
    version, problem = manifest_version(root / scope / ".claude-plugin" / "plugin.json")
    if version is None:
        return [f"[{scope}] .claude-plugin/plugin.json {problem}"]
    changelog = root / scope / "CHANGELOG.md"
    if not changelog.is_file():
        return [f"[{scope}] CHANGELOG.md not found"]
    section = changelog_section(changelog.read_text(encoding="utf-8"), version)
    if section is None:
        return [f"[{scope}] CHANGELOG.md has no ## [{version}] section"]
    if not section:
        return [f"[{scope}] CHANGELOG.md section ## [{version}] is empty"]
    return []


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1:
        _ = sys.stderr.write("usage: check-changelog-entry.py <plugin>\n")
        return 2
    errors = check(repo_root(), argv[0])
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ plugins/{argv[0]}: CHANGELOG.md has an entry for its version\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
