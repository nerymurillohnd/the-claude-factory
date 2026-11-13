#!/usr/bin/env python3
"""Content rules (CO-07 to CO-12) for a skill's links, reference depth and files."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import TYPE_CHECKING
from urllib.parse import unquote

from validators.skill_lint.discover import MARKDOWN
from validators.skill_lint.model import Finding, Severity
from validators.skill_lint.refs import Resolver, depths, escapes, reference_graph

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validators.skill_lint.discover import Skill
    from validators.skill_lint.markdown_model import MarkdownDoc

SKILLS_DOC = "https://code.claude.com/docs/en/skills"
BEST_PRACTICES_DOC = (
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
)
SOURCES: dict[str, str] = {
    "CO-07": SKILLS_DOC,
    "CO-08": "https://claude.com/docs/skills/how-to",
    "CO-09": BEST_PRACTICES_DOC,
    "CO-10": BEST_PRACTICES_DOC,
    "CO-11": BEST_PRACTICES_DOC,
    "CO-12": BEST_PRACTICES_DOC,
}

SKILL_MD = "SKILL.md"
TOC_MIN_LINES = 101
TOC_WINDOW = 20
TOC_MIN_LINKS = 2
TOC_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s.*\]\(#[^)]+\)")
HEADING = re.compile(r"^ {0,3}#{1,6}\s")
ESCAPING_TOKEN = re.compile(r"(?:\$\{?CLAUDE_(?:SKILL_DIR|PLUGIN_ROOT)\}?/|(?<![\w.])\.\./)\S*")
MONTH = "January|February|March|April|May|June|July|August|September|October|November|December"
CO11 = (
    re.compile(
        rf"\b(before|after|until|since|as of)\s+((?:{MONTH}|Q[1-4])\s+)?(19|20)\d{{2}}\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(currently|now|today|recently)\b.{0,40}\b(19|20)\d{2}\b", re.IGNORECASE),
    re.compile(r"\bin (19|20)\d{2}\b", re.IGNORECASE),
)
EXEMPT_PARTS = frozenset({"evals", "__pycache__"})
EXEMPT_NAMES = frozenset({".DS_Store", "__init__.py"})


def _finding(rule: str, severity: Severity, path: str, line: int | None, message: str) -> Finding:
    """Build one finding with the rule's source URL."""
    return Finding(rule, severity, path, line, message, SOURCES[rule])


def _anchor_ok(fragment: str, doc: MarkdownDoc | None) -> bool:
    """Tell whether a link fragment names an anchor of the target document."""
    if doc is None or not fragment:
        return True
    wanted = unquote(fragment).lower()
    return wanted in {anchor.lower() for anchor in doc.anchors}


def _co07_co08_links(skill: Skill, docs: Mapping[str, MarkdownDoc]) -> list[Finding]:
    """CO-07 and CO-08 for Markdown links: each resolves inside the skill folder."""
    resolver = Resolver(skill)
    findings: list[Finding] = []
    for rel, doc in sorted(docs.items()):
        for link in doc.links:
            path, _, fragment = link.target.partition("#")
            path = path.partition("?")[0]
            if not path:
                if not _anchor_ok(fragment, doc):
                    message = f"anchor `#{fragment}` names no heading in this file"
                    findings.append(_finding("CO-07", Severity.ERROR, rel, link.line, message))
                continue
            if escapes(skill, path, rel):
                message = f"link `{link.target}` leaves the skill folder"
                findings.append(_finding("CO-08", Severity.ERROR, rel, link.line, message))
                continue
            target = resolver.resolve(path, rel, link=True)
            if target is None:
                message = f"link `{link.target}` names no file in the skill"
                findings.append(_finding("CO-07", Severity.ERROR, rel, link.line, message))
            elif not _anchor_ok(fragment, docs.get(target)):
                message = f"anchor `#{fragment}` names no heading in {target}"
                findings.append(_finding("CO-07", Severity.ERROR, rel, link.line, message))
    return findings


def _co08_paths(skill: Skill, docs: Mapping[str, MarkdownDoc]) -> list[Finding]:
    """CO-08 for path tokens in code and symlinks: none reaches outside the skill folder."""
    findings: list[Finding] = []
    for rel, doc in sorted(docs.items()):
        for snippet in doc.code:
            tokens = {match.group(0) for match in ESCAPING_TOKEN.finditer(snippet.text)}
            for token in sorted(tokens):
                if escapes(skill, token, rel):
                    message = f"path `{token}` leaves the skill folder"
                    findings.append(_finding("CO-08", Severity.ERROR, rel, snippet.line, message))
    real_root = skill.root.resolve()
    for rel in skill.files:
        path = skill.root / rel
        if path.is_symlink() and not Path(os.path.realpath(path)).is_relative_to(real_root):
            message = "symlink points outside the skill folder"
            findings.append(_finding("CO-08", Severity.ERROR, rel, None, message))
    return findings


def _exempt(rel: str) -> bool:
    """Tell whether a file is exempt from CO-12."""
    parts = rel.split("/")
    return bool(EXEMPT_PARTS.intersection(parts[:-1])) or parts[-1] in EXEMPT_NAMES


def _co09_co12(skill: Skill) -> list[Finding]:
    """CO-09 (a Markdown file deeper than one level) and CO-12 (a file nothing references)."""
    reached = depths(reference_graph(skill))
    findings: list[Finding] = []
    for rel in skill.files:
        if rel == SKILL_MD:
            continue
        depth = reached.get(rel)
        if depth is None:
            if not _exempt(rel):
                message = "no file of the skill references this file"
                findings.append(_finding("CO-12", Severity.WARNING, rel, None, message))
        elif depth > 1 and rel.endswith(MARKDOWN):
            message = f"reached only through another file (depth {depth}); link it from SKILL.md"
            findings.append(_finding("CO-09", Severity.ERROR, rel, None, message))
    return findings


def _has_toc(lines: list[str]) -> bool:
    """Tell whether a reference file has a table of contents near its top."""
    start = next((i + 1 for i, line in enumerate(lines) if HEADING.match(line)), 0)
    window = [line for line in lines[start:] if line.strip()][:TOC_WINDOW]
    return sum(1 for line in window if TOC_ITEM.match(line)) >= TOC_MIN_LINKS


def _co10(skill: Skill) -> list[Finding]:
    """CO-10: a reference file over 100 lines has a table of contents."""
    findings: list[Finding] = []
    for rel, text in sorted(skill.text.items()):
        if rel == SKILL_MD or not rel.endswith(MARKDOWN):
            continue
        lines = text.replace("\r\n", "\n").split("\n")
        if lines and lines[-1] == "":
            _ = lines.pop()
        if len(lines) >= TOC_MIN_LINES and not _has_toc(lines):
            message = f"{len(lines)} lines and no table of contents in its first lines"
            findings.append(_finding("CO-10", Severity.ERROR, rel, 1, message))
    return findings


def _co11(docs: Mapping[str, MarkdownDoc]) -> list[Finding]:
    """CO-11: time-sensitive text outside code."""
    findings: list[Finding] = []
    for rel, doc in sorted(docs.items()):
        for line, text in doc.prose:
            match = next((m for pattern in CO11 if (m := pattern.search(text))), None)
            if match is not None:
                message = f"time-sensitive text: `{match.group(0)}`"
                findings.append(_finding("CO-11", Severity.WARNING, rel, line, message))
    return findings


def check(skill: Skill) -> list[Finding]:
    """Run CO-07 to CO-12 on one skill."""
    docs = skill.markdown
    return (
        _co07_co08_links(skill, docs)
        + _co08_paths(skill, docs)
        + _co09_co12(skill)
        + _co10(skill)
        + _co11(docs)
    )
