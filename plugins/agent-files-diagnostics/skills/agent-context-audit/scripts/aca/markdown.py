"""Deterministic reading of Markdown instruction files: units, imports, frontmatter, comments.

A unit is one instruction-sized block (a list item, a paragraph, a table row, a code block, a
block comment or the frontmatter). Units make finding IDs stable and let every instruction get
a disposition without trusting a model to segment the file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import TYPE_CHECKING
from urllib.parse import unquote

if TYPE_CHECKING:
    from collections.abc import Callable

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^ {0,3}(#{1,6})(?:\s+(.*?))?\s*#*\s*$")
LIST_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d{1,9}[.)])(?:\s+|$)")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
CODE_SPAN = re.compile(r"(`+)(?:.+?)\1")
WHITESPACE = re.compile(r"\s+")
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d{1,9}[.)])\s+")
PATH_LIKE = re.compile(r"(/|\.[A-Za-z0-9]{1,10}$|^~|^\.)")
IMPORT_STOP = ".,;:!?)]}>\"'"
IMPORT_OPENERS = " \t([{"
LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
LINK_DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*<?([^\s>]+)>?")
NOT_A_FILE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|//|#)")
YAML_KEY = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?:\s+(.*))?$")
YAML_RESERVED_START = ("@", "`", "%")
BLOCK_SCALAR = ("|", ">", "|-", ">-", "|+", ">+")
FRONTMATTER_MARK = "---"
MIN_QUOTED = 2


@dataclass(frozen=True)
class Unit:
    """One instruction-sized block of a file, with 1-based inclusive line numbers."""

    start: int
    end: int
    kind: str
    text: str
    heading: str = ""


@dataclass(frozen=True)
class ImportRef:
    """An @-reference in a Markdown memory file."""

    line: int
    raw: str
    target: str
    quoted: bool
    path_like: bool


@dataclass(frozen=True)
class LinkRef:
    """A Markdown link to a local file: its line, as written, and the path without anchor."""

    line: int
    raw: str
    target: str


@dataclass
class Frontmatter:
    """The YAML block between leading --- markers (1-based inclusive lines)."""

    start: int
    end: int
    data: dict[str, object] = field(default_factory=dict)
    error: str = ""


def split_lines(text: str) -> list[str]:
    """Split text the way a line-numbered reader counts it (no phantom last line)."""
    if not text:
        return []
    lines = text.split("\n")
    if text.endswith("\n"):
        _ = lines.pop()
    return [line.removesuffix("\r") for line in lines]


def normalize(text: str) -> str:
    """Collapse whitespace and drop list markers, so trivial reflows keep the same identity."""
    joined = " ".join(LIST_MARKER.sub("", line).strip() for line in text.split("\n"))
    return WHITESPACE.sub(" ", joined).strip()


def find_frontmatter(lines: list[str]) -> Frontmatter | None:
    """Return the frontmatter block when the file opens with ---, parsed with strict YAML rules."""
    if not lines or lines[0].strip() != FRONTMATTER_MARK:
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_MARK:
            data, error = parse_yaml(lines[1:index])
            return Frontmatter(start=1, end=index + 1, data=data, error=error)
    return Frontmatter(start=1, end=len(lines), error="the frontmatter has no closing --- line")


def _fence_end(lines: list[str], start: int, marker: str) -> int:
    """Index of the line closing a fence opened at start (or the last line)."""
    char, size = marker[0], len(marker)
    closing = re.compile(rf"^ {{0,3}}{re.escape(char)}{{{size},}}\s*$")
    for index in range(start + 1, len(lines)):
        if closing.match(lines[index]):
            return index
    return len(lines) - 1


def _comment_end(lines: list[str], start: int) -> int:
    for index in range(start, len(lines)):
        if "-->" in lines[index]:
            return index
    return len(lines) - 1


def _starts_block(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or bool(FENCE.match(line))
        or bool(HEADING.match(line))
        or bool(LIST_ITEM.match(line))
        or stripped.startswith(("|", ">", "<!--"))
    )


@dataclass
class _Cursor:
    lines: list[str]
    index: int = 0
    heading: list[str] = field(default_factory=list)
    found: list[Unit] = field(default_factory=list)

    @property
    def line(self) -> str:
        return self.lines[self.index]

    def emit(self, first: int, last: int, kind: str) -> None:
        text = "\n".join(self.lines[first : last + 1])
        self.found.append(Unit(first + 1, last + 1, kind, text, " > ".join(self.heading)))
        self.index = last + 1


def _fence(cursor: _Cursor) -> bool:
    match = FENCE.match(cursor.line)
    if match is None:
        return False
    cursor.emit(cursor.index, _fence_end(cursor.lines, cursor.index, match.group(1)), "code")
    return True


def _comment(cursor: _Cursor) -> bool:
    if not cursor.line.strip().startswith("<!--"):
        return False
    cursor.emit(cursor.index, _comment_end(cursor.lines, cursor.index), "comment")
    return True


def _blank(cursor: _Cursor) -> bool:
    if cursor.line.strip():
        return False
    cursor.index += 1
    return True


def _heading(cursor: _Cursor) -> bool:
    match = HEADING.match(cursor.line)
    if match is None:
        return False
    level = len(match.group(1))
    del cursor.heading[level - 1 :]
    cursor.heading.extend([""] * (level - 1 - len(cursor.heading)))
    cursor.heading.append((match.group(2) or "").strip())
    cursor.index += 1
    return True


def _table_row(cursor: _Cursor) -> bool:
    if not cursor.line.strip().startswith("|"):
        return False
    lines, index = cursor.lines, cursor.index
    is_separator = bool(TABLE_SEPARATOR.match(lines[index]))
    next_is_separator = index + 1 < len(lines) and bool(TABLE_SEPARATOR.match(lines[index + 1]))
    if is_separator or next_is_separator:
        cursor.index += 1
    else:
        cursor.emit(index, index, "table-row")
    return True


def _continuation(cursor: _Cursor, prefix: str) -> int:
    lines, last = cursor.lines, cursor.index
    while last + 1 < len(lines):
        following = lines[last + 1]
        if prefix and not following.strip().startswith(prefix):
            break
        if not prefix and _starts_block(following):
            break
        last += 1
    return last


def _list_item(cursor: _Cursor) -> bool:
    if not LIST_ITEM.match(cursor.line):
        return False
    cursor.emit(cursor.index, _continuation(cursor, ""), "item")
    return True


def _quote(cursor: _Cursor) -> bool:
    if not cursor.line.strip().startswith(">"):
        return False
    cursor.emit(cursor.index, _continuation(cursor, ">"), "quote")
    return True


def _paragraph(cursor: _Cursor) -> bool:
    cursor.emit(cursor.index, _continuation(cursor, ""), "paragraph")
    return True


BLOCK_READERS: tuple[Callable[[_Cursor], bool], ...] = (
    _fence,
    _comment,
    _blank,
    _heading,
    _table_row,
    _list_item,
    _quote,
    _paragraph,
)


def units(lines: list[str]) -> list[Unit]:
    """Split a Markdown file into instruction units; headings are context, not units."""
    cursor = _Cursor(lines)
    front = find_frontmatter(lines)
    if front is not None:
        cursor.emit(0, front.end - 1, "frontmatter")
    while cursor.index < len(lines):
        _ = any(reader(cursor) for reader in BLOCK_READERS)
    return cursor.found


def _code_free_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Lines outside frontmatter, fences and block comments, with code spans blanked out."""
    skipped: set[int] = set()
    for unit in units(lines):
        if unit.kind in {"code", "comment", "frontmatter"}:
            skipped.update(range(unit.start, unit.end + 1))
    return [
        (number, CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line))
        for number, line in enumerate(lines, start=1)
        if number not in skipped
    ]


def _read_target(line: str, start: int) -> tuple[str, bool]:
    """Read an import target that starts at index start; returns (target, quoted)."""
    if start < len(line) and line[start] in "\"'":
        close = line.find(line[start], start + 1)
        return line[start + 1 : close if close != -1 else len(line)], True
    chars: list[str] = []
    index = start
    while index < len(line) and not line[index].isspace():
        if line[index] == "\\" and line[index + 1 : index + 2] == " ":
            chars.append(" ")
            index += 2
            continue
        chars.append(line[index])
        index += 1
    return "".join(chars).rstrip(IMPORT_STOP), False


def imports(lines: list[str]) -> list[ImportRef]:
    """Find @path imports the way Claude Code reads them: outside code and comments."""
    found: list[ImportRef] = []
    for number, line in _code_free_lines(lines):
        for match in re.finditer("@", line):
            at = match.start()
            if at > 0 and line[at - 1] not in IMPORT_OPENERS:
                continue
            target, quoted = _read_target(line, at + 1)
            if target:
                raw = line[at : at + 1 + len(target) + (MIN_QUOTED if quoted else 0)].strip()
                found.append(ImportRef(number, raw, target, quoted, bool(PATH_LIKE.search(target))))
    return found


def links(lines: list[str]) -> list[LinkRef]:
    """Inline links, images and link definitions to local files, outside code and comments."""
    found: list[LinkRef] = []
    for number, line in _code_free_lines(lines):
        raws = [match.group(1) for match in LINK.finditer(line)]
        definition = LINK_DEFINITION.match(line)
        if definition:
            raws.append(definition.group(1))
        for raw in raws:
            if NOT_A_FILE.match(raw):
                continue
            target = unquote(raw.split("#", 1)[0].split("?", 1)[0])
            if target:
                found.append(LinkRef(number, raw, target))
    return found


def block_comments(lines: list[str]) -> list[Unit]:
    """Block-level HTML comments outside fences: stripped before Claude Code loads the file."""
    return [unit for unit in units(lines) if unit.kind == "comment"]


# --- strict YAML subset (frontmatter only) ------------------------------------------------


def _strip_comment(value: str) -> str:
    """Drop a trailing # comment outside quotes."""
    quote = ""
    for index, char in enumerate(value):
        if quote:
            quote = "" if char == quote else quote
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def _quoted(value: str) -> tuple[object, str]:
    if len(value) < MIN_QUOTED or not value.endswith(value[0]):
        return value, "a quoted value is not closed"
    return value[1:-1], ""


def _flow_list(value: str) -> tuple[object, str]:
    if not value.endswith("]"):
        return value, "a [ ] list is not closed"
    inner = value[1:-1].strip()
    items = [item.strip().strip("\"'") for item in inner.split(",")] if inner else []
    return [item for item in items if item], ""


def _plain(value: str) -> tuple[object, str]:
    if value.startswith(YAML_RESERVED_START):
        return value, f"a plain value cannot start with {value[0]!r} (quote it)"
    if ": " in value:
        return value, "a plain value contains ': ' (mapping values are not allowed here)"
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true", ""
    return value, ""


def _scalar(value: str) -> tuple[object, str]:
    """Parse one YAML scalar or flow sequence; returns (value, error)."""
    value = _strip_comment(value.strip())
    if not value:
        return None, ""
    if value[0] in "\"'":
        return _quoted(value)
    if value.startswith("["):
        return _flow_list(value)
    return _plain(value)


def _block_lines(lines: list[str], start: int) -> tuple[list[str], int]:
    """Collect the indented or dashed lines that belong to the key before start."""
    block: list[str] = []
    index = start
    while index < len(lines) and (not lines[index].strip() or lines[index][:1] in " \t-"):
        if lines[index].strip():
            block.append(lines[index])
        index += 1
    return block, index


def _block_value(block: list[str], head: str) -> tuple[object, str]:
    if head in BLOCK_SCALAR:
        return "\n".join(line.strip() for line in block), ""
    items: list[object] = []
    for line in block:
        stripped = line.strip()
        if not stripped.startswith("- ") and stripped != "-":
            return None, ""
        value, error = _scalar(stripped[1:])
        if error:
            return None, error
        items.append(value)
    return items, ""


def parse_yaml(lines: list[str]) -> tuple[dict[str, object], str]:
    """Parse the flat key/value YAML used in frontmatter; returns (data, first error)."""
    data: dict[str, object] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        number = index + 2
        if "\t" in line[: len(line) - len(line.lstrip())]:
            return data, f"line {number}: tab indentation"
        index += 1
        if not line.strip() or line.strip().startswith("#"):
            continue
        match = YAML_KEY.match(line)
        if match is None:
            return data, f"line {number}: expected 'key: value'"
        key, rest = match.group(1), (match.group(2) or "").strip()
        if rest and rest not in BLOCK_SCALAR:
            value, error = _scalar(rest)
        else:
            block, index = _block_lines(lines, index)
            value, error = _block_value(block, rest)
        if error:
            return data, f"line {number}: {error}"
        data[key] = value
    return data, ""
