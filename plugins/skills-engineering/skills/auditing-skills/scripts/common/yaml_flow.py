"""Flow collections, `[a, b]` and `{a: 1}`, nested and over several lines.

Inside a flow collection, line breaks, blanks and comments separate tokens, and a plain scalar
ends at `,`, a bracket, a brace, a `: ` or ` #`. A pair inside a sequence (`[a: 1]`), a `?` key
and a collection used as a key are reported as unsupported.
"""

from common.yaml_source import (
    BLANKS,
    FLOW_INDICATORS,
    MAX_DEPTH,
    Node,
    Source,
    plain_can_start,
)

type Position = tuple[int, int]


def _is_flow_indicator_colon(line: str, k: int) -> bool:
    """A `:` that separates a key from its value in flow context."""
    return line[k] == ":" and (
        k + 1 >= len(line) or line[k + 1] in BLANKS or line[k + 1] in FLOW_INDICATORS
    )


class FlowReader:
    """Reads one flow collection and everything nested in it."""

    def __init__(self, src: Source, opening: Position, depth: int) -> None:
        """Remember where the outermost bracket opens, for an unclosed-flow error."""
        self.src: Source = src
        self.opening: Position = opening
        self.depth: int = depth

    def char(self, at: Position) -> str:
        """The character at a position, or "" past the end of its line."""
        line = self.src.lines[at[0]]
        return line[at[1]] if at[1] < len(line) else ""

    def skip(self, at: Position) -> Position:
        """Skip blanks, line breaks and comments; an unclosed-flow error at the end of the text."""
        i, k = at
        while True:
            line = self.src.lines[i]
            while k < len(line) and line[k] in BLANKS:
                k += 1
            if k < len(line) and not (line[k] == "#" and (k == 0 or line[k - 1] in BLANKS)):
                return i, k
            i, k = i + 1, 0
            if i >= len(self.src.lines):
                self.src.fail("unclosed-flow", "a flow collection that never closes", *self.opening)

    def collection(self, at: Position) -> tuple[Node, Position]:
        """The flow sequence or mapping whose bracket is at `at`, and the position after it."""
        self.depth += 1
        if self.depth > MAX_DEPTH:
            self.src.fail("too-deep", f"nesting deeper than {MAX_DEPTH} levels", *at)
        is_map = self.char(at) == "{"
        close = "}" if is_map else "]"
        node = Node(
            kind="map" if is_map else "seq",
            style="flow",
            raw="",
            value="",
            line=self.src.first_line + at[0],
            column=at[1] + 1,
            end_line=self.src.first_line + at[0],
        )
        seen: set[str] = set()
        pos = self.skip((at[0], at[1] + 1))
        while self.char(pos) != close:
            if is_map:
                pos = self.map_entry(pos, node, seen)
            else:
                item, pos = self.entry(pos)
                node.items.append(item)
                pos = self.skip(pos)
                if _is_flow_indicator_colon(self.src.lines[pos[0]], pos[1]):
                    self.src.fail("unsupported", "a key: value pair inside a flow sequence", *pos)
            pos = self.after_entry(pos, close)
        self.depth -= 1
        node.end_line = self.src.first_line + pos[0]
        node.raw = self.src.span(at, (pos[0], pos[1] + 1))
        return node, (pos[0], pos[1] + 1)

    def after_entry(self, pos: Position, close: str) -> Position:
        """After an entry: a comma, or the closing bracket left for the caller to see."""
        ch = self.char(pos)
        if ch == ",":
            return self.skip((pos[0], pos[1] + 1))
        if ch != close:
            self.src.fail("syntax-error", f"expected `,` or `{close}` in a flow collection", *pos)
        return pos

    def map_entry(self, pos: Position, node: Node, seen: set[str]) -> Position:
        """One `key: value` or `key` entry of a flow mapping."""
        if self.char(pos) in "[{":
            self.src.fail("unsupported", "a flow collection used as a key", *pos)
        if self.char(pos) == "?" and self.char((pos[0], pos[1] + 1)) in {"", " ", "\t"}:
            self.src.fail("unsupported", "a complex key", *pos)
        key, after = self.entry(pos)
        if key.kind == "alias":
            self.src.fail("unsupported", "an alias used as a key", *pos)
        if key.value in seen:
            self.src.fail("duplicate-key", f"the key `{key.value}` appears twice", *pos)
        seen.add(key.value)
        after = self.skip(after)
        if self.char(after) != ":":
            node.pairs.append((key, self.src.null(*after)))
            return after
        value_at = self.skip((after[0], after[1] + 1))
        if self.char(value_at) in {",", "}"}:
            node.pairs.append((key, self.src.null(*value_at)))
            return value_at
        value, end = self.entry(value_at)
        node.pairs.append((key, value))
        return self.skip(end)

    def entry(self, pos: Position) -> tuple[Node, Position]:
        """One node inside a flow collection, and the position after it."""
        ch = self.char(pos)
        if ch in "[{":
            return self.collection(pos)
        if ch in "&!":
            return self.with_properties(pos)
        if ch == "*":
            node, end = self.src.alias(*pos)
            return node, (pos[0], end)
        if ch in "'\"":
            scanned = self.src.scan_quoted(*pos)
            end = (scanned.end_i, scanned.end_k + 1)
            style = "single" if ch == "'" else "double"
            raw = self.src.span(pos, end)
            return self.src.scalar_node(style, raw, scanned.value, pos, scanned.end_i), end
        return self.plain(pos)

    def with_properties(self, pos: Position) -> tuple[Node, Position]:
        """A node with an anchor or a tag, or an empty node holding only them."""
        anchor, tag, k = self.src.properties(*pos)
        at = self.skip((pos[0], k))
        if self.char(at) in {",", "]", "}", ":"}:
            node, end = self.src.null(*at), at
        elif self.char(at) == "*":
            self.src.fail("syntax-error", "an alias can't have properties", *at)
        else:
            node, end = self.entry(at)
        node.anchor, node.tag = anchor, tag
        return node, end

    def plain(self, pos: Position) -> tuple[Node, Position]:
        """A plain scalar in flow context, folded over lines like a block one."""
        line = self.src.lines[pos[0]]
        ch = line[pos[1]]
        # In flow context, `-`, `?` and `:` start a plain scalar only before a safe character.
        if not plain_can_start(line, pos[1]) or (
            ch in "-?:" and line[pos[1] + 1] in FLOW_INDICATORS
        ):
            self.src.fail("syntax-error", f"a plain value can't start with `{ch}`", *pos)
        parts: list[str] = []
        i, k = pos
        end = pos
        blanks = 0
        while True:
            text = self.src.lines[i]
            stop = self.plain_stop(text, k)
            piece = text[k:stop].rstrip(BLANKS)
            if piece:
                parts.append(("\n" * blanks if blanks else " ") if parts else "")
                parts.append(piece)
                end, blanks = (i, k + len(piece)), 0
            if stop < len(text) or i + 1 >= len(self.src.lines):
                break
            i, k, blanks = self.next_plain_line(i, blanks)
            if k < 0:
                break
        raw = self.src.span(pos, end)
        return self.src.scalar_node("plain", raw, "".join(parts), pos, end[0]), end

    def plain_stop(self, text: str, k: int) -> int:
        """Where a flow plain scalar's text on this line stops."""
        j = k
        while j < len(text):
            ch = text[j]
            if ch in FLOW_INDICATORS or _is_flow_indicator_colon(text, j):
                return j
            if ch == "#" and j > k and text[j - 1] in BLANKS:
                return j
            j += 1
        return j

    def next_plain_line(self, i: int, blanks: int) -> tuple[int, int, int]:
        """The next line a flow plain scalar continues on, its start and the blank lines skipped.

        The start is -1 when the scalar ends there: at a comment, a flow indicator or the end.
        """
        while i + 1 < len(self.src.lines):
            i += 1
            text = self.src.lines[i]
            stripped = text.lstrip(BLANKS)
            if not stripped:
                blanks += 1
                continue
            k = len(text) - len(stripped)
            if (
                stripped[0] == "#"
                or stripped[0] in FLOW_INDICATORS
                or _is_flow_indicator_colon(text, k)
            ):
                return i, -1, blanks
            return i, k, blanks
        return i, -1, blanks
