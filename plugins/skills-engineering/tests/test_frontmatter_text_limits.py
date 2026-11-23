#!/usr/bin/env python3
"""Tests for frontmatter.description, frontmatter.listing-cap and frontmatter.compatibility.

Every length is in code points, with the UTF-16 length beside it in `data`. The listing cap
joins `description` and `when_to_use` with " - ", the separator Claude Code's listing shows.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, rules, run_check

DESCRIPTION = "frontmatter.description"
LISTING_CAP = "frontmatter.listing-cap"
COMPATIBILITY = "frontmatter.compatibility"
EMOJI = "\N{GRINNING FACE}"


def skill(yaml: str) -> str:
    """A SKILL.md named demo-skill whose frontmatter also holds yaml."""
    return f"---\nname: demo-skill\n{yaml}\n---\nBody.\n"


class TextLimitTestCase(unittest.TestCase):
    """Helpers shared by these tests."""

    def result(self, check: str, yaml: str, args: tuple[str, ...] = ()) -> JsonObject:
        """Run one check; fail the test unless it exits 0."""
        code, result = run_check(check, skill(yaml), args=args)
        self.assertEqual(code, 0)
        return result

    def data(self, result: JsonObject) -> JsonObject:
        """A result's data object."""
        data = result.get("data")
        if not isinstance(data, JsonObject):
            self.fail(f"expected data, got {result!r}")
        return data

    def rule_names(self, check: str, yaml: str) -> list[str]:
        """The rules of a result's findings, in order."""
        return [rule for rule, _line in rules(self.result(check, yaml))]

    def found(self, check: str, yaml: str) -> list[tuple[str, str, list[object]]]:
        """Each finding's (rule, field, surfaces), in order."""
        findings = self.result(check, yaml).get("findings")
        items: list[object] = findings if is_list(findings) else []
        out: list[tuple[str, str, list[object]]] = []
        for item in items:
            if isinstance(item, JsonObject):
                surfaces = item.get("surfaces")
                listed: list[object] = surfaces if is_list(surfaces) else []
                out.append((str(item.get("rule")), str(item.get("field")), listed))
        return out


class DescriptionTest(TextLimitTestCase):
    """frontmatter.description."""

    def test_length_limit(self) -> None:
        """1,024 characters pass and 1,025 are too long."""
        self.assertEqual(self.rule_names(DESCRIPTION, f"description: {'a' * 1024}"), [])
        self.assertEqual(self.rule_names(DESCRIPTION, f"description: {'a' * 1025}"), ["too-long"])

    def test_xml_tag(self) -> None:
        """An XML tag is an angle bracket, and data lists the tag."""
        result = self.result(DESCRIPTION, "description: Use <tag> here.")
        self.assertEqual(rules(result), [("angle-bracket", 3)])
        self.assertEqual(self.data(result).get("xml_tags"), ["<tag>"])

    def test_greater_than(self) -> None:
        """A lone `>` is an angle bracket too."""
        self.assertEqual(self.rule_names(DESCRIPTION, "description: a > b"), ["angle-bracket"])

    def test_missing(self) -> None:
        """No description: Claude Code falls back to the body's first non-empty line."""
        result = self.result(DESCRIPTION, "license: MIT")
        self.assertEqual(rules(result), [("missing", None)])
        self.assertEqual(self.data(result).get("claude_code_fallback"), "first non-empty body line")

    def test_not_a_string(self) -> None:
        """A number isn't a description."""
        self.assertEqual(self.rule_names(DESCRIPTION, "description: 5"), ["not-a-string"])

    def test_not_a_string_surfaces(self) -> None:
        """A scalar of another type fails uploads only: the open-spec validator reads it as text.

        A list is no text on either surface.
        """
        self.assertEqual(
            self.found(DESCRIPTION, "description: 5"), [("not-a-string", "description", ["upload"])]
        )
        self.assertEqual(
            self.found(DESCRIPTION, "description: [a]"),
            [("not-a-string", "description", ["open-spec", "upload"])],
        )

    def test_yaml11_only_boolean_is_text(self) -> None:
        """`n` and `1e3` are text to PyYAML, which uploads load with."""
        self.assertEqual(self.rule_names(DESCRIPTION, "description: n"), [])
        self.assertEqual(self.rule_names(DESCRIPTION, "description: 1e3"), [])

    def test_when_to_use_angle_brackets_without_description(self) -> None:
        """With no description, `<` in when_to_use is still reported; findings sort by position."""
        self.assertEqual(
            self.found(DESCRIPTION, "when_to_use: Use for <branch> work"),
            [
                ("angle-bracket", "when_to_use", ["claude-code"]),
                ("missing", "description", ["open-spec", "upload"]),
            ],
        )

    def test_empty(self) -> None:
        """Blanks only."""
        self.assertEqual(self.rule_names(DESCRIPTION, 'description: "  "'), ["empty"])

    def test_emoji_are_one_character_each(self) -> None:
        """1,000 emoji are 1,000 characters and 2,000 UTF-16 units."""
        result = self.result(DESCRIPTION, f"description: {EMOJI * 1000}")
        self.assertEqual(rules(result), [])
        data = self.data(result)
        self.assertEqual((data.get("length"), data.get("utf16_length")), (1000, 2000))

    def test_when_to_use_angle_brackets(self) -> None:
        """Claude Code escapes `<` and `>` in when_to_use too; uploads don't read the field."""
        yaml = "description: Use for branch work.\nwhen_to_use: Use for <branch> work"
        self.assertEqual(
            self.found(DESCRIPTION, yaml), [("angle-bracket", "when_to_use", ["claude-code"])]
        )

    def test_block_scalar_description_1024(self) -> None:
        """1,024 characters plus a block scalar's newline: too long raw, within the upload limit.

        The open-spec validator counts the raw value; the upload validator strips it first.
        """
        yaml = f"description: |\n  {'a' * 1024}"
        self.assertEqual(
            self.found(DESCRIPTION, yaml), [("too-long", "description", ["open-spec"])]
        )

    def test_block_scalar_description_1025_after_strip(self) -> None:
        """1,025 characters stay too long on both surfaces after the strip."""
        yaml = f"description: |\n  {'a' * 1025}"
        self.assertEqual(
            self.found(DESCRIPTION, yaml), [("too-long", "description", ["open-spec", "upload"])]
        )


class ListingCapTest(TextLimitTestCase):
    """frontmatter.listing-cap."""

    def test_cut_in_when_to_use(self) -> None:
        """1,000 + 3 + 600 characters: the cut falls 533 characters into when_to_use."""
        yaml = f"description: {'d' * 1000}\nwhen_to_use: {'w' * 600}"
        result = self.result(LISTING_CAP, yaml)
        self.assertEqual(rules(result), [("over-cap", 4)])
        data = self.data(result)
        self.assertEqual(
            (
                data.get("combined_length"),
                data.get("first_lost_field"),
                data.get("first_lost_offset"),
                data.get("line"),
                data.get("cap_setting"),
            ),
            (1603, "when_to_use", 533, 4, "skillListingMaxDescChars"),
        )
        self.assertEqual(data.get("around_cut"), f"{'w' * 40}|{'w' * 40}")

    def test_exactly_at_the_cap(self) -> None:
        """1,536 combined characters are all listed."""
        yaml = f"description: {'d' * 1000}\nwhen_to_use: {'w' * 533}"
        self.assertEqual(self.rule_names(LISTING_CAP, yaml), [])

    def test_cap_option(self) -> None:
        """`--cap 100` with a description of 150."""
        result = self.result(LISTING_CAP, f"description: {'d' * 150}", ("--cap", "100"))
        data = self.data(result)
        self.assertEqual(
            (data.get("cap"), data.get("first_lost_field"), data.get("first_lost_offset")),
            (100, "description", 100),
        )

    def test_description_alone(self) -> None:
        """A description of 1,600 is cut at its own character 1,536."""
        result = self.result(LISTING_CAP, f"description: {'d' * 1600}")
        data = self.data(result)
        self.assertEqual(
            (data.get("first_lost_field"), data.get("first_lost_offset"), data.get("line")),
            ("description", 1536, 3),
        )

    def test_cap_below_one_cant_run(self) -> None:
        """A cap of 0 is a usage error: exit 2."""
        code, _result = run_check(LISTING_CAP, skill("description: x"), args=("--cap", "0"))
        self.assertEqual(code, 2)

    def test_no_line_for_a_block_scalar(self) -> None:
        """The cut's line is given only for a value on one line."""
        result = self.result(LISTING_CAP, f"description: |\n  {'d' * 1600}")
        self.assertIsNone(self.data(result).get("line"))


class CompatibilityTest(TextLimitTestCase):
    """frontmatter.compatibility."""

    def test_absent(self) -> None:
        """No compatibility field is fine."""
        self.assertEqual(self.rule_names(COMPATIBILITY, "description: x"), [])

    def test_length_limit(self) -> None:
        """500 characters pass and 501 are too long."""
        self.assertEqual(self.rule_names(COMPATIBILITY, f"compatibility: {'c' * 500}"), [])
        self.assertEqual(
            self.rule_names(COMPATIBILITY, f"compatibility: {'c' * 501}"), ["too-long"]
        )

    def test_empty(self) -> None:
        """An empty string."""
        self.assertEqual(self.rule_names(COMPATIBILITY, 'compatibility: ""'), ["empty"])

    def test_not_a_string(self) -> None:
        """A number."""
        self.assertEqual(self.rule_names(COMPATIBILITY, "compatibility: 7"), ["not-a-string"])

    def test_yaml11_only_boolean_is_text(self) -> None:
        """`y` is text to PyYAML and to the open-spec validator."""
        self.assertEqual(self.rule_names(COMPATIBILITY, "compatibility: y"), [])

    def test_compatibility_raw_length(self) -> None:
        """500 characters plus a block scalar's newline: no validator strips it, on any surface."""
        yaml = f"compatibility: |\n  {'c' * 500}"
        self.assertEqual(
            self.found(COMPATIBILITY, yaml),
            [("too-long", "compatibility", ["open-spec", "upload"])],
        )


if __name__ == "__main__":
    _ = unittest.main()
