#!/usr/bin/env python3
"""The parts of a skill's Markdown and how one line is read: links, slugs, inline code, prose."""

from __future__ import annotations

from dataclasses import dataclass
import html
import re
import unicodedata
from urllib.parse import unquote

INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
LINK_TARGET = r"(?P<target><[^<>\n]*>|[^\s()<>]*(?:\([^\s()]*\)[^\s()]*)*)"
LINK_TITLE = r"""(?:\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?"""
INLINE_LINK = re.compile(
    r"!?\[(?P<text>(?:[^\[\]]|\[[^\]]*\])*)\]\(\s*" + LINK_TARGET + LINK_TITLE + r"\s*\)"
)
REF_DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:\s*(<[^<>\n]*>|\S+)" + LINK_TITLE + r"\s*$")
EXPLICIT_ANCHOR = re.compile(r"""<a\s[^>]*?\b(?:id|name)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
FRAGMENT = re.compile(r"^([^#?]*)(.*)$", re.DOTALL)
EXTERNAL = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]+:|//)")
"""A URI scheme of two or more characters (RFC 3986), or a network path. A one-letter
scheme is a Windows drive (C:), kept as a path so PO-02 sees its backslashes."""
SLUG_DROPPED_CATEGORIES = frozenset(
    {"No", "Pd", "Pe", "Pf", "Pi", "Po", "Ps", "Sc", "Sk", "Sm", "So"}
    | {"Cc", "Cf", "Cn", "Co", "Zl", "Zp", "Zs"}
)
"""The Unicode general categories github-slugger 2.0.0 removes (script/generate-regex.js):
Other_Number, every punctuation but Connector (so _ stays), Symbol, Control, Private_Use,
Format, Unassigned and Separator. Letters, the space and the hyphen always stay."""
SLUG_KEPT = frozenset({" ", "-"})
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


def _slug_keeps(char: str) -> bool:
    """Tell whether github-slugger keeps a character of the lowercased heading text."""
    return (
        char in SLUG_KEPT
        or char.isalpha()
        or unicodedata.category(char) not in SLUG_DROPPED_CATEGORIES
    )


def github_slug(text: str, seen: dict[str, int]) -> str:
    """Return GitHub's anchor slug for a heading's text, numbering repeats through seen."""
    base = "".join(c for c in text.lower() if _slug_keeps(c)).replace(" ", "-")
    slug = base
    while slug in seen:
        seen[base] += 1
        slug = f"{base}-{seen[base]}"
    seen[slug] = 0
    return slug


def _strip_markup(text: str) -> str:
    """Strip link, tag, * and _ emphasis markup, then decode entities, outside code spans."""
    text = MARKUP_LINK.sub(r"\1", text)
    text = MARKUP_TAG.sub("", text).replace("*", "")
    return html.unescape(MARKUP_EMPHASIS.sub(r"\1", text))


def _plain(text: str) -> str:
    """Render heading text as GitHub does: code spans verbatim, markup stripped elsewhere."""
    parts: list[str] = []
    end = 0
    for match in INLINE_CODE.finditer(text):
        parts.extend((_strip_markup(text[end : match.start()]), match.group(2).strip()))
        end = match.end()
    parts.append(_strip_markup(text[end:]))
    return "".join(parts).strip()


def _target(raw: str) -> str | None:
    """Unwrap and decode a link target; None for external or empty targets."""
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    raw = raw.strip()
    if not raw or EXTERNAL.match(raw):
        return None
    split = FRAGMENT.match(raw)
    path, rest = (split.group(1), split.group(2)) if split else (raw, "")
    path = unquote(path).replace("#", "%23").replace("?", "%3F")
    return path + unquote(rest)


class DocBuilder:
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

    def text_line(self, raw: str, line: int, comment: str = "") -> None:
        """Record the inline code, ! commands, links, anchors and prose of a line.

        comment is the line's HTML comment text: it joins the prose and nothing else.
        """
        definition = REF_DEFINITION.match(raw)
        if definition is not None and not definition.group(1).startswith("^"):
            target = _target(definition.group(2))
            if target is not None:
                self.links.append(Link(target, line))
            return
        prose = INLINE_CODE.sub(lambda match: self._inline(raw, match, line), raw)
        for match in INLINE_LINK.finditer(prose):
            target = _target(match.group("target"))
            if target is not None:
                self.links.append(Link(target, line))
        prose = INLINE_LINK.sub(lambda match: match.group("text"), prose)
        self.anchors.update(found.group(1) for found in EXPLICIT_ANCHOR.finditer(prose))
        prose = f"{prose.strip()} {comment.strip()}".strip()
        if prose:
            self.prose.append((line, prose))

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
