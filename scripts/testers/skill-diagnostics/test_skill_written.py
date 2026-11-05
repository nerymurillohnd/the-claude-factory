#!/usr/bin/env python3
"""Tests for skill-diagnostics' hooks/skill_written.py.

Run: python3 -m unittest discover -s scripts/testers/skill-diagnostics -v
Standard library only; runs on the python3 on PATH on Linux, macOS and Windows.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "plugins" / "skill-diagnostics" / "hooks" / "skill_written.py"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def text_at(value: object, *keys: str) -> str:
    """Return the string under keys in nested JSON objects, or "" when absent or not a string."""
    for key in keys:
        if not isinstance(value, JsonObject):
            return ""
        value = value.get(key)
    return value if isinstance(value, str) else ""


def skill_md(root: Path) -> str:
    """Return the default SKILL.md path inside a test root."""
    return str(root / "project" / "skills" / "greet" / "SKILL.md")


def fire(
    root: Path,
    mode: str | None = None,
    path: str | None = None,
    session: str = "s1",
    raw: str | None = None,
) -> tuple[int, str]:
    """Run the hook on one Write event under root; return its exit code and context."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_")}
    env["CLAUDE_PLUGIN_DATA"] = str(root / "data")
    env["CLAUDE_CONFIG_DIR"] = str(root / ".claude")
    env["CLAUDE_PLUGIN_ROOT"] = str(REPO / "plugins" / "skill-diagnostics")
    if mode is not None:
        env["CLAUDE_PLUGIN_OPTION_ON_SKILL_WRITE"] = mode
    event = {
        "session_id": session,
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": path or skill_md(root)},
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
        context = text_at(_decode(proc.stdout), "hookSpecificOutput", "additionalContext")
    return proc.returncode, context


class SkillWrittenHook(unittest.TestCase):
    """The hook's modes, deduplication, skipped folders and failure handling."""

    def make_root(self) -> Path:
        """Return a fresh temporary folder, removed when the test ends."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name)

    def test_default_mode_suggests_the_audit(self) -> None:
        """Default mode suggests the audit."""
        code, context = fire(self.make_root())
        self.assertEqual(code, 0)
        self.assertIn("offer the user an audit", context)
        self.assertIn("/skill-diagnostics:audit", context)

    def test_run_mode_asks_to_run_it(self) -> None:
        """Run mode asks to run it."""
        _, context = fire(self.make_root(), "run")
        self.assertIn("run /skill-diagnostics:audit", context)

    def test_off_mode_is_silent(self) -> None:
        """Off mode is silent."""
        code, context = fire(self.make_root(), "off")
        self.assertEqual((code, context), (0, ""))

    def test_invalid_mode_falls_back_to_suggest(self) -> None:
        """Invalid mode falls back to suggest."""
        _, context = fire(self.make_root(), "sometimes")
        self.assertIn("offer the user an audit", context)

    def test_notifies_once_per_skill_per_session(self) -> None:
        """Notifies once per skill per session."""
        root = self.make_root()
        _, first = fire(root)
        _, second = fire(root)
        _, other_session = fire(root, session="s2")
        self.assertTrue(first)
        self.assertEqual(second, "")
        self.assertTrue(other_session)

    def test_ignores_plugin_cache_paths(self) -> None:
        """Ignores plugin cache paths."""
        root = self.make_root()
        cached = str(root / ".claude" / "plugins" / "cache" / "m" / "p" / "1.0.0" / "SKILL.md")
        _, context = fire(root, path=cached)
        self.assertEqual(context, "")

    def test_ignores_the_plugin_itself_but_not_a_sibling_folder(self) -> None:
        """Ignores the plugin itself but not a sibling folder."""
        root = self.make_root()
        own = str(REPO / "plugins" / "skill-diagnostics" / "skills" / "audit" / "SKILL.md")
        sibling = str(REPO / "plugins" / "skill-diagnostics-extra" / "skills" / "a" / "SKILL.md")
        self.assertEqual(fire(root, path=own)[1], "")
        self.assertIn("skill-diagnostics-extra", fire(root, path=sibling)[1])

    def test_relative_path_names_a_real_directory(self) -> None:
        """Relative path names a real directory."""
        _, context = fire(self.make_root(), path="SKILL.md")
        self.assertNotIn("the skill at  was", context)
        self.assertIn(str(Path.cwd()), context)

    def test_prunes_old_session_state(self) -> None:
        """Prunes old session state."""
        root = self.make_root()
        folder = root / "data" / "notified"
        folder.mkdir(parents=True)
        old = folder / "old.txt"
        _ = old.write_text("x\n", encoding="utf-8")
        stale = 40 * 24 * 3600
        os.utime(old, (old.stat().st_atime - stale, old.stat().st_mtime - stale))
        _ = fire(root)
        self.assertFalse(old.exists())

    def test_ignores_folders_claude_code_manages(self) -> None:
        """Ignores the folders Claude Code manages."""
        root = self.make_root()
        config = root / ".claude"
        managed = (
            "plugins/synced/notes/skills/a/SKILL.md",
            "plugins/marketplaces/m/skills/a/SKILL.md",
            "skills/synced/a/SKILL.md",
        )
        for rel in managed:
            self.assertEqual(fire(root, path=str(config / rel))[1], "", msg=rel)
        self.assertIn(
            "/skill-diagnostics:audit",
            fire(root, path=str(config / "skills" / "mine" / "SKILL.md"))[1],
        )

    def test_a_project_folder_named_plugins_cache_is_not_skipped(self) -> None:
        """A project folder named plugins/cache is not skipped."""
        root = self.make_root()
        project = str(root / "work" / "plugins" / "cache" / "skills" / "a" / "SKILL.md")
        self.assertIn("/skill-diagnostics:audit", fire(root, path=project)[1])

    def test_path_with_spaces_is_quoted(self) -> None:
        """A path with spaces is quoted."""
        root = self.make_root()
        spaced = str(root / "My Skills" / "greet" / "SKILL.md")
        _, context = fire(root, path=spaced)
        self.assertIn('/skill-diagnostics:audit "' + str(Path(spaced).parent) + '"', context)

    def test_bad_input_never_blocks(self) -> None:
        """Bad input never blocks."""
        code, context = fire(self.make_root(), raw="not json")
        self.assertEqual((code, context), (0, ""))


if __name__ == "__main__":
    _ = unittest.main()
