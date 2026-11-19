#!/usr/bin/env python3
"""Tests for the tool-versions command line: its report and exit codes."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING
import unittest

from checkers.tool_versions.cli import main

if TYPE_CHECKING:
    from collections.abc import Callable

INSTALL = "uv tool install ruff==0.17.5 && uv tool install zizmor==1.32.0"


def fetch_from(versions: dict[str, str]) -> Callable[[str], bytes]:
    """A fake fetch that answers PyPI's JSON API from a name-to-version table."""

    def fetch(url: str) -> bytes:
        name = url.rstrip("/").split("/")[-2]
        if name not in versions:
            msg = f"unreachable: {url}"
            raise OSError(msg)
        return json.dumps({"info": {"version": versions[name]}}).encode()

    return fetch


def run(versions: dict[str, str], install: str = INSTALL) -> tuple[int, str]:
    """Run the command line on a package.json with the given tools:install script."""
    out = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        package = Path(tmp) / "package.json"
        _ = package.write_text(json.dumps({"scripts": {"tools:install": install}}))
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = main([str(package)], fetch_from(versions))
    return code, out.getvalue()


class CliTest(unittest.TestCase):
    """Exit 0 when every pin is current, 1 when one is outdated, 2 when PyPI can't be read."""

    def test_all_current(self) -> None:
        """Every pin matches PyPI: exit 0, each tool reported current."""
        code, output = run({"ruff": "0.17.5", "zizmor": "1.32.0"})
        self.assertEqual(code, 0, output)
        self.assertIn("ruff 0.17.5: current", output)

    def test_outdated_pin(self) -> None:
        """A newer release on PyPI: exit 1, naming the pin and the release."""
        code, output = run({"ruff": "0.17.6", "zizmor": "1.32.0"})
        self.assertEqual(code, 1, output)
        self.assertIn("ruff 0.17.5 -> 0.17.6", output)
        self.assertIn("tools:install", output)

    def test_unreachable_index(self) -> None:
        """PyPI can't be read: exit 2, never a pass."""
        code, output = run({"ruff": "0.17.5"})
        self.assertEqual(code, 2, output)
        self.assertIn("zizmor", output)


if __name__ == "__main__":
    _ = unittest.main()
