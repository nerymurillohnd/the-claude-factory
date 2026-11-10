#!/usr/bin/env python3
"""Tests for skill-diagnostics' record-verdict.py, the script that clears the audit gate.

Run: scripts/testers/run_unittest.py scripts/testers/skill-diagnostics
Standard library only. The last test also runs hooks/audit-gate.sh, so it needs bash and jq.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / "plugins" / "skill-diagnostics"
SCRIPT = PLUGIN / "skills" / "skills-best-practices" / "scripts" / "record-verdict.py"
GATE = PLUGIN / "hooks" / "audit-gate.sh"
VERDICTS = ("pass", "pass-with-warnings", "fail", "not-determinable")
OLD = 1_577_836_800  # 2020-01-01, so the verdict is newer than the skill.


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run record-verdict.py with these arguments."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=cwd,
    )


def make_skill(folder: Path) -> Path:
    """Create a skill folder whose files are dated 2020; return it."""
    folder.mkdir(parents=True)
    skill_md = folder / "SKILL.md"
    _ = skill_md.write_text("---\nname: demo\ndescription: Demo.\n---\n", encoding="utf-8")
    os.utime(skill_md, (OLD, OLD))
    os.utime(folder, (OLD, OLD))
    return folder


class RecordVerdict(unittest.TestCase):
    """The verdict file the gate reads, and the command-line contract."""

    def work(self) -> tuple[Path, Path]:
        """Return a new temporary folder, removed after the test, and its data folder."""
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        return tmp, tmp / "data"

    def test_writes_key_matching_gate(self) -> None:
        """The file name escapes %, / and : in that order; stdout is the file's object."""
        tmp, data = self.work()
        skill = make_skill(tmp / "a b" / "x:y%z")
        done = run("--data-dir", str(data), str(skill), "pass")
        self.assertEqual(done.returncode, 0, done.stderr)
        prefix = str(tmp).replace("%", "%25").replace("/", "%2F").replace(":", "%3A")
        verdict_file = data / "verdicts" / f"{prefix}%2Fa b%2Fx%3Ay%25z"
        listing = sorted(path.name for path in (data / "verdicts").iterdir())
        self.assertTrue(verdict_file.is_file(), listing)
        written = _decode(verdict_file.read_text(encoding="utf-8"))
        printed = _decode(done.stdout)
        self.assertEqual(written, printed)
        self.assertIsInstance(written, JsonObject)
        if isinstance(written, JsonObject):
            self.assertEqual(written.get("skill"), str(skill))
            self.assertEqual(written.get("verdict"), "pass")
            recorded_at = written.get("recorded_at")
            self.assertIsInstance(recorded_at, str)
            self.assertRegex(str(recorded_at), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d$")

    def test_rejects_unknown_verdict(self) -> None:
        """An unknown verdict exits 2 and stderr names the four accepted values."""
        tmp, data = self.work()
        skill = make_skill(tmp / "skill")
        done = run("--data-dir", str(data), str(skill), "maybe")
        self.assertEqual(done.returncode, 2)
        self.assertEqual(done.stdout, "")
        for verdict in VERDICTS:
            self.assertIn(verdict, done.stderr)
        self.assertFalse((data / "verdicts").exists())

    def test_missing_arguments_exit_2(self) -> None:
        """Missing arguments exit 2 and the usage names the accepted values."""
        _, data = self.work()
        done = run("--data-dir", str(data))
        self.assertEqual(done.returncode, 2)
        for verdict in VERDICTS:
            self.assertIn(verdict, done.stderr)

    def test_relative_skill_dir_is_made_absolute(self) -> None:
        """A relative skill folder is recorded under its absolute path."""
        tmp, data = self.work()
        skill = make_skill(tmp / "work" / "my skill")
        done = run("--data-dir", str(data), "my skill", "not-determinable", cwd=skill.parent)
        self.assertEqual(done.returncode, 0, done.stderr)
        printed = _decode(done.stdout)
        self.assertIsInstance(printed, JsonObject)
        if isinstance(printed, JsonObject):
            self.assertEqual(printed.get("skill"), str(skill))

    def test_requires_skill_md(self) -> None:
        """A folder without SKILL.md is a usage error: exit 2, nothing written."""
        tmp, data = self.work()
        folder = tmp / "not-a-skill"
        folder.mkdir()
        done = run("--data-dir", str(data), str(folder), "pass")
        self.assertEqual(done.returncode, 2)
        self.assertIn("SKILL.md", done.stderr)
        self.assertFalse((data / "verdicts").exists())

    def test_help_exits_zero(self) -> None:
        """--help prints the usage with the verdicts and exits 0."""
        done = run("--help")
        self.assertEqual(done.returncode, 0)
        for verdict in VERDICTS:
            self.assertIn(verdict, done.stdout)

    def test_cannot_write_exits_1(self) -> None:
        """A data folder that cannot be created exits 1 with the reason on stderr."""
        tmp, _ = self.work()
        skill = make_skill(tmp / "skill")
        blocker = tmp / "file"
        _ = blocker.write_text("", encoding="utf-8")
        done = run("--data-dir", str(blocker / "data"), str(skill), "pass")
        self.assertEqual(done.returncode, 1)
        self.assertNotEqual(done.stderr, "")

    def test_verdict_newer_than_skill_clears_gate(self) -> None:
        """After the verdict, audit-gate.sh stays silent for that pending skill."""
        tmp, data = self.work()
        skill = make_skill(tmp / "project" / "skills" / "demo")
        pending = data / "pending"
        pending.mkdir(parents=True)
        _ = (pending / "s1").write_text(f"{skill}\n", encoding="utf-8")
        environment = {
            **os.environ,
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
            "CLAUDE_PLUGIN_DATA": str(data),
            "CLAUDE_PROJECT_DIR": str(tmp / "project"),
            "CLAUDE_CONFIG_DIR": str(tmp / "config"),
            "CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE": "gate",
        }
        bash = shutil.which("bash")
        if bash is None:
            self.fail("bash is not on PATH")
        stop = json.dumps({"session_id": "s1", "hook_event_name": "Stop"})

        def gate() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [bash, str(GATE)],
                input=stop,
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )

        before = gate()
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertIn(str(skill), before.stdout)
        done = run("--data-dir", str(data), str(skill), "pass")
        self.assertEqual(done.returncode, 0, done.stderr)
        after = gate()
        self.assertEqual(after.returncode, 0, after.stderr)
        self.assertEqual(after.stdout, "")


if __name__ == "__main__":
    _ = unittest.main()
