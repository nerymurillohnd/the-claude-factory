"""JSON values with the line span each one occupies, for line-accurate findings on settings files.

The standard decoder validates the text first; this reader then walks the same text and records
where every value starts and ends, so a unit can quote the exact lines of a permission rule, a
hook or an MCP server entry.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aca.jsonutil import loads

WHITESPACE = " \t\r\n"
LITERALS = {"true": True, "false": False, "null": None}
NUMBER_CHARS = "+-0123456789.eE"


@dataclass
class Node:
    """A decoded JSON value and its 1-based inclusive line span."""

    value: object
    start: int
    end: int
    members: dict[str, Node] = field(default_factory=dict)
    items: list[Node] = field(default_factory=list)
    key_line: int = 0


class _Reader:
    """Walks valid JSON text, building nodes with line spans."""

    def __init__(self, text: str) -> None:
        self.text: str = text
        self.pos: int = 0
        self.line_starts: list[int] = [0]
        for index, char in enumerate(text):
            if char == "\n":
                self.line_starts.append(index + 1)

    def line_of(self, pos: int) -> int:
        """Return the 1-based line holding the character at pos."""
        low, high = 0, len(self.line_starts) - 1
        while low < high:
            middle = (low + high + 1) // 2
            if self.line_starts[middle] <= pos:
                low = middle
            else:
                high = middle - 1
        return low + 1

    def skip(self) -> None:
        """Advance past whitespace."""
        while self.pos < len(self.text) and self.text[self.pos] in WHITESPACE:
            self.pos += 1

    def string(self) -> str:
        """Read a string literal starting at the opening quote."""
        start = self.pos
        self.pos += 1
        while self.text[self.pos] != '"':
            self.pos += 2 if self.text[self.pos] == "\\" else 1
        self.pos += 1
        decoded = loads(self.text[start : self.pos])
        return decoded if isinstance(decoded, str) else ""

    def scalar(self) -> object:
        """Read a number or a literal."""
        for word, value in LITERALS.items():
            if self.text.startswith(word, self.pos):
                self.pos += len(word)
                return value
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] in NUMBER_CHARS:
            self.pos += 1
        return loads(self.text[start : self.pos])

    def value(self) -> Node:
        """Read any value."""
        self.skip()
        start = self.line_of(self.pos)
        char = self.text[self.pos]
        if char == "{":
            return self.obj(start)
        if char == "[":
            return self.array(start)
        value = self.string() if char == '"' else self.scalar()
        return Node(value=value, start=start, end=self.line_of(self.pos - 1))

    def obj(self, start: int) -> Node:
        """Read an object."""
        node = Node(value={}, start=start, end=start)
        values: dict[str, object] = {}
        self.pos += 1
        self.skip()
        while self.text[self.pos] != "}":
            self.skip()
            key_line = self.line_of(self.pos)
            key = self.string()
            self.skip()
            self.pos += 1  # the colon
            child = self.value()
            child.key_line = key_line
            child.start = min(child.start, key_line)
            node.members[key] = child
            values[key] = child.value
            self.skip()
            if self.text[self.pos] == ",":
                self.pos += 1
            self.skip()
        self.pos += 1
        node.value = values
        node.end = self.line_of(self.pos - 1)
        return node

    def array(self, start: int) -> Node:
        """Read an array."""
        node = Node(value=[], start=start, end=start)
        self.pos += 1
        self.skip()
        while self.text[self.pos] != "]":
            child = self.value()
            node.items.append(child)
            self.skip()
            if self.text[self.pos] == ",":
                self.pos += 1
            self.skip()
        self.pos += 1
        node.value = [child.value for child in node.items]
        node.end = self.line_of(self.pos - 1)
        return node


def parse(text: str) -> tuple[Node | None, str]:
    """Parse JSON text into a node tree; returns (None, error) when the text is not valid JSON."""
    try:
        _ = loads(text)
    except ValueError as error:
        return None, str(error)
    if not text.strip():
        return None, "the file is empty"
    reader = _Reader(text)
    return reader.value(), ""
