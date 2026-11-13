#!/usr/bin/env python3
"""Tests for bash-lsp-intelligence's hooks/check.mjs, run with stub shfmt and shellcheck."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from testers.plugin_hooks.helpers import (
    GIT_ENV,
    PLUGINS,
    Outcome,
    clone,
    field,
    logged,
    need,
    repository,
    run_hook,
    tool_dir,
    write,
)

HOOK = PLUGINS / "bash-lsp-intelligence" / "hooks" / "check.mjs"
SCRIPT = "#!/usr/bin/env bash\necho hi\n"
# One more than the hook's MAX_FILES.
TOO_MANY = 21
BLOCKED = 2


class BashHookTest(unittest.TestCase):
    """What the hook checks, what it leaves alone, and that it never blocks without a finding."""

    def _run(
        self, tmp: Path, event: dict[str, object], *, tools: bool = True, **extra: str
    ) -> tuple[Outcome, list[str]]:
        """Run the hook in project tmp/work and return (outcome, stub calls)."""
        node = need("node")
        bin_dir = tmp / "bin"
        if not bin_dir.is_dir():
            _ = tool_dir(tmp, ("git", "bash", "sh"), ("shfmt", "shellcheck") if tools else ())
        log = tmp / "log.txt"
        env = {
            "PATH": str(bin_dir),
            "HOME": str(tmp / "home"),
            "CLAUDE_PLUGIN_DATA": str(tmp / "data"),
            "CLAUDE_PROJECT_DIR": str(tmp / "work"),
            "STUB_LOG": str(log),
            **GIT_ENV,
            **extra,
        }
        return run_hook([node, str(HOOK)], event, env), logged(log)

    @staticmethod
    def _bash(tmp: Path) -> dict[str, object]:
        """A PostToolUse event of a Bash command that ran in the project for a minute."""
        return {
            "session_id": "s1",
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "cwd": str(tmp / "work"),
            "tool_input": {"command": "true"},
            "tool_response": {"stdout": "", "stderr": "", "interrupted": False, "isImage": False},
            "duration_ms": 60000,
        }

    @staticmethod
    def _edit(path: Path) -> dict[str, object]:
        """A PostToolUse event of an Edit of path."""
        return {
            "session_id": "s1",
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": str(path)},
        }

    def test_missing_tool_gives_one_notice_and_never_blocks(self) -> None:
        """Without shfmt the hook exits 0, tells the user and Claude once, then stays silent."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            write(tmp / "work" / "a.sh", SCRIPT)
            first, _ = self._run(tmp, self._edit(tmp / "work" / "a.sh"), tools=False)
            second, _ = self._run(tmp, self._edit(tmp / "work" / "a.sh"), tools=False)
        self.assertEqual((first.code, first.stderr), (0, ""))
        self.assertIn("shfmt is not installed", field(first.stdout, "systemMessage"))
        context = field(first.stdout, "hookSpecificOutput", "additionalContext")
        self.assertIn("Do not treat them as checked", context)
        self.assertEqual((second.code, second.stdout, second.stderr), (0, "", ""))

    def test_clone_into_a_plain_folder_is_left_alone(self) -> None:
        """Files a clone wrote are unchanged for Git: no tool runs on them and nothing is said."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repository(tmp / "origin", {"a.sh": SCRIPT, "bin/b.sh": SCRIPT})
            clone(tmp / "origin", tmp / "work" / "clone")
            outcome, calls = self._run(tmp, self._bash(tmp))
        self.assertEqual(outcome, Outcome(0, "", ""))
        self.assertEqual(calls, [])

    def test_edit_inside_a_nested_work_tree_is_checked(self) -> None:
        """Of a cloned repository's files, only the one the command modified is checked."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            repository(tmp / "origin", {"a.sh": SCRIPT, "b.sh": SCRIPT})
            clone(tmp / "origin", tmp / "work" / "clone")
            write(tmp / "work" / "clone" / "a.sh", f"{SCRIPT}echo more\n")
            outcome, calls = self._run(tmp, self._bash(tmp))
        self.assertEqual((outcome.code, outcome.stderr), (0, ""))
        self.assertIn("passed · clone/a.sh", field(outcome.stdout, "systemMessage"))
        self.assertTrue(any(call.endswith("clone/a.sh") for call in calls), calls)
        self.assertFalse(any(call.endswith("b.sh") for call in calls), calls)

    def test_arrival_outside_git_is_not_checked(self) -> None:
        """More loose files than the hook checks per command: none is touched, Claude is told."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            for number in range(TOO_MANY):
                write(tmp / "work" / "tree" / f"s{number}.sh", SCRIPT)
            outcome, calls = self._run(tmp, self._bash(tmp))
        self.assertEqual((outcome.code, outcome.stderr), (0, ""))
        context = field(outcome.stdout, "hookSpecificOutput", "additionalContext")
        self.assertIn(f"left {TOO_MANY} shell files outside a Git work tree", context)
        self.assertEqual(calls, [])

    def test_output_git_ignores_is_left_alone(self) -> None:
        """Of the files a command changed, the one Git ignores is output and is not checked."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            work = tmp / "work"
            repository(work, {".gitignore": "generated/\n", "kept.sh": SCRIPT})
            write(work / "generated" / "hook.sh", SCRIPT)
            write(work / "kept.sh", f"{SCRIPT}echo more\n")
            event = self._bash(tmp)
            changed = [str(work / "generated" / "hook.sh"), str(work / "kept.sh")]
            event["tool_response"] = {"bashEditDiff": {"changedFiles": changed}}
            outcome, calls = self._run(tmp, event)
        self.assertEqual((outcome.code, outcome.stderr), (0, ""))
        self.assertTrue(any(call.endswith("kept.sh") for call in calls), calls)
        self.assertFalse(any(call.endswith("hook.sh") for call in calls), calls)

    def test_findings_still_block(self) -> None:
        """A finding still reaches Claude through stderr and exit 2."""
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw).resolve()
            write(tmp / "work" / "a.sh", SCRIPT)
            outcome, _ = self._run(tmp, self._edit(tmp / "work" / "a.sh"), STUB_EXIT_shellcheck="1")
        self.assertEqual(outcome.code, BLOCKED)
        self.assertIn("shellcheck (", outcome.stderr)
        self.assertIn("Fix these findings in a.sh", outcome.stderr)


if __name__ == "__main__":
    _ = unittest.main()
