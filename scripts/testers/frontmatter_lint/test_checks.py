#!/usr/bin/env python3
"""Tests for the frontmatter value rules of frontmatter-lint."""

from __future__ import annotations

import unittest

from validators.frontmatter_lint.checks import check_text


def _rules(text: str) -> list[tuple[str, int]]:
    """Return each finding as (rule, line)."""
    return [(finding.rule, finding.line) for finding in check_text(text)]


class ValueRulesTest(unittest.TestCase):
    """FM-01 parse, FM-02 colon in a value, FM-03 quoted value."""

    def test_plain_values_pass(self) -> None:
        """Plain values with no colon and no quotes give no finding."""
        text = "---\nname: demo\ndescription: Does one thing, then another.\n---\nbody\n"
        self.assertEqual(_rules(text), [])

    def test_colon_space_does_not_parse(self) -> None:
        """A value with ': ' fails strict YAML and is reported as FM-01 on its line."""
        text = "---\nname: demo\ndescription: In its clone: validates\n---\n"
        self.assertEqual(_rules(text), [("FM-01", 3)])

    def test_colon_without_space_is_flagged(self) -> None:
        """A value holding a colon with no space after it parses, and is FM-02."""
        text = "---\nname: demo\ndescription: See step:2 first\n---\n"
        self.assertEqual(_rules(text), [("FM-02", 3)])

    def test_double_and_single_quotes_are_flagged(self) -> None:
        """A quoted value is FM-03, whatever it holds."""
        text = "---\nname: demo\ndescription: \"Quoted\"\nargument-hint: '[path]'\n---\n"
        self.assertEqual(_rules(text), [("FM-03", 3), ("FM-03", 4)])

    def test_quoted_value_with_colon_reports_both(self) -> None:
        """A quoted value that holds a colon is FM-02 and FM-03."""
        text = '---\nname: demo\ndescription: "Use when: asked"\n---\n'
        self.assertEqual(sorted(_rules(text)), [("FM-02", 3), ("FM-03", 3)])

    def test_nested_values_are_checked(self) -> None:
        """Values inside maps, lists and block scalars are checked with their own line."""
        text = (
            "---\nname: demo\nhooks:\n  Stop:\n    - hooks:\n        - type: agent\n"
            "          prompt: |\n            Check this: then that.\n---\n"
        )
        self.assertEqual(_rules(text), [("FM-02", 7)])

    def test_plugin_skill_identifiers_are_allowed(self) -> None:
        """A <plugin>:<skill> item of the skills list keeps its colon."""
        text = "---\nname: demo\nskills:\n  - svelte-development:svelte-best-practices\n---\n"
        self.assertEqual(_rules(text), [])

    def test_identifier_form_elsewhere_is_flagged(self) -> None:
        """The identifier form is allowed only in the skills list."""
        text = "---\nname: demo\ntools:\n  - svelte-development:svelte-best-practices\n---\n"
        self.assertEqual(_rules(text), [("FM-02", 4)])

    def test_prose_in_skills_list_is_flagged(self) -> None:
        """A skills item that is not a bare identifier is not exempt."""
        text = "---\nname: demo\nskills:\n  - see this:now\n---\n"
        self.assertEqual(_rules(text), [("FM-02", 4)])

    def test_no_frontmatter_gives_no_finding(self) -> None:
        """A file that doesn't open with --- is left to the other validators."""
        self.assertEqual(_rules("# Title\n\nname: x\n"), [])

    def test_unclosed_frontmatter_is_fm01(self) -> None:
        """An opening fence with no closing fence is FM-01 on line 1."""
        self.assertEqual(_rules("---\nname: demo\n"), [("FM-01", 1)])

    def test_crlf_and_bom_are_tolerated(self) -> None:
        """A BOM and CRLF line endings don't create findings."""
        text = "﻿---\r\nname: demo\r\ndescription: Plain\r\n---\r\n"
        self.assertEqual(_rules(text), [])

    def test_non_string_values_pass(self) -> None:
        """Booleans and numbers are not text and are not checked."""
        text = "---\nname: demo\ndisable-model-invocation: true\nmaxTurns: 3\n---\n"
        self.assertEqual(_rules(text), [])


if __name__ == "__main__":
    _ = unittest.main()
