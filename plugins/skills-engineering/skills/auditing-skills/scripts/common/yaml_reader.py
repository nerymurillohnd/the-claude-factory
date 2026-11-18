"""A YAML reader for skill frontmatter that keeps every node's file position and style.

It reads block mappings and sequences; plain scalars over several lines; single- and
double-quoted scalars with YAML's escapes and line folding; literal and folded block scalars;
flow sequences and mappings; and anchors, aliases and tags on any node. Whatever it can't read
with certainty raises ReadError with a rule and a 1-based file position; it never guesses. An
alias is kept as an alias node and never expanded, and nesting stops at MAX_DEPTH, so it never
raises RecursionError.
"""

from typing import NoReturn

from common.yaml_block_scalar import read_block_scalar
from common.yaml_flow import FlowReader
from common.yaml_source import (
    BLANKS,
    MAX_DEPTH,
    Node,
    ReadError,
    Source,
    Where,
    blank_after,
    colon_at,
    content_end,
    is_entry,
    plain_can_start,
)

__all__ = ["Node", "ReadError", "read"]


class _Parser(Source):
    """Recursive descent over the block's lines, with an explicit depth counter."""

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
            if line.startswith(marker) and blank_after(line, 3):
                self.fail("unsupported", "a document marker inside the frontmatter", i, 0)

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

    def rest_of_line(self, i: int, k: int, what: str) -> None:
        """Check that only blanks and a comment follow a value ending at (i, k)."""
        line = self.lines[i]
        j = k
        while j < len(line) and line[j] in BLANKS:
            j += 1
        if j >= len(line) or (line[j] == "#" and j > k):
            return
        if line[j] == ":" and blank_after(line, j + 1):
            self.fail("colon-in-value", f"`: ` after {what}", i, j)
        self.fail("syntax-error", f"text after {what}", i, j)

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
        if is_entry(line, c):
            if where == "after-key":
                self.fail("syntax-error", "a sequence entry on the same line as its key", i, c)
            return self.block_seq(i, c, depth + 1)
        if where != "after-key" and self.key_at(i, c) is not None:
            return self.block_map(i, c, depth + 1)
        if line[c] in "&!":
            return self.with_properties(i, c, parent, depth, where)
        return self.scalar(i, c, parent, depth, where)

    def value_below(
        self, i: int, c: int, parent: int, depth: int, where: Where
    ) -> tuple[Node, int]:
        """A value that starts on a later line, or an empty value."""
        j = self.next_content(i + 1)
        if j < len(self.lines):
            indent = self.indent(j)
            if indent > parent:
                return self.block_value(j, indent, parent, depth + 1, "line-start")
            if where == "after-key" and indent == parent and is_entry(self.lines[j], indent):
                return self.block_seq(j, indent, depth + 1)
        return self.null(i, c), i + 1

    def with_properties(
        self, i: int, c: int, parent: int, depth: int, where: Where
    ) -> tuple[Node, int]:
        """A node after its anchor or tag, on this line or below; the anchor is known first."""
        anchor, tag, k = self.properties(i, c)
        line = self.lines[i]
        if k >= len(line) or line[k] == "#":
            node, nxt = self.value_below(i, k, parent, depth, where)
        elif is_entry(line, k):
            self.fail("syntax-error", "a sequence entry after properties on the same line", i, k)
        elif self.key_at(i, k) is not None:
            self.fail("unsupported", "properties before a key on the same line", i, c)
        elif line[k] == "*":
            self.fail("syntax-error", "an alias can't have properties", i, k)
        else:
            node, nxt = self.scalar(i, k, parent, depth, where)
        if (anchor is not None and node.anchor is not None) or (tag is not None and node.tag):
            self.fail("syntax-error", "a second set of properties on one node", i, c)
        node.anchor = anchor if anchor is not None else node.anchor
        node.tag = tag if tag is not None else node.tag
        return node, nxt

    def scalar(self, i: int, c: int, parent: int, depth: int, where: Where) -> tuple[Node, int]:
        """A node that is not a block collection: a scalar, an alias or a flow collection."""
        line = self.lines[i]
        ch = line[c]
        if ch == "?" and blank_after(line, c + 1):
            self.fail("unsupported", "a complex key", i, c)
        if ch in "'\"":
            return self.quoted_value(i, c)
        if ch in "|>":
            return read_block_scalar(self, i, c, parent)
        if ch in "[{":
            return self.flow_value(i, c, depth, where)
        if ch == "*":
            return self.alias_value(i, c, where)
        if not plain_can_start(line, c):
            self.fail("syntax-error", f"a plain value can't start with `{ch}`", i, c)
        return self.plain(i, c, parent)

    def flow_value(self, i: int, c: int, depth: int, where: Where) -> tuple[Node, int]:
        """A flow collection as a block value: nothing but a comment may follow it."""
        node, (end_i, end_k) = FlowReader(self, (i, c), depth).collection((i, c))
        line = self.lines[end_i]
        j = end_k
        while j < len(line) and line[j] in BLANKS:
            j += 1
        if where != "after-key" and line[j : j + 1] == ":" and blank_after(line, j + 1):
            self.fail("unsupported", "a flow collection used as a key", i, c)
        self.rest_of_line(end_i, end_k, "a flow collection")
        return node, end_i + 1

    def alias_value(self, i: int, c: int, where: Where) -> tuple[Node, int]:
        """An alias as a block value: nothing but a comment may follow it."""
        node, end = self.alias(i, c)
        line = self.lines[i]
        j = end
        while j < len(line) and line[j] in BLANKS:
            j += 1
        if where != "after-key" and line[j : j + 1] == ":" and blank_after(line, j + 1):
            self.fail("unsupported", "an alias used as a key", i, c)
        self.rest_of_line(i, end, "an alias")
        return node, i + 1

    # Collections

    def block_map(self, i: int, c: int, depth: int) -> tuple[Node, int]:
        """A block mapping whose entries start at column c, the first on line i."""
        pairs: list[tuple[Node, Node]] = []
        seen: set[str] = set()
        while True:
            found = self.key_at(i, c)
            if found is None:
                self.no_key(i, c)
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
            if not is_entry(self.lines[j], c):
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

    def no_key(self, i: int, c: int) -> NoReturn:
        """Reject a mapping line with no key: a key form no check reads, or a syntax error."""
        line = self.lines[i]
        if line[c] in "*[{&!" and colon_at(line[c:]) is not None:
            self.fail(
                "unsupported",
                "a key that is an alias or a flow collection, or has properties",
                i,
                c,
            )
        self.fail("syntax-error", "expected `key: value` here", i, c)

    def key_at(self, i: int, c: int) -> tuple[Node, int] | None:
        """The key starting at (i, c) and the index after its `:`, or None if no key is there."""
        line = self.lines[i]
        ch = line[c]
        if ch == "?" and blank_after(line, c + 1):
            self.fail("unsupported", "a complex key", i, c)
        if ch in "'\"":
            return self.quoted_key(i, c)
        if not plain_can_start(line, c):
            return None
        end = content_end(line, c)
        colon = colon_at(line[c:end] + " ")
        if colon is None:
            return None
        text = line[c : c + colon].rstrip(BLANKS)
        return self.scalar_node("plain", text, text, (i, c), i), c + colon + 1

    def quoted_key(self, i: int, c: int) -> tuple[Node, int] | None:
        """A quoted key closed on its own line and followed by `:`."""
        scanned = self.scan_quoted(i, c)
        if scanned.end_i != i:
            return None
        line = self.lines[i]
        k = scanned.end_k + 1
        while k < len(line) and line[k] in BLANKS:
            k += 1
        if line[k : k + 1] != ":" or not blank_after(line, k + 1):
            return None
        style = "single" if line[c] == "'" else "double"
        raw = line[c : scanned.end_k + 1]
        return self.scalar_node(style, raw, scanned.value, (i, c), i), k + 1

    # Scalars

    def plain(self, i: int, c: int, parent: int) -> tuple[Node, int]:
        """A plain scalar from (i, c), over every following line indented deeper than parent."""
        line = self.lines[i]
        end = content_end(line, c)
        colon = colon_at(line[c:end] + " ")
        if colon is not None:
            self.fail("colon-in-value", "`: ` inside a plain value", i, c + colon)
        parts = [line[c:end]]
        last, last_end = i, end
        if end == len(line.rstrip(BLANKS)):
            last, last_end = self.plain_continuation(i, parent, parts)
        raw = self.span((i, c), (last, last_end))
        return self.scalar_node("plain", raw, "".join(parts), (i, c), last), last + 1

    def plain_continuation(self, i: int, parent: int, parts: list[str]) -> tuple[int, int]:
        """Fold a plain scalar's continuation lines into parts; return its last line and end."""
        last, last_end = i, content_end(self.lines[i], 0)
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
            end = content_end(text, start)
            if colon_at(text[start:end] + " ") is not None:
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
        self.rest_of_line(scanned.end_i, scanned.end_k + 1, "a quoted value")
        style = "single" if self.lines[i][c] == "'" else "double"
        raw = self.span((i, c), (scanned.end_i, scanned.end_k + 1))
        node = self.scalar_node(style, raw, scanned.value, (i, c), scanned.end_i)
        return node, scanned.end_i + 1


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
