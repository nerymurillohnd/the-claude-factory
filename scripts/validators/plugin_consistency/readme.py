#!/usr/bin/env python3
"""Plugin README and root catalog checks (PC-06 to PC-08)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from release.release_tools.repo import MARKETPLACE_NAME, entries, manifest, version

from validators.plugin_consistency.model import Finding

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

MIN_WORDS = 40
_FENCE = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_TAG = re.compile(r"<[^>]+>")
_WORD = re.compile(r"[A-Za-z0-9][\w'\u2019-]*")
_ROW = re.compile(r"\(\./plugins/(?P<name>[^)#/]+)#readme\)")
_COUNT = re.compile(r"^\|\s*\[(?P<title>[^\]]+)\]\([^)]*\)\s*\|\s*(?P<count>[0-9]+)\s*\|")
_VERSION_CELL = re.compile(r"`([0-9]+\.[0-9]+\.[0-9]+)`")


def prose_words(text: str) -> int:
    """Count the words outside fenced code blocks, link targets and HTML tags."""
    prose = _TAG.sub(" ", _LINK_TARGET.sub("]", _FENCE.sub(" ", text)))
    return len(_WORD.findall(prose))


def readme_findings(root: Path) -> Iterator[Finding]:
    """PC-06 placeholders and length; PC-07 the badge and commands name the plugin."""
    for entry in entries(root):
        name = str(entry.get("name", ""))
        rel = f"plugins/{name}/README.md"
        path = root / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if "{{" in text:
            yield Finding("PC-06", rel, "a template placeholder {{…}} is left")
        if prose_words(text) < MIN_WORDS:
            yield Finding("PC-06", rel, f"fewer than {MIN_WORDS} words outside code blocks")
        if f"plugins%2F{name}%2F.claude-plugin%2Fplugin.json" not in text:
            yield Finding("PC-07", rel, "the version badge doesn't read this plugin's plugin.json")
        for verb in ("install", "update", "uninstall"):
            if f"claude plugin {verb} {name}@{MARKETPLACE_NAME}" not in text:
                yield Finding("PC-07", rel, f"no `claude plugin {verb} {name}@{MARKETPLACE_NAME}`")


def slug(title: str) -> str:
    """Return a heading's words, lowercased and joined with hyphens, emoji dropped."""
    return "-".join(re.findall(r"[a-z0-9]+", title.lower()))


def _catalog(text: str) -> tuple[dict[str, int], dict[str, list[tuple[str, str]]]]:
    """Return the summary counts and, per category section, (plugin, version cell) rows."""
    counts: dict[str, int] = {}
    sections: dict[str, list[tuple[str, str]]] = {}
    inside, section = False, ""
    for line in text.splitlines():
        if line.startswith("## "):
            inside = "catalog" in line.lower()
            section = ""
            continue
        if not inside:
            continue
        if line.startswith("### "):
            section = line[4:].strip()
            sections[section] = []
        elif count := _COUNT.match(line):
            counts[count["title"].strip()] = int(count["count"])
        elif section and (row := _ROW.search(line)):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            found = next((m[1] for c in cells if (m := _VERSION_CELL.fullmatch(c))), "")
            sections[section].append((row["name"], found))
    return counts, sections


def _row_findings(
    root: Path, entry: dict[str, object], rows: set[tuple[str, str, str]]
) -> Iterator[Finding]:
    """PC-08 for one listed plugin: one row, under its category, at its version."""
    name = str(entry.get("name", ""))
    found = [(title, ver) for row_name, title, ver in rows if row_name == name]
    if len(found) != 1:
        yield Finding("PC-08", "README.md", f"{name}: {len(found)} catalog rows, expected 1")
        return
    title, ver = found[0]
    category = str(entry.get("category", ""))
    if not slug(title).startswith(category):
        yield Finding("PC-08", "README.md", f"{name}: under {title!r}, category {category!r}")
    current = version(manifest(root, name))
    if ver != current:
        yield Finding("PC-08", "README.md", f"{name}: catalog {ver}, plugin.json {current}")


def catalog_findings(root: Path) -> Iterator[Finding]:
    """PC-08: one catalog row per listed plugin, no row for another, and right section counts."""
    path = root / "README.md"
    counts, sections = _catalog(path.read_text(encoding="utf-8") if path.is_file() else "")
    rows = {(name, title, ver) for title, items in sections.items() for name, ver in items}
    listed = {str(entry.get("name", "")) for entry in entries(root)}
    for entry in entries(root):
        yield from _row_findings(root, entry, rows)
    for name in sorted({row[0] for row in rows} - listed):
        yield Finding("PC-08", "README.md", f"{name}: catalog row for an unlisted plugin")
    for title, items in sections.items():
        if counts.get(title) != len(items):
            got = counts.get(title)
            yield Finding("PC-08", "README.md", f"{title}: count {got}, rows {len(items)}")
