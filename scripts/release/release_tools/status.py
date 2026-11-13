#!/usr/bin/env python3
"""Report what a release needs: changed and untagged versions, bad semver, dependents."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, Literal, cast, override

from release.release_tools.repo import (
    GitError,
    entries,
    git,
    manifest,
    plugin_names,
    remote_tags,
    version,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

type Kind = Literal["changed", "untagged", "bad-semver", "dependent"]
type Level = Literal["major", "minor", "patch"]
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_LEVELS: tuple[Level, ...] = ("major", "minor", "patch")


@dataclass(frozen=True)
class Row:
    """One line of the report."""

    plugin: str
    kind: Kind
    detail: str

    @override
    def __str__(self) -> str:
        """Return the row as `<kind>: <detail>`."""
        return f"{self.kind}: {self.detail}"


def next_version(current: str | None, level: Level) -> str:
    """Raise the field of level by one and reset the fields after it; a new plugin is 0.1.0."""
    if current is None:
        return "0.1.0"
    if not SEMVER.match(current):
        msg = f"{current!r} is not MAJOR.MINOR.PATCH"
        raise ValueError(msg)
    fields = [int(part) for part in current.split(".")]
    index = _LEVELS.index(level)
    fields[index] += 1
    fields[index + 1 :] = [0] * (2 - index)
    return ".".join(str(part) for part in fields)


def _changed(root: Path, base: str) -> Iterator[Row]:
    """Yield each plugin whose work-tree version differs from the base's."""
    for plugin in plugin_names(root):
        now = version(manifest(root, plugin))
        before = version(manifest(root, plugin, base))
        if now != before:
            yield Row(plugin, "changed", f"{plugin} {before or 'new'} -> {now}")


def _untagged(root: Path, base: str, remote: str) -> Iterator[Row]:
    """Yield each plugin version on the base that has no tag on the remote."""
    tags = remote_tags(root, remote)
    listed = git(root, "ls-tree", "-d", "--name-only", base, "plugins/")
    if listed.returncode != 0:
        raise GitError(listed.stderr.strip() or f"git ls-tree {base} failed")
    for folder in listed.stdout.split():
        plugin = folder.removeprefix("plugins/")
        found = version(manifest(root, plugin, base))
        if found and f"{plugin}--v{found}" not in tags:
            yield Row(plugin, "untagged", f"{plugin}--v{found}")


def _bad_semver(root: Path) -> Iterator[Row]:
    """Yield each work-tree version that is not MAJOR.MINOR.PATCH."""
    for plugin in plugin_names(root):
        found = version(manifest(root, plugin))
        if found is not None and not SEMVER.match(found):
            yield Row(plugin, "bad-semver", f"{plugin} {found}")


def _dependency(raw: object) -> str:
    """Return `<name> <range>` for one dependencies entry; a bare name has range `any`."""
    if isinstance(raw, dict):
        item = cast("dict[str, object]", raw)
        name = str(item.get("name", "?"))
        where = item.get("marketplace")
        return f"{name}{f'@{where}' if where else ''} {item.get('version') or 'any'}"
    return f"{raw if isinstance(raw, str) else json.dumps(raw)} any"


def _dependents(root: Path) -> Iterator[Row]:
    """Yield every declared dependency, from plugin.json and from the marketplace entry."""
    for entry in entries(root):
        plugin = str(entry.get("name", ""))
        declared: list[object] = []
        for source in (manifest(root, plugin) or {}, entry):
            raw = source.get("dependencies")
            if isinstance(raw, list):
                declared.extend(cast("list[object]", raw))
        for item in declared:
            yield Row(plugin, "dependent", f"{plugin} needs {_dependency(item)}")


def status(root: Path, base: str = "origin/main", remote: str = "origin") -> list[Row]:
    """Return the report rows: changed, untagged, bad-semver, then dependent."""
    return [
        *_changed(root, base),
        *_untagged(root, base, remote),
        *_bad_semver(root),
        *_dependents(root),
    ]


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.base: str = "origin/main"
        self.remote: str = "origin"
        self.next: str | None = None
        self.level: Level | None = None
        self.json: bool = False
        self.root: Path = Path()


def _parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(prog="release-status", description=__doc__)
    _ = parser.add_argument("--base", default="origin/main", help="ref to compare with")
    _ = parser.add_argument("--remote", default="origin", help="remote whose tags count")
    _ = parser.add_argument("--next", metavar="PLUGIN", help="print PLUGIN's next version")
    _ = parser.add_argument("--level", choices=_LEVELS, help="semver level for --next")
    _ = parser.add_argument("--json", action="store_true", help="print the rows as JSON")
    _ = parser.add_argument("--root", type=Path, default=Path(), help="repository root")
    return parser


def _print_next(args: Args) -> int:
    """Print the next version of args.next at args.level."""
    if args.level is None or args.next not in plugin_names(args.root):
        _ = sys.stderr.write("release-status: --next needs a listed plugin and --level\n")
        return 2
    try:
        current = version(manifest(args.root, args.next, args.base))
        _ = sys.stdout.write(next_version(current, args.level) + "\n")
    except ValueError as error:
        _ = sys.stderr.write(f"release-status: {args.next}: {error}\n")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    """Print the report; exit 1 on a bad semver version or a git failure, 2 on usage errors."""
    args = _parser().parse_args(argv, namespace=Args())
    if args.next is not None:
        return _print_next(args)
    try:
        rows = status(args.root, args.base, args.remote)
    except GitError as error:
        _ = sys.stderr.write(f"release-status: {error}\n")
        return 1
    if args.json:
        data = [{"plugin": r.plugin, "kind": r.kind, "detail": r.detail} for r in rows]
        _ = sys.stdout.write(json.dumps(data, indent=2) + "\n")
    else:
        _ = sys.stdout.write("".join(f"{row}\n" for row in rows))
    return 1 if any(row.kind == "bad-semver" for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
