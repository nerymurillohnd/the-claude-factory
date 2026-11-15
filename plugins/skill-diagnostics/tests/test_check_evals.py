#!/usr/bin/env python3
"""Tests for skills-best-practices' scripts/check-evals.py on plugin eval suites."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, TypeGuard
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

_decode: Callable[[str], object] = json.JSONDecoder().decode

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "skills-best-practices"
    / "scripts"
    / "check-evals.py"
)

SKILL_MD = "---\nname: demo-skill\ndescription: Demo.\n---\n\nBody.\n"
SKILL_FIRED = (
    "---\ntype: tool_used\ntool: Skill\n"
    'input_match: \'"skill"\\s*:\\s*"(?:[\\w-]+:)?demo-skill"\'\n---\n'
)
MUST_NOT_FIRE = (
    "---\ntype: tool_used\ntool: Skill\n"
    'input_match: \'"skill"\\s*:\\s*"(?:[\\w-]+:)?demo-skill"\'\nmin: 0\nmax: 0\n---\n'
)

CASE_YAML = """schema_version: "1.1"
name: inline
execution:
  prompt: Do it.
graders:
  - name: inline-grader
    {grader}
"""


class Plugin:
    """A throwaway plugin with one skill and an eval suite."""

    def __init__(self, base: Path, *, root_manifest: bool = False) -> None:
        """Write the manifest, at the root or in .claude-plugin/, and the skill."""
        self.root: Path = base / "demo-plugin"
        manifest = (
            self.root / "plugin.json"
            if root_manifest
            else self.root / ".claude-plugin" / "plugin.json"
        )
        manifest.parent.mkdir(parents=True, exist_ok=True)
        _ = manifest.write_text('{"name": "demo-plugin"}\n', encoding="utf-8")
        self.skill: Path = self.root / "skills" / "demo-skill"
        self.skill.mkdir(parents=True)
        _ = (self.skill / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")

    def write(self, relative: str, text: str) -> None:
        """Write a file below the plugin root."""
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")

    def case(self, name: str, graders: dict[str, str]) -> None:
        """Write a case with a prompt and the given grader files."""
        self.write(f"evals/{name}/prompt.md", "Do the demo task.\n")
        for grader, text in graders.items():
            self.write(f"evals/{name}/graders/{grader}.md", text)

    def run(self) -> dict[str, object]:
        """Run the script on the skill and return its JSON result."""
        done = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), str(self.skill)],
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode != 0:
            message = f"exit {done.returncode}: {done.stderr}"
            raise AssertionError(message)
        return as_object(_decode(done.stdout))


def is_object(value: object) -> TypeGuard[dict[str, object]]:
    """Whether a decoded JSON value is an object, whose keys are always strings."""
    return isinstance(value, dict)


def is_array(value: object) -> TypeGuard[list[object]]:
    """Whether a decoded JSON value is an array."""
    return isinstance(value, list)


def as_object(value: object) -> dict[str, object]:
    """A decoded JSON object; any other value fails the test."""
    if not is_object(value):
        message = f"expected a JSON object, got {value!r}"
        raise TypeError(message)
    return value


def evals_of(result: dict[str, object]) -> dict[str, object]:
    """The result's evals object."""
    return as_object(result["evals"])


def failures(result: dict[str, object], check: str) -> list[str]:
    """The locations of the failed results of one check."""
    entries = result["checks"]
    if not is_array(entries):
        message = "checks is not a JSON array"
        raise TypeError(message)
    found: list[str] = []
    for raw in entries:
        entry = as_object(raw)
        if entry["check"] == check and entry["status"] == "fail":
            found.append(str(entry["location"]))
    return found


class CheckEvalsTest(unittest.TestCase):
    """Plugin eval discovery, V-7 and V-8."""

    def plugin(self, *, root_manifest: bool = False) -> Plugin:
        """A throwaway plugin in a folder removed after the test."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Plugin(Path(tmp.name), root_manifest=root_manifest)

    def test_root_level_manifest_is_a_plugin_root(self) -> None:
        """A plugin.json at the plugin root is a manifest, as claude plugin eval reads it."""
        plugin = self.plugin(root_manifest=True)
        plugin.case("fires", {"skill-fired": SKILL_FIRED})
        result = plugin.run()
        evals = evals_of(result)
        self.assertEqual(evals["plugin_root"], str(plugin.root.resolve()))
        self.assertEqual(evals["plugin_cases"], ["evals/fires"])

    def test_root_level_manifest_sets_the_eval_dir(self) -> None:
        """experimental.evals in a root-level plugin.json moves the suite."""
        plugin = self.plugin(root_manifest=True)
        plugin.write("plugin.json", '{"name": "demo-plugin", "experimental": {"evals": "qa"}}\n')
        plugin.write("qa/fires/prompt.md", "Do the demo task.\n")
        plugin.write("qa/fires/graders/skill-fired.md", SKILL_FIRED)
        evals = evals_of(plugin.run())
        self.assertEqual(evals["plugin_cases"], ["qa/fires"])

    def test_nested_group_cases_are_found(self) -> None:
        """A case nested under a non-case group directory is found."""
        plugin = self.plugin()
        plugin.case("triggers/fires", {"skill-fired": SKILL_FIRED})
        evals = evals_of(plugin.run())
        self.assertEqual(evals["plugin_cases"], ["evals/triggers/fires"])

    def test_inline_flags_in_an_llm_rubric_pass(self) -> None:
        """V-7 checks regex patterns only; an llm rubric may mention (?i)."""
        plugin = self.plugin()
        rubric = "---\ntype: llm\n---\n\nPASS if the reply says to use flags: i, not (?i).\n"
        plugin.case("teaches", {"skill-fired": SKILL_FIRED, "rubric": rubric})
        self.assertEqual(failures(plugin.run(), "V-7"), [])

    def test_inline_flags_in_a_regex_pattern_fail(self) -> None:
        """V-7 flags (?i) in a regex grader's pattern."""
        plugin = self.plugin()
        grader = "---\ntype: regex\npattern: '(?i)refund'\n---\n"
        plugin.case("refunds", {"skill-fired": SKILL_FIRED, "mentions": grader})
        self.assertEqual(failures(plugin.run(), "V-7"), ["evals/refunds/graders/mentions.md"])

    def test_inline_flags_in_a_regex_body_fail(self) -> None:
        """V-7 flags (?i) in a regex pattern written as the grader's body."""
        plugin = self.plugin()
        grader = "---\ntype: regex\n---\n\n(?i)refund\n"
        plugin.case("refunds", {"skill-fired": SKILL_FIRED, "mentions": grader})
        self.assertEqual(failures(plugin.run(), "V-7"), ["evals/refunds/graders/mentions.md"])

    def test_inline_flags_in_case_yaml_llm_criteria_pass(self) -> None:
        """V-7 ignores (?i) in an inline llm grader's criteria."""
        plugin = self.plugin()
        plugin.write(
            "evals/inline/case.yaml",
            CASE_YAML.format(grader="type: llm\n    criteria: PASS if demo-skill avoids (?i)."),
        )
        self.assertEqual(failures(plugin.run(), "V-7"), [])

    def test_inline_flags_in_case_yaml_pattern_fail(self) -> None:
        """V-7 flags (?i) in an inline regex grader's pattern."""
        plugin = self.plugin()
        plugin.write(
            "evals/inline/case.yaml",
            CASE_YAML.format(grader="type: regex\n    pattern: '(?i)demo-skill'"),
        )
        self.assertEqual(failures(plugin.run(), "V-7"), ["evals/inline/case.yaml"])

    def test_must_not_invoke_beside_a_scored_grader_needs_arm_both(self) -> None:
        """V-8 fails when another grader of the case is scored."""
        plugin = self.plugin()
        reply = "---\ntype: regex\npattern: done\n---\n"
        plugin.case("quiet", {"not-fired": MUST_NOT_FIRE, "reply": reply})
        self.assertEqual(failures(plugin.run(), "V-8"), ["evals/quiet/graders/not-fired.md"])

    def test_must_not_invoke_beside_with_only_graders_passes(self) -> None:
        """Every grader excluded: they are all scored, so V-8 passes."""
        plugin = self.plugin()
        reply = "---\ntype: regex\npattern: done\narm: with-only\n---\n"
        plugin.case("quiet", {"not-fired": MUST_NOT_FIRE, "reply": reply})
        self.assertEqual(failures(plugin.run(), "V-8"), [])

    def test_must_not_invoke_beside_plugin_mock_calls_grader_passes(self) -> None:
        """A mock_calls grader on the plugin's own mocked server is excluded too."""
        plugin = self.plugin()
        plugin.write(".mcp.json", '{"mcpServers": {"tracker": {"command": "tracker"}}}\n')
        plugin.write("evals/mocks/tracker/create_issue.md", "Created issue #1.\n")
        calls = "---\ntype: regex\ntarget: mock_calls\npattern: create_issue\n---\n"
        plugin.case("quiet", {"not-fired": MUST_NOT_FIRE, "calls": calls})
        self.assertEqual(failures(plugin.run(), "V-8"), [])

    def test_must_not_invoke_beside_foreign_mock_calls_grader_fails(self) -> None:
        """A mock_calls grader on a server the plugin doesn't declare is scored."""
        plugin = self.plugin()
        plugin.write("evals/mocks/tracker/create_issue.md", "Created issue #1.\n")
        calls = "---\ntype: llm\nfocus: mock_calls\n---\n\nPASS if an issue was created.\n"
        plugin.case("quiet", {"not-fired": MUST_NOT_FIRE, "calls": calls})
        self.assertEqual(failures(plugin.run(), "V-8"), ["evals/quiet/graders/not-fired.md"])

    def test_must_not_invoke_with_arm_both_passes(self) -> None:
        """arm: both satisfies V-8."""
        plugin = self.plugin()
        reply = "---\ntype: regex\npattern: done\n---\n"
        fixed = MUST_NOT_FIRE.replace("max: 0\n", "max: 0\narm: both\n")
        plugin.case("quiet", {"not-fired": fixed, "reply": reply})
        self.assertEqual(failures(plugin.run(), "V-8"), [])


if __name__ == "__main__":
    _ = unittest.main()
