"""scripts/validators/skill-references.py: dead skill and path references fail, the rest pass.

Each test builds a small repository under a temporary directory and runs the validator's `check`
on it; the last one runs it on this repository, which must pass.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING, Protocol, cast, override
import unittest

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "scripts" / "validators" / "skill-references.py"


class Validator(Protocol):
    """The part of the validator module these tests call."""

    def check(self, root: Path) -> tuple[list[str], int]:
        """Every dead reference, in a stable order, and how many references were checked."""
        ...


def load() -> Validator:
    """The validator module, imported from its hyphenated file name."""
    spec = importlib.util.spec_from_file_location("skill_references", VALIDATOR)
    if spec is None or spec.loader is None:
        msg = f"cannot load {VALIDATOR}"
        raise ImportError(msg)
    module: ModuleType = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast("Validator", cast("object", module))


def repo(tmp_path: Path, skill_text: str, claude_md: str = "# Project\n") -> Path:
    """A repository with one project skill `alpha`, one plugin `beta` and the given texts."""
    skill = tmp_path / ".claude" / "skills" / "alpha"
    (skill / "scripts").mkdir(parents=True)
    _ = (skill / "scripts" / "run.py").write_text("")
    _ = (skill / "SKILL.md").write_text(skill_text)
    _ = (tmp_path / ".claude" / "CLAUDE.md").write_text(claude_md)
    plugin = tmp_path / "plugins" / "beta"
    (plugin / "skills" / "gamma").mkdir(parents=True)
    _ = (plugin / "skills" / "gamma" / "SKILL.md").write_text("")
    (tmp_path / "scripts").mkdir()
    _ = (tmp_path / "scripts" / "lib.mjs").write_text("")
    return tmp_path


def errors(tmp_path: Path, skill_text: str, claude_md: str = "# Project\n") -> list[str]:
    """The errors the validator reports for a repository built from the given texts."""
    return load().check(repo(tmp_path, skill_text, claude_md))[0]


class SkillReferenceTests(unittest.TestCase):
    """The validator's check on small repositories, then on this one."""

    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name)

    def test_dead_path_fails(self) -> None:
        """Dead path fails."""
        found = errors(self.tmp, "Run `scripts/release-notes.mjs` first.\n")
        self.assertEqual(len(found), 1)
        self.assertIn(".claude/skills/alpha/SKILL.md:1", found[0])
        self.assertIn("scripts/release-notes.mjs", found[0])

    def test_dead_path_in_claude_md_fails(self) -> None:
        """A dead path in CLAUDE.md fails."""
        found = errors(self.tmp, "ok\n", claude_md="See `.claude/rules/workflow.md`.\n")
        self.assertEqual(len(found), 1)
        self.assertIn(".claude/CLAUDE.md:1", found[0])

    def test_dead_skill_name_fails(self) -> None:
        """Dead skill name fails."""
        found = errors(
            self.tmp, "Use the `plugin-development` skill.\nSkills: `alpha`; also `gone`.\n"
        )
        self.assertEqual(len(found), 2)
        self.assertIn("plugin-development", found[0])
        self.assertIn("gone", found[1])

    def test_dead_plugin_skill_fails(self) -> None:
        """Dead plugin skill fails."""
        found = errors(self.tmp, "Apply `beta:missing`, then `beta:gamma`.\n")
        self.assertEqual(len(found), 1)
        self.assertIn("beta:missing", found[0])

    def test_live_references_pass(self) -> None:
        """Live references pass."""
        text = (
            "The `alpha` skill runs `scripts/run.py` and reads `scripts/lib.mjs:12`.\n"
            "Skill: `plugin-authoring`. Apply `other-plugin:skill`"
            " and `plugins/beta/skills/gamma`.\n"
        )
        self.assertEqual(errors(self.tmp, text), [])

    def test_examples_and_plugin_relative_paths_are_ignored(self) -> None:
        """Examples and plugin relative paths are ignored."""
        text = (
            "Write `plugins/my-plugin/README.md`, `plugins/<name>/LICENSE`,"
            " `.claude-plugin/plugin.json`, `scripts/*.py`, `~/.claude/x.md`,"
            " `.claude/settings.local.json` and `scripts/a b`.\n"
        )
        self.assertEqual(errors(self.tmp, text), [])

    def test_allowed_entry_passes(self) -> None:
        """Allowed entry passes."""
        root = repo(self.tmp, "ok\n")
        policy = root / ".claude" / "skills" / "testing-plugins" / "references"
        policy.mkdir(parents=True)
        _ = (policy / "eval-policy.md").write_text("1. Copy it to `.github/workflows/evals.yml`.\n")
        self.assertEqual(load().check(root)[0], [])

    def test_repository_passes(self) -> None:
        """This repository passes."""
        found, count = load().check(ROOT)
        self.assertEqual(found, [])
        self.assertGreater(count, 0)
