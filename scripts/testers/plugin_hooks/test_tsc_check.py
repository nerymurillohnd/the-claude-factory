#!/usr/bin/env python3
"""Tests for the changed-file selection of the TypeScript plugins' hooks/tsc-check.sh.

They hold with or without a TypeScript compiler on the machine: a file the hook selects is
named in its output either as checked or as not type-checked, and a file it leaves alone is
never named.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from testers.plugin_hooks.helpers import (
    GIT_ENV,
    PLUGINS,
    Outcome,
    clone,
    field,
    need,
    repository,
    run_hook,
    write,
)

HOOKS = (
    PLUGINS / "typescript6-lsp-intelligence" / "hooks" / "tsc-check.sh",
    PLUGINS / "typescript7-lsp-intelligence" / "hooks" / "tsc-check.sh",
)
MODULE = "export const answer: number = 42\n"
# One more than the hook's MAX_LOOSE_FILES.
TOO_MANY = 21


class TscHookTest(unittest.TestCase):
    """Which files a Bash command's hook run selects."""

    def _run(
        self, tmp: Path, hook: Path = HOOKS[0], *, changed: tuple[Path, ...] | None = None
    ) -> Outcome:
        """Run the hook for a Bash command that ran in project tmp/work for a minute.

        With changed, the event carries that list as the files Claude Code recorded.
        """
        response: dict[str, object] = {"stdout": "", "stderr": "", "interrupted": False}
        if changed is not None:
            response["bashEditDiff"] = {"changedFiles": [str(path) for path in changed]}
        event: dict[str, object] = {
            "session_id": "s1",
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "cwd": str(tmp / "work"),
            "tool_input": {"command": "true"},
            "tool_response": response,
            "duration_ms": 60000,
        }
        (tmp / "home").mkdir(exist_ok=True)
        env = {
            "PATH": os.environ["PATH"],
            "HOME": str(tmp / "home"),
            "TMPDIR": str(tmp),
            "CLAUDE_PLUGIN_DATA": str(tmp / "data"),
            "CLAUDE_PROJECT_DIR": str(tmp / "work"),
            **GIT_ENV,
        }
        return run_hook([need("bash"), str(hook)], event, env)

    def test_both_plugins_ship_the_same_hook(self) -> None:
        """The hook is byte-identical in typescript6 and typescript7, as its header says."""
        self.assertEqual(HOOKS[0].read_bytes(), HOOKS[1].read_bytes())

    def test_clone_into_a_plain_folder_is_left_alone(self) -> None:
        """Files a clone wrote are unchanged for Git: the hook prints nothing."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repository(tmp / "origin", {"a.ts": MODULE, "src/b.ts": MODULE})
            clone(tmp / "origin", tmp / "work" / "clone")
            outcome = self._run(tmp)
        self.assertEqual(outcome, Outcome(0, "", ""))

    def test_edit_inside_a_nested_work_tree_is_selected(self) -> None:
        """Of a cloned repository's files, only the one the command modified is selected."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repository(tmp / "origin", {"a.ts": MODULE, "b.ts": MODULE})
            clone(tmp / "origin", tmp / "work" / "clone")
            write(tmp / "work" / "clone" / "a.ts", f"{MODULE}export const more = 1\n")
            outcome = self._run(tmp)
        self.assertEqual(outcome.code, 0)
        self.assertIn("clone/a.ts", outcome.stdout)
        self.assertNotIn("b.ts", outcome.stdout)

    def test_output_git_ignores_is_left_alone(self) -> None:
        """Of the files a command changed, the one Git ignores is output and is not selected."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            work = tmp / "work"
            repository(work, {".gitignore": "generated/\n", "kept.ts": MODULE})
            write(work / "generated" / "built.ts", MODULE)
            write(work / "kept.ts", f"{MODULE}export const more = 1\n")
            outcome = self._run(tmp, changed=(work / "generated" / "built.ts", work / "kept.ts"))
        self.assertEqual(outcome.code, 0)
        self.assertIn("kept.ts", outcome.stdout)
        self.assertNotIn("built.ts", outcome.stdout)

    def test_arrival_outside_git_is_not_checked(self) -> None:
        """More loose files than the hook checks per command: none is selected, Claude is told."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            for number in range(TOO_MANY):
                write(tmp / "work" / "tree" / f"m{number}.ts", MODULE)
            outcome = self._run(tmp)
        self.assertEqual((outcome.code, outcome.stderr), (0, ""))
        context = field(outcome.stdout, "hookSpecificOutput", "additionalContext")
        expected = f"left {TOO_MANY} TypeScript or JavaScript files outside a Git work tree"
        self.assertIn(expected, context)
        self.assertNotIn("m0.ts", outcome.stdout)

    def test_a_few_loose_files_are_selected(self) -> None:
        """Outside Git, a handful of new files is an edit: the hook selects them."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            write(tmp / "work" / "new.ts", MODULE)
            outcome = self._run(tmp)
        self.assertEqual(outcome.code, 0)
        self.assertIn("new.ts", outcome.stdout)


if __name__ == "__main__":
    _ = unittest.main()
