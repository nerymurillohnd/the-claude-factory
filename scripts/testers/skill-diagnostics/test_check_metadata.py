#!/usr/bin/env python3
"""Tests for skills-best-practices' check-metadata.py (frontmatter, name, description, origin).

Run: python3 -m unittest discover -s scripts/testers/skill-diagnostics -p 'test_check_*.py' -v
Standard library only. Each case builds a skill folder in a temporary directory and runs the
script on it as a separate process, with CLAUDE_CONFIG_DIR pointed at a temporary folder so the
maintainer's own ~/.claude never takes part.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, cast, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
SCRIPTS = REPO / "plugins" / "skill-diagnostics" / "skills" / "skills-best-practices" / "scripts"
SCRIPT = SCRIPTS / "check-metadata.py"
MAX_CHECKS = 200
MAX_DETAIL = 300


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


@dataclass(frozen=True)
class Run:
    """One run of the script: exit code, stdout and stderr."""

    code: int
    stdout: str
    stderr: str

    def json(self) -> JsonObject:
        """The JSON object the script printed."""
        value = _decode(self.stdout)
        if not isinstance(value, JsonObject):
            msg = f"no JSON object on stdout: {self.stdout[:200]!r}"
            raise TypeError(msg)
        return value

    def checks(self) -> list[JsonObject]:
        """Every check result."""
        value = self.json().get("checks")
        if not isinstance(value, list):
            msg = "checks is not a list"
            raise TypeError(msg)
        return [c for c in cast("list[object]", value) if isinstance(c, JsonObject)]

    def having(self, check: str, status: str | None = None) -> list[JsonObject]:
        """The results of one check id, optionally with one status."""
        return [
            c
            for c in self.checks()
            if c.get("check") == check and (status is None or c.get("status") == status)
        ]

    def failed(self) -> list[str]:
        """Ids of the checks that failed."""
        return [str(c.get("check")) for c in self.checks() if c.get("status") == "fail"]


def scratch(case: unittest.TestCase) -> Path:
    """A temporary folder removed when the test ends."""
    root = Path(tempfile.mkdtemp()).resolve()
    case.addCleanup(shutil.rmtree, root)
    return root


def write(root: Path, files: dict[str, str]) -> None:
    """Write each relative path with its text, creating folders as needed."""
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(text, encoding="utf-8")


def run(skill: Path, config: Path, *args: str) -> Run:
    """Run check-metadata.py on a skill folder with CLAUDE_CONFIG_DIR set to config."""
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = str(config)
    cmd = [sys.executable, "-I", str(SCRIPT), str(skill), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60, env=env)
    return Run(proc.returncode, proc.stdout, proc.stderr)


def frontmatter(*lines: str, body: str = "# Skill\n\nDo the thing.\n") -> str:
    """A SKILL.md whose frontmatter holds the given lines."""
    return "---\n" + "".join(line + "\n" for line in lines) + "---\n" + body


GOOD = (
    "name: tiny-skill",
    "description: Formats tiny reports. Use when the user asks for a tiny report.",
)


class Base(unittest.TestCase):
    """Builds a loose skill folder named tiny-skill under a temporary root."""

    root: Path = Path()
    config: Path = Path()

    @override
    def setUp(self) -> None:
        """Create the temporary root and an empty config folder."""
        self.root = scratch(self)
        self.config = self.root / "config"
        self.config.mkdir()

    def skill(self, text: str, name: str = "tiny-skill", parent: Path | None = None) -> Path:
        """Write SKILL.md into <parent or root>/<name> and return the folder."""
        folder = (parent or self.root / "loose") / name
        write(folder, {"SKILL.md": text})
        return folder

    def check(self, text: str, name: str = "tiny-skill") -> Run:
        """Write the skill and run the script on it."""
        result = run(self.skill(text, name), self.config)
        self.assertEqual(result.code, 0, result.stderr)
        return result


class Frontmatter(Base):
    """FM-4: the frontmatter starts on line 1, closes and parses."""

    def test_valid_skill_has_no_failure(self) -> None:
        """A minimal valid skill passes every proved check."""
        result = self.check(frontmatter(*GOOD))
        self.assertEqual(result.failed(), [])
        self.assertTrue(result.having("M-1", "pass"))
        self.assertTrue(result.having("M-2", "pass"))
        out = result.json()
        self.assertEqual(out.get("script"), "check-metadata")
        self.assertEqual(out.get("ran"), True)
        self.assertEqual(out.get("truncated"), 0)

    def test_frontmatter_not_on_line_one(self) -> None:
        """A blank line before --- means Claude Code reads no frontmatter."""
        result = self.check("\n" + frontmatter(*GOOD))
        fails = result.having("M-1", "fail")
        self.assertTrue(fails)
        self.assertEqual(fails[0].get("location"), "SKILL.md:1")
        self.assertEqual(fails[0].get("item"), "FM-4")

    def test_frontmatter_not_closed(self) -> None:
        """A frontmatter without its closing --- fails M-1."""
        result = self.check("---\nname: tiny-skill\ndescription: x\n# body\n")
        self.assertTrue(result.having("M-1", "fail"))

    def test_tab_indentation_does_not_parse(self) -> None:
        """Strict YAML forbids tabs for indentation."""
        result = self.check(frontmatter(*GOOD, "metadata:", "\tauthor: me"))
        self.assertTrue(result.having("M-2", "fail"))

    def test_duplicate_key_does_not_parse(self) -> None:
        """Strict YAML rejects a key given twice."""
        result = self.check(frontmatter(*GOOD, "name: tiny-skill"))
        self.assertTrue(result.having("M-2", "fail"))

    def test_bad_indentation_does_not_parse(self) -> None:
        """A key indented under a scalar value is not valid YAML."""
        result = self.check(frontmatter("name: tiny-skill", "  description: x"))
        self.assertTrue(result.having("M-2", "fail"))

    def test_supported_forms_parse(self) -> None:
        """Quoted, block, flow and nested forms of the subset all parse."""
        result = self.check(
            frontmatter(
                "name: 'tiny-skill'",
                "description: >-",
                "  Formats tiny reports.",
                "  Use when the user asks for a tiny report.",
                'license: "MIT \\u00a9 me"',
                "compatibility: |",
                "  Needs python3.",
                "allowed-tools: [Read, Grep]",
                "arguments:",
                "  - file",
                "  - mode",
                "metadata:",
                "  author: 'it''s me'",
                "  version: '1.0'",
                "# a comment line",
            )
        )
        self.assertEqual(result.failed(), [])

    def test_plain_multiline_description_parses(self) -> None:
        """A plain value continued on more-indented lines is one folded string."""
        result = self.check(
            frontmatter(
                "name: tiny-skill",
                "description: Formats tiny reports.",
                "  Use when the user asks for a tiny report.",
            )
        )
        self.assertEqual(result.failed(), [])

    def test_folded_description_length_is_measured_after_folding(self) -> None:
        """A folded description longer than 1,024 characters fails M-12."""
        lines = ["  " + "word " * 19 + "word" for _ in range(12)]
        result = self.check(frontmatter("name: tiny-skill", "description: >", *lines))
        self.assertTrue(result.having("M-12", "fail"))


class Name(Base):
    """FM-1: the name limits of every surface."""

    def test_name_too_long(self) -> None:
        """65 characters is one too many."""
        name = "a" * 65
        result = self.check(frontmatter(f"name: {name}", GOOD[1]), name=name)
        self.assertTrue(result.having("M-4", "fail"))

    def test_name_with_uppercase(self) -> None:
        """Only a-z, 0-9 and hyphens."""
        result = self.check(frontmatter("name: Tiny-Skill", GOOD[1]), name="Tiny-Skill")
        self.assertTrue(result.having("M-5", "fail"))

    def test_name_with_leading_hyphen(self) -> None:
        """No leading hyphen."""
        result = self.check(frontmatter("name: -tiny", GOOD[1]), name="-tiny")
        self.assertTrue(result.having("M-6", "fail"))

    def test_name_with_double_hyphen(self) -> None:
        """No double hyphen."""
        result = self.check(frontmatter("name: tiny--skill", GOOD[1]), name="tiny--skill")
        self.assertTrue(result.having("M-6", "fail"))

    def test_name_differs_from_folder(self) -> None:
        """The name must match the folder name."""
        result = self.check(frontmatter("name: other-skill", GOOD[1]))
        fails = result.having("M-7", "fail")
        self.assertTrue(fails)
        self.assertEqual(fails[0].get("location"), "SKILL.md:2")

    def test_name_with_reserved_word(self) -> None:
        """Uploads and the API refuse names containing claude or anthropic."""
        result = self.check(frontmatter("name: claude-helper", GOOD[1]), name="claude-helper")
        self.assertTrue(result.having("M-8", "fail"))

    def test_folder_named_synced(self) -> None:
        """Claude Code does not load a folder named synced."""
        result = self.check(frontmatter("name: synced", GOOD[1]), name="synced")
        self.assertTrue(result.having("M-9", "fail"))

    def test_name_with_zero_width_character(self) -> None:
        """Claude Code refuses zero-width characters."""
        result = self.check(frontmatter("name: tiny\u200bskill", GOOD[1]), name="tiny\u200bskill")
        self.assertTrue(result.having("M-10", "fail"))


class Description(Base):
    """FM-1: description limits; compatibility limit."""

    def test_empty_description(self) -> None:
        """An empty description fails M-11."""
        result = self.check(frontmatter("name: tiny-skill", 'description: ""'))
        self.assertTrue(result.having("M-11", "fail"))

    def test_missing_description(self) -> None:
        """A missing description fails M-11."""
        result = self.check(frontmatter("name: tiny-skill"))
        self.assertTrue(result.having("M-11", "fail"))

    def test_description_too_long(self) -> None:
        """1,025 characters is one too many."""
        result = self.check(frontmatter("name: tiny-skill", "description: " + "a" * 1025))
        self.assertTrue(result.having("M-12", "fail"))

    def test_description_with_xml_tag(self) -> None:
        """Uploads and the API refuse XML tags in the description."""
        result = self.check(frontmatter("name: tiny-skill", "description: Formats <b>reports"))
        self.assertTrue(result.having("M-13", "fail"))

    def test_description_and_when_to_use_too_long(self) -> None:
        """The listing cuts description + when_to_use at 1,536 characters."""
        result = self.check(
            frontmatter(
                "name: tiny-skill", "description: " + "a" * 1000, "when_to_use: " + "b" * 600
            )
        )
        self.assertTrue(result.having("M-14", "fail"))

    def test_compatibility_too_long(self) -> None:
        """Compatibility holds at most 500 characters."""
        result = self.check(frontmatter(*GOOD, "compatibility: " + "c" * 501))
        self.assertTrue(result.having("M-15", "fail"))


class Origin(Base):
    """Section 2: the origin and the surfaces it reaches; FM-2 depends on them."""

    def test_loose_origin(self) -> None:
        """A folder outside every known place is loose and reaches Claude Code only."""
        result = self.check(frontmatter(*GOOD))
        out = result.json()
        self.assertEqual(out.get("origin"), "loose")
        self.assertEqual(out.get("surfaces"), ["claude-code"])

    def test_plugin_origin(self) -> None:
        """An ancestor with .claude-plugin/plugin.json makes a plugin skill."""
        plugin = self.root / "my-plugin"
        write(plugin, {".claude-plugin/plugin.json": '{"name": "my-plugin"}'})
        result = run(self.skill(frontmatter(*GOOD), parent=plugin / "skills"), self.config)
        out = result.json()
        self.assertEqual(out.get("origin"), "plugin")
        self.assertEqual(out.get("surfaces"), ["claude-code", "chat", "cowork"])

    def test_personal_origin(self) -> None:
        """A skill under <config>/skills/ is personal."""
        result = run(self.skill(frontmatter(*GOOD), parent=self.config / "skills"), self.config)
        out = result.json()
        self.assertEqual(out.get("origin"), "personal")
        self.assertEqual(out.get("surfaces"), ["claude-code"])

    def test_account_origin(self) -> None:
        """A skill under <config>/skills/synced/ is a claude.ai account skill."""
        parent = self.config / "skills" / "synced"
        result = run(self.skill(frontmatter(*GOOD), parent=parent), self.config)
        out = result.json()
        self.assertEqual(out.get("origin"), "account")
        surfaces = cast("list[object]", out.get("surfaces"))
        for surface in ("chat", "cowork", "cloud-sessions", "project-cloud-threads", "claude-code"):
            self.assertIn(surface, surfaces)

    def test_project_origin(self) -> None:
        """A skill under a repository's .claude/skills/ is a project skill."""
        parent = self.root / "repo" / ".claude" / "skills"
        result = run(self.skill(frontmatter(*GOOD), parent=parent), self.config)
        out = result.json()
        self.assertEqual(out.get("origin"), "project")
        self.assertEqual(out.get("surfaces"), ["claude-code", "cloud-sessions"])


class Fields(Base):
    """FM-2: fields outside the six standard ones, judged by origin."""

    EXTRA: tuple[str, ...] = (*GOOD, "when_to_use: When a report is tiny.")

    def test_extra_field_on_loose_skill_passes(self) -> None:
        """A loose skill reaches only Claude Code, so Claude Code fields are fine."""
        result = self.check(frontmatter(*self.EXTRA))
        self.assertFalse(result.having("M-16", "fail"))
        passes = result.having("M-16", "pass")
        self.assertTrue(passes)
        self.assertIn("when_to_use", str(passes[0].get("detail")))

    def test_extra_field_on_plugin_skill_fails(self) -> None:
        """A plugin skill reaches chat, where uploads reject non-standard fields."""
        plugin = self.root / "my-plugin"
        write(plugin, {".claude-plugin/plugin.json": '{"name": "my-plugin"}'})
        result = run(self.skill(frontmatter(*self.EXTRA), parent=plugin / "skills"), self.config)
        fails = result.having("M-16", "fail")
        self.assertTrue(fails)
        self.assertEqual(fails[0].get("location"), "SKILL.md:4")

    def test_extra_field_on_account_skill_fails(self) -> None:
        """An account skill is an upload."""
        parent = self.config / "skills" / "synced"
        result = run(self.skill(frontmatter(*self.EXTRA), parent=parent), self.config)
        self.assertTrue(result.having("M-16", "fail"))

    def test_extra_field_on_personal_skill_passes_with_warning(self) -> None:
        """A personal skill passes, and the detail says enabling it on claude.ai would fail."""
        result = run(
            self.skill(frontmatter(*self.EXTRA), parent=self.config / "skills"), self.config
        )
        passes = result.having("M-16", "pass")
        self.assertTrue(passes)
        self.assertIn("claude.ai", str(passes[0].get("detail")))


class StrictYaml(Base):
    """FM-5: strict-YAML traps in plain values; metadata is a map."""

    def test_metadata_not_a_map(self) -> None:
        """Metadata must be a map."""
        result = self.check(frontmatter(*GOOD, "metadata: me"))
        self.assertTrue(result.having("M-17", "fail"))

    def test_colon_space_in_plain_value(self) -> None:
        """'Use when: ...' breaks strict YAML."""
        result = self.check(frontmatter("name: tiny-skill", "description: Use when: reports"))
        fails = result.having("M-18", "fail")
        self.assertTrue(fails)
        self.assertEqual(fails[0].get("location"), "SKILL.md:3")
        self.assertEqual(fails[0].get("item"), "FM-5")

    def test_space_hash_in_plain_value(self) -> None:
        """' #' starts a comment in strict YAML."""
        result = self.check(frontmatter("name: tiny-skill", "description: Formats issue #12 well"))
        self.assertTrue(result.having("M-18", "fail"))

    def test_leading_bracket_in_plain_value(self) -> None:
        """A value starting with [ is read as a list."""
        result = self.check(frontmatter("name: tiny-skill", "description: [WIP] formats reports"))
        self.assertTrue(result.having("M-18", "fail"))

    def test_leading_indicator_in_plain_value(self) -> None:
        """A value starting with @ or * is reserved or an alias."""
        result = self.check(frontmatter("name: tiny-skill", "description: @team formats reports"))
        self.assertTrue(result.having("M-18", "fail"))

    def test_boolean_word_where_string_expected(self) -> None:
        """'no' reads as a boolean in YAML 1.1 parsers."""
        result = self.check(frontmatter(*GOOD, "license: no"))
        self.assertTrue(result.having("M-18", "fail"))

    def test_null_word_in_metadata_value(self) -> None:
        """'~' reads as null."""
        result = self.check(frontmatter(*GOOD, "metadata:", "  owner: ~"))
        self.assertTrue(result.having("M-18", "fail"))

    def test_quoted_values_are_not_traps(self) -> None:
        """Quoting removes every trap."""
        result = self.check(
            frontmatter("name: tiny-skill", 'description: "Use when: issue #12"', "license: 'no'")
        )
        self.assertFalse(result.having("M-18", "fail"))
        self.assertTrue(result.having("M-18", "pass"))


class Combinations(Base):
    """FM-6: combinations that disable the skill."""

    def test_nobody_can_invoke(self) -> None:
        """disable-model-invocation: true with user-invocable: false."""
        result = self.check(
            frontmatter(*GOOD, "disable-model-invocation: true", "user-invocable: false")
        )
        fails = result.having("M-19", "fail")
        self.assertTrue(fails)
        self.assertEqual(fails[0].get("item"), "FM-6")

    def test_paths_on_a_skill_claude_cannot_start(self) -> None:
        """Paths does nothing when Claude may not start the skill: a lead."""
        result = self.check(
            frontmatter(*GOOD, "disable-model-invocation: true", "paths: ['src/**']")
        )
        leads = result.having("M-20", "lead")
        self.assertTrue(leads)
        self.assertEqual(leads[0].get("kind"), "lead")
        self.assertFalse(result.having("M-19", "fail"))


class Contract(Base):
    """Exit codes, help, bounded output and the result shape."""

    def test_findings_exit_zero(self) -> None:
        """A skill with failures still exits 0 and prints one JSON object."""
        result = self.check(frontmatter("name: Bad--Name", "description: <x>"), name="other")
        self.assertEqual(result.code, 0)
        self.assertTrue(result.failed())
        for check in result.checks():
            self.assertIn(check.get("kind"), ("proved", "lead"))
            self.assertIn(check.get("status"), ("pass", "fail", "lead"))
            self.assertLessEqual(len(str(check.get("detail"))), MAX_DETAIL)
            self.assertRegex(str(check.get("item")), r"^[A-Z]{2}-\d+$")

    def test_usage_exit_2(self) -> None:
        """No such folder, or a folder without SKILL.md, is a usage error."""
        missing = run(self.root / "nope", self.config)
        self.assertEqual(missing.code, 2)
        self.assertEqual(missing.stdout, "")
        self.assertTrue(missing.stderr)
        empty = self.root / "empty"
        empty.mkdir()
        no_skill = run(empty, self.config)
        self.assertEqual(no_skill.code, 2)
        self.assertIn("SKILL.md", no_skill.stderr)

    def test_help(self) -> None:
        """--help prints usage and exits 0."""
        result = run(self.root, self.config, "--help")
        self.assertEqual(result.code, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_output_is_bounded(self) -> None:
        """More than 200 failures: at most 200 checks, the rest counted in truncated."""
        traps = [f"  key{i}: a: b" for i in range(250)]
        result = self.check(frontmatter(*GOOD, "metadata:", *traps))
        self.assertLessEqual(len(result.checks()), MAX_CHECKS)
        truncated = result.json().get("truncated")
        self.assertIsInstance(truncated, int)
        self.assertGreater(truncated if isinstance(truncated, int) else 0, 0)

    def test_output_file_matches_stdout(self) -> None:
        """--output writes the same JSON object as stdout, creating parent folders."""
        out = self.root / "results" / "nested" / "metadata.json"
        result = run(self.skill(frontmatter(*GOOD)), self.config, "--output", str(out))
        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(out.read_text(encoding="utf-8"), result.stdout)
        self.assertEqual(result.json().get("script"), "check-metadata")

    def test_unwritable_output_exits_1(self) -> None:
        """An --output path that can't be written exits 1 and names the path on stderr."""
        blocker = self.root / "a-file"
        _ = blocker.write_text("x", encoding="utf-8")
        out = blocker / "metadata.json"
        result = run(self.skill(frontmatter(*GOOD)), self.config, "--output", str(out))
        self.assertEqual(result.code, 1)
        self.assertIn("--output", result.stderr)
        self.assertIn(str(out), result.stderr)

    def test_skill_path_is_absolute(self) -> None:
        """The skill path in the output is absolute."""
        result = self.check(frontmatter(*GOOD))
        self.assertTrue(Path(str(result.json().get("skill"))).is_absolute())

    def test_proved_checks_only_on_owned_items(self) -> None:
        """check-metadata proves only FM-1, FM-2, FM-4, FM-5 and FM-6."""
        result = self.check(frontmatter(*GOOD, "disable-model-invocation: true", "paths: x"))
        for check in result.checks():
            if check.get("kind") == "proved":
                self.assertIn(check.get("item"), ("FM-1", "FM-2", "FM-4", "FM-5", "FM-6"))


if __name__ == "__main__":
    _ = unittest.main()
