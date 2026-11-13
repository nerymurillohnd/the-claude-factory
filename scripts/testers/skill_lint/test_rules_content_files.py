#!/usr/bin/env python3
"""Tests for the content rules on links, reference depth and files (CO-07 to CO-12)."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.model import Severity
from validators.skill_lint.rules_content_files import check

from testers.skill_lint.helpers import build_skill, load

HEAD = "---\nname: demo-skill\ndescription: Demo skill. Use when testing.\n---\n\n# Demo\n\n"


def _skill_md(body: str) -> str:
    """Return a valid SKILL.md with the given body after its heading."""
    return HEAD + body


def _lines(count: int) -> str:
    """Return count numbered text lines."""
    return "".join(f"line {i}\n" for i in range(count))


class LinkRulesTest(unittest.TestCase):
    """CO-07 and CO-08 on links and paths."""

    def _rules(self, files: dict[str, str]) -> list[str]:
        """Build a skill and return the rule ids it reports."""
        with tempfile.TemporaryDirectory() as tmp:
            return [f.rule for f in check(load(build_skill(Path(tmp), files)))]

    def test_co07_missing_file(self) -> None:
        """A link to a missing file is CO-07."""
        rules = self._rules({"SKILL.md": _skill_md("See [x](references/none.md).\n")})
        self.assertEqual(rules, ["CO-07"])

    def test_co07_missing_anchor(self) -> None:
        """A link to a missing anchor in another file is CO-07."""
        files = {
            "SKILL.md": _skill_md("See [x](references/a.md#nope).\n"),
            "references/a.md": "# A\n\n## Real\n",
        }
        self.assertEqual(self._rules(files), ["CO-07"])

    def test_co07_existing_anchor_ok(self) -> None:
        """A link to an existing anchor in another file is fine."""
        files = {
            "SKILL.md": _skill_md("See [x](references/a.md#real-one).\n"),
            "references/a.md": "# A\n\n## Real one\n",
        }
        self.assertEqual(self._rules(files), [])

    def test_co07_same_file_anchor(self) -> None:
        """A same-file anchor resolves against the file's own headings."""
        ok = self._rules({"SKILL.md": _skill_md("See [x](#demo).\n")})
        bad = self._rules({"SKILL.md": _skill_md("See [x](#missing).\n")})
        self.assertEqual((ok, bad), ([], ["CO-07"]))

    def test_co07_assets_template_links_ignored(self) -> None:
        """Links in an assets/ template point into the document it produces, so CO-07 skips them."""
        files = {
            "SKILL.md": _skill_md("Fill [t](assets/t.md).\n"),
            "assets/t.md": "# {{name}}\n\nSee [log](./CHANGELOG.md) and [x](#nope).\n",
        }
        self.assertEqual(self._rules(files), [])

    def test_co07_assets_without_placeholder_checked(self) -> None:
        """An assets/ file with no placeholder is not a template, so CO-07 still applies."""
        files = {
            "SKILL.md": _skill_md("Read [e](assets/e.md).\n"),
            "assets/e.md": "# E\n\nSee [x](references/none.md).\n",
        }
        self.assertEqual(self._rules(files), ["CO-07"])

    def test_co08_assets_template_escape_still_reported(self) -> None:
        """A link that leaves the skill folder from assets/ is still CO-08."""
        files = {
            "SKILL.md": _skill_md("Fill [t](assets/t.md).\n"),
            "assets/t.md": "# {{name}}\n\nSee [x](../../other.md).\n",
        }
        self.assertEqual(self._rules(files), ["CO-08"])

    def test_co08_dotdot_link(self) -> None:
        """A link that leaves the skill folder is CO-08, not CO-07."""
        rules = self._rules({"SKILL.md": _skill_md("See [x](../other/SKILL.md).\n")})
        self.assertEqual(rules, ["CO-08"])

    def test_co08_code_path_escape(self) -> None:
        """A `../` path in code that leaves the folder is CO-08."""
        body = "```bash\npython3 ../../shared/run.py\n```\n"
        self.assertEqual(self._rules({"SKILL.md": _skill_md(body)}), ["CO-08"])

    def test_co08_symlink_outside(self) -> None:
        """A symlink inside the skill that points outside is CO-08 (Review Focus 4)."""
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside.md"
            _ = outside.write_text("# Outside\n", encoding="utf-8")
            skill = build_skill(Path(tmp), {"SKILL.md": _skill_md("See [x](references/x.md).\n")})
            (skill / "references").mkdir()
            (skill / "references" / "x.md").symlink_to(outside)
            findings = check(load(skill))
        self.assertIn(("CO-08", "references/x.md"), [(f.rule, f.path) for f in findings])


class DepthAndFileRulesTest(unittest.TestCase):
    """CO-09, CO-10 and CO-12."""

    def _findings(self, files: dict[str, str]) -> list[tuple[str, str]]:
        """Build a skill and return (rule, path) pairs."""
        with tempfile.TemporaryDirectory() as tmp:
            return [(f.rule, f.path) for f in check(load(build_skill(Path(tmp), files)))]

    def test_co09_depth_two(self) -> None:
        """A Markdown file reached only through another file is CO-09, not CO-12."""
        files = {
            "SKILL.md": _skill_md("See [a](references/a.md).\n"),
            "references/a.md": "# A\n\nSee [b](b.md).\n",
            "references/b.md": "# B\n",
        }
        self.assertEqual(self._findings(files), [("CO-09", "references/b.md")])

    def test_co10_toc_missing(self) -> None:
        """A 101-line reference with no table of contents is CO-10."""
        files = {
            "SKILL.md": _skill_md("See [a](references/a.md).\n"),
            "references/a.md": "# A\n" + _lines(100),
        }
        self.assertEqual(self._findings(files), [("CO-10", "references/a.md")])

    def test_co10_toc_present(self) -> None:
        """Two in-file anchor links after the first heading count as a table of contents."""
        toc = "# A\n\n- [One](#one)\n- [Two](#two)\n\n## One\n\n## Two\n"
        files = {
            "SKILL.md": _skill_md("See [a](references/a.md).\n"),
            "references/a.md": toc + _lines(100),
        }
        self.assertEqual(self._findings(files), [])

    def test_co10_assets_template_exempt(self) -> None:
        """A long assets/ template is output, not a reference to navigate, so CO-10 skips it."""
        files = {
            "SKILL.md": _skill_md("Fill [t](assets/t.md).\n"),
            "assets/t.md": "# {{name}}\n" + _lines(200),
        }
        self.assertEqual(self._findings(files), [])

    def test_co10_assets_without_placeholder_checked(self) -> None:
        """A long assets/ file with no placeholder, such as examples, still needs a TOC."""
        files = {
            "SKILL.md": _skill_md("Read [e](assets/e.md).\n"),
            "assets/e.md": "# E\n" + _lines(200),
        }
        self.assertEqual(self._findings(files), [("CO-10", "assets/e.md")])

    def test_co10_100_lines_ok(self) -> None:
        """A 100-line reference needs no table of contents."""
        files = {
            "SKILL.md": _skill_md("See [a](references/a.md).\n"),
            "references/a.md": "# A\n" + _lines(99),
        }
        self.assertEqual(self._findings(files), [])

    def test_co12_orphan(self) -> None:
        """A file nothing references is a CO-12 warning."""
        with tempfile.TemporaryDirectory() as tmp:
            files = {"SKILL.md": _skill_md("Hello.\n"), "assets/unused.txt": "x\n"}
            findings = check(load(build_skill(Path(tmp), files)))
        self.assertEqual([(f.rule, f.severity) for f in findings], [("CO-12", Severity.WARNING)])

    def test_co12_exemptions(self) -> None:
        """Evals, __init__.py and __pycache__ files are never orphans."""
        files = {
            "SKILL.md": _skill_md("Hello.\n"),
            "evals/evals.json": "{}\n",
            "scripts/__init__.py": "",
            "scripts/__pycache__/a.pyc": "x",
        }
        self.assertEqual(self._findings(files), [])

    def test_co12_binary_referenced_ok(self) -> None:
        """A binary file linked from SKILL.md is referenced."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": _skill_md("![a](assets/a.png)\n")})
            (skill / "assets").mkdir()
            _ = (skill / "assets" / "a.png").write_bytes(b"\x89PNG\x00")
            self.assertEqual(check(load(skill)), [])

    def test_co12_script_named_in_code_ok(self) -> None:
        """A script run from a code block is referenced."""
        files = {
            "SKILL.md": _skill_md("```bash\npython3 scripts/run.py\n```\n"),
            "scripts/run.py": "#!/usr/bin/env python3\n",
        }
        self.assertEqual(self._findings(files), [])


class TimeSensitiveTest(unittest.TestCase):
    """CO-11."""

    def _rules(self, body: str) -> list[tuple[str, Severity]]:
        """Return the (rule, severity) pairs for a SKILL.md body."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": _skill_md(body)})
            return [(f.rule, f.severity) for f in check(load(skill))]

    def test_co11_dated_conditional(self) -> None:
        """A dated conditional is a CO-11 warning."""
        self.assertEqual(self._rules("Before March 2026, use X.\n"), [("CO-11", Severity.WARNING)])

    def test_co11_other_forms(self) -> None:
        """'currently ... 2026' and 'in 2025' are CO-11."""
        self.assertEqual(len(self._rules("Currently the API (2026) is stable.\n")), 1)
        self.assertEqual(len(self._rules("This changed in 2025.\n")), 1)

    def test_co11_in_code_ignored(self) -> None:
        """The same text inside a fence is ignored."""
        self.assertEqual(self._rules("```text\nBefore March 2026, use X.\n```\n"), [])

    def test_co11_plain_year_ok(self) -> None:
        """A bare year without a time-sensitive phrase is fine."""
        self.assertEqual(self._rules("Version 2026.1 is the format.\n"), [])


if __name__ == "__main__":
    _ = unittest.main()
