#!/usr/bin/env python3
"""Tests for the strict YAML check, frontmatter.yaml, run through frontmatter-checks.py.

It reports the strict-YAML failures claude plugin validate passes, and the bytes that aren't
UTF-8; what validate already reports gives `not_run` with the reason to read validate instead.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, rules, run_check

CHECK = "frontmatter.yaml"
VALIDATE_REASON = "the frontmatter has an error claude plugin validate reports"
NO_BLOCK_REASON = "no frontmatter block: claude plugin validate reports it"


def skill(yaml: str) -> str:
    """A SKILL.md whose frontmatter holds yaml, starting on file line 2."""
    return f"---\n{yaml}\n---\nBody.\n"


class YamlCheckTest(unittest.TestCase):
    """The four strict-YAML failures, the not-run cases and not-utf8."""

    def result(self, content: str | bytes) -> JsonObject:
        """Run the check on content; fail the test unless it exits 0."""
        code, result = run_check(CHECK, content)
        self.assertEqual(code, 0)
        return result

    def first_finding(self, result: JsonObject) -> JsonObject:
        """The result's first finding, failing the test when it has none."""
        findings = result.get("findings")
        if not is_list(findings) or not findings or not isinstance(findings[0], JsonObject):
            self.fail(f"expected a finding, got {result!r}")
        return findings[0]

    def test_duplicate_key(self) -> None:
        """A key twice is reported on its second line, as an inference."""
        result = self.result(skill("name: a\nname: b"))
        self.assertEqual(rules(result), [("duplicate-key", 3)])
        finding = self.first_finding(result)
        self.assertEqual(finding.get("basis"), "inference")
        self.assertEqual(finding.get("surfaces"), ["open-spec", "upload"])
        self.assertEqual(finding.get("field"), "name")

    def test_colon_in_value(self) -> None:
        """`: ` inside a plain value, with the official basis and the tested condition."""
        result = self.result(skill("description: Use when: x"))
        self.assertEqual(rules(result), [("colon-in-value", 2)])
        finding = self.first_finding(result)
        self.assertEqual(finding.get("basis"), "official")
        self.assertEqual(
            finding.get("condition"),
            "Claude Code accepted it when tested; packaging and upload reject it",
        )

    def test_trailing_colon(self) -> None:
        """A plain value ending with `:` is a colon in a value too."""
        self.assertEqual(rules(self.result(skill("description: a:"))), [("colon-in-value", 2)])

    def test_unclosed_flow(self) -> None:
        """An unclosed bracket, at the line it opens on."""
        self.assertEqual(rules(self.result(skill("t: [Read"))), [("unclosed-flow", 2)])

    def test_key_under_scalar(self) -> None:
        """A key indented under a scalar value."""
        result = self.result(skill("name: a\n  b: c"))
        self.assertEqual(rules(result), [("key-under-scalar", 3)])

    def test_validate_reports_quotes_and_tabs(self) -> None:
        """An unclosed quote and a tab in the indentation are left to validate."""
        for yaml in ('d: "abc', "m:\n\tk: v"):
            with self.subTest(yaml=yaml):
                result = self.result(skill(yaml))
                self.assertEqual(
                    (result.get("status"), result.get("reason")), ("not_run", VALIDATE_REASON)
                )

    def test_no_block_or_not_a_mapping(self) -> None:
        """A list as the root, and a file whose first line isn't the marker, are not run."""
        for content in (skill("- a"), "\n---\nname: a\n---\n"):
            with self.subTest(content=content):
                result = self.result(content)
                self.assertEqual(
                    (result.get("status"), result.get("reason")), ("not_run", NO_BLOCK_REASON)
                )

    def test_latin1(self) -> None:
        """A Latin-1 byte gives not-utf8 at its line and column."""
        result = self.result(b"---\nname: caf\xe9\n---\n")
        self.assertEqual(rules(result), [("not-utf8", 2)])
        finding = self.first_finding(result)
        self.assertEqual((finding.get("column"), finding.get("found")), (10, "0xE9"))

    def test_utf16(self) -> None:
        """A UTF-16 file gives not-utf8 at line 1, with no traceback."""
        result = self.result("---\nname: a\n---\n".encode("utf-16"))
        self.assertEqual(rules(result), [("not-utf8", 1)])

    def test_valid_block(self) -> None:
        """A valid block has no findings, and data gives the closing line."""
        result = self.result(skill("name: demo\ndescription: Does a thing."))
        self.assertEqual((result.get("status"), rules(result)), ("ran", []))
        self.assertEqual(result.get("data"), {"close_line": 4})


if __name__ == "__main__":
    _ = unittest.main()
