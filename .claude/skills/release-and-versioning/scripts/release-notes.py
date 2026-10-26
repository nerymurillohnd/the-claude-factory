#!/usr/bin/env python3
"""Release notes: print a plugin's release tag, or the notes its GitHub Release carries.

`release-notes.py <plugin> --tag` prints `<plugin>--v<version>` for the version in plugin.json.
`release-notes.py <plugin>` prints that version's CHANGELOG.md section followed by the update
command, the body release.yml publishes. It fails when the version or its entry is missing.

It reads the plugin's plugin.json and CHANGELOG.md only: it never writes, starts a process or
uses the network.
Exit 0 = printed, 1 = no version or no entry, 2 = wrong arguments.
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

MARKETPLACE_NAME = "the-claude-factory"
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


def plugin_version(plugin: Path) -> str | None:
    """The plugin.json version, or None when it cannot be read."""
    try:
        data = _decode((plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    version = cast("dict[str, object]", data).get("version")
    return version if isinstance(version, str) and version else None


def render(root: Path, name: str, *, tag_only: bool) -> tuple[str, str | None]:
    """The text to print, and None, or why there is none."""
    plugin = root / "plugins" / name
    version = plugin_version(plugin)
    if version is None:
        return "", f"No version found for {name}"
    tag = f"{name}--v{version}"
    if tag_only:
        return tag, None
    changelog = plugin / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8") if changelog.is_file() else ""
    body = changelog_section(text, version)
    if not body:
        return "", f"No CHANGELOG entry for {tag}"
    install = f"```bash\nclaude plugin update {name}@{MARKETPLACE_NAME}\n```"
    return f"{body}\n\n---\n\n**Update:**\n\n{install}", None


def main(argv: list[str]) -> int:
    """Print the tag or the notes, or why not."""
    names = [a for a in argv if a != "--tag"]
    if len(names) != 1:
        _ = sys.stderr.write("usage: release-notes.py <plugin> [--tag]\n")
        return 2
    text, problem = render(repo_root(), names[0], tag_only="--tag" in argv)
    if problem is not None:
        _ = sys.stderr.write(f"✖ {problem}\n")
        return 1
    _ = sys.stdout.write(f"{text}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
