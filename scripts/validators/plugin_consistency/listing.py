#!/usr/bin/env python3
"""Directory listing checks (PC-09 and PC-10): each plugin's icon and listing URLs.

`claude plugin validate --profile directory` only reports an icon path that is not a file in the
plugin: it accepts a plugin with no icon and a PNG of any shape or size. These checks keep every
plugin on the project's icon convention (ADR_2026-11-13_restore-plugin-icon-sources-and-checks).
They read files only and never render the SVG sources.
"""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

from release.release_tools.repo import entries, manifest

from validators.plugin_consistency.model import Finding

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

ICON = "./.claude-plugin/icon.png"
SOURCES = "scripts/generators/plugin-icons"
MIN_SIDE = 512
MAX_SIDE = 2048
MAX_BYTES = 2 * 1024 * 1024
URL_FIELDS = ("documentationUrl", "supportUrl", "privacyPolicyUrl")
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_IHDR_END = 24  # signature (8), chunk length (4), "IHDR" (4), width (4), height (4)


def png_size(path: Path) -> tuple[int, int] | None:
    """Return the width and height in a PNG's IHDR chunk, or None when the file is not a PNG."""
    with path.open("rb") as handle:
        head = handle.read(_IHDR_END)
    if len(head) < _IHDR_END or head[:8] != _PNG_SIGNATURE or head[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", head[16:_IHDR_END])
    return int(width), int(height)


def _icon_problem(root: Path, name: str) -> str | None:
    """Return why a listed plugin's icon breaks the convention, or None when it holds."""
    data = manifest(root, name) or {}
    if data.get("icon") != ICON:
        return f'"icon" is {data.get("icon")!r}, expected {ICON!r}'
    plugin = (root / "plugins" / name).resolve()
    path = plugin / ".claude-plugin" / "icon.png"
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(plugin):
        return "icon.png is not a regular file inside the plugin"
    size = png_size(path)
    if size is None:
        return "icon.png is not a PNG"
    width, height = size
    if width != height or not MIN_SIDE <= width <= MAX_SIDE:
        return f"icon.png is {width}x{height}, expected square, {MIN_SIDE} to {MAX_SIDE} px"
    if path.stat().st_size >= MAX_BYTES:
        return f"icon.png is {path.stat().st_size} bytes, expected under {MAX_BYTES}"
    return None


def icon_findings(root: Path) -> Iterator[Finding]:
    """PC-09: every listed plugin has a valid icon and an SVG source; no source is stray."""
    listed = {str(entry.get("name", "")) for entry in entries(root)}
    for name in sorted(listed):
        rel = f"plugins/{name}/.claude-plugin/plugin.json"
        problem = _icon_problem(root, name)
        if problem:
            yield Finding("PC-09", rel, problem)
        if not (root / SOURCES / f"{name}.svg").is_file():
            yield Finding("PC-09", SOURCES, f"{name}: no {name}.svg source")
    for source in sorted((root / SOURCES).glob("*.svg")):
        if source.stem not in listed:
            yield Finding("PC-09", f"{SOURCES}/{source.name}", "source for an unlisted plugin")


def url_findings(root: Path) -> Iterator[Finding]:
    """PC-10: each listed plugin sets every listing URL field to an https:// URL."""
    for entry in entries(root):
        name = str(entry.get("name", ""))
        data = manifest(root, name) or {}
        for field in URL_FIELDS:
            value = data.get(field)
            if not (isinstance(value, str) and value.startswith("https://")):
                rel = f"plugins/{name}/.claude-plugin/plugin.json"
                yield Finding("PC-10", rel, f"{field} is {value!r}, expected an https:// URL")
