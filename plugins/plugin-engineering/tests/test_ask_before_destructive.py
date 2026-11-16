#!/usr/bin/env python3
"""Tests for the migrating-plugins skill's PreToolUse hook, ask-before-destructive.sh."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, NamedTuple
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

SKILL = Path(__file__).resolve().parent.parent / "skills" / "migrating-plugins"
SCRIPT = SKILL / "scripts" / "ask-before-destructive.sh"
CATALOG = "/work/.claude-plugin/marketplace.json"

_decode: Callable[[str], object] = json.JSONDecoder().decode


class Outcome(NamedTuple):
    """What a hook run returned."""

    code: int
    stdout: str
    stderr: str


def run_hook(payload: dict[str, object]) -> Outcome:
    """Run the hook as Claude Code does: the input JSON on stdin, then read exit code and output."""
    done = subprocess.run(
        [str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return Outcome(done.returncode, done.stdout, done.stderr)


def bash(command: str) -> dict[str, object]:
    """A PreToolUse input for a Bash call, with a cwd that names a plugins folder."""
    return {
        "hook_event_name": "PreToolUse",
        "cwd": "/work/plugins/demo",
        "tool_name": "Bash",
        "tool_input": {"command": command, "description": "test"},
    }


def edit(file_path: str, old: str, new: str) -> dict[str, object]:
    """A PreToolUse input for an Edit call."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Edit",
        "tool_input": {"file_path": file_path, "old_string": old, "new_string": new},
    }


ASK_PREFIX = (
    '{"hookSpecificOutput":{"hookEventName":"PreToolUse",'
    '"permissionDecision":"ask","permissionDecisionReason":"migrating-plugins: '
)


class AskBeforeDestructiveTest(unittest.TestCase):
    """Each destructive action gets an ask decision; everything else passes silently."""

    def assert_asks(self, outcome: Outcome) -> None:
        """The hook exited 0 with an ask decision from this skill."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        parsed = _decode(outcome.stdout)
        self.assertIsInstance(parsed, dict)
        self.assertTrue(outcome.stdout.startswith(ASK_PREFIX), outcome.stdout)

    def assert_passes(self, outcome: Outcome) -> None:
        """The hook exited 0 and printed nothing."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        self.assertEqual(outcome.stdout, "")

    def test_plugin_cli_removals_ask(self) -> None:
        """Every plugin CLI command that deletes options, secrets or data asks."""
        for command in (
            "claude plugin uninstall demo@market",
            "claude plugin remove demo@market --scope project",
            "claude plugin marketplace remove market",
            "claude plugin marketplace rm market",
            "claude plugin prune",
            "claude plugin autoremove",
            "claude plugin restore-set-aside demo@market --discard",
        ):
            with self.subTest(command=command):
                self.assert_asks(run_hook(bash(command)))

    def test_safe_plugin_commands_pass(self) -> None:
        """Plugin CLI commands that delete nothing pass."""
        for command in (
            "claude plugin list --json",
            "claude plugin prune --dry-run",
            "claude plugin restore-set-aside demo@market",
            "claude plugin marketplace update market",
            "claude plugin validate --strict plugins/demo",
        ):
            with self.subTest(command=command):
                self.assert_passes(run_hook(bash(command)))

    def test_deleting_plugin_files_asks(self) -> None:
        """Deleting plugin, marketplace or plugin-state files asks."""
        for command in (
            "rm -rf plugins/demo",
            "rm .claude-plugin/marketplace.json",
            "rmdir ~/.claude/plugins/cache/market",
            "unlink plugins/demo/.claude-plugin/plugin.json",
            "git rm -r plugins/demo",
            "find plugins/demo -name '*.tmp' -delete",
            "cd /work && rm -rf plugins/demo",
        ):
            with self.subTest(command=command):
                self.assert_asks(run_hook(bash(command)))

    def test_deleting_other_files_passes(self) -> None:
        """Deleting files outside plugins, and finding without deleting, pass."""
        for command in (
            "rm -rf build/output",
            "find plugins/demo -name '*.md'",
            "git rm docs/old.md",
        ):
            with self.subTest(command=command):
                self.assert_passes(run_hook(bash(command)))

    def test_cwd_never_matches(self) -> None:
        """A cwd that names a plugins folder doesn't make a harmless rm ask."""
        self.assert_passes(run_hook(bash("rm notes.txt")))

    def test_marketplace_edits_that_remove_plugins_ask(self) -> None:
        """Turning on forceRemoveDeletedPlugins, or a null rename, asks."""
        force = '"name": "m", "forceRemoveDeletedPlugins": true'
        self.assert_asks(run_hook(edit(CATALOG, '"name": "m"', force)))
        retire = '"renames": {"old-plugin": null}'
        self.assert_asks(run_hook(edit(CATALOG, '"renames": {}', retire)))

    def test_other_edits_pass(self) -> None:
        """A rename to a new name, and edits of other files, pass."""
        self.assert_passes(run_hook(edit(CATALOG, '"renames": {}', '"renames": {"old": "new"}')))
        self.assert_passes(run_hook(edit("/work/README.md", "a", "forceRemoveDeletedPlugins")))

    def test_input_without_tool_passes(self) -> None:
        """An input with no tool fields passes."""
        self.assert_passes(run_hook({"hook_event_name": "PreToolUse"}))


if __name__ == "__main__":
    _ = unittest.main()
