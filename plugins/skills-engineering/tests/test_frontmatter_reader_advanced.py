#!/usr/bin/env python3
"""Tests for the frontmatter reader's block scalars, flow collections, properties and types.

Every case reads YAML whose first line is file line 2, as a SKILL.md block is, and whose last
line ends with a line break, as the line before the closing `---` does. The differential test
compares the reader and its YAML 1.2 types with ruamel.yaml, run in a child process so its
untyped API stays out of this file; it is skipped where ruamel.yaml isn't installed.
"""

import importlib.util
import json
import subprocess
import sys
import time
from typing import TypeGuard
import unittest

from frontmatter_helpers import SCRIPTS, is_list, parse_json

sys.path.insert(0, str(SCRIPTS))

from common.yaml_reader import Node, ReadError, read
from common.yaml_types import to_python, yaml11_tag, yaml12_tag

# Reads a JSON array of YAML texts on stdin and prints, for each, the repr of what
# ruamel.yaml loads or "error".
RUAMEL_LOADER = """
import json, sys
from ruamel.yaml import YAML
out = []
for text in json.load(sys.stdin):
    try:
        out.append(repr(YAML(typ="safe", pure=True).load(text)))
    except Exception:
        out.append("error")
print(json.dumps(out))
"""

VALID = [
    "name: demo",
    "description: a plain value\n  over two lines",
    'description: "an escaped\\ttab and \\u00e9"',
    "description: 'it''s quoted'",
    "d: |\n  a\n  b\n",
    "d: |-\n  a\n  b\n",
    "d: |+\n  a\n\n",
    "d: >\n  a\n  b\n\n  c\n",
    "d: >-\n  a\n  b",
    "d: >\n  a\n\n  b\n   c\n  d\n",
    "d: |2\n   a\n  b",
    "d: | # a comment\n  text",
    "- |\n  in a sequence\n- b",
    "t: [Read, Grep]",
    't: [Read, "Bash(git *)"]',
    "t: []",
    "m: {}",
    "m: {a: 1, b: [x, y]}",
    "t: [a,\n  b,\n  c]",
    "t: [a, b,]",
    "m: {a: [1, {b: c}], d: e}",
    "t: [a #c\n , b]",
    "t: [a\n  b, c]",
    "m: {a, b: 2}",
    "m: {a: , b: 2}",
    "name: &n demo\nalias: *n",
    "base: &b\n  x: 1\ncopy: *b",
    "t: [!!str 1, &x 2, *x]",
    "k: !!str 12",
    "k: !!int '12'",
    "k: !!float 1",
    "k: &a\n  - x",
    "n: [~, null, Null, NULL, '']",
    "b: [true, True, FALSE, on, yes, n]",
    "i: [0, 17, 017, -3, +12, 0o7, 0x1F]",
    "f: [1.5, 1., .5, 1e3, -2.5E-2, .inf, -.Inf]",
    "s: [0o8, 1:30, 0x, ., yes]",
    "empty:",
    "tools:\n  - Read\n  - Grep\nname: x",
    "metadata:\n  a: '1'\n  b:\n    c: d",
]

INVALID = [
    "t: [Read",
    "m: {a: 1",
    "t: [,]",
    "a: 1\nb: *a",
    "k: [a] x",
    "k: [a]: b",
    "m: {a: 1, a: 2}",
    "a: 1\na: 2",
    "d: 'never closed",
    "x: &a *b",
    'd: "\\q"',
    "d: |x\n  a",
    "d: |0\n  a",
    "m: {a: 1}}",
    "t: [a, , b]",
]


def is_dict(value: object) -> TypeGuard[dict[object, object]]:
    """Narrow a built value to a mapping."""
    return isinstance(value, dict)


class AdvancedTestCase(unittest.TestCase):
    """Helpers shared by these tests."""

    def pairs(self, node: Node) -> dict[str, Node]:
        """A mapping's values by key text, failing the test when node isn't a mapping."""
        self.assertEqual(node.kind, "map")
        return {key.value: value for key, value in node.pairs}

    def value(self, text: str, key: str) -> Node:
        """The value of one top-level key."""
        return self.pairs(read(text, 2))[key]

    def error(self, text: str) -> ReadError:
        """The ReadError reading text raises, failing the test when it raises none."""
        with self.assertRaises(ReadError) as caught:
            _ = read(text, 2)
        return caught.exception

    def scalar(self, text: str) -> Node:
        """The single value of `k: <text>`."""
        return self.value(f"k: {text}", "k")


class BlockScalarTest(AdvancedTestCase):
    """Literal and folded block scalars."""

    def test_literal_clip(self) -> None:
        """`|` keeps the line breaks and one final break."""
        node = self.value("d: |\n  a\n  b\n", "d")
        self.assertEqual((node.value, node.style, node.line), ("a\nb\n", "literal", 2))

    def test_folded_strip(self) -> None:
        """`>-` folds the lines into one and drops the final break."""
        node = self.value("d: >-\n  a\n  b", "d")
        self.assertEqual((node.value, node.style), ("a b", "folded"))

    def test_keep(self) -> None:
        """`|+` keeps the trailing empty line."""
        self.assertEqual(self.value("d: |+\n  a\n", "d").value, "a\n\n")

    def test_indentation_digit(self) -> None:
        """`|2` sets the content indentation, so one extra space stays in the text."""
        self.assertEqual(self.value("d: |2\n   a\n  b", "d").value, " a\nb\n")

    def test_more_indented_lines_keep_their_breaks(self) -> None:
        """A more-indented line inside `>` is not folded."""
        node = self.value("d: >\n  a\n\n  b\n   c\n  d\n", "d")
        self.assertEqual(node.value, "a\nb\n c\nd\n")

    def test_the_next_key_follows(self) -> None:
        """The mapping goes on after the block scalar ends."""
        found = self.pairs(read("d: |\n  a\nname: x", 2))
        self.assertEqual((found["d"].value, found["name"].value), ("a\n", "x"))

    def test_zero_indentation_is_an_error(self) -> None:
        """`|0` is not a valid indentation indicator."""
        self.assertEqual(self.error("d: |0\n  a").rule, "syntax-error")

    def test_text_after_the_header_is_an_error(self) -> None:
        """Only a comment may follow the header."""
        self.assertEqual(self.error("d: |x\n  a").rule, "syntax-error")


class FlowTest(AdvancedTestCase):
    """Flow sequences and mappings."""

    def test_flow_sequence(self) -> None:
        """A flow sequence of two, the second quoted."""
        node = self.value('t: [Read, "Bash(git *)"]', "t")
        self.assertEqual((node.kind, node.style), ("seq", "flow"))
        self.assertEqual([i.value for i in node.items], ["Read", "Bash(git *)"])
        self.assertEqual([i.style for i in node.items], ["plain", "double"])

    def test_flow_mapping(self) -> None:
        """A flow mapping of one pair."""
        node = self.value("m: {a: 1}", "m")
        self.assertEqual((node.kind, node.style), ("map", "flow"))
        self.assertEqual(self.pairs(node)["a"].value, "1")

    def test_positions(self) -> None:
        """Items of a flow sequence over several lines keep their own lines and columns."""
        node = self.value("t: [a,\n  b]", "t")
        found = [(i.value, i.line, i.column) for i in node.items]
        self.assertEqual(found, [("a", 2, 5), ("b", 3, 3)])
        self.assertEqual((node.line, node.end_line, node.raw), (2, 3, "[a,\n  b]"))

    def test_unclosed_flow(self) -> None:
        """An unclosed bracket is reported at the line it opens on."""
        caught = self.error("t: [Read")
        self.assertEqual((caught.rule, caught.line, caught.column), ("unclosed-flow", 2, 4))

    def test_unclosed_flow_over_lines(self) -> None:
        """The opening line is reported even when the text runs on."""
        caught = self.error("name: x\nt: [Read,\n  Grep")
        self.assertEqual((caught.rule, caught.line), ("unclosed-flow", 3))

    def test_trailing_comma(self) -> None:
        """A comma before the closing bracket is allowed."""
        self.assertEqual(len(self.value("t: [a, b,]", "t").items), 2)

    def test_empty_entry_is_an_error(self) -> None:
        """Two commas in a row leave an empty entry."""
        self.assertEqual(self.error("t: [a, , b]").rule, "syntax-error")

    def test_pair_in_a_sequence_is_unsupported(self) -> None:
        """`[a: 1]` is read by no check, so it is reported as unsupported."""
        self.assertEqual(self.error("t: [a: 1]").rule, "unsupported")

    def test_duplicate_flow_key(self) -> None:
        """A key twice in one flow mapping."""
        self.assertEqual(self.error("m: {a: 1, a: 2}").rule, "duplicate-key")

    def test_text_after_flow(self) -> None:
        """Only a comment may follow a flow collection that is a value."""
        self.assertEqual(self.error("k: [a] x").rule, "syntax-error")
        self.assertEqual(self.error("k: [a]: b").rule, "colon-in-value")

    def test_flow_key_is_unsupported(self) -> None:
        """A flow collection used as a block key."""
        self.assertEqual(self.error("- [a]: b").rule, "unsupported")

    def test_comment_after_flow(self) -> None:
        """A comment after the closing bracket is dropped."""
        self.assertEqual(len(self.value("t: [a] # tools", "t").items), 1)


class PropertiesTest(AdvancedTestCase):
    """Anchors, aliases and tags."""

    def test_anchor(self) -> None:
        """`&n` names the node it precedes."""
        node = self.value("name: &n demo", "name")
        self.assertEqual((node.anchor, node.value, node.raw), ("n", "demo", "demo"))

    def test_alias(self) -> None:
        """`*n` is an alias node holding the anchor's name."""
        node = self.value("name: &n demo\nx: *n", "x")
        self.assertEqual((node.kind, node.value, node.raw, node.line), ("alias", "n", "*n", 3))

    def test_tag(self) -> None:
        """`!!str` is kept on the node it precedes."""
        node = self.value("d: !!str 1", "d")
        self.assertEqual((node.tag, node.value), ("!!str", "1"))

    def test_verbatim_tag(self) -> None:
        """A verbatim tag is kept whole."""
        self.assertEqual(self.scalar("!<tag:yaml.org,2002:str> 1").tag, "!<tag:yaml.org,2002:str>")

    def test_anchor_on_a_mapping_below(self) -> None:
        """An anchor alone after `key:` names the mapping on the next lines."""
        node = self.value("k: &a\n  x: 1", "k")
        self.assertEqual((node.kind, node.anchor), ("map", "a"))

    def test_anchor_and_tag_on_a_flow_collection(self) -> None:
        """Both properties apply to the flow sequence after them."""
        node = self.scalar("!!seq &a [1]")
        self.assertEqual((node.kind, node.anchor, node.tag), ("seq", "a", "!!seq"))

    def test_unknown_alias(self) -> None:
        """An alias to an anchor not defined before it."""
        self.assertEqual(self.error("a: 1\nb: *a").rule, "syntax-error")

    def test_alias_with_properties(self) -> None:
        """An alias can't take an anchor or a tag."""
        self.assertEqual(self.error("x: &a *b").rule, "syntax-error")

    def test_properties_before_a_key_are_unsupported(self) -> None:
        """`&a k: v` would anchor the key, which no check reads."""
        self.assertEqual(self.error("&a k: v").rule, "unsupported")

    def test_alias_as_a_key_is_unsupported(self) -> None:
        """An alias used as a block key."""
        self.assertEqual(self.error("a: &a 1\n*a : 2").rule, "unsupported")

    def test_self_reference_returns_quickly(self) -> None:
        """An alias inside its own anchor is never expanded."""
        start = time.perf_counter()
        node = self.value("a: &x [*x]", "a")
        self.assertLess(time.perf_counter() - start, 1)
        self.assertEqual((node.anchor, node.items[0].kind), ("x", "alias"))

    def test_deep_flow_nesting(self) -> None:
        """5,000 nested brackets stop at the depth limit, not in a RecursionError."""
        caught = self.error("t: " + "[" * 5000)
        self.assertEqual(caught.rule, "too-deep")


class Yaml11Test(AdvancedTestCase):
    """YAML 1.1 implicit types."""

    def test_types(self) -> None:
        """Each plain value resolves as YAML 1.1 loaders read it."""
        cases = {
            "on": "bool",
            "Yes": "bool",
            "n": "bool",
            "OFF": "bool",
            "0o7": "str",
            "017": "int",
            "1_000": "int",
            "0x1F": "int",
            "1:30": "int",
            "1e3": "float",
            "1.5": "float",
            ".inf": "float",
            "2026-11-17": "timestamp",
            "2026-11-17T10:00:00Z": "timestamp",
            "~": "null",
            "": "null",
            "_": "str",
            "demo": "str",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(yaml11_tag(self.scalar(text)), expected)

    def test_quoted_and_block_scalars_are_strings(self) -> None:
        """Only plain scalars resolve implicitly."""
        self.assertEqual(yaml11_tag(self.scalar("'on'")), "str")
        self.assertEqual(yaml11_tag(self.value("k: |\n  on", "k")), "str")

    def test_explicit_tag_wins(self) -> None:
        """`!!str` keeps a value a string, and `!!int` makes one an integer."""
        self.assertEqual(yaml11_tag(self.scalar("!!str on")), "str")
        self.assertEqual(yaml11_tag(self.scalar("!!int '7'")), "int")

    def test_collections_are_rejected(self) -> None:
        """Type resolution applies to scalars only."""
        with self.assertRaises(TypeError):
            _ = yaml11_tag(self.scalar("[a]"))


class Yaml12Test(AdvancedTestCase):
    """YAML 1.2 core schema types."""

    def test_types(self) -> None:
        """Each plain value resolves as the 1.2 core schema says."""
        cases = {
            "on": "str",
            "yes": "str",
            "True": "bool",
            "0o7": "int",
            "017": "int",
            "1_000": "str",
            "1e3": "float",
            "2026-11-17": "str",
            "null": "null",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(yaml12_tag(self.scalar(text)), expected)


class ToPythonTest(AdvancedTestCase):
    """Building Python values from nodes."""

    def test_yaml11_values(self) -> None:
        """YAML 1.1 reads octal, sexagesimal and boolean words."""
        node = read("a: 017\nb: 1:30\nc: on\nd: 1_000", 2)
        self.assertEqual(to_python(node, "1.1"), {"a": 15, "b": 90, "c": True, "d": 1000})

    def test_yaml12_values(self) -> None:
        """YAML 1.2 keeps those as written."""
        node = read("a: 017\nb: 0o17\nc: on", 2)
        self.assertEqual(to_python(node, "1.2"), {"a": 17, "b": 15, "c": "on"})

    def test_alias_shares_the_anchored_value(self) -> None:
        """An alias gives the same object as its anchor."""
        result = to_python(read("a: &x [1]\nb: *x", 2), "1.2")
        if not is_dict(result):
            self.fail(f"expected a dict, got {result!r}")
        self.assertIs(result.get("a"), result.get("b"))

    def test_self_reference(self) -> None:
        """A sequence holding an alias to itself contains itself."""
        result = to_python(read("a: &x [*x]", 2), "1.2")
        if not is_dict(result):
            self.fail(f"expected a dict, got {result!r}")
        inner = result.get("a")
        if not is_list(inner):
            self.fail(f"expected a list, got {inner!r}")
        self.assertIs(inner[0], inner)

    def test_unknown_tag(self) -> None:
        """A tag no constructor knows can't be built."""
        with self.assertRaises(ValueError):
            _ = to_python(read("x: !foo 1", 2), "1.2")


def ruamel_results(texts: list[str]) -> list[object]:
    """What ruamel.yaml loads from each text and the line break after it, as a repr, or "error".

    The break is the one the frontmatter's last line has before the closing `---`.
    """
    completed = subprocess.run(
        [sys.executable, "-I", "-c", RUAMEL_LOADER],
        input=json.dumps([f"{text}\n" for text in texts]),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    results = parse_json(completed.stdout)
    if not is_list(results):
        msg = f"expected a JSON array, got: {completed.stdout!r}"
        raise TypeError(msg)
    return results


def reader_result(text: str) -> str:
    """What the reader and to_python build from text, as a repr, or "error"."""
    try:
        return repr(to_python(read(text, 2), "1.2"))
    except (ReadError, ValueError):
        return "error"


@unittest.skipUnless(importlib.util.find_spec("ruamel"), "ruamel.yaml is not installed")
class DifferentialTest(unittest.TestCase):
    """The reader agrees with ruamel.yaml on valid and invalid YAML."""

    def test_fixture_counts(self) -> None:
        """40 valid fixtures and 15 invalid ones."""
        self.assertEqual((len(VALID), len(INVALID)), (40, 15))

    def test_valid_fixtures(self) -> None:
        """Both build the same value from each valid fixture."""
        for text, expected in zip(VALID, ruamel_results(VALID), strict=True):
            with self.subTest(text=text):
                self.assertNotEqual(expected, "error")
                self.assertEqual(reader_result(text), expected)

    def test_invalid_fixtures(self) -> None:
        """Both reject each invalid fixture."""
        for text, expected in zip(INVALID, ruamel_results(INVALID), strict=True):
            with self.subTest(text=text):
                self.assertEqual((reader_result(text), expected), ("error", "error"))


if __name__ == "__main__":
    _ = unittest.main()
