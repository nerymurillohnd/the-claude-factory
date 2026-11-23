#!/usr/bin/env python3
"""Tests for the skill-checks.py command line: help, check ids, families and the old-run sweep.

The check ids are read from each family module's `CHECK: Final = "<id>"` line with `ast`, so the
expected list never comes from the registry under test. TMPDIR points at a test folder in every
run, so the sweep never touches the real temp folder.
"""

import ast
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import override
import unittest

from frontmatter_helpers import ENTRY, SCRIPTS, run_python

OLD_PREFIX = "auditing-skills-fm-"
OLD_MARKER = ".auditing-skills-results"


def declared_ids(family: str) -> list[str]:
    """Every `CHECK: Final = "<id>"` constant in a family's modules, sorted."""
    ids: list[str] = []
    for path in sorted((SCRIPTS / family).glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        ids.extend(
            node.value.value
            for node in tree.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "CHECK"
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    return sorted(ids)


class CommandLineTest(unittest.TestCase):
    """What a user or a skill sees when it calls the entry."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway folders; setUp fills them, tearDown removes them."""
        super().__init__(method_name)
        self.tmp: Path = Path()
        self.temp_root: Path = Path()
        self.skill: Path = Path()
        self.env: dict[str, str] = {}

    @override
    def setUp(self) -> None:
        """A throwaway temp root and one clean skill."""
        self.tmp = Path(tempfile.mkdtemp())
        self.temp_root = self.tmp / "temp-root"
        self.temp_root.mkdir()
        self.skill = self.tmp / "skills" / "demo-skill" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        _ = self.skill.write_text(
            "---\nname: demo-skill\ndescription: Use when testing the entry.\n---\nbody\n",
            encoding="utf-8",
        )
        self.env = {**os.environ, "TMPDIR": str(self.temp_root)}

    @override
    def tearDown(self) -> None:
        """Remove the throwaway folders."""
        shutil.rmtree(self.tmp)

    def entry(self, *args: str) -> tuple[int, str, str]:
        """Run the entry; return its exit code, stdout and stderr."""
        done = run_python([str(ENTRY), *args], env=self.env)
        return done.returncode, done.stdout, done.stderr

    def test_help_lists_ids_and_exit_codes(self) -> None:
        """--help names every check id and both exit codes."""
        code, out, err = self.entry("--help")
        self.assertEqual(code, 0, err)
        ids = declared_ids("frontmatter")
        self.assertGreaterEqual(len(ids), 11)
        missing = [check for check in ids if check not in out]
        self.assertEqual(missing, [], out)
        self.assertIn("exit 0", out)
        self.assertIn("exit 2", out)

    def test_check_help(self) -> None:
        """`check --help` prints its usage and exits 0."""
        code, out, err = self.entry("check", "--help")
        self.assertEqual(code, 0, err)
        self.assertIn("check", out)

    def test_unknown_id_lists_valid(self) -> None:
        """An unknown id exits 2 and its one stderr line names the valid ids."""
        code, out, err = self.entry("check", "nope", str(self.skill))
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(len(err.splitlines()), 1, err)
        self.assertIn("frontmatter.yaml", err)

    def test_family_filter(self) -> None:
        """`run --family frontmatter` runs that family's checks; an unknown family exits 2."""
        code, out, err = self.entry("run", "--family", "frontmatter", str(self.skill))
        self.assertEqual(code, 0, err)
        lines = out.splitlines()
        self.assertTrue(lines[-1].startswith("results: "), out)
        self.assertEqual(len(lines) - 1, len(declared_ids("frontmatter")), out)
        code, out, _ = self.entry("run", "--family", "nope", str(self.skill))
        self.assertEqual((code, out), (2, ""))

    def test_sweep_removes_old_prefix(self) -> None:
        """A run removes a 25-hour-old results folder of the earlier entry, with its marker."""
        day_ago = time.time() - 25 * 3600
        old = self.temp_root / f"{OLD_PREFIX}old"
        old.mkdir()
        _ = (old / OLD_MARKER).write_text("", encoding="utf-8")
        os.utime(old, (day_ago, day_ago))
        code, _, err = self.entry("run", str(self.skill))
        self.assertEqual(code, 0, err)
        self.assertFalse(old.exists())


if __name__ == "__main__":
    _ = unittest.main()
