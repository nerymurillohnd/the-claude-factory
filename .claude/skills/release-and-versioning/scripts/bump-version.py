#!/usr/bin/env python3
"""Bump version: raise a plugin's version and turn [Unreleased] into the dated section.

Writes plugins/<plugin>/.claude-plugin/plugin.json (the new version) and
plugins/<plugin>/CHANGELOG.md (the `## [X.Y.Z] - YYYY-MM-DD` section below an empty
`## [Unreleased]`, and the link references of both). It refuses `marketplace`, an unknown
level, a missing manifest or version, and a missing or empty [Unreleased]; on a refusal it
writes nothing. It does not regenerate the README catalog: run
`node scripts/generators/catalog.mjs` next.

It reads and writes those two files only: it never starts a process or uses the network.
Exit 0 = bumped, 1 = refused, 2 = wrong arguments (<plugin> <major|minor|patch>).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import sys
from typing import cast

REPO_URL = "https://github.com/nerymurillohnd/the-claude-factory"
LEVELS = ("major", "minor", "patch")
MARKETPLACE_REFUSAL = (
    "The marketplace has no version. Add a line under today's date heading in CHANGELOG.md instead."
)
_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def bumped(version: str, level: str) -> str:
    """`version` raised by `level`, pre-release and build metadata dropped."""
    parts = re.split(r"[-+]", version)[0].split(".")
    nums = [int(p) if p.isdigit() else 0 for p in parts[:3]]
    major, minor, patch = [*nums, 0, 0, 0][:3]
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def changelog_section(text: str, version: str) -> str | None:
    """Body of the `## [version]` section, stripped; None when there is no such heading."""
    pattern = rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|^\[[^\]]+\]:|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


def rolled(text: str, name: str, version: str, day: str) -> str:
    """The changelog with [Unreleased] moved under `## [version] - day`, and its links."""
    heading = f"## [Unreleased]\n\n## [{version}] - {day}\n\n"
    text = re.sub(r"^## \[Unreleased\]\s*\n", lambda _: heading, text, count=1, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    tag = f"{name}--v{version}"
    compare = f"[Unreleased]: {REPO_URL}/compare/{tag}...HEAD"
    links = f"{compare}\n[{version}]: {REPO_URL}/releases/tag/{tag}"
    if re.search(r"^\[Unreleased\]:.*$", text, re.MULTILINE):
        return re.sub(r"^\[Unreleased\]:.*$", lambda _: links, text, count=1, flags=re.MULTILINE)
    return f"{text.rstrip()}\n\n{links}\n"


def read_manifest(path: Path) -> tuple[dict[str, object], str | None]:
    """The plugin.json object, or an empty one and why it cannot be bumped."""
    scope = path.relative_to(path.parents[2]).as_posix()
    if not path.is_file():
        return {}, f"plugins/{scope} not found"
    try:
        data = _decode(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, f"plugins/{scope} is not valid JSON: {e}"
    if not isinstance(data, dict):
        return {}, f"plugins/{scope} is not a JSON object"
    return cast("dict[str, object]", data), None


def bump(root: Path, name: str, level: str) -> tuple[str, str | None]:
    """Apply the bump: the line to print, and None, or why it was refused."""
    if name == "marketplace":
        return "", MARKETPLACE_REFUSAL
    if level not in LEVELS:
        return "", f'Unknown bump level "{level}" (use major, minor or patch)'
    plugin = root / "plugins" / name
    manifest_path = plugin / ".claude-plugin" / "plugin.json"
    manifest, problem = read_manifest(manifest_path)
    current = manifest.get("version")
    if problem is None and (not isinstance(current, str) or not current):
        problem = f"plugins/{name}/.claude-plugin/plugin.json has no version"
    changelog = plugin / "CHANGELOG.md"
    if problem is None and not changelog.is_file():
        problem = f"plugins/{name}/CHANGELOG.md not found"
    if problem is not None or not isinstance(current, str):
        return "", problem
    text = changelog.read_text(encoding="utf-8")
    unreleased = changelog_section(text, "Unreleased")
    if unreleased is None:
        return "", 'CHANGELOG.md has no "## [Unreleased]" section'
    if not unreleased:
        return "", "[Unreleased] is empty — document the changes before bumping"
    new = bumped(current, level)
    day = datetime.now(UTC).date().isoformat()
    _ = changelog.write_text(rolled(text, name, new, day), encoding="utf-8")
    manifest["version"] = new
    body = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    _ = manifest_path.write_text(body, encoding="utf-8")
    return f"{name}: {current} → {new}", None


def main(argv: list[str]) -> int:
    """Bump and report, or print why not."""
    if len(argv) != len(("plugin", "level")):
        _ = sys.stderr.write("usage: bump-version.py <plugin> <major|minor|patch>\n")
        return 2
    line, problem = bump(repo_root(), argv[0], argv[1])
    if problem is not None:
        _ = sys.stderr.write(f"✖ {problem}\n")
        return 1
    _ = sys.stdout.write(f"✔ {line}\nNext: node scripts/generators/catalog.mjs\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
