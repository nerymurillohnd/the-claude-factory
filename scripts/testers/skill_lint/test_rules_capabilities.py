#!/usr/bin/env python3
"""Tests for the capability rules (CA) and the inventory."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from validators.skill_lint.model import Severity
from validators.skill_lint.rules_capabilities import Hook, check, inventory

from testers.skill_lint.helpers import build_skill, load

HOOKS = """hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: ./scripts/guard.sh
          once: true
"""


def _skill_md(body: str = "Hello.\n", extra: str = "") -> str:
    """Return a valid SKILL.md with optional extra frontmatter and a body."""
    head = f"---\nname: demo-skill\ndescription: Demo skill. Use when testing.\n{extra}---\n"
    return head + "\n# Demo\n\n" + body


def _rules(files: dict[str, str]) -> list[tuple[str, Severity]]:
    """Build a skill and return its (rule, severity) pairs."""
    with tempfile.TemporaryDirectory() as tmp:
        return [(f.rule, f.severity) for f in check(load(build_skill(Path(tmp), files)))]


class InventoryTest(unittest.TestCase):
    """CA-00: the inventory."""

    def test_inventory_lists_all(self) -> None:
        """Injected commands, hooks and allowed-tools entries are listed exactly."""
        extra = HOOKS + "allowed-tools: Read Bash(git status*)\n"
        files = {"SKILL.md": _skill_md("Now: !`date`\n", extra=extra)}
        with tempfile.TemporaryDirectory() as tmp:
            found = inventory(load(build_skill(Path(tmp), files)))
        self.assertEqual([(rel, b.command) for rel, b in found.bang], [("SKILL.md", "date")])
        hook = Hook("PreToolUse", "Bash", "command", "./scripts/guard.sh", once=True)
        self.assertEqual(found.hooks, (hook,))
        self.assertEqual(found.allowed_tools, ("Read", "Bash(git status*)"))

    def test_inventory_comma_separated_and_list(self) -> None:
        """allowed-tools also reads as comma-separated text or a YAML list."""
        with tempfile.TemporaryDirectory() as tmp:
            text = load(
                build_skill(Path(tmp), {"SKILL.md": _skill_md(extra="allowed-tools: Read, Grep\n")})
            )
        with tempfile.TemporaryDirectory() as tmp:
            listed = load(
                build_skill(Path(tmp), {"SKILL.md": _skill_md(extra="allowed-tools: [Read]\n")})
            )
        self.assertEqual(inventory(text).allowed_tools, ("Read", "Grep"))
        self.assertEqual(inventory(listed).allowed_tools, ("Read",))


class CapabilityRulesTest(unittest.TestCase):
    """CA-01 to CA-04."""

    def test_valid_skill_clean(self) -> None:
        """A plain skill gives no findings."""
        self.assertEqual(_rules({"SKILL.md": _skill_md()}), [])

    def test_ca01_arguments_placeholder(self) -> None:
        """$ARGUMENTS inside an injected command is CA-01."""
        files = {"SKILL.md": _skill_md("Found: !`grep $ARGUMENTS x`\n")}
        self.assertEqual(_rules(files), [("CA-01", Severity.ERROR)])

    def test_ca01_index_and_positional(self) -> None:
        """$ARGUMENTS[0] and $1 are CA-01."""
        files = {"SKILL.md": _skill_md("A: !`cat $ARGUMENTS[0]`\n\nB: !`cat $1`\n")}
        self.assertEqual(_rules(files), [("CA-01", Severity.ERROR)] * 2)

    def test_ca01_declared_name(self) -> None:
        """A declared argument name inside an injected command is CA-01."""
        files = {"SKILL.md": _skill_md("A: !`cat $file`\n", extra="arguments: [file]\n")}
        self.assertEqual(_rules(files), [("CA-01", Severity.ERROR)])

    def test_ca01_shell_vars_ok(self) -> None:
        """$HOME, $PATH and an undeclared $f are not placeholders."""
        files = {"SKILL.md": _skill_md("A: !`ls $HOME $PATH $f`\n")}
        self.assertEqual(_rules(files), [])

    def test_ca02_unscoped_bash(self) -> None:
        """Bash and Bash(*) are two CA-02 warnings."""
        files = {"SKILL.md": _skill_md(extra="allowed-tools: Bash Bash(*)\n")}
        self.assertEqual(_rules(files), [("CA-02", Severity.WARNING)] * 2)

    def test_ca03_self_approved(self) -> None:
        """An injected command the skill's own allowed-tools approves is CA-03."""
        extra = "allowed-tools: Bash(git status*)\n"
        files = {"SKILL.md": _skill_md("Now: !`git status`\n", extra=extra)}
        self.assertEqual(_rules(files), [("CA-03", Severity.WARNING)])

    def test_ca03_word_boundary_pattern(self) -> None:
        """`Bash(git status *)` approves `git status` and `git status -s`, not `git log`."""
        extra = "allowed-tools: Bash(git status *)\n"
        body = "A: !`git status`\n\nB: !`git status -s`\n\nC: !`git log`\n"
        self.assertEqual(
            _rules({"SKILL.md": _skill_md(body, extra=extra)}), [("CA-03", Severity.WARNING)] * 2
        )

    def test_ca04_network_in_script(self) -> None:
        """Curl in a shell script and requests in Python are two CA-04 warnings."""
        files = {
            "SKILL.md": _skill_md("Uses scripts/a.sh and scripts/b.py.\n"),
            "scripts/a.sh": "#!/usr/bin/env bash\ncurl -s https://example.com\n",
            "scripts/b.py": "import requests\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            findings = check(load(build_skill(Path(tmp), files)))
        self.assertEqual(
            [(f.rule, f.path, f.line) for f in findings],
            [("CA-04", "scripts/a.sh", 2), ("CA-04", "scripts/b.py", 1)],
        )

    def test_ca04_markdown_ignored(self) -> None:
        """Curl in SKILL.md is not a CA-04 finding."""
        files = {"SKILL.md": _skill_md("```bash\ncurl -s https://example.com\n```\n")}
        self.assertEqual(_rules(files), [])


if __name__ == "__main__":
    _ = unittest.main()
