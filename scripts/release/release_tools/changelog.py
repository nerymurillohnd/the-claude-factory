#!/usr/bin/env python3
"""Date a plugin's [Unreleased] changelog section as its release and update the links."""

from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
from pathlib import Path
import re
import sys

from release.release_tools.repo import UNRELEASED, VERSION_HEADING, manifest, version

_UNRELEASED_LINK = re.compile(r"^\[Unreleased\]: .*$", re.MULTILINE)


class ChangelogError(Exception):
    """The changelog can't be dated as it stands."""


def date_release(text: str, plugin: str, new: str, day: str, repo_url: str) -> str:
    """Turn [Unreleased] into `## [new] - day`, add an empty [Unreleased], and fix the links."""
    match = UNRELEASED.search(text)
    if match is None:
        msg = "no ## [Unreleased] section"
        raise ChangelogError(msg)
    notes = match["body"].strip()
    if not notes:
        msg = "## [Unreleased] is empty: ask the owner what the version changes"
        raise ChangelogError(msg)
    older = VERSION_HEADING.findall(text)
    if new in older:
        msg = f"## [{new}] already exists"
        raise ChangelogError(msg)
    section = f"## [Unreleased]\n\n## [{new}] - {day}\n\n{notes}\n\n"
    text = text[: match.start()] + section + text[match.end() :]
    tag = f"{plugin}--v{new}"
    link = (
        f"{repo_url}/compare/{plugin}--v{older[0]}...{tag}"
        if older
        else f"{repo_url}/releases/tag/{tag}"
    )
    unreleased = f"[Unreleased]: {repo_url}/compare/{tag}...HEAD\n[{new}]: {link}"
    if _UNRELEASED_LINK.search(text) is None:
        return text.rstrip("\n") + f"\n\n{unreleased}\n"
    return _UNRELEASED_LINK.sub(lambda _: unreleased, text, count=1)


def _day(value: str) -> str:
    """Accept only a YYYY-MM-DD date."""
    try:
        return date.fromisoformat(value).isoformat() if len(value) == len("YYYY-MM-DD") else ""
    except ValueError:
        return ""


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.plugin: str = ""
        self.date: str = ""
        self.root: Path = Path()


def main(argv: list[str] | None = None) -> int:
    """Rewrite plugins/<plugin>/CHANGELOG.md; exit 1 when it can't be dated, 2 on usage."""
    parser = argparse.ArgumentParser(prog="release-changelog", description=__doc__)
    _ = parser.add_argument("plugin", help="plugin name")
    _ = parser.add_argument(
        "--date", default="", help="release day, YYYY-MM-DD; default today in UTC"
    )
    _ = parser.add_argument("--root", type=Path, default=Path(), help="repository root")
    args = parser.parse_args(argv, namespace=Args())
    day = _day(args.date) if args.date else datetime.now(UTC).date().isoformat()
    if not day:
        parser.error(f"--date {args.date!r} is not YYYY-MM-DD")
    data = manifest(args.root, args.plugin)
    current = version(data)
    repo_url = data.get("repository") if data else None
    path = args.root / "plugins" / args.plugin / "CHANGELOG.md"
    if current is None or not isinstance(repo_url, str) or not path.is_file():
        _ = sys.stderr.write(
            f"release-changelog: {args.plugin}: no version, repository or CHANGELOG.md\n"
        )
        return 2
    try:
        text = date_release(path.read_text(encoding="utf-8"), args.plugin, current, day, repo_url)
    except ChangelogError as error:
        _ = sys.stderr.write(f"release-changelog: {args.plugin}: {error}\n")
        return 1
    _ = path.write_text(text, encoding="utf-8")
    _ = sys.stdout.write(f"{path}: [{current}] - {day}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
