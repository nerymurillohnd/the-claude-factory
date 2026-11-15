#!/usr/bin/env python3
"""Tests for .claude/hooks/guard-quality-gates.py, run as Claude Code runs it: JSON on stdin."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Mapping

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "guard-quality-gates.py"


class GuardQualityGatesTest(unittest.TestCase):
    """The guard asks for protected files and new suppressions, and stays silent otherwise."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway project each test writes into."""
        super().__init__(method_name)
        self.root: Path = Path()

    @override
    def setUp(self) -> None:
        """Make an empty project folder."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name).resolve()

    def guard(self, tool: str, tool_input: Mapping[str, object]) -> tuple[int, str]:
        """Run the hook on one tool call; return (exit code, decision or '')."""
        data = {"tool_name": tool, "tool_input": tool_input, "cwd": str(self.root)}
        done = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(data),
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(self.root)},
            capture_output=True,
            text=True,
            check=False,
        )
        decision = re.search(r'"permissionDecision":\s*"(\w+)"', done.stdout)
        return done.returncode, decision[1] if decision else ""

    def edit(self, rel: str, old: str, new: str) -> tuple[int, str]:
        """Run the hook on an Edit of rel."""
        path = str(self.root / rel)
        return self.guard("Edit", {"file_path": path, "old_string": old, "new_string": new})

    def notebook(self, cell_source: str, new_source: str) -> tuple[int, str]:
        """Run the hook on a NotebookEdit that replaces the only cell of a notebook."""
        path = self.root / "nb.ipynb"
        cell: dict[str, object] = {"id": "c1", "cell_type": "code", "source": cell_source}
        notebook: dict[str, object] = {"cells": [cell], "nbformat": 4, "nbformat_minor": 5}
        _ = path.write_text(json.dumps(notebook), encoding="utf-8")
        tool_input = {"notebook_path": str(path), "cell_id": "c1", "new_source": new_source}
        return self.guard("NotebookEdit", tool_input)

    def test_project_instructions_are_protected(self) -> None:
        """.claude/CLAUDE.md is protected, whatever the case of its letters."""
        self.assertEqual(self.edit(".claude/CLAUDE.md", "a", "b"), (0, "ask"))

    def test_ordinary_file_passes(self) -> None:
        """A file outside the protected set, with no suppression, gets no decision."""
        self.assertEqual(self.edit("src/app.py", "a = 1", "a = 2"), (0, ""))

    def test_added_suppression_asks(self) -> None:
        """A new suppression goes to Nery."""
        self.assertEqual(self.edit("src/app.py", "a = 1", "a = 1  # noqa: E501"), (0, "ask"))

    def test_swapped_suppression_asks(self) -> None:
        """Replacing one suppression with another keeps the count but is still new."""
        old, new = "a = 1  # noqa: E501", "a = 1  # type: ignore"
        self.assertEqual(self.edit("src/app.py", old, new), (0, "ask"))

    def test_untouched_suppression_passes(self) -> None:
        """An edit that keeps an existing suppression line as it was adds nothing."""
        old = "a = 1  # noqa: E501\nb = 2"
        new = "a = 1  # noqa: E501\nb = 3"
        self.assertEqual(self.edit("src/app.py", old, new), (0, ""))

    def test_notebook_cell_keeping_its_suppression_passes(self) -> None:
        """Editing a cell compares with its previous source, not with nothing."""
        source = "import os  # noqa: F401\n"
        self.assertEqual(self.notebook(source, source + "print(os.sep)\n"), (0, ""))

    def test_notebook_cell_adding_a_suppression_asks(self) -> None:
        """A suppression the cell didn't have goes to Nery."""
        self.assertEqual(self.notebook("x = 1\n", "x = 1  # type: ignore\n"), (0, "ask"))

    def bash(self, command: str) -> tuple[int, str]:
        """Run the hook on a Bash call."""
        return self.guard("Bash", {"command": command})

    def test_bash_writing_a_protected_file_asks(self) -> None:
        """Bash can write protected files too: redirects, sed -i, cp, scripts and git."""
        heredoc = "python3 - <<'EOF'\nPath('.github/workflows/validate.yml').write_text('x')\nEOF"
        commands = (
            "sed -i 's/a/b/' ruff.toml",
            "echo x >> .claude/CLAUDE.md",
            "echo x > 'ruff'.toml",
            "cp /tmp/x .github/workflows/validate.yml",
            heredoc,
            "git checkout -- pyrightconfig.json",
            "mv a.py .claude/hooks/guard.py",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.bash(command), (0, "ask"))

    def test_bash_writing_every_file_asks(self) -> None:
        """A command that rewrites the whole tree reaches protected files without naming them."""
        commands = (
            "npx biome check --write .",
            "ruff check --fix .",
            "git stash",
            "git reset --hard",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.bash(command), (0, "ask"))

    def test_bash_reading_or_writing_elsewhere_passes(self) -> None:
        """Reads of protected files, and writes to other files, get no decision."""
        commands = (
            "cat .claude/settings.json",
            "git diff -- .github/workflows/validate.yml",
            "grep -n include pyrightconfig.json",
            "sed -i 's/a/b/' plugins/demo/package.json",
            "ruff check --fix scripts/validators/skill-lint.py",
            "echo hi > /dev/null",
            "npm run test:scripts",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.bash(command), (0, ""))

    def test_bash_without_a_command_blocks(self) -> None:
        """A Bash call the guard can't read fails closed."""
        self.assertEqual(self.guard("Bash", {"description": "x"})[0], 2)

    def test_unreadable_input_blocks(self) -> None:
        """Input that isn't JSON fails closed with exit 2."""
        done = subprocess.run(
            [sys.executable, str(HOOK)],
            input="not json",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(done.returncode, 2)


if __name__ == "__main__":
    _ = unittest.main()
