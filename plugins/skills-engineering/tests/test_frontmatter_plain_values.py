#!/usr/bin/env python3
"""Tests for the plain-value check, frontmatter.plain-values, run through frontmatter-checks.py.

It reports plain values a YAML parser reads differently than they are written: a comment that
cuts the text, a leading indicator, a collection, properties, and text read as a boolean or null.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, rules, run_check

CHECK = "frontmatter.plain-values"


def skill(yaml: str) -> str:
    """A SKILL.md whose frontmatter holds yaml, starting on file line 2."""
    return f"---\n{yaml}\n---\nBody.\n"


class PlainValuesTest(unittest.TestCase):
    """Each rule, the values it leaves alone, and its prerequisite."""

    def result(self, yaml: str) -> JsonObject:
        """Run the check on a frontmatter; fail the test unless it exits 0."""
        code, result = run_check(CHECK, skill(yaml))
        self.assertEqual(code, 0)
        return result

    def test_comment_truncates(self) -> None:
        """` #` ends the plain value there."""
        result = self.result("description: Run it # carefully")
        self.assertEqual(rules(result), [("comment-truncates", 2)])
        findings = result.get("findings")
        first = findings[0] if is_list(findings) and findings else None
        if not isinstance(first, JsonObject):
            self.fail(f"expected a finding, got {result!r}")
        self.assertEqual(first.get("surfaces"), ["open-spec", "upload"])
        self.assertEqual(first.get("basis"), "inference")
        self.assertEqual(first.get("field"), "description")

    def test_reads_as_collection(self) -> None:
        """A text field written as a flow sequence."""
        self.assertEqual(rules(self.result("argument-hint: [file]")), [("reads-as-collection", 2)])

    def test_reads_as_boolean(self) -> None:
        """`yes` as a name."""
        self.assertEqual(rules(self.result("name: yes")), [("reads-as-boolean", 2)])

    def test_reads_as_null(self) -> None:
        """`~` as a description."""
        self.assertEqual(rules(self.result("description: ~")), [("reads-as-null", 2)])

    def test_leading_indicator(self) -> None:
        """A plain value starting with `-`."""
        self.assertEqual(rules(self.result("compatibility: -x")), [("leading-indicator", 2)])

    def first(self, yaml: str) -> JsonObject:
        """The first finding of a run."""
        findings = self.result(yaml).get("findings")
        first = findings[0] if is_list(findings) and findings else None
        if not isinstance(first, JsonObject):
            self.fail(f"expected a finding for {yaml!r}")
        return first

    def test_plain_values_cc_field_surface(self) -> None:
        """A Claude Code field outside the specification concerns Claude Code only."""
        self.assertEqual(self.first("argument-hint: [file]").get("surfaces"), ["claude-code"])

    def test_leading_dash_is_convention(self) -> None:
        """YAML 1.2 and PyYAML read `-x` as text, so quoting it is a convention."""
        self.assertEqual(self.first("compatibility: -x").get("basis"), "convention")

    def test_quoted_value_is_fine(self) -> None:
        """A quoted `yes` is text."""
        self.assertEqual(rules(self.result('description: "yes"')), [])

    def test_metadata_at_any_depth(self) -> None:
        """A metadata value read as a boolean, on its own line."""
        self.assertEqual(rules(self.result("metadata:\n  flag: on")), [("reads-as-boolean", 3)])

    def test_boolean_field_is_fine(self) -> None:
        """A boolean field may hold a boolean form."""
        self.assertEqual(rules(self.result("user-invocable: no")), [])

    def test_anchor_alias_tag(self) -> None:
        """An anchor on a text field."""
        self.assertEqual(rules(self.result("description: &d text")), [("anchor-alias-tag", 2)])

    def test_colon_cases_go_to_the_yaml_check(self) -> None:
        """Data says where `: ` inside a value is reported."""
        result = self.result("name: demo")
        self.assertEqual(result.get("data"), {"colon_cases": "reported by frontmatter.yaml"})

    def test_syntax_error_skips_the_check(self) -> None:
        """A failed strict-YAML check leaves this check not run."""
        result = self.result("name: a\nname: b")
        self.assertEqual(
            (result.get("status"), result.get("reason")), ("not_run", "frontmatter.yaml failed")
        )


if __name__ == "__main__":
    _ = unittest.main()
