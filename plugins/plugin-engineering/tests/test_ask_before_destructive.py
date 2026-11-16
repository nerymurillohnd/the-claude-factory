#!/usr/bin/env python3
"""Tests for the migrating-plugins skill's PreToolUse hook, ask-before-destructive.sh."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING, NamedTuple
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

SKILL = Path(__file__).resolve().parent.parent / "skills" / "migrating-plugins"
SCRIPT = SKILL / "scripts" / "ask-before-destructive.sh"
CATALOG = "/work/.claude-plugin/marketplace.json"

# A grep that fails with exit 2 on every -Eq or -Evq check and runs the real grep otherwise.
FAKE_GREP = """#!/usr/bin/env bash
case "$1" in -Eq | -Evq) exit 2 ;; esac
exec REAL_GREP "$@"
"""

_decode: Callable[[str], object] = json.JSONDecoder().decode


class Outcome(NamedTuple):
    """What a hook run returned."""

    code: int
    stdout: str
    stderr: str


def run_hook(payload: dict[str, object], env: dict[str, str] | None = None) -> Outcome:
    """Run the hook as Claude Code does: the input JSON on stdin, then read exit code and output."""
    done = subprocess.run(
        [str(SCRIPT)],
        env=env,
        input=json.dumps(payload, separators=(",", ":")),
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


def write(file_path: str, content: str) -> dict[str, object]:
    """A PreToolUse input for a Write call."""
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
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

    def assert_asks(self, outcome: Outcome, keyword: str = "") -> None:
        """The hook exited 0 with an ask decision from this skill, whose reason has keyword."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        self.assertEqual(outcome.stderr, "")
        self.assertIn(keyword, outcome.stdout)
        parsed = _decode(outcome.stdout)
        self.assertIsInstance(parsed, dict)
        self.assertTrue(outcome.stdout.startswith(ASK_PREFIX), outcome.stdout)

    def assert_passes(self, outcome: Outcome) -> None:
        """The hook exited 0 and printed nothing."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        self.assertEqual(outcome.stdout, "")

    def test_plugin_cli_removals_ask(self) -> None:
        """Every plugin CLI command that deletes options, secrets or data asks."""
        for command, keyword in (
            ("claude plugin uninstall demo@market", "uninstalling"),
            ("claude plugin uninstall demo@market --keep-data", "uninstalling"),
            ("claude plugin remove demo@market --scope project", "uninstalling"),
            ("claude plugin rm demo", "uninstalling"),
            ("claude plugin uninstall", "uninstalling"),
            ("claude plugin marketplace remove market", "removing a marketplace"),
            ("claude plugin marketplace rm market", "removing a marketplace"),
            ("claude plugin marketplace remove", "removing a marketplace"),
            ("claude plugin prune", "prune"),
            ("claude plugin autoremove", "prune"),
            ("claude plugin prune --dry-run && claude plugin prune", "prune"),
            ("claude plugin prune; echo --dry-run", "prune"),
            ("claude plugin restore-set-aside demo@market --discard", "--discard"),
            ("claude plugins uninstall demo@market", "uninstalling"),
            ("claude plugins marketplace rm market", "removing a marketplace"),
            ("claude plugins prune", "prune"),
            ("cd /work\nclaude plugin uninstall demo", "uninstalling"),
        ):
            with self.subTest(command=command):
                self.assert_asks(run_hook(bash(command)), keyword)

    def test_safe_plugin_commands_pass(self) -> None:
        """Plugin CLI commands that delete nothing pass."""
        for command in (
            "claude plugin list --json",
            "claude plugin prune --dry-run",
            "claude plugin autoremove --dry-run",
            "claude plugin prune --dry-run --json",
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
            'rm -rf "plugins/demo"',
            "rm -rf 'plugins/demo'",
            "rm -rf /abs/plugins/demo",
            "rm ~/.claude/plugins/installed_plugins.json",
            "rm installed_plugins.json",
            "rm known_marketplaces.json",
            "rm plugin.json",
            "rm marketplace.json",
            "rm -rf ~/.claude/plugins",
            "x;rm plugins/demo",
            "(rm plugins/demo)",
            "ls | xargs rm plugins/demo",
            "find plugins/demo -name x -exec rm {} +",
            "cd /work\nrm -rf plugins/demo",
            "rm\t-rf plugins/demo",
            "rm -rf plugins",
            "cd plugins && rm -rf demo",
            "find plugins -delete",
            "rm -rf ~/.claude",
            'rm -rf "${CLAUDE_PLUGIN_DATA}"',
            'find . -path "*plugins/*" -delete',
        ):
            with self.subTest(command=command):
                self.assert_asks(run_hook(bash(command)))

    def test_deleting_other_files_passes(self) -> None:
        """Deleting files outside plugins, and finding without deleting, pass."""
        for command in (
            "rm -rf build/output",
            "find plugins/demo -name '*.md'",
            "git rm docs/old.md",
            "rm -rf myplugins/demo",
        ):
            with self.subTest(command=command):
                self.assert_passes(run_hook(bash(command)))

    def test_cwd_never_matches(self) -> None:
        """A cwd that names a plugins folder doesn't make a harmless rm ask."""
        self.assert_passes(run_hook(bash("rm notes.txt")))

    def test_description_never_matches(self) -> None:
        """Only the command is matched, never the call's description."""
        payload = bash("ls")
        payload["tool_input"] = {"command": "ls", "description": "rm -rf plugins/demo"}
        self.assert_passes(run_hook(payload))

    def test_marketplace_edits_that_remove_plugins_ask(self) -> None:
        """Turning on forceRemoveDeletedPlugins, or a null rename, asks."""
        force = '"name": "m", "forceRemoveDeletedPlugins": true'
        self.assert_asks(run_hook(edit(CATALOG, '"name": "m"', force)), "forceRemoveDeletedPlugins")
        retire = '"renames": {"old-plugin": null}'
        self.assert_asks(run_hook(edit(CATALOG, '"renames": {}', retire)), "null")
        # An edit inside the renames map often doesn't include the "renames" key itself.
        entry = '"old-plugin": null,\n    "older": "new"'
        self.assert_asks(run_hook(edit(CATALOG, '"older": "new"', entry)), "null")

    def test_marketplace_writes_that_remove_plugins_ask(self) -> None:
        """A Write of the catalog asks on the same changes as an Edit."""
        retire = '{"name": "m", "plugins": [], "renames": {"old": null}}'
        self.assert_asks(run_hook(write(CATALOG, retire)), "null")
        force = '{"name": "m", "plugins": [], "forceRemoveDeletedPlugins": true}'
        self.assert_asks(run_hook(write(CATALOG, force)), "forceRemoveDeletedPlugins")
        self.assert_passes(run_hook(write(CATALOG, '{"name": "m", "plugins": []}')))

    def test_other_edits_pass(self) -> None:
        """A rename to a new name, and edits of other files, pass."""
        self.assert_passes(run_hook(edit(CATALOG, '"renames": {}', '"renames": {"old": "new"}')))
        self.assert_passes(run_hook(edit("/work/README.md", "a", "forceRemoveDeletedPlugins")))

    def test_grep_error_blocks(self) -> None:
        """A grep that fails with exit 2 makes the hook fail with 1, which blocks, never pass."""
        with tempfile.TemporaryDirectory() as folder:
            fake = Path(folder) / "grep"
            real = shutil.which("grep")
            self.assertIsNotNone(real)
            _ = fake.write_text(FAKE_GREP.replace("REAL_GREP", str(real)), encoding="utf-8")
            fake.chmod(0o755)
            env = {**os.environ, "PATH": f"{folder}{os.pathsep}{os.environ.get('PATH', '')}"}
            for payload in (
                bash("claude plugin marketplace remove market"),
                edit(CATALOG, "a", '"forceRemoveDeletedPlugins": true'),
            ):
                with self.subTest(payload=payload):
                    outcome = run_hook(payload, env)
                    self.assertEqual(outcome.code, 1, outcome.stdout)
                    self.assertEqual(outcome.stdout, "")

    def test_input_without_tool_passes(self) -> None:
        """An input with no tool fields passes."""
        self.assert_passes(run_hook({"hook_event_name": "PreToolUse"}))


if __name__ == "__main__":
    _ = unittest.main()
