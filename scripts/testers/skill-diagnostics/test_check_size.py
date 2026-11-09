#!/usr/bin/env python3
"""Tests for skills-best-practices' check-size.py (SKILL.md lines and body tokens).

Run: scripts/testers/run_unittest.py scripts/testers/skill-diagnostics
Standard library only. Each case writes a SKILL.md in a temporary folder and runs the script on
it as a separate process.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, cast
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
    / "check-size.py"
)
HEAD = "---\nname: tiny-skill\ndescription: Formats tiny reports.\n---\n"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def as_object(text: str) -> JsonObject:
    """Decode text that must hold one JSON object."""
    value = _decode(text)
    if not isinstance(value, JsonObject):
        message = f"expected a JSON object, got {text[:200]!r}"
        raise TypeError(message)
    return value


def statuses(result: JsonObject) -> dict[str, str]:
    """Check id to status."""
    checks = result.get("checks")
    if not isinstance(checks, list):
        message = "no checks list"
        raise TypeError(message)
    found: dict[str, str] = {}
    for entry in cast("list[object]", checks):
        if isinstance(entry, JsonObject):
            found[str(entry.get("check"))] = str(entry.get("status"))
    return found


def body_of_tokens(tokens: int) -> str:
    """A body of exactly tokens * 2.8 characters, rounded down, in lines of 70."""
    size = int(tokens * 2.8)
    line = "x" * 69 + "\n"
    full, rest = divmod(size, len(line))
    return line * full + "y" * rest


class CheckSize(unittest.TestCase):
    """Lines, tokens, the lead band and the command-line contract."""

    def run_on(self, text: str, *extra: str) -> subprocess.CompletedProcess[str]:
        """Write text as SKILL.md in a new folder and run the script on it."""
        folder = Path(self.enterContext(tempfile.TemporaryDirectory())) / "tiny-skill"
        folder.mkdir()
        _ = (folder / "SKILL.md").write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(folder), *extra],
            capture_output=True,
            text=True,
            check=False,
        )

    def checked(self, text: str) -> JsonObject:
        """The JSON result of a run that must exit 0."""
        result = self.run_on(text)
        self.assertEqual(result.returncode, 0, result.stderr)
        return as_object(result.stdout)

    def test_500_lines_pass_and_501_fail(self) -> None:
        """Z-1 counts the whole file, frontmatter included."""
        at_limit = self.checked(HEAD + "x\n" * 496)
        self.assertEqual(statuses(at_limit)["Z-1"], "pass")
        over = self.checked(HEAD + "x\n" * 497)
        self.assertEqual(statuses(over)["Z-1"], "fail")

    def test_last_line_without_newline_counts(self) -> None:
        """A last line without a newline is a line."""
        result = self.checked(HEAD + "x\n" * 495 + "end")
        size = result.get("size")
        self.assertIsInstance(size, JsonObject)
        if isinstance(size, JsonObject):
            self.assertEqual(size.get("lines"), 500)

    def test_tokens_estimate_excludes_frontmatter(self) -> None:
        """The body starts after the closing ---; tokens are characters / 2.8, rounded up."""
        result = self.checked(HEAD + "a" * 28)
        size = result.get("size")
        self.assertIsInstance(size, JsonObject)
        if isinstance(size, JsonObject):
            self.assertEqual(size.get("body_characters"), 28)
            self.assertEqual(size.get("body_tokens"), 10)

    def test_no_frontmatter_counts_the_whole_file(self) -> None:
        """Without a frontmatter the whole file is the body."""
        result = self.checked("# Title\n")
        size = result.get("size")
        if isinstance(size, JsonObject):
            self.assertEqual(size.get("body_characters"), 8)

    def test_over_5000_tokens_fails(self) -> None:
        """Z-2 fails above 5,000 tokens and no lead is added."""
        found = statuses(self.checked(HEAD + body_of_tokens(5001) + "zz"))
        self.assertEqual(found["Z-2"], "fail")
        self.assertNotIn("Z-3", found)

    def test_lead_band(self) -> None:
        """Between 4,500 and 5,000 tokens Z-2 passes and Z-3 is a lead."""
        found = statuses(self.checked(HEAD + body_of_tokens(4800)))
        self.assertEqual(found["Z-2"], "pass")
        self.assertEqual(found["Z-3"], "lead")

    def test_small_skill_passes(self) -> None:
        """A short skill passes Z-1 and Z-2 with no lead."""
        found = statuses(self.checked(HEAD + "# Tiny\n\nDo one thing.\n"))
        self.assertEqual(found, {"Z-1": "pass", "Z-2": "pass"})

    def test_output_file_matches_stdout(self) -> None:
        """--output writes the same JSON, creating its folder."""
        target = Path(self.enterContext(tempfile.TemporaryDirectory())) / "a" / "size.json"
        result = self.run_on(HEAD + "x\n", "--output", str(target))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), result.stdout)

    def test_usage_errors_exit_2(self) -> None:
        """No such folder, or a folder without SKILL.md, exits 2."""
        empty = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for folder in (empty / "missing", empty):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(folder)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")

    def test_not_utf8_exits_1(self) -> None:
        """A SKILL.md that is not UTF-8 can't be measured: exit 1."""
        folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        _ = (folder / "SKILL.md").write_bytes(b"\xff\xfe\x00bad")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(folder)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("UTF-8", result.stderr)


if __name__ == "__main__":
    _ = unittest.main()
