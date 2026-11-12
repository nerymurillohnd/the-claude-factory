"""Tests for the skill-lint finding model."""

from __future__ import annotations

import unittest

from validators.skill_lint.model import Family, Finding, Severity


class FindingTest(unittest.TestCase):
    """The Finding record and its derived family."""

    def test_family_from_rule_prefix(self) -> None:
        """The family comes from the two-letter prefix of the rule id."""
        f = Finding("SC-02", Severity.ERROR, "scripts/x.sh", 1, "m", "https://e")
        self.assertIs(f.family, Family.SCRIPTS)
