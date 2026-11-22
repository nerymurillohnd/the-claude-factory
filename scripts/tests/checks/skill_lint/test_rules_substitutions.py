"""Tests for the substitution rules: CA-05 (argument placeholders) and CA-06 (path variables)."""

from pathlib import Path
import tempfile
import unittest

from scripts.checks.skill_lint.model import Severity, SkillKind
from scripts.checks.skill_lint.rules_substitutions import check
from scripts.tests.checks.skill_lint.helpers import build_skill, load


def _skill_md(body: str, extra: str = "") -> str:
    """Return a valid SKILL.md with optional extra frontmatter and the given body."""
    head = f"---\nname: demo-skill\ndescription: Demo skill. Use when testing.\n{extra}---\n"
    return head + "\n# Demo\n\n" + body


def _found(
    files: dict[str, str], layout: SkillKind = "plugin"
) -> list[tuple[str, Severity, str, int | None]]:
    """Build a skill and return its (rule, severity, path, line) findings."""
    with tempfile.TemporaryDirectory() as tmp:
        skill = load(build_skill(Path(tmp), files, layout=layout))
        return [(f.rule, f.severity, f.path, f.line) for f in check(skill)]


def _rules(files: dict[str, str], layout: SkillKind = "plugin") -> list[str]:
    """Build a skill and return only its rule ids."""
    return [rule for rule, *_ in _found(files, layout)]


class ArgumentPlaceholderTest(unittest.TestCase):
    """CA-05: an argument placeholder in a skill that declares no arguments."""

    def test_dollar_digit_in_prose(self) -> None:
        """A dollar sign before a digit in prose is an error on its own line."""
        found = _found({"SKILL.md": _skill_md("It stops as partial at $0 cost.\n")})
        self.assertEqual(found, [("CA-05", Severity.ERROR, "SKILL.md", 8)])

    def test_arguments_in_inline_code(self) -> None:
        """$ARGUMENTS inside inline code is still replaced."""
        self.assertEqual(
            _rules({"SKILL.md": _skill_md("A prompt hook's `$ARGUMENTS` holds the input.\n")}),
            ["CA-05"],
        )

    def test_indexed_arguments(self) -> None:
        """$ARGUMENTS[N] is a placeholder too."""
        self.assertEqual(_rules({"SKILL.md": _skill_md("Read $ARGUMENTS[1] first.\n")}), ["CA-05"])

    def test_placeholder_in_a_fence_reports_its_own_line(self) -> None:
        """A placeholder inside a code fence is reported on the line that holds it."""
        body = "Run:\n\n```bash\nawk '{print $1}' file\n```\n"
        found = _found({"SKILL.md": _skill_md(body)})
        self.assertEqual(found, [("CA-05", Severity.ERROR, "SKILL.md", 11)])

    def test_single_backslash_escapes(self) -> None:
        """One backslash before the token keeps it literal."""
        body = "Costs \\$1.00 and keeps `\\$ARGUMENTS`.\n"
        self.assertEqual(_found({"SKILL.md": _skill_md(body)}), [])

    def test_double_backslash_does_not_escape(self) -> None:
        """Two backslashes leave the placeholder live."""
        self.assertEqual(
            _rules({"SKILL.md": _skill_md("A doubled \\\\$1 still expands.\n")}), ["CA-05"]
        )

    def test_declared_arguments_are_intended(self) -> None:
        """A skill that declares arguments or an argument hint uses placeholders on purpose."""
        for extra in ("argument-hint: '[issue]'\n", "arguments: issue branch\n"):
            with self.subTest(extra=extra):
                files = {"SKILL.md": _skill_md("Fix issue $0 on $ARGUMENTS.\n", extra)}
                self.assertEqual(_found(files), [])

    def test_injected_command_is_left_to_ca01(self) -> None:
        """Placeholders inside ! commands belong to CA-01."""
        body = "Status: !`git log -1 $ARGUMENTS`\n\n```!\necho $0\n```\n"
        self.assertEqual(_found({"SKILL.md": _skill_md(body)}), [])

    def test_frontmatter_and_references_are_not_rendered(self) -> None:
        """Only the SKILL.md body is substituted, so reference files are never findings."""
        files = {
            "SKILL.md": _skill_md("See [the reference](references/r.md).\n"),
            "references/r.md": "# R\n\nawk '{print $0}' and `$ARGUMENTS`.\n",
        }
        self.assertEqual(_found(files), [])

    def test_shell_variables_are_not_placeholders(self) -> None:
        """Ordinary shell variables are not argument placeholders."""
        body = "Use `$HOME`, `${var}` and `$PATH`.\n"
        self.assertEqual(_found({"SKILL.md": _skill_md(body)}), [])


class PathVariableTest(unittest.TestCase):
    """CA-06: a path variable written as a bare name."""

    def test_bare_plugin_root_in_a_plugin_skill(self) -> None:
        """A bare plugin-root variable in a plugin skill is a warning on its line."""
        found = _found({"SKILL.md": _skill_md("Quote `${CLAUDE_PLUGIN_ROOT}` in shell form.\n")})
        self.assertEqual(found, [("CA-06", Severity.WARNING, "SKILL.md", 8)])

    def test_path_uses_are_intended(self) -> None:
        """A variable followed by a path, quoted or not, is the intended use."""
        body = (
            "Run `${CLAUDE_SKILL_DIR}/scripts/a.sh`.\n"
            'Or `"${CLAUDE_PLUGIN_ROOT}"/scripts/b.sh` and ${CLAUDE_PROJECT_DIR}/x.\n'
        )
        self.assertEqual(_found({"SKILL.md": _skill_md(body)}), [])

    def test_a_variable_inside_a_command_is_a_value(self) -> None:
        """Inside a fenced block or a longer inline command, the variable is used as a value."""
        body = (
            "```bash\npython3 run.py --data-dir ${CLAUDE_PLUGIN_DATA} x\n```\n\n"
            "Run `tool --root ${CLAUDE_PLUGIN_ROOT} --check`.\n"
        )
        self.assertEqual(_found({"SKILL.md": _skill_md(body)}), [])

    def test_bare_variable_in_prose(self) -> None:
        """A variable written in prose, outside any code, is named rather than used."""
        files = {"SKILL.md": _skill_md("Claude Code substitutes ${CLAUDE_SKILL_DIR} here.\n")}
        self.assertEqual(_rules(files), ["CA-06"])

    def test_value_variables_are_intended(self) -> None:
        """The session id and effort variables exist to be read as values."""
        body = "Effort is ${CLAUDE_EFFORT}; session ${CLAUDE_SESSION_ID}.\n"
        self.assertEqual(_found({"SKILL.md": _skill_md(body)}), [])

    def test_plugin_variables_outside_a_plugin_are_left_to_po01(self) -> None:
        """Outside a plugin the plugin variables are not substituted; PO-01 owns them."""
        files = {"SKILL.md": _skill_md("Quote `${CLAUDE_PLUGIN_ROOT}` here.\n")}
        self.assertEqual(_found(files, layout="project"), [])

    def test_bare_project_dir_in_a_project_skill(self) -> None:
        """The project-dir variable is substituted in every skill."""
        files = {"SKILL.md": _skill_md("The hook reads `${CLAUDE_PROJECT_DIR}`.\n")}
        self.assertEqual(_rules(files, layout="project"), ["CA-06"])


if __name__ == "__main__":
    _ = unittest.main()
