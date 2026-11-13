#!/usr/bin/env python3
"""Tests for skill-diagnostics' Stop gate: hooks/session-start.sh, then hooks/audit-gate.sh."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from testers.plugin_hooks.helpers import (
    GIT_ENV,
    LONG_AGO,
    PLUGINS,
    Outcome,
    age,
    clone,
    field,
    git,
    need,
    repository,
    run_hook,
    write,
)

HOOKS = PLUGINS / "skill-diagnostics" / "hooks"
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
