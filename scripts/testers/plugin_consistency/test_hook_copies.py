#!/usr/bin/env python3
"""Tests that plugins sharing one hook script ship the same bytes of it."""

from __future__ import annotations

from pathlib import Path
import unittest

PLUGINS = Path(__file__).resolve().parents[3] / "plugins"


class HookCopiesTest(unittest.TestCase):
    """The copies of a hook that a header says are shared."""

    def test_both_typescript_plugins_ship_the_same_hook(self) -> None:
        """The hook is byte-identical in typescript6 and typescript7, as its header says."""
        copies = [
            (PLUGINS / name / "hooks" / "tsc-check.sh").read_bytes()
            for name in ("typescript6-lsp-intelligence", "typescript7-lsp-intelligence")
        ]
        self.assertEqual(copies[0], copies[1])


if __name__ == "__main__":
    _ = unittest.main()
