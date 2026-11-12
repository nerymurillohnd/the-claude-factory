"""Tests for the content rules."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.discover import load_skill
from validators.skill_lint.model import Finding, Severity
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

    def test_non_utf8_skill_md_reports_co01(self) -> None:
        """A SKILL.md that is not UTF-8 gives CO-01 without raising."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": b"---\nname: \xff\xfe\n---\n"})
            findings = check(load_skill(skill / "SKILL.md", mode_reader=lambda _: {}))
        self.assertEqual([f.rule for f in findings], ["CO-01"])
        self.assertIn("not valid UTF-8", findings[0].message)


def _skill_md(frontmatter: str, body: str = "# Demo\n") -> str:
    """Return a SKILL.md with the given frontmatter lines and body."""
    return f"---\n{frontmatter}---\n\n{body}"


def _findings(content: str, name: str = "demo-skill") -> list[Finding]:
    """Build a skill with this SKILL.md in a folder called name and check it."""
    with tempfile.TemporaryDirectory() as tmp:
        skill = build_skill(Path(tmp), {"SKILL.md": content}, name=name)
        return check(load_skill(skill / "SKILL.md", mode_reader=lambda _: {}))


def _rules(content: str, name: str = "demo-skill") -> list[str]:
    """Return the rule ids found in this SKILL.md."""
    return [f.rule for f in _findings(content, name)]


class Co02Test(unittest.TestCase):
    """CO-02: the name."""

    def test_co02_missing_name(self) -> None:
        """A missing name is reported on line 1."""
        findings = _findings(_skill_md("description: Does a thing.\n"))
        self.assertEqual([f.rule for f in findings], ["CO-02"])
        self.assertEqual(findings[0].line, 1)
        self.assertEqual(findings[0].severity, Severity.ERROR)

    def test_co02_bad_chars(self) -> None:
        """Uppercase and underscore give a charset and a folder-mismatch finding."""
        findings = _findings(_skill_md("name: Demo_Skill\ndescription: Ok.\n"))
        self.assertEqual([f.rule for f in findings], ["CO-02", "CO-02"])
        self.assertEqual(findings[0].line, 2)

    def test_co02_double_hyphen(self) -> None:
        """A double hyphen fails."""
        content = _skill_md("name: demo--skill\ndescription: Ok.\n")
        self.assertEqual(_rules(content, "demo--skill"), ["CO-02"])

    def test_co02_length(self) -> None:
        """A 65-character name fails once."""
        name = "a" * 65
        content = _skill_md(f"name: {name}\ndescription: Ok.\n")
        self.assertEqual(_rules(content, name), ["CO-02"])

    def test_co02_folder_mismatch(self) -> None:
        """A valid name that differs from the folder fails."""
        content = _skill_md("name: other\ndescription: Ok.\n")
        self.assertEqual(_rules(content), ["CO-02"])

    def test_co02_zero_width(self) -> None:
        """A zero-width space in the name fails once when the folder matches."""
        name = "demo\u200b-skill"
        content = _skill_md(f'name: "{name}"\ndescription: Ok.\n')
        self.assertEqual(_rules(content, name), ["CO-02"])

    def test_co02_malformed_and_mismatch(self) -> None:
        """A malformed name that also differs from its folder gives both findings."""
        findings = _findings(_skill_md("name: Demo_Skill\ndescription: Ok.\n"))
        messages = [f.message for f in findings]
        self.assertEqual(len(findings), 2)
        self.assertTrue(any("invalid" in m for m in messages))
        self.assertTrue(any("folder name" in m for m in messages))

    def test_co02_64_ok(self) -> None:
        """A 64-character name in a matching folder passes."""
        name = "a" * 64
        self.assertEqual(_rules(_skill_md(f"name: {name}\ndescription: Ok.\n"), name), [])

    def test_co02_non_string(self) -> None:
        """A numeric name gives a finding without raising."""
        self.assertEqual(_rules(_skill_md("name: 123\ndescription: Ok.\n")), ["CO-02"])


class Co03Test(unittest.TestCase):
    """CO-03: the description."""

    def test_co03_empty(self) -> None:
        """An empty description fails."""
        content = _skill_md('name: demo-skill\ndescription: ""\n')
        self.assertEqual(_rules(content), ["CO-03"])

    def test_co03_1025(self) -> None:
        """A 1,025-character description fails."""
        content = _skill_md(f"name: demo-skill\ndescription: {'a' * 1025}\n")
        self.assertEqual(_rules(content), ["CO-03"])

    def test_co03_1024_ok(self) -> None:
        """A 1,024-character description passes."""
        content = _skill_md(f"name: demo-skill\ndescription: {'a' * 1024}\n")
        self.assertEqual(_rules(content), [])

    def test_co03_non_string(self) -> None:
        """A list description gives a finding without raising."""
        content = _skill_md("name: demo-skill\ndescription: [a]\n")
        self.assertEqual(_rules(content), ["CO-03"])

    def test_co03_xml(self) -> None:
        """An XML tag in the description fails."""
        content = _skill_md("name: demo-skill\ndescription: Use <tag> here.\n")
        self.assertEqual(_rules(content), ["CO-03"])


class Co04Test(unittest.TestCase):
    """CO-04: the listing budget."""

    def test_co04_1537(self) -> None:
        """1,537 characters across description and when_to_use say truncated."""
        content = _skill_md(
            f"name: demo-skill\ndescription: {'a' * 1000}\nwhen_to_use: {'b' * 537}\n"
        )
        findings = _findings(content)
        self.assertEqual([f.rule for f in findings], ["CO-04"])
        self.assertIn("truncated", findings[0].message)

    def test_co04_1536_ok(self) -> None:
        """Exactly 1,536 characters pass."""
        content = _skill_md(
            f"name: demo-skill\ndescription: {'a' * 1000}\nwhen_to_use: {'b' * 536}\n"
        )
        self.assertEqual(_rules(content), [])


class Co05Test(unittest.TestCase):
    """CO-05: compatibility and metadata."""

    def test_co05_compat_501(self) -> None:
        """A 501-character compatibility fails."""
        content = _skill_md(f"name: demo-skill\ndescription: Ok.\ncompatibility: {'a' * 501}\n")
        self.assertEqual(_rules(content), ["CO-05"])

    def test_co05_compat_499_ok(self) -> None:
        """A 499-character compatibility passes."""
        content = _skill_md(f"name: demo-skill\ndescription: Ok.\ncompatibility: {'a' * 499}\n")
        self.assertEqual(_rules(content), [])

    def test_co05_compat_empty(self) -> None:
        """An empty compatibility fails."""
        content = _skill_md('name: demo-skill\ndescription: Ok.\ncompatibility: ""\n')
        self.assertEqual(_rules(content), ["CO-05"])

    def test_co05_compat_null(self) -> None:
        """A null compatibility fails."""
        content = _skill_md("name: demo-skill\ndescription: Ok.\ncompatibility:\n")
        self.assertEqual(_rules(content), ["CO-05"])

    def test_co05_metadata_null(self) -> None:
        """A null metadata fails."""
        content = _skill_md("name: demo-skill\ndescription: Ok.\nmetadata:\n")
        self.assertEqual(_rules(content), ["CO-05"])

    def test_co05_metadata_non_string(self) -> None:
        """A metadata value that is not a string fails."""
        content = _skill_md("name: demo-skill\ndescription: Ok.\nmetadata:\n  a: 1\n")
        self.assertEqual(_rules(content), ["CO-05"])


def _no_blank(body: str) -> str:
    """Return a valid SKILL.md whose body starts on the line after the closing fence."""
    return f"---\nname: demo-skill\ndescription: Ok.\n---\n{body}"


class Co06Test(unittest.TestCase):
    """CO-06: the body length."""

    def test_co06_body_500_fails(self) -> None:
        """A body of exactly 500 lines fails."""
        content = _no_blank("line\n" * 500)
        self.assertEqual(_rules(content), ["CO-06"])

    def test_co06_body_499_ok(self) -> None:
        """A body of 499 lines passes."""
        content = _no_blank("line\n" * 499)
        self.assertEqual(_rules(content), [])


class CleanTest(unittest.TestCase):
    """The valid skill and CO-01 gating."""

    def test_valid_skill_clean(self) -> None:
        """The valid skill has no CO-02 to CO-06 findings."""
        self.assertEqual(_rules(VALID_SKILL_MD), [])

    def test_co01_failure_skips_later_rules(self) -> None:
        """When the frontmatter fails to parse, only CO-01 is reported."""
        self.assertEqual(_rules("# no frontmatter\n"), ["CO-01"])
