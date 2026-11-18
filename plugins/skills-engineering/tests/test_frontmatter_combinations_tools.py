#!/usr/bin/env python3
"""Tests for frontmatter.field-combinations and frontmatter.allowed-tools.

frontmatter.field-combinations finds fields that cancel each other; frontmatter.allowed-tools
splits the pre-approved tools into entries and flags the list form and an unscoped Bash.
"""

import unittest

from frontmatter_helpers import JsonObject, is_list, rules, run_check

COMBINATIONS = "frontmatter.field-combinations"
ALLOWED_TOOLS = "frontmatter.allowed-tools"


def skill(yaml: str) -> str:
    """A SKILL.md named demo-skill whose frontmatter also holds yaml, from file line 4."""
    return f"---\nname: demo-skill\ndescription: Does a thing.\n{yaml}\n---\nBody.\n"


class CombinationTestCase(unittest.TestCase):
    """Helpers shared by these tests."""

    def result(self, check: str, yaml: str) -> JsonObject:
        """Run one check; fail the test unless it exits 0."""
        code, result = run_check(check, skill(yaml))
        self.assertEqual(code, 0)
        return result

    def rule_names(self, check: str, yaml: str) -> list[str]:
        """The rules of a result's findings, in order."""
        return [rule for rule, _line in rules(self.result(check, yaml))]

    def findings(self, check: str, yaml: str) -> list[JsonObject]:
        """A result's findings."""
        found = self.result(check, yaml).get("findings")
        if not is_list(found):
            self.fail(f"expected findings, got {found!r}")
        return [item for item in found if isinstance(item, JsonObject)]

    def data(self, check: str, yaml: str) -> JsonObject:
        """A result's data object."""
        data = self.result(check, yaml).get("data")
        if not isinstance(data, JsonObject):
            self.fail(f"expected data, got {data!r}")
        return data


class FieldCombinationsTest(CombinationTestCase):
    """frontmatter.field-combinations."""

    def test_uninvocable(self) -> None:
        """Neither Claude nor the user can invoke the skill."""
        yaml = "disable-model-invocation: true\nuser-invocable: false"
        found = self.findings(COMBINATIONS, yaml)
        self.assertEqual(
            [(f.get("rule"), f.get("basis"), f.get("surfaces")) for f in found],
            [("uninvocable", "inference", ["claude-code"])],
        )

    def test_paths_ignored(self) -> None:
        """`paths` does nothing when Claude can't invoke the skill."""
        yaml = 'paths: "*.py"\ndisable-model-invocation: yes'
        self.assertEqual(self.rule_names(COMBINATIONS, yaml), ["paths-ignored"])

    def test_agent_without_fork(self) -> None:
        """`agent` applies only with `context: fork`."""
        found = self.findings(COMBINATIONS, "agent: Explore")
        self.assertEqual(
            [(f.get("rule"), f.get("basis"), f.get("field")) for f in found],
            [("fork-only-field", "official", "agent")],
        )

    def test_agent_with_fork(self) -> None:
        """With `context: fork`, `agent` applies."""
        self.assertEqual(self.rule_names(COMBINATIONS, "agent: Explore\ncontext: fork"), [])

    def test_background_with_fork(self) -> None:
        """`background: false` with a fork."""
        self.assertEqual(self.rule_names(COMBINATIONS, "background: false\ncontext: fork"), [])

    def test_background_without_fork(self) -> None:
        """`background` without a fork, even false, does nothing."""
        self.assertEqual(self.rule_names(COMBINATIONS, "background: false"), ["fork-only-field"])

    def test_invocable_combinations(self) -> None:
        """Only one of the two switches off gives nothing."""
        for yaml in ("disable-model-invocation: true", "user-invocable: no\npaths: x"):
            with self.subTest(yaml=yaml):
                self.assertEqual(self.rule_names(COMBINATIONS, yaml), [])


class AllowedToolsTest(CombinationTestCase):
    """frontmatter.allowed-tools."""

    def test_list_form(self) -> None:
        """A YAML list is outside the open specification's string form."""
        found = self.findings(ALLOWED_TOOLS, "allowed-tools: [Read, Grep]")
        self.assertEqual(
            [(f.get("rule"), f.get("surfaces"), f.get("basis"), f.get("condition")) for f in found],
            [
                (
                    "list-form",
                    ["open-spec", "upload"],
                    "official",
                    "for a skill meant to work outside Claude Code",
                )
            ],
        )
        self.assertEqual(
            self.data(ALLOWED_TOOLS, "allowed-tools: [Read, Grep]").get("entries"),
            ["Read", "Grep"],
        )

    def test_bare_bash(self) -> None:
        """`Bash` approves every command."""
        found = self.findings(ALLOWED_TOOLS, "allowed-tools: Bash")
        self.assertEqual(
            [(f.get("rule"), f.get("surfaces"), f.get("basis")) for f in found],
            [("unscoped-bash", ["claude-code"], "official")],
        )

    def test_scoped_entries(self) -> None:
        """A space inside parentheses doesn't split an entry."""
        yaml = "allowed-tools: Read Bash(git diff:*)"
        self.assertEqual(self.rule_names(ALLOWED_TOOLS, yaml), [])
        self.assertEqual(
            self.data(ALLOWED_TOOLS, yaml).get("entries"), ["Read", "Bash(git diff:*)"]
        )

    def test_comma_separated_wildcard(self) -> None:
        """`Bash(*)` after a comma."""
        self.assertEqual(
            self.rule_names(ALLOWED_TOOLS, 'allowed-tools: "Read, Bash(*)"'), ["unscoped-bash"]
        )

    def test_empty_prefix_wildcard(self) -> None:
        """`Bash( :* )` with its spaces removed is `Bash(:*)`, an inference."""
        found = self.findings(ALLOWED_TOOLS, 'allowed-tools: "Bash( :* )"')
        self.assertEqual(
            [(f.get("rule"), f.get("basis")) for f in found], [("unscoped-bash", "inference")]
        )

    def test_unbalanced_parentheses(self) -> None:
        """An unclosed parenthesis is reported in data, not as a crash."""
        yaml = 'allowed-tools: "Bash(git"'
        self.assertEqual(self.rule_names(ALLOWED_TOOLS, yaml), [])
        data = self.data(ALLOWED_TOOLS, yaml)
        self.assertEqual((data.get("unparsed_entries"), data.get("entries")), (["Bash(git"], []))

    def test_stray_closing_parenthesis(self) -> None:
        """A `)` with no `(` makes its entry unparsed."""
        data = self.data(ALLOWED_TOOLS, "allowed-tools: Read) Grep")
        self.assertEqual((data.get("unparsed_entries"), data.get("entries")), (["Read)"], ["Grep"]))

    def test_absent(self) -> None:
        """No allowed-tools."""
        self.assertEqual(self.rule_names(ALLOWED_TOOLS, "license: MIT"), [])


if __name__ == "__main__":
    _ = unittest.main()
