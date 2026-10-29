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
    def check(self, root: Path) -> tuple[list[str], int]: ...


def load() -> Validator:
    """The validator module, imported from its hyphenated file name."""
    spec = importlib.util.spec_from_file_location("skill_references", VALIDATOR)
    assert spec is not None
    assert spec.loader is not None
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
    return load().check(repo(tmp_path, skill_text, claude_md))[0]


class SkillReferenceTests(unittest.TestCase):
    tmp: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name)

    def test_dead_path_fails(self) -> None:
        found = errors(self.tmp, "Run `scripts/release-notes.mjs` first.\n")
        assert len(found) == 1
        assert ".claude/skills/alpha/SKILL.md:1" in found[0]
        assert "scripts/release-notes.mjs" in found[0]

    def test_dead_path_in_claude_md_fails(self) -> None:
        found = errors(self.tmp, "ok\n", claude_md="See `.claude/rules/workflow.md`.\n")
        assert len(found) == 1
        assert ".claude/CLAUDE.md:1" in found[0]

    def test_dead_skill_name_fails(self) -> None:
        found = errors(
            self.tmp, "Use the `plugin-development` skill.\nSkills: `alpha`; also `gone`.\n"
        )
        assert len(found) == 2
        assert "plugin-development" in found[0]
        assert "gone" in found[1]

    def test_dead_plugin_skill_fails(self) -> None:
        found = errors(self.tmp, "Apply `beta:missing`, then `beta:gamma`.\n")
        assert len(found) == 1
        assert "beta:missing" in found[0]

    def test_live_references_pass(self) -> None:
        text = (
            "The `alpha` skill runs `scripts/run.py` and reads `scripts/lib.mjs:12`.\n"
            "Skill: `plugin-authoring`. Apply `other-plugin:skill`"
            " and `plugins/beta/skills/gamma`.\n"
        )
        assert errors(self.tmp, text) == []

    def test_examples_and_plugin_relative_paths_are_ignored(self) -> None:
        text = (
            "Write `plugins/my-plugin/README.md`, `plugins/<name>/LICENSE`,"
            " `.claude-plugin/plugin.json`, `scripts/*.py`, `~/.claude/x.md`,"
            " `.claude/settings.local.json` and `scripts/a b`.\n"
        )
        assert errors(self.tmp, text) == []

    def test_allowed_entry_passes(self) -> None:
        root = repo(self.tmp, "ok\n")
        policy = root / ".claude" / "skills" / "testing-plugins" / "references"
        policy.mkdir(parents=True)
        _ = (policy / "eval-policy.md").write_text("1. Copy it to `.github/workflows/evals.yml`.\n")
        assert load().check(root)[0] == []

    def test_repository_passes(self) -> None:
        found, count = load().check(ROOT)
        assert found == []
        assert count > 0
