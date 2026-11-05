#!/usr/bin/env python3
"""Plugin icons: every plugin declares a directory listing icon the directory accepts.

Every plugin's .claude-plugin/plugin.json must set "icon" to "./.claude-plugin/icon.png", and that
file must be a regular PNG inside the plugin, square, 512 to 2048 px a side and under 2 MB: the
limits `claude plugin validate --strict` gives in its ICON_MISSING fix text. Each plugin also needs
its source, scripts/generators/plugin-icons/<plugin>.svg, and every source needs its plugin, so an
icon can always be rendered again (ADR_2026-11-05_every-plugin-ships-a-directory-icon). Each error
names the plugin and why it fails.

It reads files only: it never imports or runs plugin code, starts a process or uses the network.
It does not render the SVG sources or compare them with the PNGs: the generator
scripts/generators/plugin-icons.mjs renders them, by hand.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import struct
import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable

ICON = "./.claude-plugin/icon.png"
SOURCES = "scripts/generators/plugin-icons"
MIN_SIDE = 512
MAX_SIDE = 2048
MAX_BYTES = 2 * 1024 * 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IHDR_END = 24  # signature (8), chunk length (4), "IHDR" (4), width (4), height (4)

_decode: Callable[[str], object] = json.JSONDecoder().decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


def png_size(path: Path) -> tuple[int, int] | None:
    """The width and height in a PNG's IHDR chunk, or None when the file is not a PNG."""
    with path.open("rb") as f:
        head = f.read(IHDR_END)
    if len(head) < IHDR_END or head[:8] != PNG_SIGNATURE or head[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", head[16:IHDR_END])
    return width, height


def declared_icon(manifest: Path) -> tuple[object, str | None]:
    """The manifest's "icon" value, or the reason the manifest cannot be read."""
    try:
        data = _decode(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f".claude-plugin/plugin.json cannot be read: {exc}"
    if not isinstance(data, dict):
        return None, ".claude-plugin/plugin.json is not a JSON object"
    return cast("dict[str, object]", data).get("icon"), None


def icon_problems(plugin: Path) -> list[str]:
    """Why the plugin's icon does not pass, empty when it does."""
    icon, problem = declared_icon(plugin / ".claude-plugin" / "plugin.json")
    if problem is not None:
        return [problem]
    problems: list[str] = []
    if icon != ICON:
        problems.append(f'"icon" must be "{ICON}", found {json.dumps(icon)}')
    return [*problems, *image_problems(plugin / ".claude-plugin" / "icon.png")]


def image_problems(path: Path) -> list[str]:
    """Why the icon file is not one the directory accepts, empty when it is."""
    if path.is_symlink():
        return [".claude-plugin/icon.png is a symlink: commit a regular file"]
    if not path.is_file():
        return [".claude-plugin/icon.png is missing"]
    problems: list[str] = []
    size = path.stat().st_size
    if size >= MAX_BYTES:
        problems.append(f".claude-plugin/icon.png is {size} bytes; the directory takes under 2 MB")
    dimensions = png_size(path)
    if dimensions is None:
        return [*problems, ".claude-plugin/icon.png is not a PNG file"]
    width, height = dimensions
    if width != height:
        problems.append(f".claude-plugin/icon.png is {width}x{height} px; it must be square")
    if not MIN_SIDE <= min(width, height) <= max(width, height) <= MAX_SIDE:
        problems.append(
            f".claude-plugin/icon.png is {width}x{height} px; each side must be 512 to 2048 px"
        )
    return problems


def check(root: Path) -> list[str]:
    """Every icon error under `root`, in a stable order."""
    plugins_dir = root / "plugins"
    if not plugins_dir.is_dir():
        return ["[plugins/] must be a directory"]
    plugins = sorted(p.name for p in plugins_dir.iterdir() if p.is_dir() and not p.is_symlink())
    sources_dir = root / SOURCES
    sources = (
        {p.stem for p in sources_dir.iterdir() if p.suffix == ".svg" and p.is_file()}
        if sources_dir.is_dir()
        else set[str]()
    )
    errors: list[str] = []
    for name in plugins:
        errors.extend(f"[plugins/{name}] {p}" for p in icon_problems(plugins_dir / name))
        if name not in sources:
            errors.append(f"[plugins/{name}] {SOURCES}/{name}.svg, the icon source, is missing")
    errors.extend(
        f"[{SOURCES}/{name}.svg] no plugin is named {name}: remove the source or rename it"
        for name in sorted(sources - set(plugins))
    )
    return errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/plugin-icons.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Plugin icons check failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write("✔ Every plugin declares an icon the directory accepts, with its source\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
