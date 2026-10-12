"""Tests for skill-diagnostics' check_skill.py.

Run: python3 -m unittest discover -s .github/scripts/tests/skill-diagnostics -v
Set CHECK_SKILL to test another checker build (for example the claude-essentials one).
Standard library only; runs on Python 3.9+ on Linux, macOS and Windows.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CHECKER = Path(
    os.environ.get(
        "CHECK_SKILL",
        REPO / "plugins" / "skill-diagnostics" / "skills" / "audit" / "scripts" / "check_skill.py",
    )
)
IS_WINDOWS = os.name == "nt"


def run(skill_dir: Path, *args: str) -> tuple[int, dict]:
    """Run the checker on a directory; return its exit code and parsed JSON."""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--format", "json", *args, str(skill_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    try:
        report = json.loads(proc.stdout) if proc.stdout.strip() else {}
    except json.JSONDecodeError:
        report = {}
    return proc.returncode, report


def findings(report: dict) -> list[dict]:
    return report.get("findings", [])


def has(
    report: dict,
    *,
    severity: str | None = None,
    line: int | None = None,
    rule: str | None = None,
    file: str = "SKILL.md",
) -> bool:
    """True when a finding matches. A finding without a 'rule' key (older checkers) matches any rule."""
    for f in findings(report):
        if f.get("file") != file:
            continue
        if severity and f.get("severity") != severity:
            continue
        if line is not None and f.get("line") != line:
            continue
        if rule and "rule" in f and f["rule"] != rule:
            continue
        if rule and "rule" not in f and severity is None and line is None:
            continue
        return True
    return False


class SkillCase(unittest.TestCase):
    """Builds a throwaway skill directory per test."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.skill = self.root / "demo-skill"
        self.skill.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, rel: str, text: str, executable: bool = False) -> Path:
        path = self.skill / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:  # LF on every OS
            handle.write(textwrap.dedent(text).lstrip("\n"))
        if executable:
            path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return path

    def skill_md(self, frontmatter: str, body: str = "Do the task.\n") -> None:
        self.write("SKILL.md", "---\n" + textwrap.dedent(frontmatter).strip("\n") + "\n---\n\n" + body)


GOOD = """
name: demo-skill
description: Formats release notes from git tags. Use when the user asks for release notes.
"""


class CleanSkill(SkillCase):
    def test_clean_skill_exits_zero_without_errors(self) -> None:
        self.skill_md(GOOD)
        code, report = run(self.skill)
        self.assertEqual(code, 0, report)
        self.assertFalse([f for f in findings(report) if f["severity"] == "error"], report)

    def test_bad_path_exits_two(self) -> None:
        code, _ = run(self.root / "missing")
        self.assertEqual(code, 2)


class Frontmatter(SkillCase):
    def test_missing_opening_marker_is_error(self) -> None:
        self.write("SKILL.md", "name: demo-skill\n---\nBody\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", line=1, rule="frontmatter-start"))

    def test_unknown_field_warns_with_suggestion(self) -> None:
        self.skill_md(GOOD + "disable_model_invocation: true\n")
        _, report = run(self.skill)
        hit = [f for f in findings(report) if f.get("rule") == "field-unknown"]
        self.assertTrue(hit, report)
        self.assertIn("disable-model-invocation", hit[0]["message"])

    def test_invalid_effort_value_is_error(self) -> None:
        self.skill_md(GOOD + "effort: extreme\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", rule="field-value"))

    def test_upload_target_rejects_claude_code_only_fields(self) -> None:
        self.skill_md(GOOD + 'argument-hint: "[tag]"\n')
        code, report = run(self.skill, "--target", "upload")
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", rule="field-unknown"))
        code, _ = run(self.skill, "--target", "code")
        self.assertEqual(code, 0)


class Name(SkillCase):
    def test_name_over_64_chars_is_error(self) -> None:
        self.skill_md("name: " + "a" * 65 + "\ndescription: Does a thing. Use when asked.\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", rule="name-length"))

    def test_double_hyphen_is_error(self) -> None:
        self.skill_md("name: demo--skill\ndescription: Does a thing. Use when asked.\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="error", rule="name-format"))

    def test_reserved_word_is_error_for_upload(self) -> None:
        """Regression: the claude-essentials checker only warned."""
        self.skill = self.root / "claude-helper"
        self.skill.mkdir()
        self.skill_md("name: claude-helper\ndescription: Does a thing. Use when asked.\n")
        code, report = run(self.skill, "--target", "upload")
        self.assertEqual(code, 1, report)
        self.assertTrue(has(report, severity="error", line=2, rule="name-reserved"))

    def test_reserved_word_is_info_for_claude_code(self) -> None:
        """Claude Code accepts the word, so a valid Claude Code skill must not fail."""
        self.skill = self.root / "claude-helper"
        self.skill.mkdir()
        self.skill_md("name: claude-helper\ndescription: Does a thing. Use when asked.\n")
        code, report = run(self.skill)
        self.assertEqual(code, 0, report)
        self.assertTrue(has(report, severity="info", line=2, rule="name-reserved"))

    def test_name_must_match_directory(self) -> None:
        self.skill_md("name: other-name\ndescription: Does a thing. Use when asked.\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="name-directory"))
        _, report = run(self.skill, "--target", "upload")
        self.assertTrue(has(report, severity="error", rule="name-directory"))

    def test_synced_directory_is_error_for_claude_code(self) -> None:
        self.skill = self.root / "synced"
        self.skill.mkdir()
        self.skill_md("name: synced\ndescription: Does a thing. Use when asked.\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1, report)
        self.assertTrue(has(report, severity="error", rule="name-reserved-local"))
        _, report = run(self.skill, "--target", "upload")
        self.assertFalse(has(report, rule="name-reserved-local"), report)

    def test_anthropic_skills_name_is_error_for_claude_code(self) -> None:
        self.skill_md("name: anthropic-skills\ndescription: Does a thing. Use when asked.\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="error", rule="name-reserved-local"))


class Description(SkillCase):
    def test_block_scalar_description_is_still_checked(self) -> None:
        """Regression: the claude-essentials checker skipped every check for `>` descriptions."""
        self.skill_md("name: demo-skill\ndescription: >\n  I can help you with notes.\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", line=3, rule="description-one-line"), report)
        self.assertTrue(has(report, severity="warning", line=3, rule="description-person"), report)

    def test_unquoted_colon_space_is_error_with_reword_hint(self) -> None:
        self.skill_md("name: demo-skill\ndescription: Formats notes. Use when: the user asks.\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1)
        hit = [f for f in findings(report) if f.get("rule") == "yaml-quoting"]
        self.assertTrue(hit, report)
        self.assertIn("reword", hit[0].get("hint", "").lower())

    def test_unquoted_space_hash_truncates_and_is_error(self) -> None:
        self.skill_md("name: demo-skill\ndescription: Tracks issue #12 and others. Use when asked.\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", rule="yaml-quoting"))

    def test_unneeded_quotes_are_info(self) -> None:
        self.skill_md('name: demo-skill\ndescription: "Formats notes. Use when asked."\n')
        code, report = run(self.skill)
        self.assertEqual(code, 0)
        self.assertTrue(has(report, severity="info", rule="yaml-quoting"))

    def test_needed_quotes_are_not_reported(self) -> None:
        self.skill_md('name: demo-skill\ndescription: "Formats notes. Use when: asked."\n')
        _, report = run(self.skill)
        self.assertFalse([f for f in findings(report) if f.get("rule") == "yaml-quoting"], report)

    def test_listing_cap_warns_by_default_and_respects_flag(self) -> None:
        text = "Formats notes. Use when asked. " + "x" * 1600
        self.skill_md(f"name: demo-skill\ndescription: {text}\n")
        code, report = run(self.skill)
        self.assertEqual(code, 0, report)
        self.assertTrue(has(report, severity="warning", rule="description-listing-cap"))
        _, report = run(self.skill, "--listing-cap", "2048")
        self.assertFalse(has(report, rule="description-listing-cap"), report)

    def test_upload_target_limits_description_to_1024(self) -> None:
        text = "Formats notes. Use when asked. " + "x" * 1100
        self.skill_md(f"name: demo-skill\ndescription: {text}\n")
        code, report = run(self.skill, "--target", "upload")
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", rule="description-length"))

    def test_angle_bracket_tag_is_error_for_upload_only(self) -> None:
        self.skill_md("name: demo-skill\ndescription: Formats <b>notes</b>. Use when asked.\n")
        _, report = run(self.skill, "--target", "upload")
        self.assertTrue(has(report, severity="error", rule="description-tags"))
        code, report = run(self.skill)
        self.assertEqual(code, 0, report)
        self.assertTrue(has(report, severity="info", rule="description-tags"))

    def test_missing_trigger_clause_warns(self) -> None:
        self.skill_md("name: demo-skill\ndescription: Formats notes.\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="description-trigger"))


class Arguments(SkillCase):
    def test_unescaped_money_amount_warns(self) -> None:
        """Regression: the claude-essentials checker did not detect argument placeholders."""
        self.skill_md(GOOD, "Charge $1.00 per report.\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", line=6), report)

    def test_declared_argument_never_used_warns(self) -> None:
        self.skill_md(GOOD + "arguments: [tag, branch]\n", "Start from $tag.\n")
        _, report = run(self.skill)
        hit = [f for f in findings(report) if f.get("rule") == "arguments-unused"]
        self.assertTrue(hit and "branch" in hit[0]["message"], report)


class Body(SkillCase):
    def test_long_body_is_warning_not_error(self) -> None:
        """Regression: the claude-essentials checker failed (exit 1) at 500 lines."""
        self.skill_md(GOOD, "line\n" * 520)
        code, report = run(self.skill)
        self.assertEqual(code, 0, report)
        self.assertTrue(has(report, severity="warning", rule="body-lines"))

    def test_dynamic_context_is_error_for_upload_and_warning_for_cowork(self) -> None:
        self.skill_md(GOOD, "!`git status`\n")
        _, report = run(self.skill, "--target", "upload")
        self.assertTrue(has(report, severity="error", rule="dynamic-context"))
        _, report = run(self.skill, "--target", "cowork")
        self.assertTrue(has(report, severity="warning", rule="dynamic-context"))


class Files(SkillCase):
    def test_broken_link_is_error(self) -> None:
        self.skill_md(GOOD, "Read [guide](references/guide.md) first.\n")
        code, report = run(self.skill)
        self.assertEqual(code, 1)
        self.assertTrue(has(report, severity="error", rule="link-broken"))

    def test_link_with_spaces_is_checked(self) -> None:
        self.skill_md(GOOD, "Read [a](<references/my guide.md>) and [b](references/my%20notes.md).\n")
        self.write("references/my guide.md", "# Guide\n")
        _, report = run(self.skill)
        broken = [f["message"] for f in findings(report) if f.get("rule") == "link-broken"]
        self.assertEqual(broken, ["broken link: references/my notes.md"], report)  # the spaced guide resolves

    def test_fence_inside_a_longer_fence_stays_code(self) -> None:
        body = "````markdown\n```bash\nRead [x](missing.md)\n```\n````\n\nRead [y](missing-too.md).\n"
        self.skill_md(GOOD, body)
        _, report = run(self.skill)
        broken = [f["message"] for f in findings(report) if f.get("rule") == "link-broken"]
        self.assertEqual(broken, ["broken link: missing-too.md"], report)

    def test_broken_link_inside_assets_is_error(self) -> None:
        self.skill_md(GOOD)
        self.write("assets/template.md", "See [spec](missing.md).\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="error", rule="link-broken", file="assets/template.md"))

    def test_nested_reference_link_warns(self) -> None:
        self.skill_md(GOOD, "Read [a](references/a.md).\n")
        self.write("references/a.md", "# A\n\nSee [b](b.md).\n")
        self.write("references/b.md", "# B\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="reference-nested", file="references/a.md"))

    def test_long_reference_without_contents_warns(self) -> None:
        self.skill_md(GOOD, "Read [a](references/a.md).\n")
        self.write("references/a.md", "# A\n\n## Intro\n" + "text\n" * 120)
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="reference-contents", file="references/a.md"))

    def test_relative_script_call_warns(self) -> None:
        self.skill_md(GOOD, "Run `scripts/build.py data.csv`.\n")
        self.write("scripts/build.py", "#!/usr/bin/env python3\nprint('ok')\n", executable=True)
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="script-path"))

    def test_upload_skill_dir_path_reported_once_per_line(self) -> None:
        self.skill_md(GOOD, "Read `${CLAUDE_SKILL_DIR}/references/a.md` and `${CLAUDE_SKILL_DIR}/references/b.md`.\n")
        self.write("references/a.md", "# A\n")
        self.write("references/b.md", "# B\n")
        _, report = run(self.skill, "--target", "upload")
        hits = [f for f in findings(report) if f.get("rule") == "script-path"]
        self.assertEqual(len(hits), 1, report)
        self.assertNotIn("interpreter", json.dumps(hits[0]))

    def test_bare_script_file_mention_is_not_a_command(self) -> None:
        self.skill_md(GOOD, "| `scripts/build.py` | Run it, do not read it |\n")
        self.write("scripts/build.py", "#!/usr/bin/env python3\nprint('ok')\n", executable=True)
        _, report = run(self.skill)
        self.assertFalse(has(report, rule="script-path"), report)

    def test_script_without_env_shebang_warns(self) -> None:
        self.skill_md(GOOD, "Run `${CLAUDE_SKILL_DIR}/scripts/build.py`.\n")
        self.write("scripts/build.py", "print('ok')\n", executable=True)
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="script-shebang", file="scripts/build.py"))

    @unittest.skipIf(IS_WINDOWS, "the executable bit does not exist on Windows")
    def test_script_without_executable_bit_warns(self) -> None:
        self.skill_md(GOOD, "Run `${CLAUDE_SKILL_DIR}/scripts/build.py`.\n")
        self.write("scripts/build.py", "#!/usr/bin/env python3\nprint('ok')\n")
        _, report = run(self.skill)
        self.assertTrue(has(report, severity="warning", rule="script-executable", file="scripts/build.py"))

    def test_helper_module_not_run_by_path_is_not_reported(self) -> None:
        self.skill_md(GOOD, "Run `${CLAUDE_SKILL_DIR}/scripts/build.py`.\n")
        self.write("scripts/build.py", "#!/usr/bin/env python3\nimport helpers\n", executable=True)
        self.write("scripts/helpers.py", "VALUE = 1\n")
        self.write("scripts/__init__.py", "")
        _, report = run(self.skill)
        self.assertFalse([f for f in findings(report) if f["file"].startswith("scripts/")], report)


class Inventory(SkillCase):
    """--list: the full file inventory the lenses read from."""

    def test_lists_every_file_hidden_and_ignored_included(self) -> None:
        self.skill_md(GOOD)
        self.write(".env.example", "KEY=\n")
        self.write(".hidden/notes.md", "# Notes\n")
        self.write(".gitignore", "build/\n")
        self.write("build/out.txt", "x\n")
        self.write("references/deep/a/b.md", "# B\n")
        code, report = run(self.skill, "--list")
        self.assertEqual(code, 0, report)
        paths = [f["path"] for f in report["files"]]
        self.assertEqual(
            paths,
            sorted(
                [
                    ".env.example",
                    ".gitignore",
                    ".hidden/notes.md",
                    "SKILL.md",
                    "build/out.txt",
                    "references/deep/a/b.md",
                ]
            ),
        )
        self.assertEqual(report["count"], 6)
        self.assertEqual(report["not_listed"], [])

    def test_no_cap_on_the_number_of_files(self) -> None:
        self.skill_md(GOOD)
        for i in range(150):
            self.write(f"assets/f{i:03}.txt", "x\n")
        _, report = run(self.skill, "--list")
        self.assertEqual(report["count"], 151)

    def test_reports_sizes_without_checking(self) -> None:
        self.skill_md(GOOD, "Read [missing](references/none.md).\n")
        code, report = run(self.skill, "--list")
        self.assertEqual(code, 0, report)  # a broken link is not an inventory error
        self.assertNotIn("findings", report)
        self.assertGreater(report["files"][0]["bytes"], 0)

    @unittest.skipIf(IS_WINDOWS, "symlinks need extra privileges on Windows")
    def test_follows_symlinked_folders_and_reports_loops(self) -> None:
        self.skill_md(GOOD)
        outside = self.root / "shared"
        (outside / "deep").mkdir(parents=True)
        (outside / "deep" / "x.md").write_text("# X\n", encoding="utf-8")
        (self.skill / "linked").symlink_to(outside, target_is_directory=True)
        (outside / "deep" / "back").symlink_to(outside, target_is_directory=True)
        _, report = run(self.skill, "--list")
        paths = [f["path"] for f in report["files"]]
        self.assertIn("linked/deep/x.md", paths)
        self.assertIn("symlink loop", [n["reason"] for n in report["not_listed"]])

    def test_no_skill_md_is_bad_input(self) -> None:
        code, _ = run(self.root, "--list")
        self.assertEqual(code, 2)


class Output(SkillCase):
    def test_text_format_and_utf8(self) -> None:
        self.skill_md("name: demo-skill\ndescription: Formatea notas «rápido». Use when asked.\n")
        proc = subprocess.run(
            [sys.executable, str(CHECKER), "--format", "text", str(self.skill)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Summary:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
