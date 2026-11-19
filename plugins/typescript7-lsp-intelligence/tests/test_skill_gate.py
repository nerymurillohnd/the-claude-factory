#!/usr/bin/env python3
"""Tests for the skill gate: the first TypeScript edit of a session waits for its skill."""

from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import override
import unittest

DENY = re.compile(r'"permissionDecision"\s*:\s*"deny"')

PLUGIN = "typescript7-lsp-intelligence"
SKILL = "typescript7-lsp-intelligence:ts-lifecycle"
ROOT = Path(__file__).resolve().parents[1]
HOOK = ["bash", str(ROOT / "hooks" / "tsc-check.sh")]
OWN_FILE = "/project/app.ts"
OTHER_FILE = "/project/app.py"


def edit(path: str, session: str = "s1", agent: str = "") -> dict[str, object]:
    """A PreToolUse event for an Edit of path."""
    event: dict[str, object] = {
        "session_id": session,
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": path, "old_string": "a", "new_string": "b"},
    }
    if agent:
        event["agent_id"] = agent
    return event


def decision(output: str) -> str:
    """Return deny when the hook's stdout denies the tool call, else an empty string."""
    return "deny" if DENY.search(output) else ""


class SkillGateTest(unittest.TestCase):
    """The gate denies the first edit once, until the skill loads, per session and agent."""

    data: str = ""

    @override
    def setUp(self) -> None:
        """A fresh CLAUDE_PLUGIN_DATA folder for each test."""
        self.data = tempfile.mkdtemp(prefix="skill-gate-")
        self.addCleanup(shutil.rmtree, self.data, ignore_errors=True)

    def hook(self, event: Mapping[str, object], *, data: bool = True) -> str:
        """Run the hook on event; assert it exits 0 and return its stdout."""
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
        if data:
            env["CLAUDE_PLUGIN_DATA"] = self.data
        env["CLAUDE_PLUGIN_ROOT"] = str(ROOT)
        result = subprocess.run(
            HOOK, input=json.dumps(event), env=env, capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_first_edit_is_denied_once(self) -> None:
        """The first edit of the language is denied, naming the skill; the next goes through."""
        first = self.hook(edit(OWN_FILE))
        self.assertEqual(decision(first), "deny")
        self.assertIn(SKILL, first)
        self.assertEqual(decision(self.hook(edit(OWN_FILE))), "")

    def test_other_language_is_ignored(self) -> None:
        """An edit of another language's file never waits for this skill."""
        self.assertEqual(decision(self.hook(edit(OTHER_FILE))), "")

    def test_loaded_skill_lets_edits_through(self) -> None:
        """After the Skill tool loads the skill, the first edit goes through."""
        load = {
            "session_id": "s1",
            "hook_event_name": "PostToolUse",
            "tool_name": "Skill",
            "tool_input": {"skill": SKILL},
        }
        self.assertEqual(self.hook(load), "")
        self.assertEqual(decision(self.hook(edit(OWN_FILE))), "")

    def test_typed_command_counts_as_a_load(self) -> None:
        """A /skill typed by the user loads it too."""
        typed = {
            "session_id": "s1",
            "hook_event_name": "UserPromptExpansion",
            "command_name": SKILL,
        }
        _ = self.hook(typed)
        self.assertEqual(decision(self.hook(edit(OWN_FILE))), "")

    def test_compaction_asks_again(self) -> None:
        """After compaction the next edit waits for the skill again."""
        _ = self.hook(edit(OWN_FILE))
        _ = self.hook({"session_id": "s1", "hook_event_name": "PostCompact", "trigger": "auto"})
        self.assertEqual(decision(self.hook(edit(OWN_FILE))), "deny")

    def test_subagent_counts_on_its_own(self) -> None:
        """A subagent has its own context, so its first edit waits even after the main one."""
        _ = self.hook(edit(OWN_FILE))
        self.assertEqual(decision(self.hook(edit(OWN_FILE, agent="a1"))), "deny")

    def test_without_plugin_data_the_gate_is_off(self) -> None:
        """Without CLAUDE_PLUGIN_DATA the gate keeps no marker and never denies."""
        self.assertEqual(decision(self.hook(edit(OWN_FILE), data=False)), "")


if __name__ == "__main__":
    _ = unittest.main()
