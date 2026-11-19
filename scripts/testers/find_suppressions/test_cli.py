#!/usr/bin/env python3
"""Tests for the find-suppressions command line: its report and exit codes."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from validators.find_suppressions.cli import main


def run(args: list[str]) -> tuple[int, str]:
    """Run the command line and return its exit code and output."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = main(args)
    return code, out.getvalue()


def write(folder: str, name: str, text: str) -> str:
    """Write a file in the folder and return its path as text."""
    path = Path(folder) / name
    _ = path.write_text(text, encoding="utf-8")
    return str(path)


class CliTest(unittest.TestCase):
    """Exit 0 when clean, 1 with a report when a suppression is found, 2 on an unreadable file."""

    def test_clean_files_pass(self) -> None:
        """No suppression: exit 0."""
        with tempfile.TemporaryDirectory() as tmp:
            files = [write(tmp, "a.py", "X = 1\n"), write(tmp, "b.ts", "export const y = 2\n")]
            code, _ = run(files)
        self.assertEqual(code, 0)

    def test_suppression_fails_with_its_location(self) -> None:
        """A suppression: exit 1, and the report names the file, line and kind."""
        with tempfile.TemporaryDirectory() as tmp:
            path = write(tmp, "a.py", "import os  # noqa: F401\n")
            code, output = run([path])
        self.assertEqual(code, 1)
        self.assertIn(f"{path}:1: noqa:", output)
        self.assertIn("1 suppression", output)

    def test_missing_files_are_skipped(self) -> None:
        """A path that no longer exists, such as a deleted file, is not read."""
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = run([str(Path(tmp) / "gone.py")])
        self.assertEqual(code, 0)

    def test_unparsable_python_is_an_error(self) -> None:
        """A Python file that does not parse cannot be checked: exit 2."""
        with tempfile.TemporaryDirectory() as tmp:
            code, output = run([write(tmp, "bad.py", "def (:\n")])
        self.assertEqual(code, 2)
        self.assertIn("bad.py", output)


if __name__ == "__main__":
    _ = unittest.main()
