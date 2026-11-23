"""The nodes, errors and source scanning the frontmatter reader's parts share.

Source holds the lines of the YAML and what every part of the reader needs from them: file
positions, quoted scalars with YAML's escapes and folding, node properties and the anchors
defined so far.
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
# UTF-16 surrogates, which no UTF-8 text can hold on their own.
SURROGATES = (0xD800, 0xDFFF)
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


def blank_after(line: str, k: int) -> bool:
    """True when position k is past the end of the line or holds a space or tab."""
    return k >= len(line) or line[k] in BLANKS


def is_entry(line: str, c: int) -> bool:
    """True when a block sequence entry, `-` then a blank or the end, starts at column c."""
    return line[c : c + 1] == "-" and blank_after(line, c + 1)


def content_end(line: str, start: int) -> int:
    """Where a plain scalar's text on this line ends: before ` #` and trailing blanks."""
    end = len(line)
    for k in range(start + 1, len(line)):
        if line[k] == "#" and line[k - 1] in BLANKS:
            end = k
            break
    return start + len(line[start:end].rstrip(BLANKS))


def colon_at(text: str) -> int | None:
    """The index of the first `:` followed by a blank or the end, if any."""
    for k, ch in enumerate(text):
        if ch == ":" and blank_after(text, k + 1):
            return k
    return None


def plain_can_start(line: str, c: int) -> bool:
    """True when a plain scalar may start at column c."""
    ch = line[c]
    if ch in "-?:":
        return not blank_after(line, c + 1)
    return ch not in PLAIN_START_INDICATORS


@dataclass(slots=True)
class Quoted:
    """A quoted scalar scanned from the source: its text and where its closing quote is."""

    value: str
    end_i: int
    end_k: int


FLOW_INDICATORS = frozenset(",[]{}")


class Source:
    """The YAML's lines, their file positions, and the anchors defined so far."""

    def __init__(self, text: str, first_line: int) -> None:
        """Split the YAML into lines; first_line is the file line of the first one."""
        self.lines: list[str] = text.split("\n")
        self.first_line: int = first_line
        self.anchors: set[str] = set()

    def fail(self, rule: Rule, message: str, i: int, c: int) -> NoReturn:
        """Raise ReadError at line index i and character index c."""
        raise ReadError(rule, message, self.first_line + i, c + 1)

    def indent(self, i: int) -> int:
        """The number of leading spaces on line i."""
        line = self.lines[i]
        return len(line) - len(line.lstrip(" "))

    def scalar_node(
        self, style: Style, raw: str, value: str, start: tuple[int, int], end_i: int
    ) -> Node:
        """A scalar node from its text, its start (line index, character index) and last line."""
        return Node(
            kind="scalar",
            style=style,
            raw=raw,
            value=value,
            line=self.first_line + start[0],
            column=start[1] + 1,
            end_line=self.first_line + end_i,
        )

    def null(self, i: int, c: int) -> Node:
        """An empty plain scalar: a key or entry with no value."""
        return self.scalar_node("plain", "", "", (i, c), i)

    def span(self, start: tuple[int, int], end: tuple[int, int]) -> str:
        """The source text from start up to, not including, end; both are (line, character)."""
        (i, c), (j, k) = start, end
        if i == j:
            return self.lines[i][c:k]
        return "\n".join([self.lines[i][c:], *self.lines[i + 1 : j], self.lines[j][:k]])

    # Properties and aliases

    def name_end(self, i: int, k: int) -> int:
        """Where an anchor, alias or tag name that starts at k ends: a blank or a flow indicator."""
        line = self.lines[i]
        while k < len(line) and line[k] not in BLANKS and line[k] not in FLOW_INDICATORS:
            k += 1
        return k

    def tag_end(self, i: int, k: int) -> int:
        """Where the tag starting with `!` at k ends; a verbatim `!<...>` tag ends after `>`."""
        line = self.lines[i]
        if line[k + 1 : k + 2] == "<":
            close = line.find(">", k + 2)
            if close < 0:
                self.fail("syntax-error", "a verbatim tag without its closing `>`", i, k)
            return close + 1
        return self.name_end(i, k + 1)

    def properties(self, i: int, c: int) -> tuple[str | None, str | None, int]:
        """The anchor and tag starting at (i, c), and the index after them and their blanks."""
        line = self.lines[i]
        anchor: str | None = None
        tag: str | None = None
        k = c
        while k < len(line) and line[k] in "&!":
            if line[k] == "&":
                end = self.name_end(i, k + 1)
                if anchor is not None or end == k + 1:
                    self.fail("syntax-error", "an empty or second anchor", i, k)
                anchor = line[k + 1 : end]
            else:
                end = self.tag_end(i, k)
                if tag is not None:
                    self.fail("syntax-error", "a second tag on one node", i, k)
                tag = line[k:end]
            if end < len(line) and line[end] not in BLANKS and line[end] not in FLOW_INDICATORS:
                self.fail("syntax-error", "a property must be followed by a blank", i, end)
            k = end
            while k < len(line) and line[k] in BLANKS:
                k += 1
        if anchor is not None:
            self.anchors.add(anchor)
        return anchor, tag, k

    def alias(self, i: int, c: int) -> tuple[Node, int]:
        """The alias `*name` at (i, c), and the index after it; the anchor must exist already."""
        end = self.name_end(i, c + 1)
        name = self.lines[i][c + 1 : end]
        if not name:
            self.fail("syntax-error", "an alias with no name", i, c)
        if name not in self.anchors:
            self.fail("syntax-error", f"an alias to an unknown anchor `{name}`", i, c)
        node = Node(
            kind="alias",
            style=None,
            raw=self.lines[i][c:end],
            value=name,
            line=self.first_line + i,
            column=c + 1,
            end_line=self.first_line + i,
        )
        return node, end

    # Quoted scalars

    def scan_quoted(self, i: int, c: int) -> Quoted:
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
                return Quoted(value="".join(out), end_i=line_i, end_k=k)
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
        if SURROGATES[0] <= point <= SURROGATES[1]:
            self.fail("syntax-error", f"a lone surrogate `\\{code}{digits}`", line_i, k)
        out.append(chr(point))
        return k + 2 + width
