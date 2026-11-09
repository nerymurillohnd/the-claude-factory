#!/usr/bin/env python3
"""Tests for skills-best-practices' check-evals.py (evals/evals.json and plugin eval cases).

Run: scripts/testers/run_unittest.py scripts/testers/skill-diagnostics
Standard library only. Each case builds a plugin with one skill in a temporary folder and runs the
script on the skill as a separate process.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, cast, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO
    / "plugins"
    / "skill-diagnostics"
    / "skills"
    / "skills-best-practices"
    / "scripts"
    / "check-evals.py"
)
NAME = "tiny-skill"
SKILL_MD = f"---\nname: {NAME}\ndescription: Formats tiny reports.\n---\n# Tiny\n"
INVOKED = f"---\ntype: tool_used\ntool: Skill\ninput: {NAME}\nmin: 1\n---\n"
RESULT = "---\ntype: regex\nsource: final_message\npattern: report\n---\n"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def as_object(text: str) -> JsonObject:
    """Decode text that must hold one JSON object."""
    value = _decode(text)
    if not isinstance(value, JsonObject):
        message = f"expected a JSON object, got {text[:200]!r}"
        raise TypeError(message)
    return value


def statuses(result: JsonObject) -> dict[str, list[str]]:
    """Check id to the statuses it reported, in order."""
    checks = result.get("checks")
    if not isinstance(checks, list):
        message = "no checks list"
        raise TypeError(message)
    found: dict[str, list[str]] = {}
    for entry in cast("list[object]", checks):
        if isinstance(entry, JsonObject):
            found.setdefault(str(entry.get("check")), []).append(str(entry.get("status")))
    return found


def case(index: int, **extra: object) -> dict[str, object]:
    """One valid evals.json case, with fields replaced or added."""
    base: dict[str, object] = {
        "id": index,
        "prompt": f"Format report {index} from data/{index}.csv",
        "expected_output": "A one-page report with a totals row",
    }
    base.update(extra)
    return base


class CheckEvals(unittest.TestCase):
    """evals.json format, plugin case graders, the count and the command-line contract."""

    plugin: Path = Path()
    skill: Path = Path()

    @override
    def setUp(self) -> None:
        """A plugin with one skill and no evals."""
        self.plugin = Path(self.enterContext(tempfile.TemporaryDirectory())) / "tiny-plugin"
        (self.plugin / ".claude-plugin").mkdir(parents=True)
        _ = (self.plugin / ".claude-plugin" / "plugin.json").write_text(
            '{"name": "tiny-plugin"}', encoding="utf-8"
        )
        self.skill = self.plugin / "skills" / NAME
        self.skill.mkdir(parents=True)
        _ = (self.skill / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")

    def write(self, relative: str, text: str) -> Path:
        """Write a file under the plugin, creating its folders."""
        path = self.plugin / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")
        return path

    def evals_json(self, cases: list[dict[str, object]], name: str = NAME) -> None:
        """Write the skill's evals/evals.json."""
        data = {"skill_name": name, "evals": cases}
        _ = self.write(f"skills/{NAME}/evals/evals.json", json.dumps(data))

    def plugin_case(self, folder: str, *graders: str) -> None:
        """A plugin eval case with a prompt and the given grader texts."""
        _ = self.write(f"{folder}/prompt.md", "Format the tiny report.\n")
        for index, text in enumerate(graders):
            _ = self.write(f"{folder}/graders/g{index}.md", text)

    def run_on(self, *extra: str) -> subprocess.CompletedProcess[str]:
        """Run the script on the skill."""
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.skill), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def checked(self) -> JsonObject:
        """The JSON result of a run that must exit 0."""
        result = self.run_on()
        self.assertEqual(result.returncode, 0, result.stderr)
        return as_object(result.stdout)

    def test_no_evals_fails_only_the_count(self) -> None:
        """Without evals V-1 fails and no format check runs."""
        found = statuses(self.checked())
        self.assertEqual(
            found, {"V-1": ["fail"], "V-6": ["pass"], "V-7": ["pass"], "V-8": ["pass"]}
        )

    def test_three_valid_cases_pass(self) -> None:
        """Three valid cases with an existing input file pass every check."""
        _ = self.write(f"skills/{NAME}/evals/files/1.csv", "a,b\n")
        self.evals_json(
            [case(1, files=["evals/files/1.csv"], assertions=["Has totals"]), case(2), case(3)]
        )
        found = statuses(self.checked())
        for cid in ("V-1", "V-2", "V-3", "V-4", "V-5"):
            self.assertEqual(found[cid], ["pass"], cid)

    def test_two_cases_fail_the_count(self) -> None:
        """V-1 needs at least three evals."""
        self.evals_json([case(1), case(2)])
        self.assertEqual(statuses(self.checked())["V-1"], ["fail"])

    def test_wrong_skill_name_and_bad_json(self) -> None:
        """V-2 fails on another skill_name and on text that isn't JSON."""
        self.evals_json([case(1), case(2), case(3)], name="other-skill")
        self.assertEqual(statuses(self.checked())["V-2"], ["fail"])
        _ = self.write(f"skills/{NAME}/evals/evals.json", "{not json")
        self.assertEqual(statuses(self.checked())["V-2"], ["fail"])

    def test_duplicate_id_and_missing_fields(self) -> None:
        """V-3 fails on a repeated id and on an empty expected_output."""
        self.evals_json([case(1), case(1), case(3, expected_output=" ")])
        self.assertEqual(statuses(self.checked())["V-3"], ["fail", "fail"])

    def test_files_outside_or_missing(self) -> None:
        """V-4 fails on a path that leaves the skill and on one that doesn't exist."""
        self.evals_json(
            [case(1, files=["../../x.csv"]), case(2, files=["evals/files/no.csv"]), case(3)]
        )
        self.assertEqual(statuses(self.checked())["V-4"], ["fail", "fail"])

    def test_assertions_must_be_statements(self) -> None:
        """V-5 fails when assertions isn't a list of non-empty strings."""
        self.evals_json([case(1, assertions="Has totals"), case(2, assertions=[""]), case(3)])
        self.assertEqual(statuses(self.checked())["V-5"], ["fail", "fail"])

    def test_plugin_cases_count_and_pass(self) -> None:
        """Plugin cases that name the skill count toward V-1 and pass V-6 to V-8."""
        for folder in ("evals/a", "evals/b", "evals/c"):
            self.plugin_case(folder, INVOKED, RESULT)
        self.plugin_case("evals/unrelated", RESULT)
        result = self.checked()
        found = statuses(result)
        for cid in ("V-1", "V-6", "V-7", "V-8"):
            self.assertEqual(found[cid], ["pass"], cid)
        info = result.get("evals")
        self.assertIsInstance(info, JsonObject)
        if isinstance(info, JsonObject):
            self.assertEqual(info.get("plugin_cases"), ["evals/a", "evals/b", "evals/c"])

    def test_case_without_grader(self) -> None:
        """V-6 fails on a case for the skill with no grader."""
        self.plugin_case("evals/bare")
        _ = self.write("evals/bare/case.yaml", f"prompt: Use {NAME} on the report\n")
        self.assertEqual(statuses(self.checked())["V-6"], ["fail"])

    def test_inline_flags(self) -> None:
        """V-7 fails on a regex with an inline (?i) group."""
        self.plugin_case("evals/flags", INVOKED, RESULT.replace("report", "(?i)report"))
        self.assertEqual(statuses(self.checked())["V-7"], ["fail"])

    def test_must_not_invoke_needs_arm_both(self) -> None:
        """V-8 fails without arm: both when the case has another grader, and passes with it."""
        never = f"---\ntype: tool_used\ntool: Skill\ninput: {NAME}\nmin: 0\nmax: 0\n---\n"
        self.plugin_case("evals/never", never, RESULT)
        self.assertEqual(statuses(self.checked())["V-8"], ["fail"])
        _ = self.write(
            "evals/never/graders/g0.md", never.replace("max: 0\n", "max: 0\narm: both\n")
        )
        self.assertEqual(statuses(self.checked())["V-8"], ["pass"])

    def test_experimental_eval_dir(self) -> None:
        """plugin.json's experimental.evals moves the eval directory."""
        _ = self.write(
            ".claude-plugin/plugin.json", '{"name": "t", "experimental": {"evals": "suite"}}'
        )
        self.plugin_case("suite/a", INVOKED)
        self.plugin_case("evals/ignored", INVOKED)
        info = self.checked().get("evals")
        if isinstance(info, JsonObject):
            self.assertEqual(info.get("plugin_cases"), ["suite/a"])

    def test_output_file_matches_stdout(self) -> None:
        """--output writes the same JSON, creating its folder."""
        target = Path(self.enterContext(tempfile.TemporaryDirectory())) / "a" / "evals.json"
        result = self.run_on("--output", str(target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), result.stdout)

    def test_usage_errors_exit_2(self) -> None:
        """No such folder, or a folder without SKILL.md, exits 2."""
        for folder in (self.plugin / "missing", self.plugin):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(folder)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    _ = unittest.main()
