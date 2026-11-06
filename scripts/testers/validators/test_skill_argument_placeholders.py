"""scripts/validators/skill-argument-placeholders.py: a bare $N in a SKILL.md body fails.

Each test runs the validator by path on a small repository under a temporary directory
(TCF_ROOT); the last one runs it on this repository, which must pass. The forms and their
expected verdicts are the ones observed on Claude Code 2.1.319 (see the validator's docstring).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import override
import unittest

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "scripts" / "validators" / "skill-argument-placeholders.py"
ERROR = "✖ ["
ARGUMENT_2 = '"$ARGUMENTS[2]" for the argument'
LITERAL_2 = '"\\$2" for a literal "$2"'
SHELL_2 = '"${2}" for a shell parameter'
PROBLEM_2 = 'bare "$2" is replaced by the skill\'s argument 2'
MESSAGE_FOR_2 = f"{PROBLEM_2}; write {ARGUMENT_2}, {LITERAL_2}, or {SHELL_2}"

# Body lines Claude Code replaces: each must fail, at the column of its `$`.
BARE = {
    "A=$1": 3,
    "J=x$1": 4,
    "L=$1.00": 3,
    "N=$1-z": 3,
    "O=($1)": 4,
    "P=$1é": 3,
    "Q=$01": 3,
    "E=$10": 3,
    "awk '{print $0}'": 13,
    "C=\\\\$1": 5,
    "G=\\\\\\$1": 6,
}
# Body lines Claude Code leaves as written, or that name the argument explicitly: each passes.
KEPT = (
    "B=\\$1",
    "D=${1}",
    "H=$ARGUMENTS[1]",
    "K=$1y",
    "M=$1_",
    "R=$ARGUMENTS",
    "S=$HOME",
    "T=$",
)


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """The validator's run on `root`, with its output as text."""
    env = {**os.environ, "TCF_ROOT": str(root)}
    return subprocess.run(
        [str(VALIDATOR), *args], capture_output=True, text=True, env=env, check=False
    )


def errors(stderr: str) -> dict[str, list[str]]:
    """Each error line of `stderr` as {scope: [message, ...]}."""
    found: dict[str, list[str]] = {}
    for line in stderr.splitlines():
        if line.startswith(ERROR):
            scope, _, message = line.removeprefix(ERROR).partition("] ")
            found.setdefault(scope, []).append(message)
    return found


def skill(directory: Path, body: str, frontmatter: str = "name: x\ndescription: A skill.") -> None:
    """Write `directory`/SKILL.md with `frontmatter` and `body`."""
    directory.mkdir(parents=True, exist_ok=True)
    text = f"---\n{frontmatter}\n---\n{body}"
    _ = (directory / "SKILL.md").write_text(text, encoding="utf-8")


class SkillArgumentPlaceholdersTests(unittest.TestCase):
    """The validator on small repositories under a temporary directory, then on this one."""

    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name).resolve()
        (self.tmp / "plugins").mkdir()

    def test_each_form(self) -> None:
        """Each bare form fails at its line and column; each kept form passes."""
        lines = [*BARE, *KEPT]
        skill(self.tmp / "plugins" / "p" / "skills" / "forms", "\n".join(lines) + "\n")
        result = run(self.tmp)
        self.assertEqual(result.returncode, 1, msg=result.stderr)
        found = errors(result.stderr)
        prefix = "plugins/p/skills/forms/SKILL.md"
        # The body starts on line 5, after the four frontmatter lines.
        want = {f"{prefix}:{5 + i}:{column}" for i, column in enumerate(BARE.values())}
        self.assertEqual(set(found), want, msg=found)
        for scope, messages in found.items():
            self.assertEqual(len(messages), 1, msg=(scope, messages))

    def test_message_names_the_fixes(self) -> None:
        """The message names the argument, the literal and the shell forms."""
        skill(self.tmp / "plugins" / "p" / "skills" / "one", "Run $2.\n")
        found = errors(run(self.tmp).stderr)
        self.assertEqual(
            found,
            {"plugins/p/skills/one/SKILL.md:5:5": [MESSAGE_FOR_2]},
            msg=found,
        )

    def test_frontmatter_is_not_read(self) -> None:
        """A $N in the frontmatter passes: Claude Code does not substitute it."""
        skill(
            self.tmp / "plugins" / "p" / "skills" / "front",
            "Body.\n",
            "name: front\ndescription: Costs $5 per run, see $1.",
        )
        result = run(self.tmp)
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_no_frontmatter_reads_the_whole_file(self) -> None:
        """A SKILL.md with no frontmatter is all body."""
        path = self.tmp / "plugins" / "p" / "skills" / "bare"
        path.mkdir(parents=True)
        _ = (path / "SKILL.md").write_text("Use $1.\n", encoding="utf-8")
        found = errors(run(self.tmp).stderr)
        self.assertEqual(list(found), ["plugins/p/skills/bare/SKILL.md:1:5"], msg=found)

    def test_every_skill_location(self) -> None:
        """Plugin default, manifest-listed, plugin-root and project skills are all read."""
        plugin = self.tmp / "plugins" / "p"
        skill(plugin / "skills" / "default", "$1\n")
        skill(plugin / "extra" / "listed", "$1\n")
        skill(plugin, "$1\n")
        (plugin / ".claude-plugin").mkdir()
        manifest = json.dumps({"name": "p", "skills": ["./extra", "./"]})
        _ = (plugin / ".claude-plugin" / "plugin.json").write_text(manifest, encoding="utf-8")
        skill(self.tmp / ".claude" / "skills" / "project", "$1\n")
        found = errors(run(self.tmp).stderr)
        self.assertEqual(
            set(found),
            {
                "plugins/p/skills/default/SKILL.md:5:1",
                "plugins/p/extra/listed/SKILL.md:5:1",
                "plugins/p/SKILL.md:5:1",
                ".claude/skills/project/SKILL.md:5:1",
            },
            msg=found,
        )

    def test_passing_repository_counts_its_skills(self) -> None:
        """A passing repository counts its SKILL.md files."""
        skill(self.tmp / "plugins" / "p" / "skills" / "one", "${1}\n")
        skill(self.tmp / ".claude" / "skills" / "two", "\\$1\n")
        result = run(self.tmp)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("✔ 2 SKILL.md", result.stdout)

    def test_arguments_are_refused(self) -> None:
        """Any argument is a usage error."""
        result = run(self.tmp, "extra")
        self.assertEqual(result.returncode, 2, msg=result.stderr)

    def test_this_repository_passes(self) -> None:
        """This repository passes."""
        result = subprocess.run([str(VALIDATOR)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, msg=result.stderr)


if __name__ == "__main__":
    _ = unittest.main()
