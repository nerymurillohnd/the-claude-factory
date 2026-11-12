"""Tests for the content rules."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.discover import load_skill
from validators.skill_lint.model import Severity
from validators.skill_lint.rules_content import check

from testers.skill_lint.helpers import VALID_SKILL_MD, build_skill


class Co01Test(unittest.TestCase):
    """CO-01: the frontmatter parses."""

    def test_co01_reports_parse_error(self) -> None:
        """A missing opening fence is one CO-01 error on line 1."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": "# no frontmatter\n"})
            findings = check(load_skill(skill / "SKILL.md", mode_reader=lambda _: {}))
        self.assertEqual([f.rule for f in findings], ["CO-01"])
        self.assertEqual(findings[0].severity, Severity.ERROR)
        self.assertEqual(findings[0].line, 1)

    def test_valid_skill_has_no_co01(self) -> None:
        """A valid skill gives no findings."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            findings = check(load_skill(skill / "SKILL.md", mode_reader=lambda _: {}))
        self.assertEqual(findings, [])
