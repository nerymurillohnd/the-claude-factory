#!/usr/bin/env python3
"""Tests for frontmatter.keys: keys Claude Code ignores, keys uploads reject, BOM and CRLF.

Claude Code ignores a field it doesn't recognize without an error, so a misspelled or borrowed
key silently does nothing; uploads accept only the six Agent Skills fields and fail a file that
starts with a byte-order mark or ends its lines with CRLF.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, run_check

CHECK = "frontmatter.keys"


class KeysTest(unittest.TestCase):
    """Each rule, its suggestion and its surfaces."""

    def result(self, skill_md: str | bytes) -> JsonObject:
        """Run the check; fail the test unless it exits 0."""
        code, result = run_check(CHECK, skill_md)
        self.assertEqual(code, 0)
        return result

    def findings(self, skill_md: str | bytes) -> list[JsonObject]:
        """The findings of a run, in order."""
        found = self.result(skill_md).get("findings")
        items: list[object] = found if is_list(found) else []
        return [item for item in items if isinstance(item, JsonObject)]

    def by_rule(self, skill_md: str | bytes, rule: str) -> list[JsonObject]:
        """The findings of one rule."""
        return [item for item in self.findings(skill_md) if item.get("rule") == rule]

    def test_unknown_key_alias(self) -> None:
        """`tools` is the subagent field; a skill's is `allowed-tools`, never `hooks`."""
        skill = "---\nname: demo-skill\ndescription: Does a thing.\ntools: Read\n---\nBody.\n"
        unknown = self.by_rule(skill, "unknown-key")
        self.assertEqual(len(unknown), 1)
        first = unknown[0]
        self.assertEqual(
            (first.get("found"), first.get("line"), first.get("surfaces")),
            ("tools", 4, ["claude-code"]),
        )
        expected = str(first.get("expected"))
        self.assertIn("`allowed-tools`", expected)
        self.assertNotIn("hooks", expected)

    def test_unknown_key_typo(self) -> None:
        """A misspelled field gets the field within two edits."""
        skill = "---\nname: demo-skill\ndesciption: Does a thing.\n---\nBody.\n"
        unknown = self.by_rule(skill, "unknown-key")
        self.assertEqual([item.get("found") for item in unknown], ["desciption"])
        self.assertIn("`description`", str(unknown[0].get("expected")))

    def test_non_spec_key(self) -> None:
        """A Claude Code field outside the specification is an upload and open-spec finding."""
        skill = "---\nname: demo-skill\ndescription: Does a thing.\nargument-hint: x\n---\nB.\n"
        found = self.findings(skill)
        self.assertEqual(
            [(item.get("rule"), item.get("found"), item.get("surfaces")) for item in found],
            [("non-spec-key", "argument-hint", ["open-spec", "upload"])],
        )

    def test_bom_crlf(self) -> None:
        """A byte-order mark and CRLF line ends: one upload finding each."""
        skill = (
            b"\xef\xbb\xbf---\r\nname: demo-skill\r\ndescription: Does a thing.\r\n---\r\nB.\r\n"
        )
        found = self.findings(skill)
        self.assertEqual(
            sorted((str(item.get("rule")), str(item.get("surfaces"))) for item in found),
            [("bom", "['upload']"), ("crlf", "['upload']")],
        )

    def test_clean_skill(self) -> None:
        """Only specification fields, UTF-8 without a BOM, LF line ends."""
        self.assertEqual(
            self.findings("---\nname: demo-skill\ndescription: Does it.\n---\nB.\n"), []
        )


if __name__ == "__main__":
    _ = unittest.main()
