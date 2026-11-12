"""A line-based model of a skill's Markdown: links, headings, anchors, code, ! commands, prose."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import unquote

FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
LINK_TARGET = r"(<[^<>\n]*>|[^\s()<>]*(?:\([^\s()]*\)[^\s()]*)*)"
LINK_TITLE = r"""(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?"""
INLINE_LINK = re.compile(r"\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*" + LINK_TARGET + LINK_TITLE + r"\s*\)")
REF_DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(<[^<>\n]*>|\S+)" + LINK_TITLE + r"\s*$")
ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
NOT_PARAGRAPH = re.compile(r"^ {0,3}(?:[-*+>]|\d+[.)]|#|\||<)")
EXPLICIT_ANCHOR = re.compile(r"""<a\s[^>]*?\b(?:id|name)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
SKIPPED_SCHEMES = re.compile(r"^(?:https?|mailto):", re.IGNORECASE)
SLUG_DROP = re.compile(r"[^\w\- ]")
MARKUP_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
MARKUP_TAG = re.compile(r"<[^>]+>")
MARKUP_EMPHASIS = re.compile(r"(?<!\w)_+([^_]+)_+(?!\w)")
BANG_INFO = "!"


@dataclass(frozen=True)
class Link:
    """A link target outside code: unwrapped from <...>, without title, percent-decoded."""

    target: str
    line: int


@dataclass(frozen=True)
class Heading:
    """A heading, with its GitHub slug."""

    text: str
    line: int
    slug: str


@dataclass(frozen=True)
class BangCommand:
    """A ``!`cmd` `` (block False) or a fence with the info string ``!`` (block True).

    A block command's line is the line of its opening fence.
    """

    command: str
    line: int
    block: bool


@dataclass(frozen=True)
class CodeSnippet:
    """Inline code or a fenced block; a block's line is the line of its opening fence."""

    text: str
    line: int
    lang: str | None
    inline: bool


@dataclass(frozen=True)
class MarkdownDoc:
    """Everything the rules read from one Markdown text."""

    links: tuple[Link, ...]
    headings: tuple[Heading, ...]
    anchors: frozenset[str]
    bang_commands: tuple[BangCommand, ...]
    code: tuple[CodeSnippet, ...]
    prose: tuple[tuple[int, str], ...]
    """Non-blank lines outside fences, with inline code removed."""


def github_slug(text: str, seen: dict[str, int]) -> str:
    """Return GitHub's anchor slug for a heading's text, numbering repeats through seen."""
    base = SLUG_DROP.sub("", text.lower()).replace(" ", "-")
    slug = base
    while slug in seen:
        seen[base] += 1
        slug = f"{base}-{seen[base]}"
    seen[slug] = 0
    return slug


def _plain(text: str) -> str:
    """Strip inline markup from heading text the way GitHub renders it."""
    text = MARKUP_LINK.sub(r"\1", text)
    text = MARKUP_TAG.sub("", text).replace("`", "").replace("*", "")
    return MARKUP_EMPHASIS.sub(r"\1", text).strip()


def _target(raw: str) -> str | None:
    """Unwrap and decode a link target; None for external or empty targets."""
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    target = unquote(raw.strip())
    if not target or SKIPPED_SCHEMES.match(target):
        return None
    return target


class _Builder:
    """Accumulates the parts of a MarkdownDoc while lines are scanned."""

    def __init__(self) -> None:
        """Start with nothing found."""
        self.links: list[Link] = []
        self.headings: list[Heading] = []
        self.anchors: set[str] = set()
        self.bangs: list[BangCommand] = []
        self.code: list[CodeSnippet] = []
        self.prose: list[tuple[int, str]] = []
        self.seen: dict[str, int] = {}

    def heading(self, raw: str, line: int) -> None:
        """Record a heading and its slug."""
        text = _plain(raw)
        slug = github_slug(text, self.seen)
        self.headings.append(Heading(text, line, slug))
        self.anchors.add(slug)

    def fence(self, info: str, body: list[str], line: int) -> None:
        """Record a fenced block, and a block ! command when the info string is !."""
        text = "".join(f"{row}\n" for row in body)
        lang = info.split(maxsplit=1)[0] if info.split() else None
        self.code.append(CodeSnippet(text, line, lang, inline=False))
        if info == BANG_INFO:
            self.bangs.append(BangCommand(text, line, block=True))

    def text_line(self, raw: str, line: int) -> None:
        """Record the inline code, ! commands, links, anchors and prose of a line."""
        definition = REF_DEFINITION.match(raw)
        if definition is not None and not definition.group(1).startswith("^"):
            target = _target(definition.group(2))
            if target is not None:
                self.links.append(Link(target, line))
            return
        prose = INLINE_CODE.sub(lambda match: self._inline(raw, match, line), raw)
        for match in INLINE_LINK.finditer(prose):
            target = _target(match.group(1))
            if target is not None:
                self.links.append(Link(target, line))
        self.anchors.update(found.group(1) for found in EXPLICIT_ANCHOR.finditer(prose))
        if prose.strip():
            self.prose.append((line, prose.strip()))

    def _inline(self, raw: str, match: re.Match[str], line: int) -> str:
        """Record one inline code span and return the text that replaces it in prose."""
        content = match.group(2)
        if len(content) > 1 and content.startswith(" ") and content.endswith(" "):
            content = content[1:-1]
        self.code.append(CodeSnippet(content, line, None, inline=True))
        start = match.start()
        before = raw[start - 1] if start else ""
        bang = raw[start - 2] if start > 1 else ""
        if before == BANG_INFO and (start == 1 or bang.isspace()):
            self.bangs.append(BangCommand(content, line, block=False))
        return ""

    def build(self) -> MarkdownDoc:
        """Freeze what was found."""
        return MarkdownDoc(
            links=tuple(self.links),
            headings=tuple(self.headings),
            anchors=frozenset(self.anchors),
            bang_commands=tuple(self.bangs),
            code=tuple(self.code),
            prose=tuple(self.prose),
        )


def _close(lines: list[str], start: int, marker: str) -> int:
    """Return the index of the line closing a fence, or len(lines) when it never closes."""
    closing = re.compile(rf"^ {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*$")
    for index in range(start, len(lines)):
        if closing.match(lines[index]):
            return index
    return len(lines)


def _setext(lines: list[str], index: int) -> bool:
    """Tell whether a line is paragraph text underlined as a setext heading."""
    nxt = index + 1
    return (
        nxt < len(lines)
        and bool(lines[index].strip())
        and not NOT_PARAGRAPH.match(lines[index])
        and bool(SETEXT_UNDERLINE.match(lines[nxt]))
    )


def parse_markdown(text: str, first_line: int = 1) -> MarkdownDoc:
    """Parse Markdown text whose first line is file line first_line."""
    lines = text.replace("\r\n", "\n").split("\n")
    found = _Builder()
    index = 0
    while index < len(lines):
        raw = lines[index]
        line = first_line + index
        fence = FENCE_OPEN.match(raw)
        if fence is not None and not (fence.group(1)[0] == "`" and "`" in fence.group(2)):
            end = _close(lines, index + 1, fence.group(1))
            found.fence(fence.group(2).strip(), lines[index + 1 : end], line)
            index = end + 1
            continue
        heading = ATX_HEADING.match(raw)
        if heading is not None:
            found.heading(heading.group(2) or "", line)
        elif _setext(lines, index):
            found.heading(raw.strip(), line)
            found.text_line(raw, line)
            index += 2
            continue
        found.text_line(raw, line)
        index += 1
    return found.build()
