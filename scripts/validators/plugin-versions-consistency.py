#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = []
# ///
"""Plugin version consistency: every place that defines or names a plugin's version agrees.

plugins/<name>/.claude-plugin/plugin.json `version` (full SemVer) is the only source; the rest
must follow it. For every real directory in plugins/:

- .claude-plugin/marketplace.json: the plugin's `plugins[]` entry carries no `version`.
- plugins/<name>/CHANGELOG.md: a `## [Unreleased]` section; the first `## [X.Y.Z] - YYYY-MM-DD`
  section is the plugin.json version; versioned sections go strictly newest first; each has the
  link `[X.Y.Z]: <repo>/releases/tag/<name>--vX.Y.Z`, no link names a version without a section,
  and `[Unreleased]: <repo>/compare/<name>--v<version>...HEAD`.
- CHANGELOG.md: the `- **<name>** X.Y.Z` lines name exactly the versions of the plugin's
  changelog, so the highest one is the plugin.json version.
- README.md: the catalog row's Version cell is the plugin.json version.
- plugins/<name>/README.md: the Version badge reads `$.version` from this plugin's plugin.json on
  main, never a hardcoded version.

Release dates are out of scope: a plugin changelog dates the bump, the root changelog the day the
change lands. Git tags are out of scope: they are not files.
A value that is missing, empty or of the wrong type is an error, never a skip. It reads files
only: it never writes, imports or runs plugin code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling: uv runs it on Python 3.15 from its inline metadata; run it by path.
TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

import itertools
import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, TypeIs

if TYPE_CHECKING:
    from collections.abc import Callable

REPO_URL = "https://github.com/nerymurillohnd/the-claude-factory"
RAW_MAIN = "https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain"
CATALOG_START = "<!-- catalog:start -->"
CATALOG_END = "<!-- catalog:end -->"
# SemVer 2.0.0, from semver.org.
_ID = r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
SEMVER = re.compile(
    rf"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-({_ID}(?:\.{_ID})*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
VERSION_TEXT = r"\d+\.\d+\.\d+[0-9A-Za-z.+-]*"
SECTION = re.compile(rf"^## \[({VERSION_TEXT})\](.*)$", re.MULTILINE)
SECTION_TAIL = re.compile(r" - \d{4}-\d{2}-\d{2}")
VERSION_LINK = re.compile(rf"^\[({VERSION_TEXT})\]: (.*)$", re.MULTILINE)
UNRELEASED_LINK = re.compile(r"^\[Unreleased\]: (.*)$", re.MULTILINE)
ROOT_LINE = re.compile(rf"^- \*\*([a-z0-9-]+)\*\* ({VERSION_TEXT})(?=\s)", re.MULTILINE)
BADGE = re.compile(r"\[!\[Version\]\(([^)\s]+)\)")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


class DuplicateKeyError(ValueError):
    """A JSON object names the same key twice; the decoder would keep only the last one."""


def _object(pairs: list[tuple[str, object]]) -> JsonObject:
    obj = JsonObject()
    for key, value in pairs:
        if key in obj:
            msg = f'duplicate key "{key}"'
            raise DuplicateKeyError(msg)
        obj[key] = value
    return obj


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_object).decode


def is_array(value: object) -> TypeIs[list[object]]:
    """Narrow a decoded JSON value to an array; its items are still unchecked objects."""
    return isinstance(value, list)


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


class Report:
    """Collects errors as `[scope] message` lines."""

    def __init__(self, root: Path) -> None:
        """Start with no errors; every file read must resolve inside `root`."""
        self.root: Path = root.resolve()
        self.errors: list[str] = []

    def error(self, scope: str, message: str) -> None:
        """Record one error."""
        self.errors.append(f"[{scope}] {message}")


def read_text(path: Path, scope: str, report: Report) -> str | None:
    """The UTF-8 text of `path`, or None after recording why it cannot be used."""
    try:
        if not path.resolve().is_relative_to(report.root):
            report.error(scope, f"{path.name} resolves outside the repository")
            return None
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        report.error(scope, f"{path.name} is missing")
    except (OSError, ValueError) as e:
        report.error(scope, f"{path.name} cannot be read: {e}")
    return None


def read_json(path: Path, scope: str, report: Report) -> JsonObject | None:
    """The JSON object in `path`, or None after recording why it cannot be used."""
    text = read_text(path, scope, report)
    if text is None:
        return None
    try:
        value = _decode(text)
    except ValueError as e:
        report.error(scope, f"{path.name} cannot be read as JSON: {e}")
        return None
    if not isinstance(value, JsonObject):
        report.error(scope, f"{path.name} must hold a JSON object")
        return None
    return value


type Precedence = tuple[int, int, int, tuple[tuple[int, int | str], ...]]


def precedence(version: str) -> Precedence | None:
    """A sort key that orders SemVer versions by precedence, or None when `version` is not one."""
    match = SEMVER.fullmatch(version)
    if match is None:
        return None
    major, minor, patch, pre = match.groups()
    if pre is None:
        # A release ranks above every pre-release of the same version.
        return int(major), int(minor), int(patch), ((2, 0),)
    ids = tuple((0, int(p)) if p.isdigit() else (1, p) for p in pre.split("."))
    return int(major), int(minor), int(patch), ids


def plugin_directories(root: Path, report: Report) -> list[str]:
    """The names of the real directories in plugins/, sorted."""
    plugins_dir = root / "plugins"
    if plugins_dir.is_symlink() or not plugins_dir.is_dir():
        report.error("plugins/", "must be a directory, not a symlink")
        return []
    names: list[str] = []
    for p in sorted(plugins_dir.iterdir()):
        if p.is_symlink():
            report.error(f"plugins/{p.name}", "must be a directory, not a symlink")
        elif p.is_dir():
            names.append(p.name)
    return names


def manifest_version(root: Path, name: str, report: Report) -> str | None:
    """The plugin.json `version` when it is full SemVer; otherwise None after recording why."""
    scope = f"plugins/{name} plugin.json"
    manifest = read_json(root / "plugins" / name / ".claude-plugin" / "plugin.json", scope, report)
    if manifest is None:
        return None
    if "version" not in manifest:
        report.error(scope, '"version" is required')
        return None
    version = manifest["version"]
    if not isinstance(version, str) or precedence(version) is None:
        report.error(scope, f'"version" must be a full SemVer string, found {json.dumps(version)}')
        return None
    return version


def check_marketplace(root: Path, names: list[str], report: Report) -> None:
    """No `plugins[]` entry of a plugin in plugins/ carries a version."""
    scope = "marketplace.json"
    marketplace = read_json(root / ".claude-plugin" / "marketplace.json", scope, report)
    if marketplace is None:
        return
    plugins = marketplace.get("plugins")
    if not is_array(plugins):
        report.error(scope, '"plugins" must be an array')
        return
    for i, entry in enumerate(plugins):
        if not isinstance(entry, JsonObject) or "version" not in entry:
            continue
        name = entry.get("name")
        label = name if isinstance(name, str) and name in names else f"plugins[{i}]"
        report.error(
            f"{scope} {label}", '"version" must not be set: plugin.json is the only source'
        )


def changelog_sections(text: str, scope: str, report: Report) -> list[str]:
    """The versions of the `## [X.Y.Z] - YYYY-MM-DD` sections, in file order."""
    versions: list[str] = []
    for match in SECTION.finditer(text):
        version, tail = match.groups()
        if precedence(version) is None:
            report.error(scope, f'section "## [{version}]" is not a SemVer version')
            continue
        if not SECTION_TAIL.fullmatch(tail):
            report.error(scope, f'section "## [{version}]" must be "## [{version}] - YYYY-MM-DD"')
        if version in versions:
            report.error(scope, f'section "## [{version}]" appears twice')
            continue
        versions.append(version)
    return versions


def check_order(versions: list[str], scope: str, report: Report) -> None:
    """Versioned sections go strictly newest first."""
    for newer, older in itertools.pairwise(versions):
        newer_key, older_key = precedence(newer), precedence(older)
        if newer_key is not None and older_key is not None and newer_key <= older_key:
            report.error(scope, f'section "## [{older}]" must come before "## [{newer}]"')


def version_links(text: str, scope: str, report: Report) -> dict[str, str]:
    """Version → URL of each `[X.Y.Z]: <url>` link reference."""
    links: dict[str, str] = {}
    for match in VERSION_LINK.finditer(text):
        version, url = match.group(1), match.group(2)
        if version in links:
            report.error(scope, f'link "[{version}]" appears twice')
        links[version] = url
    return links


def check_unreleased_link(text: str, name: str, current: str, scope: str, report: Report) -> None:
    """Exactly one `[Unreleased]` link, comparing the current version's tag with HEAD."""
    expected = f"{REPO_URL}/compare/{name}--v{current}...HEAD"
    unreleased = [m.group(1) for m in UNRELEASED_LINK.finditer(text)]
    if len(unreleased) != 1:
        report.error(scope, f'needs exactly one link "[Unreleased]: {expected}"')
    elif unreleased[0] != expected:
        report.error(scope, f'link "[Unreleased]" must be {expected}, found {unreleased[0]}')


def check_links(text: str, name: str, versions: list[str], scope: str, report: Report) -> None:
    """One tag link per versioned section, none extra, and the [Unreleased] compare link."""
    links = version_links(text, scope, report)
    for version in versions:
        expected = f"{REPO_URL}/releases/tag/{name}--v{version}"
        if version not in links:
            report.error(scope, f'missing link "[{version}]: {expected}"')
        elif links[version] != expected:
            report.error(scope, f'link "[{version}]" must be {expected}, found {links[version]}')
    for version in sorted(links.keys() - set(versions)):
        report.error(scope, f'link "[{version}]" names a version with no section')
    if versions:
        check_unreleased_link(text, name, versions[0], scope, report)


def check_changelog(root: Path, name: str, version: str, report: Report) -> list[str] | None:
    """The plugin changelog agrees with `version`; returns its versions, newest first."""
    scope = f"plugins/{name} CHANGELOG.md"
    text = read_text(root / "plugins" / name / "CHANGELOG.md", scope, report)
    if text is None:
        return None
    if not re.search(r"^## \[Unreleased\]\s*$", text, re.MULTILINE):
        report.error(scope, 'missing "## [Unreleased]"')
    versions = changelog_sections(text, scope, report)
    if not versions:
        report.error(scope, f'has no "## [{version}] - YYYY-MM-DD" section')
        return None
    if versions[0] != version:
        report.error(
            scope,
            f'newest section is "## [{versions[0]}]"; plugin.json version is "{version}"',
        )
    check_order(versions, scope, report)
    check_links(text, name, versions, scope, report)
    return versions


def root_changelog_versions(root: Path, report: Report) -> dict[str, set[str]] | None:
    """Plugin name → the versions its `- **<name>** X.Y.Z` lines name in CHANGELOG.md."""
    text = read_text(root / "CHANGELOG.md", "CHANGELOG.md", report)
    if text is None:
        return None
    named: dict[str, set[str]] = {}
    for match in ROOT_LINE.finditer(text):
        name, version = match.groups()
        if version in named.setdefault(name, set()):
            report.error("CHANGELOG.md", f'"**{name}** {version}" appears twice')
        named[name].add(version)
    return named


def check_root_changelog(
    name: str, versions: list[str], named: dict[str, set[str]], report: Report
) -> None:
    """The root changelog names exactly the versions of the plugin's own changelog."""
    scope = "CHANGELOG.md"
    mentioned = named.get(name, set())
    for version in versions:
        if version not in mentioned:
            report.error(scope, f'no "- **{name}** {version}" line for plugins/{name} {version}')
    for version in sorted(mentioned - set(versions), key=lambda v: precedence(v) or (0, 0, 0, ())):
        report.error(
            scope, f'"- **{name}** {version}" names a version plugins/{name}/CHANGELOG.md lacks'
        )


def catalog_versions(root: Path, report: Report) -> dict[str, list[str]] | None:
    """Plugin name → the Version cell of each catalog row that links to it."""
    scope = "README.md"
    readme = read_text(root / "README.md", scope, report)
    if readme is None:
        return None
    if readme.count(CATALOG_START) != 1 or readme.count(CATALOG_END) != 1:
        report.error(scope, f"needs exactly one {CATALOG_START} and one {CATALOG_END}")
        return None
    catalog = readme[readme.index(CATALOG_START) : readme.index(CATALOG_END)]
    cells: dict[str, list[str]] = {}
    column: int | None = None
    for line in catalog.splitlines():
        if not line.startswith("|"):
            column = None
            continue
        row = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        if "Version" in row:
            column = row.index("Version")
            continue
        link = re.search(r"\]\(\./plugins/([^/#)\s]+)#readme\)", line)
        if link is None:
            continue
        if column is None or column >= len(row):
            report.error(scope, f'catalog row for "{link.group(1)}" has no Version column')
            continue
        cells.setdefault(link.group(1), []).append(row[column].strip("`"))
    return cells


def check_catalog(name: str, version: str, cells: dict[str, list[str]], report: Report) -> None:
    """Every catalog row of the plugin shows the plugin.json version."""
    rows = cells.get(name)
    if not rows:
        report.error("README.md", f'catalog has no row for "{name}"')
        return
    for cell in rows:
        if cell != version:
            report.error(
                "README.md", f'catalog shows "{name}" at `{cell}`; plugin.json version is {version}'
            )


def check_badge(root: Path, name: str, report: Report) -> None:
    """The plugin README's Version badge reads $.version from this plugin's plugin.json."""
    scope = f"plugins/{name} README.md"
    readme = read_text(root / "plugins" / name / "README.md", scope, report)
    if readme is None:
        return
    badges = [m.group(1) for m in BADGE.finditer(readme)]
    if len(badges) != 1:
        report.error(scope, f"needs exactly one Version badge, found {len(badges)}")
        return
    expected = (
        "https://img.shields.io/badge/dynamic/json?url="
        f"{RAW_MAIN}%2Fplugins%2F{name}%2F.claude-plugin%2Fplugin.json&query=%24.version&"
    )
    if not badges[0].startswith(expected):
        report.error(
            scope, f"Version badge must read $.version from plugin.json: start it with {expected}"
        )


def check(root: Path) -> list[str]:
    """Every plugin version consistency error under `root`, in a stable order."""
    report = Report(root)
    names = plugin_directories(root, report)
    check_marketplace(root, names, report)
    named = root_changelog_versions(root, report)
    cells = catalog_versions(root, report)
    for name in names:
        check_badge(root, name, report)
        version = manifest_version(root, name, report)
        if version is None:
            continue
        versions = check_changelog(root, name, version, report)
        if versions is not None and named is not None:
            check_root_changelog(name, versions, named, report)
        if cells is not None:
            check_catalog(name, version, cells, report)
    return report.errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/plugin-versions-consistency.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Plugin version checks failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write("✔ Plugin versions agree in every place that defines or names them\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
