#!/usr/bin/env python3
"""Tests for frontmatter.metadata and frontmatter.field-values, run through skill-checks.py.

frontmatter.metadata checks that `metadata` is a map of strings whose keys aren't field names;
frontmatter.field-values checks the values Claude Code documents for its other fields.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, rules, run_check

METADATA = "frontmatter.metadata"
FIELD_VALUES = "frontmatter.field-values"


def skill(yaml: str) -> str:
    """A SKILL.md named demo-skill whose frontmatter also holds yaml, from file line 4."""
    return f"---\nname: demo-skill\ndescription: Does a thing.\n{yaml}\n---\nBody.\n"


class FieldTestCase(unittest.TestCase):
    """Helpers shared by these tests."""

    def result(self, check: str, yaml: str) -> JsonObject:
        """Run one check; fail the test unless it exits 0."""
        code, result = run_check(check, skill(yaml))
        self.assertEqual(code, 0)
        return result

    def rule_names(self, check: str, yaml: str) -> list[str]:
        """The rules of a result's findings, in order."""
        return [rule for rule, _line in rules(self.result(check, yaml))]

    def first_finding(self, check: str, yaml: str) -> JsonObject:
        """The first finding of a result."""
        result = self.result(check, yaml)
        findings = result.get("findings")
        first = findings[0] if is_list(findings) and findings else None
        if not isinstance(first, JsonObject):
            self.fail(f"expected a finding, got {result!r}")
        return first

    def data(self, check: str, yaml: str) -> JsonObject:
        """A result's data object."""
        result = self.result(check, yaml)
        data = result.get("data")
        if not isinstance(data, JsonObject):
            self.fail(f"expected data, got {result!r}")
        return data


class MetadataTest(FieldTestCase):
    """frontmatter.metadata."""

    def test_absent(self) -> None:
        """No metadata is fine."""
        self.assertEqual(self.rule_names(METADATA, "license: MIT"), [])

    def test_number_value(self) -> None:
        """`{a: 1}` holds an integer, not a string."""
        self.assertEqual(self.rule_names(METADATA, "metadata: {a: 1}"), ["non-string-value"])

    def test_not_a_map(self) -> None:
        """A scalar isn't a map, on every surface."""
        finding = self.first_finding(METADATA, "metadata: x")
        self.assertEqual(
            (finding.get("rule"), finding.get("surfaces")),
            ("not-a-map", ["claude-code", "open-spec", "upload"]),
        )

    def test_reused_field_name(self) -> None:
        """A key named like a frontmatter field."""
        finding = self.first_finding(METADATA, "metadata:\n  paths: x")
        self.assertEqual(
            (finding.get("rule"), finding.get("surfaces"), finding.get("basis")),
            ("reused-field-name", ["claude-code"], "official"),
        )

    def test_quoted_version_is_a_string(self) -> None:
        """`"1.0"` stays text and `1.0` reads as a float."""
        self.assertEqual(self.rule_names(METADATA, 'metadata:\n  version: "1.0"'), [])
        self.assertEqual(
            self.rule_names(METADATA, "metadata:\n  version: 1.0"), ["non-string-value"]
        )

    def test_non_string_key(self) -> None:
        """YAML 1.1 reads the key `yes` as a boolean."""
        self.assertEqual(self.rule_names(METADATA, "metadata:\n  yes: a"), ["non-string-key"])

    def test_nested_map_value(self) -> None:
        """A map isn't a string value."""
        self.assertEqual(
            self.rule_names(METADATA, "metadata:\n  a:\n    b: c"), ["non-string-value"]
        )

    def test_null_value(self) -> None:
        """An empty value reads as null."""
        self.assertEqual(self.rule_names(METADATA, "metadata:\n  a:"), ["non-string-value"])

    def test_upload_metadata_y_n_1e3(self) -> None:
        """PyYAML, which uploads load with, reads `y`, `n` and `1e3` as strings."""
        self.assertEqual(self.rule_names(METADATA, "metadata: {flag: y, other: n, v: 1e3}"), [])

    def test_scalar_type_findings_are_upload_only(self) -> None:
        """The open-spec validator reads every scalar as a string; only uploads type them."""
        finding = self.first_finding(METADATA, "metadata: {a: 1}")
        self.assertEqual(
            (finding.get("rule"), finding.get("surfaces")), ("non-string-value", ["upload"])
        )


class FieldValuesTest(FieldTestCase):
    """frontmatter.field-values."""

    def test_boolean_outside_the_forms(self) -> None:
        """`maybe` isn't a boolean form."""
        finding = self.first_finding(FIELD_VALUES, "user-invocable: maybe")
        self.assertEqual(
            (finding.get("rule"), finding.get("basis"), finding.get("surfaces")),
            ("boolean-form", "official", ["claude-code"]),
        )

    def test_boolean_forms_any_case(self) -> None:
        """`NO`, `On` and `1` are boolean forms."""
        for value in ("NO", "On", "1"):
            with self.subTest(value=value):
                self.assertEqual(self.rule_names(FIELD_VALUES, f"user-invocable: {value}"), [])

    def test_quoted_boolean(self) -> None:
        """A quoted boolean is an inference, with its condition."""
        finding = self.first_finding(FIELD_VALUES, 'background: "true"')
        self.assertEqual(
            (finding.get("rule"), finding.get("basis"), finding.get("condition")),
            (
                "boolean-form",
                "inference",
                "quoted: unverified whether Claude Code reads it as a boolean",
            ),
        )

    def test_effort(self) -> None:
        """`turbo` isn't an effort level; `xhigh` is."""
        self.assertEqual(self.rule_names(FIELD_VALUES, "effort: turbo"), ["effort-value"])
        self.assertEqual(self.rule_names(FIELD_VALUES, "effort: xhigh"), [])

    def test_context(self) -> None:
        """Only `fork`."""
        self.assertEqual(self.rule_names(FIELD_VALUES, "context: spoon"), ["context-value"])
        self.assertEqual(self.rule_names(FIELD_VALUES, "context: fork"), [])

    def test_left_to_validate(self) -> None:
        """A non-string allowed-tools and an unknown shell are validate's."""
        self.assertEqual(self.rule_names(FIELD_VALUES, "allowed-tools: 42"), [])
        self.assertEqual(self.rule_names(FIELD_VALUES, "shell: fish"), [])

    def test_model_outside_the_values(self) -> None:
        """`gpt-4` is an inference finding."""
        finding = self.first_finding(FIELD_VALUES, "model: gpt-4")
        self.assertEqual((finding.get("rule"), finding.get("basis")), ("model-value", "inference"))

    def test_model_alias(self) -> None:
        """`opus[1m]` is an alias /model accepts."""
        self.assertEqual(self.rule_names(FIELD_VALUES, "model: opus[1m]"), [])
        data = self.data(FIELD_VALUES, "model: opus[1m]")
        self.assertEqual((data.get("model_id_unchecked"),), (False,))

    def test_model_id(self) -> None:
        """A full model id passes by its form, unchecked."""
        for model in ("claude-opus-5-5", "us.anthropic.claude-opus-5-5", "arn:aws:bedrock:x"):
            with self.subTest(model=model):
                self.assertEqual(self.rule_names(FIELD_VALUES, f"model: {model}"), [])
                data = self.data(FIELD_VALUES, f"model: {model}")
                self.assertEqual((data.get("model_id_unchecked"),), (True,))

    def test_string_or_list(self) -> None:
        """`[a, 1]` holds an integer; a string and a list of strings pass."""
        self.assertEqual(self.rule_names(FIELD_VALUES, "paths: [a, 1]"), ["string-or-list"])
        self.assertEqual(self.rule_names(FIELD_VALUES, 'paths: "src/**"'), [])
        self.assertEqual(self.rule_names(FIELD_VALUES, "disallowed-tools: [Bash, Write]"), [])
        self.assertEqual(self.rule_names(FIELD_VALUES, "arguments: {a: b}"), ["string-or-list"])

    def test_empty_value(self) -> None:
        """A field present with no value."""
        self.assertEqual(self.rule_names(FIELD_VALUES, "effort:"), ["empty-value"])
        self.assertEqual(self.rule_names(FIELD_VALUES, "user-invocable: ~"), ["empty-value"])

    def test_valid_set(self) -> None:
        """Every documented value together gives nothing."""
        yaml = (
            "disable-model-invocation: true\nuser-invocable: false\nbackground: yes\n"
            "context: fork\neffort: low\nmodel: inherit\npaths:\n  - 'src/**'\n"
            "arguments: name"
        )
        self.assertEqual(self.rule_names(FIELD_VALUES, yaml), [])


if __name__ == "__main__":
    _ = unittest.main()
