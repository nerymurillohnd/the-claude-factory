"""Tests for skill discovery and loading."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from validators.skill_lint.discover import discover, git_modes, load_skill

from testers.skill_lint.helpers import VALID_SKILL_MD, build_skill


class LoadSkillTest(unittest.TestCase):
    """Kind, command, files and executability of loaded skills."""

    def test_plugin_kind_and_command(self) -> None:
        """A plugin skill is named plugin:skill."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            loaded = load_skill(skill / "SKILL.md")
        self.assertEqual((loaded.kind, loaded.plugin), ("plugin", "demo"))
        self.assertEqual(loaded.command, "demo:demo-skill")
        self.assertIsNotNone(loaded.plugin_root)

    def test_project_kind(self) -> None:
        """A .claude/skills skill is a project skill."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD}, layout="project")
            loaded = load_skill(skill / "SKILL.md")
        self.assertEqual(loaded.kind, "project")
        self.assertEqual(loaded.command, "project:demo-skill")

    def test_standalone_kind(self) -> None:
        """Any other location is standalone."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD}, layout="standalone")
            loaded = load_skill(skill / "SKILL.md")
        self.assertEqual(loaded.kind, "standalone")
        self.assertEqual(loaded.command, "demo-skill")

    def test_binary_file_listed_not_text(self) -> None:
        """A binary file is listed in files but not read as text."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(
                Path(tmp), {"SKILL.md": VALID_SKILL_MD, "assets/a.png": b"\x89PNG\x00"}
            )
            loaded = load_skill(skill / "SKILL.md")
        self.assertIn("assets/a.png", loaded.files)
        self.assertNotIn("assets/a.png", loaded.text)
        self.assertIn("SKILL.md", loaded.text)

    def test_is_executable_untracked_uses_stat(self) -> None:
        """Without git modes, the file's permission bits decide."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(
                Path(tmp), {"SKILL.md": VALID_SKILL_MD, "run.sh": "#!/bin/sh\n", "doc.md": "x"}
            )
            (skill / "run.sh").chmod(0o755)
            (skill / "doc.md").chmod(0o644)
            loaded = load_skill(skill / "SKILL.md", mode_reader=lambda _: {})
            self.assertEqual(loaded.is_executable("run.sh"), (True, False))
            self.assertEqual(loaded.is_executable("doc.md"), (False, False))


class DiscoverTest(unittest.TestCase):
    """Repository discovery and git modes."""

    def test_discover_ignores_other_skill_md(self) -> None:
        """Only the two skill globs count, and results are sorted by command."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _ = build_skill(root, {"SKILL.md": VALID_SKILL_MD}, plugin="zeta")
            _ = build_skill(root, {"SKILL.md": VALID_SKILL_MD}, layout="project")
            other = root / "scripts" / "testers" / "x"
            other.mkdir(parents=True)
            _ = (other / "SKILL.md").write_text(VALID_SKILL_MD, encoding="utf-8")
            commands = [s.command for s in discover(root)]
        self.assertEqual(commands, ["project:demo-skill", "zeta:demo-skill"])

    def test_git_modes_outside_repo_is_empty(self) -> None:
        """A folder outside any repository gives no modes."""
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(git_modes(Path(tmp)), {})

    def test_git_modes_in_temp_repo(self) -> None:
        """Tracked files report their git mode."""
        git = shutil.which("git") or "git"
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD, "run.sh": "#!/bin/sh\n"})
            for args in (
                ["init", "-q"],
                ["add", "."],
                ["update-index", "--chmod=+x", "plugins/demo/skills/demo-skill/run.sh"],
            ):
                _ = subprocess.run([git, "-C", tmp, *args], check=True, capture_output=True)
            modes = git_modes(skill)
        self.assertEqual(modes["run.sh"], "100755")
        self.assertEqual(modes["SKILL.md"], "100644")
