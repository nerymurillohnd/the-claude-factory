#!/usr/bin/env python3
"""Tests for skill-diagnostics' save-report.py, the script that saves an audit's reports.

Run: scripts/testers/run_unittest.py scripts/testers/skill-diagnostics
Standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO
    / "plugins"
    / "skill-diagnostics"
    / "skills"
    / "skills-best-practices"
    / "scripts"
    / "save-report.py"
)
REPORT = "## description-reviewer: demo\n\nStatus: complete\n\n#### D1\n- Item: FM-1\n"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def as_object(text: str) -> JsonObject:
    """Decode text that must hold one JSON object."""
    value = _decode(text)
    if not isinstance(value, JsonObject):
        message = f"expected a JSON object, got {text!r}"
        raise TypeError(message)
    return value


def run(*args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    """Run save-report.py with these arguments and this standard input."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class SaveReport(unittest.TestCase):
    """The saved file, the printed object and the command-line contract."""

    def work(self) -> Path:
        """Return a new temporary folder, removed after the test."""
        return Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_saves_stdin_verbatim_and_creates_folders(self) -> None:
        """The report is written byte for byte, in folders that didn't exist yet."""
        target = self.work() / "skill-audit-demo" / "agents" / "description-reviewer.md"
        result = run("--output", str(target), stdin=REPORT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), REPORT)
        printed = as_object(result.stdout)
        self.assertEqual(printed["saved"], str(target.resolve()))
        self.assertEqual(printed["bytes"], len(REPORT.encode("utf-8")))
        self.assertEqual(result.stderr, "")

    def test_relative_output_is_printed_absolute(self) -> None:
        """A relative --output is resolved against the working folder."""
        tmp = self.work()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", "agents/x.md"],
            input=REPORT,
            capture_output=True,
            text=True,
            check=False,
            cwd=tmp,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        printed = as_object(result.stdout)
        self.assertEqual(Path(str(printed["saved"])), (tmp / "agents" / "x.md").resolve())

    def test_rerun_replaces_the_file(self) -> None:
        """Saving again to the same path replaces the earlier text."""
        target = self.work() / "report.md"
        self.assertEqual(run("--output", str(target), stdin="first\n").returncode, 0)
        self.assertEqual(run("--output", str(target), stdin=REPORT).returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), REPORT)

    def test_empty_input_is_a_usage_error(self) -> None:
        """Nothing on standard input exits 2 and writes no file."""
        target = self.work() / "empty.md"
        result = run("--output", str(target), stdin="  \n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("standard input", result.stderr)
        self.assertFalse(target.exists())

    def test_folder_as_output_is_a_usage_error(self) -> None:
        """An --output that is a folder exits 2."""
        result = run("--output", str(self.work()), stdin=REPORT)
        self.assertEqual(result.returncode, 2)
        self.assertIn("folder", result.stderr)

    def test_missing_output_is_a_usage_error(self) -> None:
        """--output is required."""
        result = run(stdin=REPORT)
        self.assertEqual(result.returncode, 2)

    def test_unwritable_target_exits_1(self) -> None:
        """A parent path that is a file can't hold the report: exit 1, error on stderr."""
        blocker = self.work() / "blocker"
        _ = blocker.write_text("x", encoding="utf-8")
        result = run("--output", str(blocker / "agents" / "a.md"), stdin=REPORT)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot write", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_help_names_the_exit_codes(self) -> None:
        """--help shows an example and the exit codes."""
        result = run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit codes", result.stdout)
        self.assertIn("<<'", result.stdout)


if __name__ == "__main__":
    _ = unittest.main()
