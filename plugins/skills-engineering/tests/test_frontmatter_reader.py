#!/usr/bin/env python3
"""Tests for the frontmatter reader: block mappings and sequences, scalars, and its errors.

Every case reads YAML whose first line is file line 2, as a SKILL.md block is, so each position
checked here is the line a reviewer would open.
"""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/auditing-skills/scripts"))

from common.yaml_reader import Node, ReadError, read

TAB = "\t"


class ReaderTestCase(unittest.TestCase):
    """Helpers shared by the reader tests."""

    def pairs(self, node: Node) -> dict[str, Node]:
        """A mapping's values by key text, failing the test when node isn't a mapping."""
        self.assertEqual(node.kind, "map")
        return {key.value: value for key, value in node.pairs}

    def error(self, text: str) -> ReadError:
        """The ReadError reading text raises, failing the test when it raises none."""
        with self.assertRaises(ReadError) as caught:
            _ = read(text, 2)
        return caught.exception


class BlockStructureTest(ReaderTestCase):
    """Block mappings and sequences, with their positions."""

    def test_two_pairs_with_lines(self) -> None:
        """Two top-level pairs, values a and b, on file lines 2 and 3."""
        root = read("name: a\ndescription: b", 2)
        found = [(k.value, v.value, k.line, v.line) for k, v in root.pairs]
        self.assertEqual(found, [("name", "a", 2, 2), ("description", "b", 3, 3)])

    def test_columns_are_one_based(self) -> None:
        """A key starts at column 1 and its value after `: `."""
        key, value = read("name: abc", 2).pairs[0]
        self.assertEqual((key.column, value.column), (1, 7))

    def test_nested_map(self) -> None:
        """An indented mapping under a key."""
        metadata = self.pairs(read('metadata:\n  a: "1"', 2))["metadata"]
        inner = self.pairs(metadata)["a"]
        self.assertEqual((inner.value, inner.style, inner.line), ("1", "double", 3))

    def test_sequence_under_key(self) -> None:
        """A block sequence of two under a key."""
        tools = self.pairs(read("tools:\n  - Read\n  - Grep", 2))["tools"]
        self.assertEqual((tools.kind, [i.value for i in tools.items]), ("seq", ["Read", "Grep"]))

    def test_sequence_at_the_key_indent(self) -> None:
        """A sequence may start at the same indent as its key."""
        tools = self.pairs(read("tools:\n- Read\n- Grep\nname: x", 2))
        self.assertEqual([i.value for i in tools["tools"].items], ["Read", "Grep"])
        self.assertEqual(tools["name"].value, "x")

    def test_mapping_inside_sequence_entry(self) -> None:
        """`- a: 1` starts a mapping that continues at the entry's column."""
        seq = self.pairs(read("hooks:\n  - a: 1\n    b: 2\n  - c: 3", 2))["hooks"]
        first = self.pairs(seq.items[0])
        self.assertEqual({k: v.value for k, v in first.items()}, {"a": "1", "b": "2"})
        self.assertEqual(self.pairs(seq.items[1])["c"].line, 5)

    def test_empty_value_is_null(self) -> None:
        """A key with no value holds an empty plain scalar."""
        value = self.pairs(read("license:\nname: x", 2))["license"]
        self.assertEqual(
            (value.kind, value.style, value.value, value.raw), ("scalar", "plain", "", "")
        )

    def test_comments(self) -> None:
        """Full-line comments and comments after a space are dropped."""
        root = self.pairs(read("# top\nd: x # note\n  # inner\ne: y#z", 2))
        self.assertEqual((root["d"].value, root["e"].value), ("x", "y#z"))

    def test_quoted_key(self) -> None:
        """A quoted key is compared by its text."""
        root = self.pairs(read('"name": a', 2))
        self.assertEqual(root["name"].value, "a")


class ScalarTest(ReaderTestCase):
    """Plain, single-quoted and double-quoted scalars."""

    def test_plain_folds_lines(self) -> None:
        """Lines fold with one space; a blank line gives a newline."""
        value = self.pairs(read("description: one\n  two\n\n  three", 2))["description"]
        self.assertEqual((value.value, value.style, value.end_line), ("one two\nthree", "plain", 5))
        self.assertEqual(value.raw, "one\n  two\n\n  three")

    def test_plain_keeps_url_colons_and_dashes(self) -> None:
        """A colon not followed by a space stays in a plain value, and so does `- ` text."""
        value = self.pairs(read("d: see http://x.y/z\n  - more", 2))["d"]
        self.assertEqual(value.value, "see http://x.y/z - more")

    def test_single_quoted(self) -> None:
        """'' is one quote inside single quotes."""
        value = self.pairs(read("d: 'it''s'", 2))["d"]
        self.assertEqual((value.value, value.style, value.raw), ("it's", "single", "'it''s'"))

    def test_double_quoted_escapes(self) -> None:
        """Double quotes decode the YAML escapes."""
        value = self.pairs(read('d: "a\\tb\\u00e9 \\"q\\" \\\\ \\U0001F600"', 2))["d"]
        self.assertEqual(
            value.value, f'a{TAB}b\N{LATIN SMALL LETTER E WITH ACUTE} "q" \\ \U0001f600'
        )

    def test_quoted_over_several_lines(self) -> None:
        """Quoted scalars fold their line breaks like plain ones."""
        root = self.pairs(read("a: 'one\n  two\n\n  three'\nb: \"x\\\n  y\"", 2))
        self.assertEqual((root["a"].value, root["a"].end_line), ("one two\nthree", 5))
        self.assertEqual(root["b"].value, "xy")

    def test_invalid_escape(self) -> None:
        """An escape YAML doesn't define is a syntax error."""
        self.assertEqual(self.error('d: "\\q"').rule, "syntax-error")


class ErrorTest(ReaderTestCase):
    """What the reader rejects, and where."""

    def test_colon_in_value(self) -> None:
        """`: ` inside a plain value."""
        caught = self.error("d: Use when: x")
        self.assertEqual((caught.rule, caught.line, caught.column), ("colon-in-value", 2, 12))

    def test_trailing_colon_in_value(self) -> None:
        """A plain value ending with `:`."""
        self.assertEqual(self.error("a: foo:").rule, "colon-in-value")

    def test_colon_after_quoted_value(self) -> None:
        """A key after a quoted value on the same line."""
        self.assertEqual(self.error('a: "q": r').rule, "colon-in-value")

    def test_unclosed_quote(self) -> None:
        """An opening quote with no closing one, reported where it opens."""
        caught = self.error('name: a\nd: "abc')
        self.assertEqual((caught.rule, caught.line, caught.column), ("unclosed-quote", 3, 4))

    def test_tab_indent(self) -> None:
        """A tab in a line's indentation."""
        caught = self.error(f"m:\n{TAB}k: v")
        self.assertEqual((caught.rule, caught.line), ("tab-indent", 3))

    def test_key_under_scalar(self) -> None:
        """A key indented under a plain scalar."""
        caught = self.error("name: a\n  b: c")
        self.assertEqual((caught.rule, caught.line), ("key-under-scalar", 3))

    def test_key_under_quoted_scalar(self) -> None:
        """A key indented under a quoted scalar."""
        self.assertEqual(self.error('name: "a"\n  b: c').rule, "key-under-scalar")

    def test_duplicate_key(self) -> None:
        """The second occurrence of a key, compared after unquoting."""
        caught = self.error("name: a\n'name': b")
        self.assertEqual((caught.rule, caught.line, caught.column), ("duplicate-key", 3, 1))

    def test_duplicate_key_nested(self) -> None:
        """Duplicates count within one mapping, at any depth."""
        self.assertEqual(self.error("m:\n  a: 1\n  a: 2").rule, "duplicate-key")
        _ = read("m:\n  a: 1\nn:\n  a: 2", 2)

    def test_bad_first_characters(self) -> None:
        """A plain value can't start with `,`, `%`, `@` or a backtick."""
        for start in (",", "%", "@", "`"):
            self.assertEqual(self.error(f"d: {start}x").rule, "syntax-error", start)

    def test_sequence_entry_after_a_key_on_one_line(self) -> None:
        """`a: - b` is not a sequence."""
        self.assertEqual(self.error("a: - b").rule, "syntax-error")

    def test_text_where_a_key_belongs(self) -> None:
        """A line with no `key:` inside a mapping."""
        self.assertEqual(self.error("a: 1\nfoo").rule, "syntax-error")

    def test_bad_dedent(self) -> None:
        """A key dedented to a column no mapping uses."""
        self.assertEqual(self.error("a:\n    b: 1\n  c: 2").rule, "syntax-error")

    def test_unsupported(self) -> None:
        """Complex keys, directives and document markers aren't read."""
        for text in ("? a", "%YAML 1.2", "a: 1\n...", "a: 1\n--- b"):
            self.assertEqual(self.error(text).rule, "unsupported", text)

    def test_too_deep(self) -> None:
        """Nesting beyond 100 levels stops with too-deep, never a RecursionError."""
        text = "".join(f"{' ' * i}k:\n" for i in range(150))
        self.assertEqual(self.error(text).rule, "too-deep")
        seq = "".join(f"{' ' * (2 * i)}-\n" for i in range(150))
        self.assertEqual(self.error(seq).rule, "too-deep")


if __name__ == "__main__":
    _ = unittest.main()
