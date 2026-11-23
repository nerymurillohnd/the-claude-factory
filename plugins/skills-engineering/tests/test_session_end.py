"""Tests for the SessionEnd hook: session-end.py and the command in hooks/hooks.json.

Each test builds a throwaway plugin data folder and runs the hook the way Claude Code does: the
input JSON on stdin and CLAUDE_PLUGIN_DATA in the environment. TMPDIR points at a test folder, so
the hook's sweep never touches the real temp folder.
"""

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from typing import override
import unittest
from unittest import mock

from frontmatter_helpers import (
    ENTRY as CHECKS_ENTRY,
    SCRIPTS,
    JsonObject,
    is_list,
    parse_json,
    run_python,
)

sys.path.insert(0, str(SCRIPTS))

from engine import results, session_end

ENTRY = SCRIPTS / "session-end.py"
PYTHON_311 = Path("/usr/bin/python3.11")
LOG_LIMIT = 64 * 1024
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
        self.assertTrue(self.checks.is_dir())

    def test_resume_keeps_the_session(self) -> None:
        """A session that ends for a resume or a branch keeps its results; other reasons don't."""
        ended = self.session("ended")
        run = self.run_folder(ended, "a")
        self.end(json.dumps({"session_id": "ended", "reason": "resume"}))
        self.assertTrue(run.exists())
        for reason in ("clear", "logout", "prompt_input_exit", "other"):
            with self.subTest(reason=reason):
                session = self.session(f"ended-{reason}")
                _ = self.run_folder(session, "a")
                self.end(json.dumps({"session_id": f"ended-{reason}", "reason": reason}))
                self.assertFalse(session.exists())

    def test_unsafe_ids_enter_no_marked_folder(self) -> None:
        """Ids reaching the data folder, a nested session or checks/ itself remove nothing."""
        _ = (self.data / SESSION_MARKER).write_text("", encoding="utf-8")
        data_run = self.run_folder(self.data, "in-data")
        nested = self.session("b", parent=self.checks / "a")
        nested_run = self.run_folder(nested, "nested")
        direct_run = self.run_folder(self.checks, "direct")
        for session_id in ("..", "a/b", ".", "", "a\\b"):
            with self.subTest(session_id=session_id):
                self.end(json.dumps({"session_id": session_id}))
                for kept in (data_run, nested_run, direct_run):
                    self.assertTrue(kept.exists(), kept)

    def test_sweep_keeps_a_fresh_empty_session(self) -> None:
        """An empty session folder with a fresh marker is a live session: the sweep keeps it."""
        live = self.session("live")
        self.end(json.dumps({"session_id": "ended"}))
        self.assertTrue((live / SESSION_MARKER).is_file())

    def test_symlinked_checks_folder_is_left_alone(self) -> None:
        """A checks folder that is a symlink is never entered."""
        shutil.rmtree(self.checks)
        elsewhere = self.tmp / "elsewhere"
        session = self.session("s", parent=elsewhere)
        run = self.run_folder(session, "a")
        self.checks.symlink_to(elsewhere, target_is_directory=True)
        self.end(json.dumps({"session_id": "s"}))
        self.assertTrue(run.exists())
        self.assertTrue(self.checks.is_symlink())

    def test_symlinked_session_marker_is_no_marker(self) -> None:
        """A session folder whose marker is a symlink is not a session folder."""
        folder = self.checks / "s"
        folder.mkdir()
        real = self.tmp / "real-marker"
        _ = real.write_text("", encoding="utf-8")
        (folder / SESSION_MARKER).symlink_to(real)
        run = self.run_folder(folder, "a")
        self.end(json.dumps({"session_id": "s"}))
        self.assertTrue(run.exists())

    def test_round_trip_with_skill_checks(self) -> None:
        """Two runs into checks/<id>, then the session's end: checks/ is gone."""
        skill = self.tmp / "skills" / "demo-skill" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        _ = skill.write_text(
            "---\nname: demo-skill\ndescription: Use when testing the round trip.\n---\nbody\n",
            encoding="utf-8",
        )
        for _attempt in range(2):
            done = run_python(
                [str(CHECKS_ENTRY), "run", "--out", str(self.checks / "sid"), str(skill)],
                env=self.env,
            )
            self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(len(list((self.checks / "sid").glob(f"{PREFIX}*"))), 2)
        self.end(json.dumps({"session_id": "sid"}))
        self.assertFalse(self.checks.exists())

    @unittest.skipUnless(PYTHON_311.exists(), "needs /usr/bin/python3.11")
    def test_below_the_floor_is_silent(self) -> None:
        """Python 3.11 exits 0 silently and writes no bytecode into the plugin."""
        done = run_python([str(ENTRY)], env=self.env, python=str(PYTHON_311), stdin="{}")
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))
        caches = [p for p in SCRIPTS.rglob("*.pyc") if p.stat().st_mtime > time.time() - 60]
        self.assertEqual(caches, [])

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
        """Put a python3 on PATH that only records its arguments, one per line."""
        fake = self.bin / "python3"
        _ = fake.write_text(
            f"#!/bin/sh\nprintf '%s\\n' \"$@\" > '{self.started}'\n", encoding="utf-8"
        )
        fake.chmod(0o755)

    def test_no_python_is_silent(self) -> None:
        """With checks/ present and no Python at all, the command exits 0 and prints nothing."""
        (self.tmp / "data" / "checks").mkdir(parents=True)
        self.assertEqual(self.run_hook(), (0, "", ""))

    def test_no_checks_folder_starts_no_python(self) -> None:
        """Without checks/, Python never starts; with it, Python runs session-end.py."""
        self.fake_python3()
        self.assertEqual(self.run_hook(), (0, "", ""))
        self.assertFalse(self.started.exists())
        (self.tmp / "data" / "checks").mkdir(parents=True)
        self.assertEqual(self.run_hook(), (0, "", ""))
        script = Path(self.started.read_text(encoding="utf-8").splitlines()[0])
        self.assertTrue(script.is_file(), script)
        self.assertEqual(script.parts[-2:], ("scripts", "session-end.py"))

    def test_real_python_removes_the_session(self) -> None:
        """With a real python3 on PATH, the command removes the session's runs and checks/."""
        (self.bin / "python3").symlink_to(sys.executable)
        session = self.tmp / "data" / "checks" / "s"
        session.mkdir(parents=True)
        _ = (session / SESSION_MARKER).write_text("", encoding="utf-8")
        run = session / f"{PREFIX}a"
        run.mkdir()
        _ = (run / MARKER).write_text("", encoding="utf-8")
        temp_root = self.tmp / "temp-root"
        temp_root.mkdir()
        self.env["TMPDIR"] = str(temp_root)
        self.assertEqual(self.run_hook(), (0, "", ""))
        self.assertFalse(session.exists())
        self.assertFalse((self.tmp / "data" / "checks").exists())


class HookFailureTest(unittest.TestCase):
    """An unexpected error in the hook is logged to the data folder, never shown."""

    def __init__(self, method_name: str = "runTest") -> None:
        """Hold the throwaway data folder."""
        super().__init__(method_name)
        self.data: Path = Path()

    @override
    def setUp(self) -> None:
        """A throwaway data folder with a checks folder."""
        self.data = Path(tempfile.mkdtemp())
        (self.data / "checks").mkdir()

    @override
    def tearDown(self) -> None:
        """Remove the throwaway data folder."""
        shutil.rmtree(self.data)

    def end_with_error(self, data: str) -> tuple[object, str]:
        """Run main() in process with remove_session raising; return its exit and its output."""
        out = io.StringIO()
        code: object = "raised"
        with (
            mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_DATA": data}),
            mock.patch.object(sys, "stdin", io.StringIO(json.dumps({"session_id": "s"}))),
            mock.patch.object(results, "remove_session", side_effect=RuntimeError("boom\nmore")),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(out),
        ):
            try:
                session_end.main()
            except SystemExit as done:
                code = done.code
            except RuntimeError:
                code = "raised"
        return code, out.getvalue()

    def test_error_is_logged_and_silent(self) -> None:
        """The hook exits 0, prints nothing, and appends one line to session-end.log."""
        self.assertEqual(self.end_with_error(str(self.data)), (0, ""))
        log = (self.data / "session-end.log").read_text(encoding="utf-8")
        self.assertEqual(log, "session s: RuntimeError: boom more\n")

    def test_log_stays_small(self) -> None:
        """A log past 64 KiB starts over before the new line is written."""
        log = self.data / "session-end.log"
        _ = log.write_text("x" * (LOG_LIMIT + 10) + "\n", encoding="utf-8")
        self.assertEqual(self.end_with_error(str(self.data)), (0, ""))
        self.assertEqual(log.read_text(encoding="utf-8"), "session s: RuntimeError: boom more\n")

    def test_relative_data_writes_no_log(self) -> None:
        """With a relative data folder the hook logs nothing and still exits 0 silently."""
        cwd = Path.cwd()
        os.chdir(self.data)
        try:
            self.assertEqual(self.end_with_error("relative"), (0, ""))
        finally:
            os.chdir(cwd)
        self.assertEqual(sorted(p.name for p in self.data.iterdir()), ["checks"])


if __name__ == "__main__":
    _ = unittest.main()
