"""Tests for skill-diagnostics' hooks/skill_written.py.

Run: python3 -m unittest discover -s .github/scripts/tests/skill-diagnostics -v
Standard library only; runs on Python 3.9+ on Linux, macOS and Windows.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
HOOK = REPO / "plugins" / "skill-diagnostics" / "hooks" / "skill_written.py"


class SkillWrittenHook(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.data = Path(self._tmp.name) / "data"
        self.skill_md = str(Path(self._tmp.name) / "project" / "skills" / "greet" / "SKILL.md")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def fire(self, mode: str | None = None, path: str | None = None, session: str = "s1", raw: str | None = None):
        env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_")}
        env["CLAUDE_PLUGIN_DATA"] = str(self.data)
        env["CLAUDE_PLUGIN_ROOT"] = str(REPO / "plugins" / "skill-diagnostics")
        if mode is not None:
            env["CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE"] = mode
        event = {
            "session_id": session,
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": path or self.skill_md},
        }
        proc = subprocess.run(
            [sys.executable, str(HOOK)],
            input=raw if raw is not None else json.dumps(event),
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            check=False,
        )
        context = ""
        if proc.stdout.strip():
            context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        return proc.returncode, context

    def test_default_mode_suggests_the_audit(self) -> None:
        code, context = self.fire()
        self.assertEqual(code, 0)
        self.assertIn("offer the user an audit", context)
        self.assertIn("/skill-diagnostics:audit", context)

    def test_run_mode_asks_to_run_it(self) -> None:
        _, context = self.fire("run")
        self.assertIn("run /skill-diagnostics:audit", context)

    def test_off_mode_is_silent(self) -> None:
        code, context = self.fire("off")
        self.assertEqual((code, context), (0, ""))

    def test_invalid_mode_falls_back_to_suggest(self) -> None:
        _, context = self.fire("sometimes")
        self.assertIn("offer the user an audit", context)

    def test_notifies_once_per_skill_per_session(self) -> None:
        _, first = self.fire()
        _, second = self.fire()
        _, other_session = self.fire(session="s2")
        self.assertTrue(first)
        self.assertEqual(second, "")
        self.assertTrue(other_session)

    def test_ignores_plugin_cache_paths(self) -> None:
        cached = str(Path(self._tmp.name) / ".claude" / "plugins" / "cache" / "m" / "p" / "1.0.0" / "SKILL.md")
        _, context = self.fire(path=cached)
        self.assertEqual(context, "")

    def test_bad_input_never_blocks(self) -> None:
        code, context = self.fire(raw="not json")
        self.assertEqual((code, context), (0, ""))


if __name__ == "__main__":
    unittest.main()
