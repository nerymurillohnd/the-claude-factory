#!/usr/bin/env python3
"""Check a skill's files: inventory, links, pointers, tables of contents and scripts.

Usage: python3 check-structure.py <skill-dir> [--previous <json file>] [--output FILE]

Prints one JSON object on stdout:
  {"script": "check-structure", "skill": <abs path>, "ran": true,
   "inventory": [{"path", "lines", "executable"}], "inventory_truncated": <int>,
   "checks": [{"check", "item", "kind", "status", "location", "detail"}], "truncated": <int>}
The inventory lists every file, hidden ones included, sorted by path; lines is null for a binary
file. Diagnostics go to stderr. Exit codes: 0 the script ran (findings included); 2 usage error
(no such folder, no SKILL.md, bad arguments); 1 could not run (an unexpected error, on stderr).
--previous is accepted so the four scripts share one command form; this script doesn't read it.

Check ids and the checklist item each one serves (references/checklist.md); all are proved.
SKILL.md's length is check-size.py's (Z-1); S-1 is retired so the other ids stay stable:
  S-2  BS-11  every local Markdown link resolves to a file
  S-3  BS-11  every #anchor of a link, and every file.md#anchor pointer, names a heading
  S-4  BS-1   no file is linked only from a file other than SKILL.md (one level deep)
  S-5  BS-11  no unused file (evals/, __pycache__/ and .DS_Store exempt)
  S-6  BS-9   a Markdown file over 100 lines opens with a table of contents
  S-7  BS-9   every table-of-contents entry names a heading of its file
  S-8  BS-9   no backslash in a link target or a script path
  S-9  BS-3   no CLAUDE_SKILL_DIR variable inside a Markdown link target
  S-10 SC-9   every script starts with #!/usr/bin/env <interpreter>
  S-11 SC-9   every script has the executable bit
  S-12 SU-2   no path leaves the skill folder (../ above the skill, or a plugin-root path)

How the checks read Markdown:
- A link is [text](target), ![alt](target) or a [label]: target definition, outside fenced code
  blocks and inline code. Its target resolves relative to the file that holds it, as Markdown
  does. Targets with a scheme (https:, mailto:) are external and not checked.
- Anchors are GitHub-style: the heading lowercased, punctuation other than - and _ removed
  (backticks too), spaces turned into -, and a repeated heading suffixed -1, -2, ...
  Headings inside fenced code blocks and SKILL.md's frontmatter are not headings.
- A pointer is file.md#anchor written outside a link. In plain text both its file and its
  heading must exist; inside inline code only an existing file's heading is checked, so an
  example in code is not reported. A pointer resolves from its file's folder, then the skill root.
- A table of contents is a heading named Contents or Table of contents, as the file's first
  heading below the title, followed by a list of links. S-6 skips SKILL.md and files under
  assets/ and evals/, which aren't reference files.
- "Used" (S-5) flows from SKILL.md: a file is used when SKILL.md, or a file already used, links
  to it or names its path anywhere, code included (relative to the skill root, or to the naming
  file's folder).
- A script is a text file that starts with #!, or a file under scripts/ with a script suffix
  (.py, .sh, .bash, .zsh, .js, .mjs, .cjs, .ts, .rb, .pl) or none.
- Paths outside links are read only where the skill reads or runs them: SKILL.md (code
  included, since commands live there) and scripts. Paths shown in references and assets are
  documentation or templates and are not checked. S-8 reads backslash paths in SKILL.md (and
  link targets in every Markdown file). S-12 reads links in every Markdown file, ../ paths in
  SKILL.md, and plugin-root paths in SKILL.md and scripts; a plugin-root path is allowed only
  when it resolves inside this skill (the plugin root is the nearest ancestor holding
  .claude-plugin/plugin.json).
--output FILE also writes the same JSON object to FILE (UTF-8, overwritten, parent folders
created), so the next script can read it with --previous without a shell redirect, which
Claude Code checks against its edit rules. stdout is unchanged. If FILE can't be written, the
script prints nothing on stdout, names FILE on stderr and exits 1.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote

MAX_CHECKS = 200  # the orchestrator reads the whole result inline; 200 short entries stay small
MAX_DETAIL = 300  # characters per detail, so one finding can't flood the output
MAX_FILES = 5000  # chat's plugin upload limit; a larger folder is not a skill to walk whole
MAX_INVENTORY = 1000  # inventory entries printed; the rest are counted, so a skill with a large
# assets/ folder doesn't flood the orchestrator's context with file names
MAX_READ = 2 * 1024 * 1024  # bytes of one file read for content checks; a skill's text files are
# far smaller, and the bound keeps a stray large file from slowing the walk
TOC_THRESHOLD = 100  # [PL]
SECTION_LEVEL = 2  # "##": the first heading level below a file's title
SCRIPT_SUFFIXES = frozenset({".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb"})
SCRIPT_SUFFIXES_EXTRA = frozenset({".pl", ""})
EXEMPT_PARTS = frozenset({"__pycache__", ".DS_Store"})
TOC_NAMES = frozenset({"contents", "table of contents"})
NO_TOC_FOLDERS = ("assets/", "evals/")

FENCE_RE = re.compile(r" {0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r" {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*")
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
LINK_TEXT = r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]"
LINK_TARGET = r"\(\s*(<[^>]*>|[^()\s]*(?:\([^()\s]*\)[^()\s]*)*)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
LINK_RE = re.compile(LINK_TEXT + LINK_TARGET)
DEFINITION_RE = re.compile(r" {0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")
SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
POINTER_RE = re.compile(r"(?<![\w./-])((?:[\w.-]+/)*[\w.-]+\.md)#([\w-]+)")
LIST_ITEM_RE = re.compile(r"\s*(?:[-*+]|\d+[.)])\s+")
BACKSLASH_PATH_RE = re.compile(
    r"[\w.-]+(?:\\[\w.-]+)+\.(?:py|sh|bash|zsh|js|mjs|cjs|ts|rb|pl|md|json|txt)\b"
)
PARENT_PATH_RE = re.compile(r"(?<![\w.])(?:\.\./)+[\w./-]*")
PLUGIN_ROOT_RE = re.compile(r"\$(?:\{CLAUDE_PLUGIN_ROOT\}|CLAUDE_PLUGIN_ROOT\b)/([\w./-]*)")
SHEBANG_RE = re.compile(r"#!/usr/bin/env[ \t]+(?:-S[ \t]+)?\S+")
SLUG_DROP_RE = re.compile(r"[^\w\- ]")
HEADING_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")

CHECKS: dict[str, tuple[str, str]] = {
    "S-2": ("BS-11", "proved"),
    "S-3": ("BS-11", "proved"),
    "S-4": ("BS-1", "proved"),
    "S-5": ("BS-11", "proved"),
    "S-6": ("BS-9", "proved"),
    "S-7": ("BS-9", "proved"),
    "S-8": ("BS-9", "proved"),
    "S-9": ("BS-3", "proved"),
    "S-10": ("SC-9", "proved"),
    "S-11": ("SC-9", "proved"),
    "S-12": ("SU-2", "proved"),
}
PASS_DETAILS = {
    "S-2": "every local link resolves",
    "S-3": "every anchor and pointer names a heading",
    "S-4": "every linked file is linked from SKILL.md",
    "S-5": "every file is used",
    "S-6": "every Markdown file over 100 lines has a table of contents",
    "S-7": "every table-of-contents entry names a heading",
    "S-8": "no backslash in link targets or script paths",
    "S-9": "no CLAUDE_SKILL_DIR variable in a link target",
    "S-10": "every script has a #!/usr/bin/env line",
    "S-11": "every script is executable",
    "S-12": "no path leaves the skill folder",
}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def clip(text: str) -> str:
    """Cut a detail to MAX_DETAIL characters."""
    return text if len(text) <= MAX_DETAIL else text[: MAX_DETAIL - 1] + "…"


@dataclass
class Report:
    """Collects check results; passes are added for proved checks that ran without failing."""

    table: dict[str, tuple[str, str]]
    found: list[dict[str, object]] = field(default_factory=list[dict[str, object]])
    applied: dict[str, str] = field(default_factory=dict[str, str])
    failed: set[str] = field(default_factory=set[str])
    seen: set[tuple[str, str, str]] = field(default_factory=set[tuple[str, str, str]])

    def _entry(self, cid: str, status: str, location: str | None, detail: str) -> dict[str, object]:
        item, kind = self.table[cid]
        return {
            "check": cid,
            "item": item,
            "kind": kind,
            "status": status,
            "location": location,
            "detail": clip(detail),
        }

    def fail(self, cid: str, location: str, detail: str) -> None:
        """Record a failure of a proved check, once per check, location and detail."""
        key = (cid, location, detail)
        if key in self.seen:
            return
        self.seen.add(key)
        self.failed.add(cid)
        self.found.append(self._entry(cid, "fail", location, detail))

    def ran(self, cid: str, detail: str) -> None:
        """Mark a proved check as run; it passes with this detail unless it fails."""
        _ = self.applied.setdefault(cid, detail)

    def results(self) -> tuple[list[dict[str, object]], int]:
        """Failures first, then passes, cut to MAX_CHECKS."""
        passes = [
            self._entry(cid, "pass", None, self.applied[cid])
            for cid in self.table
            if cid in self.applied and cid not in self.failed
        ]
        everything = self.found + passes
        return everything[:MAX_CHECKS], max(0, len(everything) - MAX_CHECKS)


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------


@dataclass
class FileInfo:
    """One file of the skill."""

    rel: str
    path: Path
    lines: int | None
    executable: bool
    text: str | None


def read_file(path: Path) -> tuple[int | None, str | None]:
    """Line count and text (first MAX_READ bytes) of a text file; (None, None) for binary."""
    with path.open("rb") as handle:
        head = handle.read(MAX_READ)
        newlines = head.count(b"\n")
        last = head[-1:]
        while chunk := handle.read(MAX_READ):
            newlines += chunk.count(b"\n")
            last = chunk[-1:]
    if len(head) == MAX_READ:
        _ = sys.stderr.write(
            f"check-structure: {path.name}: only the first {MAX_READ} bytes checked\n"
        )
    if b"\0" in head:
        return None, None
    lines = newlines + (1 if last not in (b"", b"\n") else 0)
    return lines, head.decode("utf-8", errors="replace")


def walk(skill: Path) -> tuple[list[FileInfo], int]:
    """Every file under the skill, hidden ones included, sorted; and the count past MAX_FILES."""
    found: list[tuple[str, Path]] = []
    for folder, dirs, names in os.walk(skill):
        dirs.sort()
        for name in names:
            path = Path(folder) / name
            found.append((path.relative_to(skill).as_posix(), path))
    found.sort()
    files: list[FileInfo] = []
    for rel, path in found[:MAX_FILES]:
        try:
            lines, text = read_file(path) if path.is_file() else (None, None)
        except OSError as error:
            _ = sys.stderr.write(f"check-structure: could not read {rel}: {error}\n")
            lines, text = None, None
        files.append(FileInfo(rel, path, lines, os.access(path, os.X_OK), text))
    return files, max(0, len(found) - MAX_FILES)


def is_script(info: FileInfo) -> bool:
    """A text file with a shebang, or a file under scripts/ with a script suffix or none."""
    if info.text is None:
        return False
    if info.text.startswith("#!"):
        return True
    suffix = posixpath.splitext(info.rel)[1].lower()
    in_scripts = info.rel.startswith("scripts/") and "__pycache__" not in info.rel
    return in_scripts and (suffix in SCRIPT_SUFFIXES or suffix in SCRIPT_SUFFIXES_EXTRA)


def plugin_root(skill: Path) -> Path | None:
    """The nearest ancestor holding .claude-plugin/plugin.json, if any."""
    for folder in (skill, *skill.parents):
        if (folder / ".claude-plugin" / "plugin.json").is_file():
            return folder
    return None


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def slug(text: str) -> str:
    """GitHub's anchor for a heading text (before the duplicate suffix)."""
    plain = HEADING_LINK_RE.sub(r"\1", text).strip().lower()
    return SLUG_DROP_RE.sub("", plain).replace(" ", "-")


@dataclass
class Link:
    """A link or a pointer found in a Markdown file."""

    line: int
    target: str
    toc: bool = False


@dataclass
class Doc:
    """A Markdown file split into prose (code masked) and code, with its headings."""

    rel: str
    prose: list[str] = field(default_factory=list[str])
    code: list[tuple[int, str]] = field(default_factory=list[tuple[int, str]])
    headings: list[tuple[int, int, str]] = field(default_factory=list[tuple[int, int, str]])
    anchors: set[str] = field(default_factory=set[str])
    links: list[Link] = field(default_factory=list[Link])

    @property
    def folder(self) -> str:
        """The file's folder, relative to the skill ('' at the root)."""
        return posixpath.dirname(self.rel)


def frontmatter_end(lines: list[str]) -> int:
    """Index of the first line after a leading frontmatter block, or 0."""
    if not lines or lines[0].rstrip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return index + 1
    return 0


def mask_code(line: str) -> tuple[str, list[str]]:
    """The line with inline code replaced by spaces, and the code spans' contents."""
    spans = [m.group(2) for m in CODE_SPAN_RE.finditer(line)]
    masked = CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), line)
    return masked, spans


def split_doc(rel: str, text: str) -> Doc:
    """Separate prose from code and collect headings."""
    doc = Doc(rel)
    lines = text.splitlines()
    start = frontmatter_end(lines)
    fence = ""
    for index, line in enumerate(lines):
        number = index + 1
        opener = FENCE_RE.match(line)
        if index < start:
            doc.prose.append("")
        elif fence:
            doc.prose.append("")
            closes = opener is not None and opener.group(1)[0] == fence[0]
            if closes and opener is not None and len(opener.group(1)) >= len(fence):
                fence = ""
            else:
                doc.code.append((number, line))
        elif opener:
            fence = opener.group(1)
            doc.prose.append("")
        else:
            masked, spans = mask_code(line)
            doc.prose.append(masked)
            doc.code.extend((number, span) for span in spans)
            heading = HEADING_RE.fullmatch(line)
            if heading:
                doc.headings.append((number, len(heading.group(1)), heading.group(2) or ""))
    doc.anchors = anchors_of(doc.headings)
    return doc


def anchors_of(headings: list[tuple[int, int, str]]) -> set[str]:
    """Every anchor, with GitHub's -1, -2 suffixes for repeated headings."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for _, _, text in headings:
        base = slug(text)
        count = counts.get(base, 0)
        anchors.add(base if count == 0 else f"{base}-{count}")
        counts[base] = count + 1
    return anchors


def toc_range(doc: Doc) -> tuple[int, int] | None:
    """Line range (heading line, next heading line) of the table of contents, if any."""
    below_title = [h for h in doc.headings if h[1] >= SECTION_LEVEL]
    if not below_title or below_title[0][2].strip().lower() not in TOC_NAMES:
        return None
    start = below_title[0][0]
    later = [h[0] for h in doc.headings if h[0] > start]
    return start, later[0] if later else len(doc.prose) + 1


def collect_links(doc: Doc) -> None:
    """Links from the prose, marking those in the table of contents."""
    toc = toc_range(doc)
    for index, line in enumerate(doc.prose):
        number = index + 1
        in_toc = toc is not None and toc[0] < number < toc[1] and bool(LIST_ITEM_RE.match(line))
        targets = [m.group(1) for m in LINK_RE.finditer(line)]
        definition = DEFINITION_RE.match(line)
        if definition:
            targets.append(definition.group(1))
        doc.links.extend(Link(number, t.strip("<>"), toc=in_toc) for t in targets)


# ---------------------------------------------------------------------------
# Link and pointer checks
# ---------------------------------------------------------------------------


@dataclass
class Skill:
    """The skill under check: its files, Markdown documents and link graph."""

    root: Path
    files: dict[str, FileInfo]
    docs: dict[str, Doc]
    plugin: Path | None
    graph: dict[str, list[tuple[int, str]]] = field(
        default_factory=dict[str, list[tuple[int, str]]]
    )

    def inside(self, rel: str) -> bool:
        """Whether a normalized relative path stays inside the skill."""
        return rel != ".." and not rel.startswith("../") and not posixpath.isabs(rel)

    def exists(self, rel: str) -> bool:
        """Whether a relative path names a file or folder of the skill."""
        return rel in ("", ".") or (self.root / rel).exists()


def location(rel: str, line: int) -> str:
    """A location relative to the skill."""
    return f"{rel}:{line}"


def resolve(folder: str, target: str) -> str:
    """A target relative to a folder, normalized; '' for the skill root."""
    joined = posixpath.normpath(posixpath.join(folder, target)) if target else folder
    return "" if joined == "." else joined


def check_anchor(skill: Skill, report: Report, doc: Doc, link: Link, rel: str) -> None:
    """S-3 or S-7 for the #anchor of a link to rel."""
    anchor = unquote(link.target.partition("#")[2])
    target = skill.docs.get(rel)
    if not anchor or target is None:
        return
    if anchor.lower() not in target.anchors:
        cid = "S-7" if link.toc and rel == doc.rel else "S-3"
        where = "this file" if rel == doc.rel else rel
        report.fail(cid, location(doc.rel, link.line), f"#{anchor} names no heading in {where}")


def check_link(skill: Skill, report: Report, doc: Doc, link: Link) -> None:
    """S-2, S-3, S-7, S-8, S-9 and S-12 for one link."""
    target = link.target
    where = location(doc.rel, link.line)
    if not target or SCHEME_RE.match(target):
        return
    if "\\" in target:
        report.fail("S-8", where, f"link target {target[:80]!r} uses a backslash; use /")
        return
    if "CLAUDE_SKILL_DIR" in target:
        report.fail("S-9", where, "CLAUDE_SKILL_DIR is not replaced in chat; link relative paths")
        return
    path = unquote(target.partition("#")[0])
    rel = doc.rel if not path else resolve(doc.folder, path)
    if path.startswith("/") or not skill.inside(rel):
        report.fail("S-12", where, f"link {target[:80]!r} leaves the skill folder")
        return
    if not skill.exists(rel):
        report.fail("S-2", where, f"link {target[:80]!r} resolves to {rel}, which doesn't exist")
        return
    if rel != doc.rel and rel in skill.files:
        skill.graph.setdefault(doc.rel, []).append((link.line, rel))
    check_anchor(skill, report, doc, link, rel)


def check_links(skill: Skill, report: Report, doc: Doc) -> None:
    """Every link of one Markdown file."""
    for link in doc.links:
        check_link(skill, report, doc, link)


def pointer_target(skill: Skill, doc: Doc, path: str) -> str | None:
    """A pointer's file: from the pointing file's folder, then from the skill root."""
    for rel in (resolve(doc.folder, path), resolve("", path)):
        if skill.inside(rel) and rel in skill.docs:
            return rel
    return None


def check_pointers(skill: Skill, report: Report, doc: Doc) -> None:
    """S-3 for file.md#anchor pointers outside links."""
    sources = [(i + 1, LINK_RE.sub(" ", line), True) for i, line in enumerate(doc.prose)]
    sources += [(number, text, False) for number, text in doc.code]
    for number, text, in_prose in sources:
        for match in POINTER_RE.finditer(text):
            path, anchor = match.group(1), match.group(2)
            rel = pointer_target(skill, doc, path)
            where = location(doc.rel, number)
            if rel is None:
                if in_prose:
                    report.fail("S-3", where, f"pointer {path}#{anchor}: {path} doesn't exist")
                continue
            if anchor.lower() not in skill.docs[rel].anchors:
                report.fail("S-3", where, f"pointer {path}#{anchor} names no heading in {rel}")


def check_depth(skill: Skill, report: Report) -> None:
    """S-4: every file linked from another file is also linked from SKILL.md."""
    direct = {rel for _, rel in skill.graph.get("SKILL.md", [])}
    for source, edges in sorted(skill.graph.items()):
        if source == "SKILL.md":
            continue
        for line, rel in edges:
            if rel != "SKILL.md" and rel not in direct:
                report.fail(
                    "S-4",
                    location(source, line),
                    f"{rel} is linked from {source} but not from SKILL.md; link it one level deep",
                )


def check_toc(report: Report, doc: Doc, lines: int) -> None:
    """S-6: a Markdown file over 100 lines opens with a table of contents."""
    if doc.rel == "SKILL.md" or doc.rel.startswith(NO_TOC_FOLDERS) or lines <= TOC_THRESHOLD:
        return
    toc = toc_range(doc)
    has_list = toc is not None and any(link.toc for link in doc.links)
    if not has_list:
        detail = (
            f"{lines} lines and no table of contents: a Contents heading with a list of links, "
            "as the first heading below the title"
        )
        report.fail("S-6", location(doc.rel, 1), detail)


# ---------------------------------------------------------------------------
# Use, paths and scripts
# ---------------------------------------------------------------------------


def mention_pattern(needle: str) -> re.Pattern[str]:
    """A path mention with path boundaries on both sides."""
    after = r"(?![\w-]|\.\w)"
    if "/" in needle:
        return re.compile(r"(?<![\w.-])" + re.escape(needle) + after)
    return re.compile(r"(?:(?<=\}/)|(?<=\./)|(?<![\w./-]))" + re.escape(needle) + after)


def mentioned(text: str, needles: set[str]) -> bool:
    """Whether any needle occurs in the text as a path."""
    return any(n in text and mention_pattern(n).search(text) for n in needles)


def used_files(skill: Skill) -> set[str]:
    """Files reached from SKILL.md through links and path mentions."""
    used = {"SKILL.md"}
    queue = ["SKILL.md"]
    while queue:
        source = queue.pop()
        text = skill.files[source].text or ""
        folder = posixpath.dirname(source)
        linked = {rel for _, rel in skill.graph.get(source, [])}
        for rel in skill.files:
            if rel in used:
                continue
            needles = {rel, posixpath.relpath(rel, folder or ".")}
            if rel in linked or mentioned(text, needles):
                used.add(rel)
                queue.append(rel)
    return used


def exempt(rel: str) -> bool:
    """Files the unused check skips."""
    parts = rel.split("/")
    return rel == "SKILL.md" or parts[0] == "evals" or bool(EXEMPT_PARTS.intersection(parts))


def check_unused(skill: Skill, report: Report) -> None:
    """S-5: every file is used."""
    used = used_files(skill)
    for rel in skill.files:
        if rel not in used and not exempt(rel):
            report.fail(
                "S-5",
                location(rel, 1),
                f"{rel} is neither linked nor named from SKILL.md or a file it uses",
            )


def check_parent_paths(skill: Skill, report: Report, doc: Doc) -> None:
    """S-12: ../ paths in a Markdown file that climb above the skill."""
    sources = [(i + 1, LINK_RE.sub(" ", line)) for i, line in enumerate(doc.prose)]
    for number, text in [*sources, *doc.code]:
        for match in PARENT_PATH_RE.finditer(text):
            rel = resolve(doc.folder, match.group(0))
            if not skill.inside(rel):
                report.fail(
                    "S-12",
                    location(doc.rel, number),
                    f"{match.group(0)[:80]} leaves the skill folder; chat copies only the skill",
                )


def check_plugin_root(skill: Skill, report: Report, info: FileInfo) -> None:
    """S-12: plugin-root paths must resolve inside the skill."""
    for index, line in enumerate((info.text or "").splitlines()):
        for match in PLUGIN_ROOT_RE.finditer(line):
            inside = False
            if skill.plugin is not None and match.group(1):
                target = (skill.plugin / match.group(1)).resolve()
                inside = target == skill.root or target.is_relative_to(skill.root)
            if not inside:
                report.fail(
                    "S-12",
                    location(info.rel, index + 1),
                    f"{match.group(0)[:80]} is outside the skill; chat copies only the skill",
                )


def check_backslash_paths(report: Report, info: FileInfo) -> None:
    """S-8: backslashes in script or file paths in a Markdown file."""
    for index, line in enumerate((info.text or "").splitlines()):
        match = BACKSLASH_PATH_RE.search(line)
        if match:
            report.fail(
                "S-8", location(info.rel, index + 1), rf"{match.group(0)[:80]} uses \; use /"
            )


def check_script(report: Report, info: FileInfo) -> None:
    """S-10 and S-11 for one script."""
    first = (info.text or "").split("\n", 1)[0].rstrip("\r")
    if not SHEBANG_RE.fullmatch(first.rstrip()):
        shown = first[:60] if first.startswith("#!") else "no shebang"
        report.fail(
            "S-10", location(info.rel, 1), f"{shown}: start with #!/usr/bin/env <interpreter>"
        )
    if not info.executable:
        report.fail("S-11", location(info.rel, 1), f"{info.rel} lacks the executable bit")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build(root: Path, files: list[FileInfo]) -> Skill:
    """Parse every Markdown file and collect its links."""
    by_rel = {f.rel: f for f in files}
    docs: dict[str, Doc] = {}
    for info in files:
        if info.rel.lower().endswith(".md") and info.text is not None:
            doc = split_doc(info.rel, info.text)
            collect_links(doc)
            docs[info.rel] = doc
    return Skill(root, by_rel, docs, plugin_root(root))


def run_checks(skill: Skill, report: Report) -> None:
    """Every check, in id order."""
    for cid, detail in PASS_DETAILS.items():
        report.ran(cid, detail)
    for doc in skill.docs.values():
        check_links(skill, report, doc)
    for doc in skill.docs.values():
        check_pointers(skill, report, doc)
        check_toc(report, doc, skill.files[doc.rel].lines or 0)
    check_parent_paths(skill, report, skill.docs["SKILL.md"])
    check_backslash_paths(report, skill.files["SKILL.md"])
    check_depth(skill, report)
    check_unused(skill, report)
    check_plugin_root(skill, report, skill.files["SKILL.md"])
    for info in skill.files.values():
        if is_script(info):
            check_plugin_root(skill, report, info)
            check_script(report, info)


def emit(text: str, output: Path | None) -> int:
    """Write the result to --output FILE when given, then to stdout; 1 if FILE can't be written."""
    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _ = output.write_text(text, encoding="utf-8", newline="")
        except OSError as error:
            _ = sys.stderr.write(
                f"check-structure: --output {output}: could not write the result: {error}\n"
            )
            return 1
    _ = sys.stdout.write(text)
    return 0


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    skill_dir: Path = Path()
    previous: Path | None = None
    output: Path | None = None


def parse_args(argv: list[str] | None) -> Args:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        prog="check-structure.py",
        description="Check a skill's files and links and print one JSON result.",
        epilog=(
            "Example: python3 check-structure.py path/to/my-skill\n"
            "Exit codes: 0 ran (findings are in the JSON), 2 usage error, 1 could not run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("skill_dir", type=Path, help="the skill folder (holds SKILL.md)")
    _ = parser.add_argument(
        "--previous", type=Path, help="accepted for a uniform command form; not read"
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="also write the JSON result to FILE (parent folders created, overwritten)",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str] | None = None) -> int:
    """Run the checks and print the JSON result."""
    args = parse_args(argv)
    root = args.skill_dir.expanduser()
    if not root.is_dir():
        _ = sys.stderr.write(f"check-structure: no such folder: {root}\n")
        return 2
    root = root.resolve()
    if not (root / "SKILL.md").is_file():
        _ = sys.stderr.write(f"check-structure: {root} has no SKILL.md; pass the skill folder\n")
        return 2
    try:
        files, skipped = walk(root)
    except OSError as error:
        _ = sys.stderr.write(f"check-structure: could not walk {root}: {error}\n")
        return 1
    if skipped:
        _ = sys.stderr.write(f"check-structure: {skipped} files past {MAX_FILES} not checked\n")
    skill = build(root, files)
    if "SKILL.md" not in skill.docs:
        _ = sys.stderr.write(f"check-structure: {root}/SKILL.md is not readable UTF-8 text\n")
        return 1
    report = Report(CHECKS)
    run_checks(skill, report)
    checks, truncated = report.results()
    inventory: list[dict[str, object]] = [
        {"path": f.rel, "lines": f.lines, "executable": f.executable} for f in files
    ]
    result: dict[str, object] = {
        "script": "check-structure",
        "skill": str(root),
        "ran": True,
        "inventory": inventory[:MAX_INVENTORY],
        "inventory_truncated": max(0, len(inventory) - MAX_INVENTORY) + skipped,
        "checks": checks,
        "truncated": truncated,
    }
    return emit(json.dumps(result, indent=1) + "\n", args.output)


if __name__ == "__main__":
    raise SystemExit(main())
