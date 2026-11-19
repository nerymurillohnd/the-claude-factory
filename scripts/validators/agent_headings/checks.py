#!/usr/bin/env python3
"""The heading rules of agent-headings, applied to one file's text.

A subagent's body is a prompt whose structure comes from uppercase labels, never from Markdown
headings (.claude/rules/code-quality/agent-and-command-style.md). Headings are recognized as
CommonMark defines them, outside the YAML frontmatter and outside fenced code blocks, where a
report template may hold headings of its own.
"""

from dataclasses import dataclass
import re

ATX = re.compile(r" {0,3}#{1,6}(?:[ \t]|$)")
SETEXT_UNDERLINE = re.compile(r" {0,3}(?:=+|-+)[ \t]*$")
FENCE_OPEN = re.compile(r" {0,3}(`{3,}|~{3,})(.*)$")
LIST_ITEM = re.compile(r" {0,3}(?:[-*+]|\d{1,9}[.)])(?:[ \t]|$)")
NOT_PARAGRAPH = re.compile(r" {0,3}(?:[>|]|<)")
FRONTMATTER_FENCE = "---"


@dataclass(frozen=True)
class Finding:
    """One heading: its 1-based line, its rule and what to do."""

    line: int
    rule: str
    message: str


def _frontmatter_end(lines: list[str]) -> int:
    """Return the index of the first body line: past a closed frontmatter, else 0."""
    if not lines or lines[0].rstrip() != FRONTMATTER_FENCE:
        return 0
    for index in range(1, len(lines)):
        if lines[index].rstrip() in {FRONTMATTER_FENCE, "..."}:
            return index + 1
    return 0


def _closes(line: str, char: str, length: int) -> bool:
    """Whether line closes a fence opened with length repetitions of char."""
    match = re.fullmatch(r" {0,3}(`+|~+)[ \t]*", line)
    return match is not None and match[1][0] == char and len(match[1]) >= length


def _is_paragraph(line: str) -> bool:
    """Whether a line can be the text a setext underline turns into a heading."""
    return bool(
        line.strip()
        and not ATX.match(line)
        and not LIST_ITEM.match(line)
        and not NOT_PARAGRAPH.match(line)
        and not SETEXT_UNDERLINE.match(line)
        and not line.startswith(("    ", "\t"))
    )


def check_text(text: str) -> list[Finding]:
    """Return every Markdown heading in the body of a subagent file."""
    lines = text.splitlines()
    findings: list[Finding] = []
    fence: tuple[str, int] | None = None
    previous = ""
    for index in range(_frontmatter_end(lines), len(lines)):
        line = lines[index]
        if fence is not None:
            if _closes(line, *fence):
                fence = None
            previous = ""
            continue
        opening = FENCE_OPEN.match(line)
        if opening and not (opening[1][0] == "`" and "`" in opening[2]):
            fence = (opening[1][0], len(opening[1]))
            previous = ""
            continue
        if ATX.match(line):
            message = "Markdown heading: make it an uppercase label on its own line, as LABEL:"
            findings.append(Finding(index + 1, "AH-01", message))
        elif SETEXT_UNDERLINE.match(line) and _is_paragraph(previous):
            message = "setext heading (a line underlined with = or -): make it an uppercase label"
            findings.append(Finding(index + 1, "AH-02", message))
        previous = line
    return findings
