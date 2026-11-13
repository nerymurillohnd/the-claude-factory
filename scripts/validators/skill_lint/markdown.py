#!/usr/bin/env python3
"""A line-based scan of a skill's Markdown into a MarkdownDoc: blocks, comments, headings."""

from __future__ import annotations

import re

from validators.skill_lint.markdown_model import INLINE_CODE, DocBuilder, MarkdownDoc

FENCE_OPEN = re.compile(r"^( *)(`{3,}|~{3,})(.*)$")
"""Any indent: a list item's fence is indented, so its lines are code either way."""
ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
NOT_PARAGRAPH = re.compile(r"^ {0,3}(?:[-*+>]|\d+[.)]|#|\||<)")
LIST_ITEM = re.compile(r"^ {0,3}(?:[-*+]|\d{1,9}[.)])(?:[ \t]|$)")
COMMENT_OPEN = "<!--"
COMMENT_CLOSE = "-->"
CODE_INDENT = 4
"""The indent of an indented code block line."""
LIST_CONTENT_INDENT = 2
"""The least indent of a line that continues a list item after a blank line."""


def _indent(row: str) -> int:
    """Return a line's leading indent in columns, with tabs at 4."""
    expanded = row.expandtabs(CODE_INDENT)
    return len(expanded) - len(expanded.lstrip(" "))


def _close(lines: list[str], start: int, marker: str, indent: int) -> int:
    """Return the index of the line closing a fence, or len(lines) when it never closes.

    The closing fence may be indented up to 3 spaces more than the opening one.
    """
    char = re.escape(marker[0])
    closing = re.compile(rf"^ {{0,{indent + 3}}}{char}{{{len(marker)},}}[ \t]*$")
    for index in range(start, len(lines)):
        if closing.match(lines[index]):
            return index
    return len(lines)


def _container_end(lines: list[str], start: int, indent: int) -> int:
    """Return the index of the first non-blank line indented less than indent."""
    for index in range(start, len(lines)):
        if lines[index].strip() and _indent(lines[index]) < indent:
            return index
    return len(lines)


def _indented_end(lines: list[str], start: int) -> int:
    """Return the index after the last line of the indented code block starting at start."""
    last = start
    for index in range(start, len(lines)):
        if not lines[index].strip():
            continue
        if _indent(lines[index]) < CODE_INDENT:
            break
        last = index
    return last + 1


def _dedent(row: str, indent: int) -> str:
    """Remove up to indent leading spaces from a code content line."""
    return row[min(indent, len(row) - len(row.lstrip(" "))) :]


def _setext(lines: list[str], index: int) -> bool:
    """Tell whether a line is paragraph text underlined as a setext heading."""
    nxt = index + 1
    return (
        nxt < len(lines)
        and bool(lines[index].strip())
        and not NOT_PARAGRAPH.match(lines[index])
        and bool(SETEXT_UNDERLINE.match(lines[nxt]))
    )


def _split_comments(raw: str, *, inside: bool) -> tuple[str, str, bool]:
    """Split a line into its text outside and inside HTML comments.

    Markers inside inline code count for nothing. Returns (outside, inside text, whether a
    comment is still open at the end of the line).
    """
    masked = INLINE_CODE.sub(lambda match: " " * len(match.group(0)), raw)
    outside: list[str] = []
    hidden: list[str] = []
    pos = 0
    while True:
        marker = COMMENT_CLOSE if inside else COMMENT_OPEN
        found = masked.find(marker, pos)
        part = raw[pos:] if found < 0 else raw[pos:found]
        (hidden if inside else outside).append(part)
        if found < 0:
            return "".join(outside), " ".join(hidden), inside
        pos = found + len(marker)
        inside = not inside


class _Scanner:
    """Walks the lines once, tracking open comments, lists and blank lines."""

    def __init__(self, text: str, first_line: int) -> None:
        """Split the text into lines and start before the first one."""
        self.lines: list[str] = text.replace("\r\n", "\n").split("\n")
        self.first_line: int = first_line
        self.found: DocBuilder = DocBuilder()
        self.in_comment: bool = False
        self.in_list: bool = False
        self.after_blank: bool = True

    def run(self) -> MarkdownDoc:
        """Scan every line and return what was found."""
        index = 0
        while index < len(self.lines):
            raw = self.lines[index]
            if not raw.strip():
                self.after_blank = True
                index += 1
                continue
            index = self._block(index) or self._text(index)
            self.after_blank = False
        return self.found.build()

    def _block(self, index: int) -> int:
        """Record an indented code block or a fence starting at index; 0 when there is none."""
        if self.in_comment:
            return 0
        raw = self.lines[index]
        line = self.first_line + index
        if _indent(raw) >= CODE_INDENT and self.after_blank and not self.in_list:
            end = _indented_end(self.lines, index)
            body = [_dedent(row, CODE_INDENT) for row in self.lines[index:end]]
            self.found.fence("", body, line)
            return end
        fence = FENCE_OPEN.match(raw)
        if fence is None or (fence.group(2)[0] == "`" and "`" in fence.group(3)):
            return 0
        indent = len(fence.group(1))
        close = _close(self.lines, index + 1, fence.group(2), indent)
        end = close
        if close == len(self.lines) and indent > 0:
            end = _container_end(self.lines, index + 1, indent)
        body = [_dedent(row, indent) for row in self.lines[index + 1 : end]]
        self.found.fence(fence.group(3).strip(), body, line)
        return end + 1 if end == close else end

    def _text(self, index: int) -> int:
        """Record a heading or text line at index and return the next index."""
        raw = self.lines[index]
        line = self.first_line + index
        started_inside = self.in_comment
        outside, hidden, self.in_comment = _split_comments(raw, inside=started_inside)
        if started_inside or raw.lstrip().startswith(COMMENT_OPEN):
            self.found.text_line(outside, line, hidden)
            return index + 1
        heading = ATX_HEADING.match(outside)
        if heading is not None:
            self.in_list = False
            self.found.heading(heading.group(2) or "", line)
        elif _setext(self.lines, index):
            self.in_list = False
            self.found.heading(outside.strip(), line)
            self.found.text_line(outside, line, hidden)
            return index + 2
        elif LIST_ITEM.match(raw):
            self.in_list = True
        elif self.after_blank and _indent(raw) < LIST_CONTENT_INDENT:
            self.in_list = False
        self.found.text_line(outside, line, hidden)
        return index + 1


def parse_markdown(text: str, first_line: int = 1) -> MarkdownDoc:
    """Parse Markdown text whose first line is file line first_line."""
    return _Scanner(text, first_line).run()
