"""Tests for skill discovery and loading."""

from __future__ import annotations

import contextlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from validators.skill_lint.discover import (
    MAX_TEXT_BYTES,
    GitError,
    discover,
    git_modes,
    load_skill,
)

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

    def test_load_skill_parses_body(self) -> None:
        """The SKILL.md body is parsed with file line numbers."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            loaded = load_skill(skill / "SKILL.md")
        self.assertEqual(loaded.frontmatter.body_start, 5)
        heading = loaded.body.headings[0]
        self.assertEqual(
            (heading.text, heading.line, heading.slug), ("Demo skill", 6, "demo-skill")
        )
        self.assertEqual(loaded.body.prose[-1], (8, "Say hello."))

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

    def test_is_executable_tracked_uses_git_mode(self) -> None:
        """A tracked file's git mode wins over its permission bits."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD, "x.sh": "#!/bin/sh\n"})
            (skill / "x.sh").chmod(0o755)
            loaded = load_skill(skill / "SKILL.md", mode_reader=lambda _: {"x.sh": "100644"})
            self.assertEqual(loaded.is_executable("x.sh"), (False, True))

    def test_symlinks_listed_but_outside_target_not_read(self) -> None:
        """Symlinks are listed; one pointing outside the folder is not read as text."""
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside.txt"
            _ = outside.write_text("secret", encoding="utf-8")
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD, "inner.md": "in"})
            (skill / "out.txt").symlink_to(outside)
            (skill / "in.md").symlink_to(skill / "inner.md")
            loaded = load_skill(skill / "SKILL.md", mode_reader=lambda _: {})
        self.assertIn("out.txt", loaded.files)
        self.assertIn("in.md", loaded.files)
        self.assertNotIn("out.txt", loaded.text)
        self.assertEqual(loaded.text["in.md"], "in")


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

    def test_git_modes_path_with_space(self) -> None:
        """A tracked path containing a space is reported verbatim."""
        git = shutil.which("git") or "git"
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD, "my notes.md": "x"})
            for args in (["init", "-q"], ["add", "."]):
                _ = subprocess.run([git, "-C", tmp, *args], check=True, capture_output=True)
            modes = git_modes(skill)
        self.assertEqual(modes["my notes.md"], "100644")

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


class CodeReviewTest(unittest.TestCase):
    """Relative paths, unread SKILL.md reasons, git failures and pruned folders."""

    def test_relative_project_path(self) -> None:
        """A relative .claude/skills path is a project skill, and discover('.') finds it."""
        with tempfile.TemporaryDirectory() as tmp, contextlib.chdir(tmp):
            _ = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD}, layout="project")
            loaded = load_skill(Path(".claude/skills/demo-skill/SKILL.md"))
            found = [s.command for s in discover(Path())]
        self.assertEqual(loaded.command, "project:demo-skill")
        self.assertTrue(loaded.root.is_absolute())
        self.assertEqual(found, ["project:demo-skill"])

    def test_relative_plugin_path(self) -> None:
        """A relative plugins/<p>/skills path is a plugin skill."""
        with tempfile.TemporaryDirectory() as tmp, contextlib.chdir(tmp):
            _ = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            loaded = load_skill(Path("plugins/demo/skills/demo-skill/SKILL.md"))
        self.assertEqual(loaded.command, "demo:demo-skill")

    def test_skill_md_symlink_outside(self) -> None:
        """A SKILL.md linking outside the folder is reported as such, not as bad UTF-8."""
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "elsewhere.md"
            _ = outside.write_text(VALID_SKILL_MD, encoding="utf-8")
            skill = build_skill(Path(tmp), {"notes.md": "x"})
            (skill / "SKILL.md").symlink_to(outside)
            loaded = load_skill(skill / "SKILL.md", mode_reader=lambda _: {})
        error = loaded.frontmatter.error
        self.assertIsNotNone(error)
        self.assertIn("outside the skill folder", error[1] if error else "")

    def test_skill_md_unreadable(self) -> None:
        """A SKILL.md that cannot be opened is reported with the OS reason."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"notes.md": "x"})
            (skill / "SKILL.md").symlink_to(skill / "missing.md")
            loaded = load_skill(skill / "SKILL.md", mode_reader=lambda _: {})
        error = loaded.frontmatter.error
        self.assertIn("cannot be read", error[1] if error else "")

    def test_git_failure_raises(self) -> None:
        """A git error other than 'not a repository' is raised, not hidden as no modes."""
        git = shutil.which("git") or "git"
        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            _ = subprocess.run([git, "init", "-q", tmp], check=True, capture_output=True)
            _ = (Path(tmp) / ".git" / "index").write_bytes(b"not an index")
            with self.assertRaises(GitError):
                _ = git_modes(skill)

    def test_git_failure_kept_on_skill(self) -> None:
        """load_skill keeps a git failure as modes_error and reads no modes."""

        def failing(_: Path) -> dict[str, str]:
            message = "fatal: detected dubious ownership"
            raise GitError(message)

        with tempfile.TemporaryDirectory() as tmp:
            skill = build_skill(Path(tmp), {"SKILL.md": VALID_SKILL_MD})
            loaded = load_skill(skill / "SKILL.md", mode_reader=failing)
        self.assertEqual(loaded.modes, {})
        self.assertEqual(loaded.modes_error, "fatal: detected dubious ownership")

    def test_vendored_folders_pruned(self) -> None:
        """node_modules, .venv and .git are not listed."""
        files = {
            "SKILL.md": VALID_SKILL_MD,
            "node_modules/x/index.js": "x",
            ".venv/lib/y.py": "y",
            ".git/HEAD": "ref",
            "scripts/run.py": "z",
        }
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
        self.assertEqual(loaded.files, ("SKILL.md", "scripts/run.py"))

    def test_large_file_listed_not_read(self) -> None:
        """A file over 1 MiB is listed but not read."""
        files = {"SKILL.md": VALID_SKILL_MD, "assets/big.txt": "a" * (MAX_TEXT_BYTES + 1)}
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load_skill(build_skill(Path(tmp), files) / "SKILL.md")
        self.assertIn("assets/big.txt", loaded.files)
        self.assertNotIn("assets/big.txt", loaded.text)
