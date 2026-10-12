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
        env["CLAUDE_CONFIG_DIR"] = str(Path(self._tmp.name) / ".claude")
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

    def test_ignores_the_plugin_itself_but_not_a_sibling_folder(self) -> None:
        own = str(REPO / "plugins" / "skill-diagnostics" / "skills" / "audit" / "SKILL.md")
        sibling = str(REPO / "plugins" / "skill-diagnostics-extra" / "skills" / "a" / "SKILL.md")
        self.assertEqual(self.fire(path=own)[1], "")
        self.assertIn("skill-diagnostics-extra", self.fire(path=sibling)[1])

    def test_relative_path_names_a_real_directory(self) -> None:
        _, context = self.fire(path="SKILL.md")
        self.assertNotIn("the skill at  was", context)
        self.assertIn(os.getcwd(), context)

    def test_prunes_old_session_state(self) -> None:
        folder = self.data / "notified"
        folder.mkdir(parents=True)
        old = folder / "old.txt"
        old.write_text("x\n", encoding="utf-8")
        stale = 40 * 24 * 3600
        os.utime(old, (old.stat().st_atime - stale, old.stat().st_mtime - stale))
        self.fire()
        self.assertFalse(old.exists())

    def test_ignores_folders_claude_code_manages(self) -> None:
        config = Path(self._tmp.name) / ".claude"
        managed = (
            "plugins/synced/notes/skills/a/SKILL.md",
            "plugins/marketplaces/m/skills/a/SKILL.md",
            "skills/synced/a/SKILL.md",
        )
        for rel in managed:
            self.assertEqual(self.fire(path=str(config / rel))[1], "", rel)
        self.assertIn("/skill-diagnostics:audit", self.fire(path=str(config / "skills" / "mine" / "SKILL.md"))[1])

    def test_a_project_folder_named_plugins_cache_is_not_skipped(self) -> None:
        project = str(Path(self._tmp.name) / "work" / "plugins" / "cache" / "skills" / "a" / "SKILL.md")
        self.assertIn("/skill-diagnostics:audit", self.fire(path=project)[1])

    def test_path_with_spaces_is_quoted(self) -> None:
        spaced = str(Path(self._tmp.name) / "My Skills" / "greet" / "SKILL.md")
        _, context = self.fire(path=spaced)
        self.assertIn('/skill-diagnostics:audit "' + str(Path(spaced).parent) + '"', context)

    def test_bad_input_never_blocks(self) -> None:
        code, context = self.fire(raw="not json")
        self.assertEqual((code, context), (0, ""))


if __name__ == "__main__":
    unittest.main()
