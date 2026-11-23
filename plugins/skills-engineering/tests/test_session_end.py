"""Tests for the SessionEnd hook: session-end.py and the command in hooks/hooks.json.

Each test builds a throwaway plugin data folder and runs the hook the way Claude Code does: the
input JSON on stdin and CLAUDE_PLUGIN_DATA in the environment. TMPDIR points at a test folder, so
the hook's sweep never touches the real temp folder.
"""

import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from typing import override
import unittest

from frontmatter_helpers import SCRIPTS, JsonObject, is_list, parse_json, run_python

ENTRY = SCRIPTS / "session-end.py"
HOOKS = SCRIPTS.parent / "hooks" / "hooks.json"
PREFIX = "skills-engineering-checks-"
MARKER = ".skills-engineering-results"
SESSION_MARKER = ".skills-engineering-session"
DAY_AGO = time.time() - 25 * 3600


def hook_command() -> str:
    """The SessionEnd command string from hooks.json."""
    data = parse_json(HOOKS.read_text(encoding="utf-8"))
    hooks = data.get("hooks") if isinstance(data, JsonObject) else None
    events = hooks.get("SessionEnd") if isinstance(hooks, JsonObject) else None
    group = events[0] if is_list(events) and events else None
    entries = group.get("hooks") if isinstance(group, JsonObject) else None
    entry = entries[0] if is_list(entries) and entries else None
    command = entry.get("command") if isinstance(entry, JsonObject) else None
    if not isinstance(command, str):
        msg = "hooks.json has no SessionEnd command"
        raise TypeError(msg)
    return command


class SessionEndTest(unittest.TestCase):
    """What the hook removes, what it keeps, and that it never speaks or fails."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway folders each test builds."""
        super().__init__(method_name)
        self.tmp: Path = Path()
        self.data: Path = Path()
        self.checks: Path = Path()
        self.env: dict[str, str] = {}

    @override
    def setUp(self) -> None:
        """A data folder with an empty checks folder, and a test temp root."""
        self.tmp = Path(tempfile.mkdtemp())
        self.data = self.tmp / "data"
        self.checks = self.data / "checks"
        self.checks.mkdir(parents=True)
        temp_root = self.tmp / "temp-root"
        temp_root.mkdir()
        self.env = {
            **os.environ,
            "TMPDIR": str(temp_root),
            "CLAUDE_PLUGIN_DATA": str(self.data),
        }

    @override
    def tearDown(self) -> None:
        """Remove the throwaway folders."""
        shutil.rmtree(self.tmp)

    def session(self, name: str, *, parent: Path | None = None, old: bool = False) -> Path:
        """A session folder holding its marker."""
        path = (parent or self.checks) / name
        path.mkdir(parents=True)
        marker = path / SESSION_MARKER
        _ = marker.write_text("", encoding="utf-8")
        if old:
            os.utime(marker, (DAY_AGO, DAY_AGO))
        return path

    @staticmethod
    def run_folder(parent: Path, name: str, *, old: bool = False) -> Path:
        """A marked run folder holding one result file."""
        path = parent / f"{PREFIX}{name}"
        path.mkdir()
        _ = (path / MARKER).write_text("", encoding="utf-8")
        _ = (path / "summary.json").write_text("{}", encoding="utf-8")
        if old:
            os.utime(path, (DAY_AGO, DAY_AGO))
        return path

    def end(self, payload: str) -> None:
        """Run the hook with this stdin; it must exit 0 and print nothing."""
        done = run_python([str(ENTRY)], env=self.env, stdin=payload)
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))

    def test_removes_this_session_only(self) -> None:
        """The session's runs and folder go; another session's stay, and so does checks/."""
        ended = self.session("ended")
        _ = self.run_folder(ended, "a")
        _ = self.run_folder(ended, "b")
        other = self.session("other")
        other_run = self.run_folder(other, "c")
        self.end(json.dumps({"session_id": "ended", "hook_event_name": "SessionEnd"}))
        self.assertFalse(ended.exists())
        self.assertTrue(other_run.exists())

    def test_removes_an_empty_checks_folder(self) -> None:
        """With the last session gone, checks/ goes too."""
        ended = self.session("ended")
        _ = self.run_folder(ended, "a")
        self.end(json.dumps({"session_id": "ended"}))
        self.assertFalse(self.checks.exists())
        self.assertTrue(self.data.exists())

    def test_sweeps_old_runs_of_other_sessions(self) -> None:
        """A crashed session's old run, and its folder, go at another session's end."""
        crashed = self.session("crashed", old=True)
        _ = self.run_folder(crashed, "old", old=True)
        live = self.session("live")
        live_run = self.run_folder(live, "fresh")
        self.end(json.dumps({"session_id": "ended"}))
        self.assertFalse(crashed.exists())
        self.assertTrue(live_run.exists())

    def test_bad_input_removes_nothing(self) -> None:
        """An unsafe, missing or malformed session id, or no data folder, changes nothing."""
        kept = self.session("kept")
        run = self.run_folder(kept, "a")
        payloads = [
            json.dumps({"session_id": ".."}),
            json.dumps({"session_id": "."}),
            json.dumps({"session_id": "a/b"}),
            json.dumps({"session_id": ""}),
            json.dumps({"session_id": 5}),
            json.dumps({}),
            json.dumps(["kept"]),
            "not json",
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                self.end(payload)
                self.assertTrue(run.exists())
        del self.env["CLAUDE_PLUGIN_DATA"]
        self.end(json.dumps({"session_id": "kept"}))
        self.assertTrue(run.exists())

    def test_keeps_symlinks_and_unmarked_folders(self) -> None:
        """A symlinked session folder isn't followed; an unmarked folder inside a session stays."""
        elsewhere = self.session("target", parent=self.tmp / "elsewhere")
        elsewhere_run = self.run_folder(elsewhere, "a")
        (self.checks / "linked").symlink_to(elsewhere, target_is_directory=True)
        self.end(json.dumps({"session_id": "linked"}))
        self.assertTrue(elsewhere_run.exists())
        mixed = self.session("mixed")
        marked = self.run_folder(mixed, "a")
        unmarked = mixed / f"{PREFIX}unmarked"
        unmarked.mkdir()
        self.end(json.dumps({"session_id": "mixed"}))
        self.assertFalse(marked.exists())
        self.assertTrue(unmarked.exists())
        self.assertTrue(mixed.exists())


class HookCommandTest(unittest.TestCase):
    """The command in hooks.json, run through sh as Claude Code runs it."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway folder each test builds."""
        super().__init__(method_name)
        self.tmp: Path = Path()
        self.bin: Path = Path()
        self.started: Path = Path()
        self.env: dict[str, str] = {}

    @override
    def setUp(self) -> None:
        """A data folder, a PATH with no real Python, and a fake python3 that records its start."""
        self.tmp = Path(tempfile.mkdtemp())
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.started = self.tmp / "started"
        self.env = {
            "PATH": str(self.bin),
            "CLAUDE_PLUGIN_ROOT": str(SCRIPTS.parent),
            "CLAUDE_PLUGIN_DATA": str(self.tmp / "data"),
        }

    @override
    def tearDown(self) -> None:
        """Remove the throwaway folder."""
        shutil.rmtree(self.tmp)

    def run_hook(self) -> tuple[int, str, str]:
        """Run the hook command through /bin/sh with a session id on stdin."""
        done = run_python(
            ["-c", hook_command()],
            env=self.env,
            python="/bin/sh",
            stdin=json.dumps({"session_id": "s"}),
        )
        return done.returncode, done.stdout, done.stderr

    def fake_python3(self) -> None:
        """Put a python3 on PATH that only records that it started."""
        fake = self.bin / "python3"
        _ = fake.write_text(f"#!/bin/sh\n: > '{self.started}'\n", encoding="utf-8")
        fake.chmod(0o755)

    def test_no_python_is_silent(self) -> None:
        """With checks/ present and no Python at all, the command exits 0 and prints nothing."""
        (self.tmp / "data" / "checks").mkdir(parents=True)
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_no_checks_folder_starts_no_python(self) -> None:
        """Without checks/, Python never starts; with it, Python does."""
        self.fake_python3()
        self.assertEqual(self.run_hook(), (0, "", ""))
        self.assertFalse(self.started.exists())
        (self.tmp / "data" / "checks").mkdir(parents=True)
        self.assertEqual(self.run_hook(), (0, "", ""))
        self.assertTrue(self.started.exists())


if __name__ == "__main__":
    _ = unittest.main()
