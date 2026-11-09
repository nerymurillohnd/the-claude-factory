#!/usr/bin/env python3
"""Reference pages: layout, relative links and anchors of a skill's Markdown references.

Usage: scripts/checkers/reference-pages.py [--links-only] DIR...

Checks every `*.md` file under each DIR, offline:
- layout (skipped by --links-only): `## Contents` lists every heading from ## to #### in page
  order, each with its exact text, its GitHub-style anchor and an indent of two spaces per level
  below ##; `## Documentation References` is the last ## section and its first line holds an
  https:// URL;
- links: every `#anchor` names a heading of the same page; every relative link or image names a
  file that exists, resolved from the linking file's folder; and a relative link to a Markdown
  file with an `#anchor` names a heading of that file.

Anchors follow GitHub: lowercase, punctuation other than `-` and `_` removed, spaces to `-`, and
a repeated slug suffixed `-1`, `-2` in page order (an H2 that repeats the H1 is `#slug-1`). A
percent-encoded anchor is decoded before it is matched. Headings and links inside fenced code
blocks and code spans are ignored. External URLs are left to scripts/checkers/markdown-urls.py.

Prints one `path:line: message` per problem, then the totals.
Exit 0 when every page passes, 1 when any check fails, 2 on a bad argument or an unreadable file.
Maintainer tooling: standard library only, run by path.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote

FENCE_OPEN = re.compile(r"^((?:[ \t]*>)*[ \t]*)(`{3,}|~{3,})(.*)$")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_SPAN = re.compile(r"`[^`]*`")
LABEL_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
TOC_LINE = re.compile(r"^(\s*)- \[(.+)\]\(#([^)\s]+)\)\s*$")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)

TOP = 2
DEEPEST = 4
INDENT = 2
CONTENTS = "Contents"
REFERENCES = "Documentation References"


class Heading:
    """One heading outside code: its line, level, visible text and anchor."""

    __slots__: tuple[str, ...] = ("anchor", "level", "line", "text")

    def __init__(self, line: int, level: int, text: str, anchor: str) -> None:
        """Store the heading's fields."""
        self.line: int = line
        self.level: int = level
        self.text: str = text
        self.anchor: str = anchor


Problem = tuple[int, str]


def prose_mask(lines: list[str]) -> list[bool]:
    """Return True for each line outside fenced code; an unclosed fence runs to the end."""
    mask = [True] * len(lines)
    fence = ""
    for i, line in enumerate(lines):
        m = FENCE_OPEN.match(line)
        if fence:
            mask[i] = False
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence):
                fence = "" if not m.group(3).strip() else fence
        elif m:
            mask[i] = False
            fence = m.group(2)
    return mask


def plain_text(text: str) -> str:
    """Return the visible text of a heading, with links reduced to their label."""
    return LABEL_LINK.sub(r"\1", text).strip()


def github_slug(text: str) -> str:
    """Return a GitHub-style anchor: lowercase, punctuation but - and _ removed, spaces to -."""
    return re.sub(r"[^\w\- ]", "", plain_text(text).lower()).replace(" ", "-")


def headings(lines: list[str]) -> list[Heading]:
    """Return every heading outside code, a repeated anchor suffixed -1, -2 in page order."""
    out: list[Heading] = []
    seen: dict[str, int] = {}
    for i, (line, prose) in enumerate(zip(lines, prose_mask(lines), strict=True)):
        m = HEADING.match(line) if prose else None
        if not m:
            continue
        text = plain_text(m.group(2))
        base = github_slug(text)
        count = seen.get(base, 0)
        seen[base] = count + 1
        out.append(Heading(i + 1, len(m.group(1)), text, base if count == 0 else f"{base}-{count}"))
    return out


def links(lines: list[str]) -> list[Problem]:
    """Return (line number, target) for every link and image outside code and code spans."""
    found: list[Problem] = []
    for i, (line, prose) in enumerate(zip(lines, prose_mask(lines), strict=True)):
        if prose:
            found += [(i + 1, m.group(1)) for m in LINK.finditer(CODE_SPAN.sub("", line))]
    return found


def read_toc(lines: list[str], start: int) -> list[tuple[int, str, str, int]]:
    """Return (depth, label, anchor, line) for each entry of the list after line `start`."""
    toc: list[tuple[int, str, str, int]] = []
    for n, line in enumerate(lines[start:], start + 1):
        if not line.strip():
            if toc:
                break
            continue
        m = TOC_LINE.match(line)
        if not m:
            break
        toc.append((len(m.group(1)) // INDENT, m.group(2), m.group(3), n))
    return toc


def check_toc(lines: list[str], heads: list[Heading]) -> list[Problem]:
    """Compare the Contents list with the page's headings from ## to ####."""
    starts = [h for h in heads if h.level == TOP and h.text == CONTENTS]
    if not starts:
        return [(1, f"no '## {CONTENTS}' section")]
    toc = read_toc(lines, starts[0].line)
    expected = [h for h in heads if TOP <= h.level <= DEEPEST and h.text != CONTENTS]
    problems: list[Problem] = []
    for (depth, label, anchor, n), head in zip(toc, expected, strict=False):
        if label != head.text:
            problems.append((n, f"Contents says '{label}', line {head.line} says '{head.text}'"))
        if anchor != head.anchor:
            problems.append((n, f"Contents links #{anchor}, '{head.text}' is #{head.anchor}"))
        if depth != head.level - TOP:
            problems.append(
                (n, f"Contents indent {depth}, level {head.level} needs {head.level - TOP}")
            )
    problems += [(h.line, f"'{h.text}' is missing from Contents") for h in expected[len(toc) :]]
    problems += [(e[3], f"Contents entry '{e[1]}' has no heading") for e in toc[len(expected) :]]
    return problems


def check_references(lines: list[str], heads: list[Heading]) -> list[Problem]:
    """Check that Documentation References is the last ## section and starts with a URL."""
    level2 = [h for h in heads if h.level == TOP]
    if not level2 or level2[-1].text != REFERENCES:
        return [(level2[-1].line if level2 else 1, f"'## {REFERENCES}' is not the last ## section")]
    body = [line for line in lines[level2[-1].line :] if line.strip()]
    if not body or "https://" not in body[0]:
        return [(level2[-1].line, f"'## {REFERENCES}' does not start with the source URL")]
    return []


class Pages:
    """Reads each Markdown file once and keeps its lines and anchors."""

    def __init__(self) -> None:
        """Start with no file read."""
        self.cache: dict[Path, tuple[list[str], set[str], list[Heading]]] = {}

    def load(self, path: Path) -> tuple[list[str], set[str], list[Heading]]:
        """Return the lines, anchors and headings of one file; OSError if it cannot be read."""
        key = path.resolve()
        if key not in self.cache:
            lines = key.read_text(encoding="utf-8").split("\n")
            heads = headings(lines)
            self.cache[key] = (lines, {h.anchor for h in heads}, heads)
        return self.cache[key]


def check_links(page: Path, pages: Pages) -> list[Problem]:
    """Check every relative link and anchor of one page."""
    lines, anchors, _ = pages.load(page)
    problems: list[Problem] = []
    for n, target in links(lines):
        if SCHEME.match(target):
            continue
        path, _, anchor = target.partition("#")
        dest = page.parent / unquote(path) if path else page
        if not dest.exists():
            problems.append((n, f"{path} does not exist"))
            continue
        if not anchor or dest.suffix != ".md" or not dest.is_file():
            continue
        names = anchors if not path else pages.load(dest)[1]
        if unquote(anchor) not in names:
            where = f"in {path}" if path else "on this page"
            problems.append((n, f"#{anchor} matches no heading {where}"))
    return problems


def check_page(page: Path, pages: Pages, *, layout: bool) -> list[Problem]:
    """Run the selected checks on one page."""
    lines, _, heads = pages.load(page)
    found = check_toc(lines, heads) + check_references(lines, heads) if layout else []
    return sorted(found + check_links(page, pages))


class Args(argparse.Namespace):
    """Typed command-line arguments."""

    links_only: bool = False
    dirs: tuple[Path, ...] | list[Path] = ()


def main(argv: list[str]) -> int:
    """Check every Markdown file under the folders named on the command line."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    _ = parser.add_argument("--links-only", action="store_true", help="skip the layout checks")
    _ = parser.add_argument("dirs", nargs="+", type=Path, metavar="DIR")
    args = parser.parse_args(argv, namespace=Args())
    dirs, links_only = args.dirs, args.links_only
    missing = [d for d in dirs if not d.is_dir()]
    if missing:
        _ = sys.stderr.write(f"not a folder: {', '.join(map(str, missing))}\n")
        return 2
    pages = Pages()
    files = sorted({f for d in dirs for f in d.rglob("*.md") if f.is_file()})
    failed = total = 0
    for page in files:
        try:
            problems = check_page(page, pages, layout=not links_only)
        except (OSError, UnicodeDecodeError) as err:
            _ = sys.stderr.write(f"{page}: cannot read: {err}\n")
            return 2
        for n, message in problems:
            _ = sys.stdout.write(f"{page}:{n}: {message}\n")
        failed += bool(problems)
        total += len(problems)
    _ = sys.stdout.write(f"{len(files)} page(s) checked, {failed} with {total} problem(s)\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
