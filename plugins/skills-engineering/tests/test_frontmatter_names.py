#!/usr/bin/env python3
"""Tests for frontmatter.name and frontmatter.name-plain, run through frontmatter-checks.py.

frontmatter.name checks the name's format, its folder, the characters Claude Code refuses and
the reserved words; frontmatter.name-plain checks that the name is written as one plain line.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, rules, run_check

NAME = "frontmatter.name"
NAME_PLAIN = "frontmatter.name-plain"


def skill(yaml: str) -> str:
    """A SKILL.md whose frontmatter holds yaml, starting on file line 2."""
    return f"---\n{yaml}\ndescription: Does a thing.\n---\nBody.\n"


class NameTestCase(unittest.TestCase):
    """Helpers shared by the name tests."""

    def result(self, check: str, yaml: str, folder: str = "demo-skill") -> JsonObject:
        """Run one check on a frontmatter in a folder; fail the test unless it exits 0."""
        code, result = run_check(check, skill(yaml), folder=folder)
        self.assertEqual(code, 0)
        return result

    def rule_names(self, check: str, yaml: str, folder: str = "demo-skill") -> list[str]:
        """The rules of a result's findings, sorted."""
        return sorted(rule for rule, _line in rules(self.result(check, yaml, folder)))


class NameFormatTest(NameTestCase):
    """frontmatter.name."""

    def test_valid_name(self) -> None:
        """A name equal to its folder, in the allowed characters."""
        result = self.result(NAME, "name: demo-skill")
        self.assertEqual(rules(result), [])
        data = result.get("data")
        if not isinstance(data, JsonObject):
            self.fail(f"expected data, got {result!r}")
        self.assertEqual(
            list(data),
            [
                "name",
                "name_source",
                "length",
                "utf16_length",
                "folder_name",
                "matches_folder",
                "unicode_version",
            ],
        )
        self.assertEqual(
            (data.get("name"), data.get("length"), data.get("matches_folder")),
            ("demo-skill", 10, True),
        )

    def test_several_rules(self) -> None:
        """Capitals, an underscore, a trailing hyphen, a reserved word and another folder."""
        self.assertEqual(
            self.rule_names(NAME, "name: Other_Name-claude-", folder="x"),
            ["charset", "folder-mismatch", "hyphen", "reserved-word"],
        )

    def test_length(self) -> None:
        """65 characters are one too many."""
        name = "a" * 65
        self.assertEqual(self.rule_names(NAME, f"name: {name}", folder=name), ["length"])

    def test_consecutive_hyphens(self) -> None:
        """`--` inside the name."""
        self.assertEqual(self.rule_names(NAME, "name: a--b", folder="a--b"), ["hyphen"])

    def test_zero_width_space(self) -> None:
        """A zero-width space is refused, and is outside the charset."""
        self.assertEqual(
            self.rule_names(NAME, 'name: "a\\u200bb"', folder="ab"),
            ["charset", "folder-mismatch", "refused-character"],
        )

    def test_angle_brackets(self) -> None:
        """`<` and `>` are refused."""
        self.assertIn("refused-character", self.rule_names(NAME, 'name: "<x>"', folder="x"))

    def test_no_break_space(self) -> None:
        """A blank other than a plain space is refused."""
        self.assertIn("refused-character", self.rule_names(NAME, 'name: "a\\u00a0b"'))

    def test_missing(self) -> None:
        """No name: Claude Code uses the folder name."""
        result = self.result(NAME, "license: MIT")
        self.assertEqual(rules(result), [("missing", None)])
        data = result.get("data")
        if not isinstance(data, JsonObject):
            self.fail(f"expected data, got {result!r}")
        self.assertEqual((data.get("name_source"), data.get("name")), ("folder", "demo-skill"))

    def test_reserved_folder_when_name_is_missing(self) -> None:
        """Without a name, the folder name is checked for the reserved words."""
        self.assertEqual(
            self.rule_names(NAME, "license: MIT", folder="claude-helper"),
            ["missing", "reserved-word"],
        )

    def test_not_a_string(self) -> None:
        """A YAML 1.1 integer isn't a name."""
        self.assertEqual(self.rule_names(NAME, "name: 12", folder="12"), ["not-a-string"])


class NamePlainTest(NameTestCase):
    """frontmatter.name-plain."""

    def test_plain_name(self) -> None:
        """A plain name on one line."""
        self.assertEqual(self.rule_names(NAME_PLAIN, "name: demo"), [])

    def test_quoted(self) -> None:
        """A quoted name."""
        self.assertEqual(self.rule_names(NAME_PLAIN, 'name: "demo"'), ["quoted"])

    def test_block_scalar(self) -> None:
        """A name written as a block scalar."""
        self.assertEqual(self.rule_names(NAME_PLAIN, "name: |\n  demo"), ["block-scalar"])

    def test_multi_line(self) -> None:
        """A plain name folded over two lines."""
        self.assertEqual(self.rule_names(NAME_PLAIN, "name: demo\n  skill"), ["multi-line"])

    def test_anchor(self) -> None:
        """An anchor on the name."""
        self.assertEqual(self.rule_names(NAME_PLAIN, "name: &a demo"), ["anchor-alias-tag"])

    def test_yaml11_types(self) -> None:
        """A date and a float as names."""
        for name in ("2026-11-17", "1e3"):
            with self.subTest(name=name):
                self.assertEqual(self.rule_names(NAME_PLAIN, f"name: {name}"), ["yaml11-type"])

    def test_boolean_is_left_to_plain_values(self) -> None:
        """`on` belongs to frontmatter.plain-values."""
        self.assertEqual(self.rule_names(NAME_PLAIN, "name: on"), [])

    def test_convention_has_no_surface(self) -> None:
        """A convention finding names no surface."""
        result = self.result(NAME_PLAIN, 'name: "demo"')
        findings = result.get("findings")
        first = findings[0] if is_list(findings) and findings else None
        if not isinstance(first, JsonObject):
            self.fail(f"expected a finding, got {result!r}")
        self.assertEqual((first.get("basis"), first.get("surfaces")), ("convention", []))


if __name__ == "__main__":
    _ = unittest.main()
