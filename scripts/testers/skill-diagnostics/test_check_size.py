#!/usr/bin/env python3
"""Tests for skills-best-practices' check-size.py (SKILL.md lines and body tokens).

Run: scripts/testers/run_unittest.py scripts/testers/skill-diagnostics
Standard library only. Each case writes a SKILL.md in a temporary folder and runs the script on
it as a separate process.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, cast, override
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


DETAILS = """Tiny (tiny-plugin) 0.1.0
  Source: tiny-plugin@inline

Per-component (rounded)
  component      always-on  on-invoke
  tiny-skill          ~90       {figure}
  helper              ~90       ~1.2k

  On-invoke cost is paid each time a skill or agent fires.
"""


class PluginDetails(unittest.TestCase):
    """The figure from `claude plugin details`, and the fallback to characters / 2.8."""

    root: Path = Path()

    @override
    def setUp(self) -> None:
        """A plugin with one skill of 28 body characters (10 estimated tokens)."""
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        plugin = self.root / "tiny-plugin"
        (plugin / ".claude-plugin").mkdir(parents=True)
        _ = (plugin / ".claude-plugin" / "plugin.json").write_text(
            '{"name": "tiny-plugin"}', encoding="utf-8"
        )
        skill = plugin / "skills" / "tiny-skill"
        skill.mkdir(parents=True)
        _ = (skill / "SKILL.md").write_text(HEAD + "a" * 28, encoding="utf-8")

    def fake_claude(self, output: str, code: int = 0) -> Path:
        """A claude that logs its arguments, prints output and exits with code."""
        folder = self.root / "bin"
        folder.mkdir(exist_ok=True)
        script = folder / "claude"
        log = self.root / "args.txt"
        head = f'#!/bin/sh\nprintf "%s\\n" "$@" > "{log}"\n'
        body = f"/bin/cat <<'END_OF_DETAILS'\n{output}END_OF_DETAILS\nexit {code}\n"
        _ = script.write_text(head + body, encoding="utf-8")
        script.chmod(script.stat().st_mode | stat.S_IXUSR)
        return folder

    def size(self, skill: Path, bin_dir: Path | None) -> JsonObject:
        """The size object of a run with bin_dir (or no claude) on PATH."""
        path = str(Path(sys.executable).parent)
        env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{path}" if bin_dir else path)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(skill)],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        size = as_object(result.stdout).get("size")
        if not isinstance(size, JsonObject):
            message = "no size object"
            raise TypeError(message)
        return size

    @property
    def skill(self) -> Path:
        """The skill folder."""
        return self.root / "tiny-plugin" / "skills" / "tiny-skill"

    def test_details_figure_is_used(self) -> None:
        """Inside a plugin, the on-invoke figure wins and --plugin-dir comes first."""
        size = self.size(self.skill, self.fake_claude(DETAILS.format(figure="~5.1k")))
        self.assertEqual(size.get("token_source"), "claude plugin details")
        self.assertEqual(size.get("body_tokens"), 5100)
        self.assertEqual(size.get("details_tokens"), 5100)
        self.assertEqual(size.get("estimated_tokens"), 10)
        args = (self.root / "args.txt").read_text(encoding="utf-8").split("\n")
        self.assertEqual(args[0], "--plugin-dir")
        self.assertEqual(args[2:5], ["plugin", "details", "tiny-plugin"])

    def test_below_rounding_figure(self) -> None:
        """A '< 20' figure reads as 20."""
        size = self.size(self.skill, self.fake_claude(DETAILS.format(figure="< 20")))
        self.assertEqual(size.get("body_tokens"), 20)

    def test_failed_call_falls_back(self) -> None:
        """A non-zero exit falls back to the estimate and says why."""
        size = self.size(self.skill, self.fake_claude("", code=1))
        self.assertEqual(size.get("token_source"), "characters / 2.8")
        self.assertEqual(size.get("body_tokens"), 10)
        self.assertIsNone(size.get("details_tokens"))
        self.assertIn("exited 1", str(size.get("details_note")))

    def test_unknown_layout_falls_back(self) -> None:
        """Output without the per-component table falls back."""
        size = self.size(self.skill, self.fake_claude("something else\n"))
        self.assertEqual(size.get("token_source"), "characters / 2.8")
        self.assertIn("no single on-invoke row", str(size.get("details_note")))

    def test_no_claude_falls_back(self) -> None:
        """Without claude on PATH the estimate is used."""
        size = self.size(self.skill, None)
        self.assertEqual(size.get("token_source"), "characters / 2.8")
        self.assertEqual(size.get("details_note"), "claude is not on PATH")

    def test_outside_a_plugin_falls_back(self) -> None:
        """A skill in no plugin never calls claude."""
        alone = self.root / "alone" / "tiny-skill"
        alone.mkdir(parents=True)
        _ = (alone / "SKILL.md").write_text(HEAD + "a" * 28, encoding="utf-8")
        size = self.size(alone, self.fake_claude(DETAILS.format(figure="~9k")))
        self.assertEqual(size.get("details_note"), "the skill is not inside a plugin")
        self.assertFalse((self.root / "args.txt").exists())


if __name__ == "__main__":
    _ = unittest.main()
