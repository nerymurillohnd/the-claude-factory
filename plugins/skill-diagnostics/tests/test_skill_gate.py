#!/usr/bin/env python3
"""Tests for skill-diagnostics' Stop gate: hooks/session-start.sh, then hooks/audit-gate.sh."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import TYPE_CHECKING, NamedTuple, cast
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

_decode: Callable[[str], object] = json.JSONDecoder().decode


# A neutral Git identity and configuration, so the machine's own settings never apply.
GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


# A commit date long before any test session, for the commits a repository already had.
LONG_AGO = "2026-01-01T00:00:00Z"


class Outcome(NamedTuple):
    """What a hook run returned."""

    code: int
    stdout: str
    stderr: str


def need(name: str) -> str:
    """The path of tool `name`; the test is skipped when it is not installed."""
    found = shutil.which(name)
    if found is None:
        message = f"{name} is not installed"
        raise unittest.SkipTest(message)
    return found


def run_hook(argv: list[str], event: dict[str, object], env: dict[str, str]) -> Outcome:
    """Run a hook command with event on stdin and exactly env as its environment."""
    done = subprocess.run(
        argv, input=json.dumps(event), env=env, capture_output=True, text=True, check=False
    )
    return Outcome(done.returncode, done.stdout, done.stderr)


def git(folder: Path, *args: str, when: str = "") -> None:
    """Run git in folder with the neutral configuration; `when` dates a commit it creates."""
    env = {**os.environ, **GIT_ENV}
    if when:
        env["GIT_AUTHOR_DATE"] = when
        env["GIT_COMMITTER_DATE"] = when
    _ = subprocess.run(
        [need("git"), "-C", str(folder), *args], env=env, check=True, capture_output=True
    )


def write(path: Path, text: str) -> None:
    """Write text to path, creating its folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(text, encoding="utf-8")


def repository(folder: Path, files: dict[str, str]) -> None:
    """Create folder as a Git repository whose only commit, made long ago, holds files."""
    folder.mkdir(parents=True)
    git(folder, "init", "-q", "-b", "main")
    for name, text in files.items():
        write(folder / name, text)
    git(folder, "add", "-A")
    git(folder, "commit", "-q", "-m", "first", when=LONG_AGO)


def clone(origin: Path, target: Path) -> None:
    """Clone origin into target, as a session's `git clone` does."""
    target.parent.mkdir(parents=True, exist_ok=True)
    git(target.parent, "clone", "-q", str(origin), str(target))


def age(path: Path, seconds: int) -> None:
    """Set the modification time of path, and of everything under it, to `seconds` ago."""
    then = time.time() - seconds
    targets = [path, *path.rglob("*")] if path.is_dir() else [path]
    for target in targets:
        os.utime(target, (then, then))


def field(stdout: str, *keys: str) -> str:
    """The string under keys in the JSON object a hook printed; "" when absent or not text."""
    value = _decode(stdout)
    for key in keys:
        if not isinstance(value, dict):
            return ""
        value = cast("dict[str, object]", value).get(key)
    return value if isinstance(value, str) else ""


HOOKS = Path(__file__).resolve().parents[1] / "hooks"
SKILL = "---\nname: pdf\ndescription: Fills PDF forms.\n---\n\n# PDF\n"
# A jq that fails with status 2 where the gate prints its answer, and is the real jq elsewhere.
BROKEN_JQ = """#!/usr/bin/env bash
if [[ "$1" == -cn ]]; then exit 2; fi
exec "{jq}" "$@"
"""


class SkillGateTest(unittest.TestCase):
    """Which skills the gate asks Claude to audit when it stops."""

    def _env(self, tmp: Path) -> dict[str, str]:
        """The environment Claude Code gives the plugin's hooks, inside tmp."""
        _ = need("jq")
        (tmp / "home").mkdir(exist_ok=True)
        (tmp / "work").mkdir(exist_ok=True)
        return {
            "PATH": os.environ["PATH"],
            "HOME": str(tmp / "home"),
            "CLAUDE_CONFIG_DIR": str(tmp / "config"),
            "CLAUDE_PLUGIN_DATA": str(tmp / "data"),
            "CLAUDE_PLUGIN_ROOT": str(HOOKS.parent),
            "CLAUDE_PROJECT_DIR": str(tmp / "work"),
            **GIT_ENV,
        }

    def _start(self, tmp: Path) -> Path:
        """Run the SessionStart hook, date the marker 50 s back and return its path."""
        event: dict[str, object] = {
            "session_id": "s1",
            "hook_event_name": "SessionStart",
            "source": "startup",
        }
        started = run_hook([need("bash"), str(HOOKS / "session-start.sh")], event, self._env(tmp))
        self.assertEqual(started, Outcome(0, "", ""))
        marker = tmp / "data" / "sessions" / "s1"
        age(marker, 50)
        return marker

    def _stop(self, tmp: Path, path: str = "") -> Outcome:
        """Run the Stop hook; `path` replaces PATH when given."""
        event: dict[str, object] = {
            "session_id": "s1",
            "hook_event_name": "Stop",
            "stop_hook_active": False,
        }
        env = self._env(tmp)
        if path:
            env["PATH"] = path
        return run_hook([need("bash"), str(HOOKS / "audit-gate.sh")], event, env)

    def _asked(self, outcome: Outcome) -> str:
        """The audits the gate asked for; fails the test when the hook itself failed."""
        self.assertEqual((outcome.code, outcome.stderr), (0, ""))
        return field(outcome.stdout, "hookSpecificOutput", "additionalContext")

    def test_marker_holds_the_session_start(self) -> None:
        """The SessionStart hook writes the start time, in seconds, into the marker."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            content = self._start(tmp).read_text(encoding="utf-8").strip()
        self.assertTrue(content.isdigit(), content)

    def test_clone_mid_session_is_silent(self) -> None:
        """A repository cloned during the session brings skills nobody changed."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repository(tmp / "origin", {"skills/pdf/SKILL.md": SKILL})
            _ = self._start(tmp)
            clone(tmp / "origin", tmp / "work" / "clone")
            outcome = self._stop(tmp)
        self.assertEqual(outcome, Outcome(0, "", ""))

    def test_checkout_mid_session_is_silent(self) -> None:
        """Switching branches rewrites a skill's files without the session changing them."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repo = tmp / "work" / "repo"
            repository(repo, {"skills/pdf/SKILL.md": SKILL})
            git(repo, "checkout", "-q", "-b", "other")
            write(repo / "skills" / "pdf" / "SKILL.md", f"{SKILL}\nMore.\n")
            git(repo, "commit", "-q", "-am", "second", when=LONG_AGO)
            age(repo, 100)
            _ = self._start(tmp)
            git(repo, "checkout", "-q", "main")
            outcome = self._stop(tmp)
        self.assertEqual(outcome, Outcome(0, "", ""))

    def test_skill_changed_through_the_shell_is_gated(self) -> None:
        """A tracked skill file rewritten during the session is modified for Git."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repo = tmp / "work" / "repo"
            repository(repo, {"skills/pdf/SKILL.md": SKILL, "skills/doc/SKILL.md": SKILL})
            age(repo, 100)
            _ = self._start(tmp)
            write(repo / "skills" / "pdf" / "SKILL.md", f"{SKILL}\nMore.\n")
            asked = self._asked(self._stop(tmp))
        self.assertIn(f"Skill {repo}/skills/pdf changed", asked)
        self.assertNotIn("skills/doc", asked)

    def test_skill_changed_and_committed_is_gated(self) -> None:
        """A commit made in the session keeps its skill gated though the work tree is clean."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repo = tmp / "work" / "repo"
            repository(repo, {"skills/pdf/SKILL.md": SKILL, "skills/doc/SKILL.md": SKILL})
            age(repo, 100)
            _ = self._start(tmp)
            write(repo / "skills" / "pdf" / "SKILL.md", f"{SKILL}\nMore.\n")
            git(repo, "commit", "-q", "-am", "change the skill")
            asked = self._asked(self._stop(tmp))
        self.assertIn(f"Skill {repo}/skills/pdf changed", asked)
        self.assertNotIn("skills/doc", asked)

    def test_skill_outside_git_follows_the_file_times(self) -> None:
        """Outside a work tree, a skill written after the session start is gated; no older one."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            write(tmp / "work" / "old" / "SKILL.md", SKILL)
            age(tmp / "work", 100)
            _ = self._start(tmp)
            write(tmp / "work" / "new" / "SKILL.md", SKILL)
            asked = self._asked(self._stop(tmp))
        self.assertIn(f"Skill {tmp}/work/new changed", asked)
        self.assertNotIn("work/old", asked)

    def test_marker_without_a_start_time_follows_the_file_times(self) -> None:
        """An empty marker, from before 0.4.1, keeps the old rule: new file times alone gate."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repository(tmp / "origin", {"skills/pdf/SKILL.md": SKILL})
            marker = self._start(tmp)
            _ = marker.write_text("", encoding="utf-8")
            age(marker, 50)
            clone(tmp / "origin", tmp / "work" / "clone")
            asked = self._asked(self._stop(tmp))
        self.assertIn("clone/skills/pdf changed", asked)

    def test_a_failure_exits_1_never_2(self) -> None:
        """Exit 2 would keep Claude from stopping, so a command failing with 2 must become 1."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            _ = self._start(tmp)
            write(tmp / "work" / "new" / "SKILL.md", SKILL)
            stub = tmp / "bin" / "jq"
            write(stub, BROKEN_JQ.replace("{jq}", need("jq")))
            stub.chmod(0o755)
            outcome = self._stop(tmp, f"{tmp / 'bin'}{os.pathsep}{os.environ['PATH']}")
        self.assertEqual(outcome.code, 1)
        self.assertIn("audit-gate.sh failed", outcome.stderr)


if __name__ == "__main__":
    _ = unittest.main()
