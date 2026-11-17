"""A YAML reader for skill frontmatter that keeps every node's file position and style.

It reads the forms frontmatter uses: block mappings and sequences, plain scalars over several
lines, and single- and double-quoted scalars with YAML's escapes and line folding. Whatever it
can't read with certainty raises ReadError with a rule and a 1-based file position; it never
guesses. It recurses once per nesting level and stops at MAX_DEPTH, so it never raises
RecursionError.
"""

from dataclasses import dataclass, field
from typing import Literal, NoReturn, override

type Kind = Literal["map", "seq", "scalar", "alias"]
type Style = Literal["plain", "single", "double", "literal", "folded", "flow"]
# What precedes a node on its line: nothing, `key:`, or `- `.
type Where = Literal["line-start", "after-key", "after-entry"]
type Rule = Literal[
    "colon-in-value",
    "unclosed-quote",
    "unclosed-flow",
    "key-under-scalar",
    "tab-indent",
    "duplicate-key",
    "syntax-error",
    "too-deep",
    "unsupported",
]

MAX_DEPTH = 100
MAX_CODE_POINT = 0x10FFFF
BLANKS = " \t"
# Characters a plain scalar can't start with; `-`, `?` and `:` can, when a non-blank follows.
PLAIN_START_INDICATORS = frozenset(",[]{}#&*!|>'\"%@`")
SIMPLE_ESCAPES = {
    "0": "\0",
    "a": "\a",
    "b": "\b",
    "t": "\t",
    "\t": "\t",
    "n": "\n",
    "v": "\v",
    "f": "\f",
    "r": "\r",
    "e": "\x1b",
    " ": " ",
    '"': '"',
    "/": "/",
    "\\": "\\",
    "N": "\x85",
    "_": "\N{NO-BREAK SPACE}",
    "L": "\N{LINE SEPARATOR}",
    "P": "\N{PARAGRAPH SEPARATOR}",
}
HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}
HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


@dataclass(slots=True)
class Node:
    """One YAML node with its 1-based file position.

    A scalar has `raw`, its exact source text, and `value`, its text after unquoting and
    folding. A mapping holds `pairs` and a sequence `items`; both have empty `raw` and `value`.
    """

    kind: Kind
    style: Style | None
    raw: str
    value: str
    line: int
    column: int
    end_line: int
    pairs: list[tuple["Node", "Node"]] = field(default_factory=list)
    items: list["Node"] = field(default_factory=list)
    anchor: str | None = None
    tag: str | None = None


class ReadError(Exception):
    """The YAML can't be read: a rule, a message and the 1-based file position."""

    def __init__(self, rule: Rule, message: str, line: int, column: int) -> None:
        """Keep the rule and the position, and say both in the message."""
        super().__init__(f"{message} (line {line}, column {column})")
        self.rule: Rule = rule
        self.message: str = message
        self.line: int = line
        self.column: int = column

    @override
    def __str__(self) -> str:
        """The message with its position."""
        return f"{self.message} (line {self.line}, column {self.column})"


def _blank_after(line: str, k: int) -> bool:
    """True when position k is past the end of the line or holds a space or tab."""
    return k >= len(line) or line[k] in BLANKS


def _is_entry(line: str, c: int) -> bool:
    """True when a block sequence entry, `-` then a blank or the end, starts at column c."""
    return line[c : c + 1] == "-" and _blank_after(line, c + 1)


def _content_end(line: str, start: int) -> int:
    """Where a plain scalar's text on this line ends: before ` #` and trailing blanks."""
    end = len(line)
    for k in range(start + 1, len(line)):
        if line[k] == "#" and line[k - 1] in BLANKS:
            end = k
            break
    return start + len(line[start:end].rstrip(BLANKS))


def _colon_at(text: str) -> int | None:
    """The index of the first `:` followed by a blank or the end, if any."""
    for k, ch in enumerate(text):
        if ch == ":" and _blank_after(text, k + 1):
            return k
    return None


def _plain_can_start(line: str, c: int) -> bool:
    """True when a plain scalar may start at column c."""
    ch = line[c]
    if ch in "-?:":
        return not _blank_after(line, c + 1)
    return ch not in PLAIN_START_INDICATORS


@dataclass(slots=True)
class _Quoted:
    """A quoted scalar scanned from the source: its text and where its closing quote is."""

    value: str
    end_i: int
    end_k: int


class _Parser:
    """Recursive descent over the block's lines, with an explicit depth counter."""

    def __init__(self, text: str, first_line: int) -> None:
        """Split the YAML into lines; first_line is the file line of the first one."""
        self.lines: list[str] = text.split("\n")
        self.first_line: int = first_line

    def fail(self, rule: Rule, message: str, i: int, c: int) -> NoReturn:
        """Raise ReadError at line index i and character index c."""
        raise ReadError(rule, message, self.first_line + i, c + 1)

    def indent(self, i: int) -> int:
        """The number of leading spaces on line i."""
        line = self.lines[i]
        return len(line) - len(line.lstrip(" "))

    def is_skippable(self, i: int) -> bool:
        """True for a blank line or a comment line."""
        stripped = self.lines[i].strip(BLANKS)
        return not stripped or stripped.startswith("#")

    def next_content(self, i: int) -> int:
        """The first content line from i on, checked for tabs and markers; len(lines) at the end."""
        while i < len(self.lines) and self.is_skippable(i):
            i += 1
        if i < len(self.lines):
            self.check_line(i)
        return i

    def check_line(self, i: int) -> None:
        """Reject a tab in the indentation, a directive and a document marker."""
        line = self.lines[i]
        leading = line[: len(line) - len(line.lstrip(BLANKS))]
        if "\t" in leading:
            self.fail("tab-indent", "a tab in the indentation", i, leading.index("\t"))
        if line.startswith("%"):
            self.fail("unsupported", "a YAML directive", i, 0)
        for marker in ("---", "..."):
            if line.startswith(marker) and _blank_after(line, 3):
                self.fail("unsupported", "a document marker inside the frontmatter", i, 0)

    def null(self, i: int, c: int) -> Node:
        """An empty plain scalar: a key or entry with no value."""
        line = self.first_line + i
        return Node(
            kind="scalar", style="plain", raw="", value="", line=line, column=c + 1, end_line=line
        )

    def looks_like_key(self, i: int) -> bool:
        """True when line i starts with `key:`."""
        try:
            return self.key_at(i, self.indent(i)) is not None
        except ReadError:
            return False

    def misindented(self, j: int, previous: Node) -> NoReturn:
        """Reject a line indented deeper than the collection it follows."""
        if previous.kind == "scalar" and self.looks_like_key(j):
            self.fail("key-under-scalar", "a key indented under a scalar", j, self.indent(j))
        self.fail("syntax-error", "a line indented where nothing can continue", j, self.indent(j))

    # Values

    def block_value(
        self, i: int, c: int, parent: int, depth: int, where: Where
    ) -> tuple[Node, int]:
        """The node starting at (i, c), and the line index to continue from.

        parent is the indentation the node's continuation lines must exceed. where says what comes
        before the node: a mapping or a sequence may start on the same line only at a line start
        or after `- `, and a sequence may sit at its key's own indent only after `key:`.
        """
        if depth > MAX_DEPTH:
            self.fail("too-deep", f"nesting deeper than {MAX_DEPTH} levels", i, c)
        line = self.lines[i]
        if c >= len(line) or line[c] == "#":
            return self.value_below(i, c, parent, depth, where)
        if _is_entry(line, c):
            if where == "after-key":
                self.fail("syntax-error", "a sequence entry on the same line as its key", i, c)
            return self.block_seq(i, c, depth + 1)
        if where != "after-key" and self.key_at(i, c) is not None:
            return self.block_map(i, c, depth + 1)
        return self.scalar(i, c, parent)

    def value_below(
        self, i: int, c: int, parent: int, depth: int, where: Where
    ) -> tuple[Node, int]:
        """A value that starts on a later line, or an empty value."""
        j = self.next_content(i + 1)
        if j < len(self.lines):
            indent = self.indent(j)
            if indent > parent:
                return self.block_value(j, indent, parent, depth + 1, "line-start")
            if where == "after-key" and indent == parent and _is_entry(self.lines[j], indent):
                return self.block_seq(j, indent, depth + 1)
        return self.null(i, c), i + 1

    def scalar(self, i: int, c: int, parent: int) -> tuple[Node, int]:
        """A scalar in block context: quoted or plain."""
        line = self.lines[i]
        ch = line[c]
        if ch == "?" and _blank_after(line, c + 1):
            self.fail("unsupported", "a complex key", i, c)
        if ch in "'\"":
            return self.quoted_value(i, c)
        if ch in "[{|>&!*":
            self.fail("unsupported", f"`{ch}` is not read yet", i, c)
        if not _plain_can_start(line, c):
            self.fail("syntax-error", f"a plain value can't start with `{ch}`", i, c)
        return self.plain(i, c, parent)

    # Collections

    def block_map(self, i: int, c: int, depth: int) -> tuple[Node, int]:
        """A block mapping whose entries start at column c, the first on line i."""
        pairs: list[tuple[Node, Node]] = []
        seen: set[str] = set()
        while True:
            found = self.key_at(i, c)
            if found is None:
                self.fail("syntax-error", "expected `key: value` here", i, c)
            key, after = found
            if key.value in seen:
                self.fail("duplicate-key", f"the key `{key.value}` appears twice", i, c)
            seen.add(key.value)
            start = after + len(self.lines[i][after:]) - len(self.lines[i][after:].lstrip(BLANKS))
            value, nxt = self.block_value(i, start, c, depth + 1, "after-key")
            pairs.append((key, value))
            j = self.next_content(nxt)
            if j >= len(self.lines) or self.indent(j) < c:
                node = Node(
                    kind="map",
                    style=None,
                    raw="",
                    value="",
                    line=pairs[0][0].line,
                    column=c + 1,
                    end_line=value.end_line,
                    pairs=pairs,
                )
                return node, j
            if self.indent(j) > c:
                self.misindented(j, value)
            i = j

    def block_seq(self, i: int, c: int, depth: int) -> tuple[Node, int]:
        """A block sequence whose `-` entries sit at column c, the first on line i."""
        items: list[Node] = []
        first = i
        while True:
            line = self.lines[i]
            start = c + 1 + len(line[c + 1 :]) - len(line[c + 1 :].lstrip(BLANKS))
            item, nxt = self.block_value(i, start, c, depth + 1, "after-entry")
            items.append(item)
            j = self.next_content(nxt)
            if j >= len(self.lines) or self.indent(j) < c:
                break
            if self.indent(j) > c:
                self.misindented(j, item)
            if not _is_entry(self.lines[j], c):
                break
            i = j
        node = Node(
            kind="seq",
            style=None,
            raw="",
            value="",
            line=self.first_line + first,
            column=c + 1,
            end_line=items[-1].end_line,
            items=items,
        )
        return node, j

    # Keys

    def key_at(self, i: int, c: int) -> tuple[Node, int] | None:
        """The key starting at (i, c) and the index after its `:`, or None if no key is there."""
        line = self.lines[i]
        ch = line[c]
        if ch == "?" and _blank_after(line, c + 1):
            self.fail("unsupported", "a complex key", i, c)
        if ch in "'\"":
            return self.quoted_key(i, c)
        if not _plain_can_start(line, c):
            return None
        end = _content_end(line, c)
        colon = _colon_at(line[c:end] + " ")
        if colon is None:
            return None
        text = line[c : c + colon].rstrip(BLANKS)
        key = Node(
            kind="scalar",
            style="plain",
            raw=text,
            value=text,
            line=self.first_line + i,
            column=c + 1,
            end_line=self.first_line + i,
        )
        return key, c + colon + 1

    def quoted_key(self, i: int, c: int) -> tuple[Node, int] | None:
        """A quoted key closed on its own line and followed by `:`."""
        scanned = self.scan_quoted(i, c)
        if scanned.end_i != i:
            return None
        line = self.lines[i]
        k = scanned.end_k + 1
        while k < len(line) and line[k] in BLANKS:
            k += 1
        if line[k : k + 1] != ":" or not _blank_after(line, k + 1):
            return None
        key = Node(
            kind="scalar",
            style="single" if line[c] == "'" else "double",
            raw=line[c : scanned.end_k + 1],
            value=scanned.value,
            line=self.first_line + i,
            column=c + 1,
            end_line=self.first_line + i,
        )
        return key, k + 1

    # Scalars

    def plain(self, i: int, c: int, parent: int) -> tuple[Node, int]:
        """A plain scalar from (i, c), over every following line indented deeper than parent."""
        line = self.lines[i]
        end = _content_end(line, c)
        colon = _colon_at(line[c:end] + " ")
        if colon is not None:
            self.fail("colon-in-value", "`: ` inside a plain value", i, c + colon)
        parts = [line[c:end]]
        last, last_end = i, end
        if end == len(line.rstrip(BLANKS)):
            last, last_end = self.plain_continuation(i, parent, parts)
        if last == i:
            raw = line[c:last_end]
        else:
            raw = "\n".join([line[c:], *self.lines[i + 1 : last], self.lines[last][:last_end]])
        node = Node(
            kind="scalar",
            style="plain",
            raw=raw,
            value="".join(parts),
            line=self.first_line + i,
            column=c + 1,
            end_line=self.first_line + last,
        )
        return node, last + 1

    def plain_continuation(self, i: int, parent: int, parts: list[str]) -> tuple[int, int]:
        """Fold a plain scalar's continuation lines into parts; return its last line and end."""
        last, last_end = i, _content_end(self.lines[i], 0)
        blanks = 0
        k = i + 1
        while k < len(self.lines):
            text = self.lines[k]
            stripped = text.strip(BLANKS)
            if not stripped:
                blanks += 1
                k += 1
                continue
            if stripped.startswith("#") or self.indent(k) <= parent:
                break
            self.check_line(k)
            start = self.indent(k)
            end = _content_end(text, start)
            if _colon_at(text[start:end] + " ") is not None:
                self.fail("key-under-scalar", "a key indented under a scalar", k, start)
            parts.append(("\n" * blanks if blanks else " ") + text[start:end])
            last, last_end, blanks = k, end, 0
            if end != len(text.rstrip(BLANKS)):
                break
            k += 1
        return last, last_end

    def quoted_value(self, i: int, c: int) -> tuple[Node, int]:
        """A quoted scalar as a value: nothing but a comment may follow it on its last line."""
        scanned = self.scan_quoted(i, c)
        line = self.lines[scanned.end_i]
        k = scanned.end_k + 1
        while k < len(line) and line[k] in BLANKS:
            k += 1
        if k < len(line):
            if line[k] == ":" and _blank_after(line, k + 1):
                self.fail("colon-in-value", "`: ` after a quoted value", scanned.end_i, k)
            if line[k] != "#" or k == scanned.end_k + 1:
                self.fail("syntax-error", "text after a quoted value", scanned.end_i, k)
        if scanned.end_i == i:
            raw = self.lines[i][c : scanned.end_k + 1]
        else:
            middle = self.lines[i + 1 : scanned.end_i]
            raw = "\n".join([self.lines[i][c:], *middle, line[: scanned.end_k + 1]])
        node = Node(
            kind="scalar",
            style="single" if self.lines[i][c] == "'" else "double",
            raw=raw,
            value=scanned.value,
            line=self.first_line + i,
            column=c + 1,
            end_line=self.first_line + scanned.end_i,
        )
        return node, scanned.end_i + 1

    def scan_quoted(self, i: int, c: int) -> _Quoted:
        """Scan a single- or double-quoted scalar from its opening quote at (i, c)."""
        quote = self.lines[i][c]
        out: list[str] = []
        kept = 0  # length of out up to its last character that survives a line break
        line_i, k = i, c + 1
        while True:
            line = self.lines[line_i]
            if k >= len(line):
                del out[kept:]
                line_i, k = self.fold_quoted(line_i, out, (i, c))
                kept = len(out)
                continue
            ch = line[k]
            if ch == quote and quote == "'" and line[k + 1 : k + 2] == "'":
                out.append("'")
                k += 2
            elif ch == quote:
                return _Quoted(value="".join(out), end_i=line_i, end_k=k)
            elif ch == "\\" and quote == '"':
                if k + 1 >= len(line):
                    line_i, k = self.escaped_break(line_i, (i, c))
                    kept = len(out)
                    continue
                k = self.escape(line_i, k, out)
            else:
                out.append(ch)
                k += 1
                if ch not in BLANKS:
                    kept = len(out)
                continue
            kept = len(out)

    def next_quoted_line(self, line_i: int, opening: tuple[int, int]) -> int:
        """The line after line_i inside a quoted scalar; an unclosed quote at the end."""
        if line_i + 1 >= len(self.lines):
            self.fail("unclosed-quote", "a quote that never closes", *opening)
        return line_i + 1

    def fold_quoted(self, line_i: int, out: list[str], opening: tuple[int, int]) -> tuple[int, int]:
        """Fold a line break inside quotes: one break is a space, each blank line a newline."""
        blanks = 0
        line_i = self.next_quoted_line(line_i, opening)
        while not self.lines[line_i].strip(BLANKS):
            blanks += 1
            line_i = self.next_quoted_line(line_i, opening)
        out.append("\n" * blanks if blanks else " ")
        text = self.lines[line_i]
        return line_i, len(text) - len(text.lstrip(BLANKS))

    def escaped_break(self, line_i: int, opening: tuple[int, int]) -> tuple[int, int]:
        """A backslash at the end of a line: join the next line with nothing between."""
        line_i = self.next_quoted_line(line_i, opening)
        text = self.lines[line_i]
        return line_i, len(text) - len(text.lstrip(BLANKS))

    def escape(self, line_i: int, k: int, out: list[str]) -> int:
        """Decode the escape whose backslash is at k; return the index after it."""
        line = self.lines[line_i]
        code = line[k + 1]
        if code in SIMPLE_ESCAPES:
            out.append(SIMPLE_ESCAPES[code])
            return k + 2
        width = HEX_ESCAPES.get(code)
        digits = line[k + 2 : k + 2 + width] if width else ""
        if width is None or len(digits) != width or any(d not in HEX_DIGITS for d in digits):
            self.fail("syntax-error", f"an invalid escape `\\{code}`", line_i, k)
        point = int(digits, 16)
        if point > MAX_CODE_POINT:
            self.fail("syntax-error", f"an escape beyond Unicode `\\{code}{digits}`", line_i, k)
        out.append(chr(point))
        return k + 2 + width


def read(yaml_text: str, first_line: int) -> Node:
    """Read the frontmatter YAML whose first line is file line first_line; raise ReadError."""
    parser = _Parser(yaml_text, first_line)
    i = parser.next_content(0)
    if i >= len(parser.lines):
        return parser.null(0, 0)
    root, nxt = parser.block_value(i, parser.indent(i), -1, 1, "line-start")
    j = parser.next_content(nxt)
    if j < len(parser.lines):
        parser.misindented(j, root)
    return root
