#!/usr/bin/env python3
"""The tests that import the scripts in process leave no bytecode in the plugin's scripts folder.

Each such test module is imported, without -B, from a copy of the plugin's tests and scripts,
and the copied scripts folder must hold no __pycache__ afterwards.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = Path("scripts")
IN_PROCESS = (
    "test_frontmatter_foundation",
    "test_frontmatter_reader",
    "test_frontmatter_reader_advanced",
    "test_frontmatter_runner",
)


class BytecodeTest(unittest.TestCase):
    """No __pycache__ under scripts/ after the in-process test modules are imported."""

    def test_in_process_imports_write_no_bytecode(self) -> None:
        """Import each module that puts scripts/ on sys.path, then look for bytecode."""
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "plugin"
            _ = shutil.copytree(PLUGIN / "tests", copy / "tests", ignore=_no_cache)
            _ = shutil.copytree(PLUGIN / SCRIPTS, copy / SCRIPTS, ignore=_no_cache)
            for module in IN_PROCESS:
                with self.subTest(module=module):
                    done = subprocess.run(
                        [sys.executable, "-c", f"import {module}"],
                        cwd=copy / "tests",
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(sorted((copy / SCRIPTS).rglob("__pycache__")), [])


def _no_cache(_folder: str, names: list[str]) -> list[str]:
    """Leave bytecode out of the copy."""
    return [name for name in names if name == "__pycache__"]


if __name__ == "__main__":
    _ = unittest.main()
