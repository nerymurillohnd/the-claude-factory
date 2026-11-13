#!/usr/bin/env python3
"""Print a plugin's release tag or its GitHub Release body (release-notes)."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from release.release_tools.repo import (
    MARKETPLACE_NAME,
    changelog_section,
    manifest,
    plugin_names,
    version,
)


class ReleaseError(Exception):
    """The plugin has nothing a release can be built from."""


def _version(root: Path, plugin: str) -> str:
    """Return the plugin's version from its plugin.json, or raise ReleaseError."""
    found = version(manifest(root, plugin))
    if found is None:
        msg = f"{plugin}: plugin.json has no version"
        raise ReleaseError(msg)
    return found


def tag_name(root: Path, plugin: str) -> str:
    """Return the tag `claude plugin tag` would create: <plugin>--v<version>."""
    return f"{plugin}--v{_version(root, plugin)}"


def release_body(root: Path, plugin: str) -> str:
    """Return the version's CHANGELOG section, a rule, then the update command."""
    current = _version(root, plugin)
    path = root / "plugins" / plugin / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    section = changelog_section(text, current)
    if not section:
        msg = f"{plugin}: CHANGELOG.md has no ## [{current}] section with notes"
        raise ReleaseError(msg)
    update = f"```bash\nclaude plugin update {plugin}@{MARKETPLACE_NAME}\n```\n"
    return f"{section}\n\n---\n\n**Update:**\n\n{update}"


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.plugin: str = ""
        self.tag: bool = False
        self.root: Path = Path()


def main(argv: list[str] | None = None) -> int:
    """Print the tag or the body; exit 1 when the body can't be built, 2 on usage errors."""
    parser = argparse.ArgumentParser(prog="release-notes", description=__doc__)
    _ = parser.add_argument("plugin", help="plugin name, as listed in marketplace.json")
    _ = parser.add_argument("--tag", action="store_true", help="print only the tag name")
    _ = parser.add_argument("--root", type=Path, default=Path(), help="repository root")
    args = parser.parse_args(argv, namespace=Args())
    if args.plugin not in plugin_names(args.root):
        _ = sys.stderr.write(f"release-notes: {args.plugin} is not in marketplace.json\n")
        return 2
    try:
        if args.tag:
            _ = sys.stdout.write(tag_name(args.root, args.plugin) + "\n")
        else:
            _ = sys.stdout.write(release_body(args.root, args.plugin))
    except ReleaseError as error:
        _ = sys.stderr.write(f"release-notes: {error}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
