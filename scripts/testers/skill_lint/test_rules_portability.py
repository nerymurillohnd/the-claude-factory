#!/usr/bin/env python3
"""Tests for the portability rules (PO)."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.model import Severity, SkillKind
from validators.skill_lint.rules_portability import check

from testers.skill_lint.helpers import build_skill, load


def _skill_md(body: str = "Hello.\n", extra: str = "", name: str = "demo-skill") -> str:
    """Return a SKILL.md with optional extra frontmatter lines and a body."""
    head = (
        f"---\nname: {name}\ndescription: Demo skill. Use when testing.\n{extra}---\n\n# Demo\n\n"
    )
    return head + body


def _run(
    files: dict[str, str], *, layout: SkillKind = "plugin", name: str = "demo-skill"
) -> list[tuple[str, Severity]]:
    """Build a skill and return the (rule, severity) pairs it reports."""
    with tempfile.TemporaryDirectory() as tmp:
        skill = build_skill(Path(tmp), files, layout=layout, name=name)
        return [(f.rule, f.severity) for f in check(load(skill))]


class PortabilityTest(unittest.TestCase):
    """PO-01 to PO-07."""

    def test_valid_skill_clean(self) -> None:
        """A plain skill gives no findings."""
        self.assertEqual(_run({"SKILL.md": _skill_md()}), [])

    def test_po01_plugin_root_in_project_skill(self) -> None:
        """`${CLAUDE_PLUGIN_ROOT}` in a project skill is PO-01."""
        files = {"SKILL.md": _skill_md("Run `${CLAUDE_PLUGIN_ROOT}/x.sh`.\n")}
        self.assertEqual(_run(files, layout="project"), [("PO-01", Severity.ERROR)])

    def test_po01_plugin_data_in_script(self) -> None:
        """`$CLAUDE_PLUGIN_DATA` in a script of a standalone skill is PO-01."""
        files = {"SKILL.md": _skill_md(), "scripts/a.sh": 'cd "$CLAUDE_PLUGIN_DATA"\n'}
        self.assertEqual(_run(files, layout="standalone"), [("PO-01", Severity.ERROR)])

    def test_po01_ok_in_plugin(self) -> None:
        """The same variable in a plugin skill is fine."""
        files = {"SKILL.md": _skill_md("Run `${CLAUDE_PLUGIN_ROOT}/x.sh`.\n")}
        self.assertEqual(_run(files), [])

    def test_po02_backslash_link(self) -> None:
        """A backslash in a link target is PO-02."""
        files = {"SKILL.md": _skill_md("See [a](references\\a.md).\n")}
        self.assertEqual(_run(files), [("PO-02", Severity.ERROR)])

    def test_po02_backslash_script_path(self) -> None:
        """A backslash in a script path in code is PO-02."""
        files = {"SKILL.md": _skill_md("```bash\npython scripts\\run.py\n```\n")}
        self.assertEqual(_run(files), [("PO-02", Severity.ERROR)])

    def test_po02_escape_in_code_ok(self) -> None:
        """A shell escape such as a newline escape in code is not a path."""
        files = {"SKILL.md": _skill_md('```bash\nprintf "a\\n"\n```\n')}
        self.assertEqual(_run(files), [])

    def test_po03_extra_fields(self) -> None:
        """Fields outside the spec give one PO-03 warning naming each of them."""
        extra = "when_to_use: Use it.\ndisable-model-invocation: true\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": _skill_md(extra=extra)})
            findings = check(load(skill))
        self.assertEqual([f.rule for f in findings], ["PO-03"])
        self.assertIn("`when_to_use`", findings[0].message)
        self.assertIn("`disable-model-invocation`", findings[0].message)
        self.assertEqual(findings[0].line, 4)

    def test_po04_bang(self) -> None:
        """An inline and a block injected command give two PO-04 warnings."""
        body = "Status: !`git status`\n\n```!\ngit log -1\n```\n"
        self.assertEqual(_run({"SKILL.md": _skill_md(body)}), [("PO-04", Severity.WARNING)] * 2)

    def test_po06_allowed_tools_list(self) -> None:
        """`allowed-tools` as a YAML list is PO-06."""
        files = {"SKILL.md": _skill_md(extra="allowed-tools: [Read, Grep]\n")}
        self.assertEqual(_run(files), [("PO-06", Severity.WARNING)])

    def test_po06_string_ok(self) -> None:
        """`allowed-tools` as a string is fine."""
        self.assertEqual(_run({"SKILL.md": _skill_md(extra="allowed-tools: Read Grep\n")}), [])

    def test_po07_reserved_word(self) -> None:
        """A name containing `claude` is a PO-07 warning."""
        files = {"SKILL.md": _skill_md(name="claude-helper")}
        self.assertEqual(_run(files, name="claude-helper"), [("PO-07", Severity.WARNING)])

    def test_no_po05_ever(self) -> None:
        """A script reached only through `${CLAUDE_SKILL_DIR}` is fine: PO-05 is withdrawn."""
        body = "```bash\npython3 ${CLAUDE_SKILL_DIR}/scripts/run.py\n```\n"
        files = {"SKILL.md": _skill_md(body), "scripts/run.py": "#!/usr/bin/env python3\n"}
        self.assertEqual(_run(files), [])


if __name__ == "__main__":
    _ = unittest.main()
