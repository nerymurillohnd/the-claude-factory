#!/usr/bin/env python3
"""Marketplace, manifest and changelog checks (PC-01 to PC-05), and the full check run."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from release.release_tools.repo import (
    MARKETPLACE,
    UNRELEASED,
    VERSION_HEADING,
    entries,
    git,
    manifest,
    marketplace,
    remote_tags,
    version,
)

from validators.plugin_consistency.model import Finding
from validators.plugin_consistency.readme import catalog_findings, readme_findings

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

__all__ = ["Finding", "check"]


def _names(root: Path) -> Iterator[Finding]:
    """PC-01: folder, plugin.json name, entry name and entry source agree; no unlisted folder."""
    listed: set[str] = set()
    for entry in entries(root):
        name = str(entry.get("name", ""))
        listed.add(name)
        data = manifest(root, name)
        if data is None:
            yield Finding("PC-01", MARKETPLACE, f"{name}: no plugins/{name}/ with a plugin.json")
            continue
        if data.get("name") != name:
            path = f"plugins/{name}/.claude-plugin/plugin.json"
            yield Finding("PC-01", path, f"name is {data.get('name')!r}, entry says {name!r}")
        if entry.get("source") != f"./plugins/{name}":
            yield Finding("PC-01", MARKETPLACE, f"{name}: source is {entry.get('source')!r}")
    for folder in sorted((root / "plugins").glob("*/.claude-plugin/plugin.json")):
        name = folder.parent.parent.name
        if name not in listed:
            yield Finding("PC-01", f"plugins/{name}", "folder is not listed in marketplace.json")


def _renames(root: Path) -> Iterator[Finding]:
    """PC-02: no renames key is still a listed plugin."""
    raw = marketplace(root).get("renames")
    keys = set(cast("dict[str, object]", raw)) if isinstance(raw, dict) else set[str]()
    for entry in entries(root):
        name = str(entry.get("name", ""))
        if name in keys:
            yield Finding("PC-02", MARKETPLACE, f"{name} is still listed but is a renames key")


def _force_remove(root: Path) -> Iterator[Finding]:
    """PC-03: forceRemoveDeletedPlugins is true."""
    if marketplace(root).get("forceRemoveDeletedPlugins") is not True:
        yield Finding("PC-03", MARKETPLACE, "forceRemoveDeletedPlugins is not true")


def _changelog(root: Path, name: str) -> str:
    """Return a plugin's CHANGELOG.md text, or an empty string."""
    path = root / "plugins" / name / "CHANGELOG.md"
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _tags(root: Path, base: str) -> Iterator[Finding]:
    """PC-04: every dated changelog version has its tag, except the version being released."""
    tags = remote_tags(root)
    for entry in entries(root):
        name = str(entry.get("name", ""))
        current = version(manifest(root, name))
        pending = current if current != version(manifest(root, name, base)) else None
        headings = cast("list[str]", VERSION_HEADING.findall(_changelog(root, name)))
        for found in headings:
            if found != pending and f"{name}--v{found}" not in tags:
                path = f"plugins/{name}/CHANGELOG.md"
                yield Finding("PC-04", path, f"[{found}] has no tag {name}--v{found}")


def _unreleased(root: Path) -> Iterator[Finding]:
    """PC-05: on main, every [Unreleased] section is empty."""
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "main":
        return
    for entry in entries(root):
        name = str(entry.get("name", ""))
        match = UNRELEASED.search(_changelog(root, name))
        if match and match["body"].strip():
            path = f"plugins/{name}/CHANGELOG.md"
            yield Finding("PC-05", path, "[Unreleased] has notes on main")


def check(root: Path, *, offline: bool = False, base: str = "origin/main") -> list[Finding]:
    """Run every check; offline skips PC-04, which reads the remote's tags."""
    findings = [*_names(root), *_renames(root), *_force_remove(root)]
    if not offline:
        findings += _tags(root, base)
    findings += _unreleased(root)
    findings += readme_findings(root)
    findings += catalog_findings(root)
    return findings
