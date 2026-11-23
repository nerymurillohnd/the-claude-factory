"""Literal (`|`) and folded (`>`) block scalars, read as PyYAML and ruamel.yaml read them.

The header takes a chomping indicator (`-` strip, `+` keep, none clip) and an indentation
digit, in either order. Without the digit, the content's indentation is that of its first
non-empty line, and never less than one more than the parent's.
"""

from dataclasses import dataclass
from typing import Literal

from common.yaml_source import BLANKS, Node, Source

type Chomping = Literal["clip", "strip", "keep"]


@dataclass(slots=True)
class _Header:
    """What a block scalar's header line says."""

    chomping: Chomping
    increment: int | None


@dataclass(slots=True)
class _Body:
    """The content lines of a block scalar, with the empty lines around and between them."""

    lines: list[str | None]  # None is an empty line
    leading: int
    trailing: int
    last: int  # line index of the last content line, or of the header when there is none
    next_i: int


def _header(src: Source, i: int, c: int) -> _Header:
    """Read the indicators after `|` or `>`, and check nothing but a comment follows them."""
    line = src.lines[i]
    chomping: Chomping = "clip"
    increment: int | None = None
    k = c + 1
    while k < len(line) and k < c + 3:
        ch = line[k]
        if ch in "+-" and chomping == "clip":
            chomping = "keep" if ch == "+" else "strip"
        elif ch in "0123456789" and increment is None:
            if ch == "0":
                src.fail("syntax-error", "a block scalar's indentation can't be 0", i, k)
            increment = int(ch)
        else:
            break
        k += 1
    rest = line[k:]
    if (rest and rest[0] not in BLANKS) or (
        rest.strip(BLANKS) and not rest.lstrip(BLANKS).startswith("#")
    ):
        src.fail("syntax-error", "text after a block scalar's indicators", i, k)
    return _Header(chomping=chomping, increment=increment)


def _content_indent(src: Source, i: int, min_indent: int) -> int:
    """The indentation of the content: the deepest leading empty line or the first content line."""
    deepest = 0
    j = i + 1
    while j < len(src.lines) and not src.lines[j].strip(" "):
        deepest = max(deepest, len(src.lines[j]))
        j += 1
    if j < len(src.lines):
        deepest = max(deepest, src.indent(j))
    return max(min_indent, deepest)


def _body(src: Source, i: int, indent: int) -> _Body:
    """Collect the content lines at the given indentation, from the line after the header."""
    lines: list[str | None] = []
    last = i
    j = i + 1
    while j < len(src.lines):
        text = src.lines[j]
        if not text.strip(" ") and len(text) <= indent:
            lines.append(None)
        elif src.indent(j) >= indent:
            lines.append(text[indent:])
            last = j
        else:
            break
        j += 1
    leading = next((n for n, line in enumerate(lines) if line is not None), len(lines))
    trailing = 0
    while lines and lines[-1] is None:
        _ = lines.pop()
        trailing += 1
    del lines[:leading]
    if not lines:
        trailing = leading
        leading = 0
    return _Body(lines=lines, leading=leading, trailing=trailing, last=last, next_i=j)


def _literal(lines: list[str | None]) -> str:
    """Literal content: every line break kept."""
    return "\n".join(line or "" for line in lines)


def _folded(lines: list[str | None]) -> str:
    """Folded content: a break between two lines that don't start with a blank becomes a space."""
    out: list[str] = []
    breaks = 0
    previous: str | None = None
    for line in lines:
        if line is None:
            breaks += 1
            continue
        if previous is not None:
            folds = previous[:1] not in BLANKS and line[:1] not in BLANKS
            if folds:
                out.append("\n" * breaks if breaks else " ")
            else:
                out.append("\n" * (breaks + 1))
        out.append(line)
        previous, breaks = line, 0
    return "".join(out)


def read_block_scalar(src: Source, i: int, c: int, parent: int) -> tuple[Node, int]:
    """The block scalar whose `|` or `>` is at (i, c), and the line index to continue from."""
    header = _header(src, i, c)
    min_indent = max(parent + 1, 1)
    if header.increment is not None:
        indent = min_indent + header.increment - 1
    else:
        indent = _content_indent(src, i, min_indent)
    body = _body(src, i, indent)
    literal = src.lines[i][c] == "|"
    text = _literal(body.lines) if literal else _folded(body.lines)
    if body.lines:
        text = "\n" * body.leading + text
        if header.chomping != "strip":
            text += "\n"
    if header.chomping == "keep":
        text += "\n" * body.trailing
    raw = src.span((i, c), (body.last, len(src.lines[body.last])))
    node = src.scalar_node("literal" if literal else "folded", raw, text, (i, c), body.last)
    return node, body.next_i
