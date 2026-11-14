#!/usr/bin/env python3
"""Tests for bash-lsp-intelligence's hooks/check.mjs, run with stub shfmt and shellcheck."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING, NamedTuple, cast
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

_decode: Callable[[str], object] = json.JSONDecoder().decode


# A stub tool logs its name and arguments, then exits with STUB_EXIT_<name> (0 by default).
STUB = """#!/usr/bin/env bash
name="${0##*/}"
printf '%s %s\\n' "${name}" "$*" >> "${STUB_LOG}"
code_var="STUB_EXIT_${name}"
exit "${!code_var:-0}"
"""


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


def tool_dir(tmp: Path, real: tuple[str, ...], stubs: tuple[str, ...] = ()) -> Path:
    """A folder to stand as the whole PATH: links to the real tools named, plus stub tools."""
    folder = tmp / "bin"
    folder.mkdir()
    for name in real:
        (folder / name).symlink_to(need(name))
    for name in stubs:
        stub = folder / name
        _ = stub.write_text(STUB, encoding="utf-8")
        stub.chmod(0o755)
    return folder


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


def folders_named(root: Path, prefix: str) -> list[str]:
    """The paths under root whose name starts with prefix: what a hook left behind, if any."""
    return sorted(str(path) for path in root.rglob(f"{prefix}*"))


def logged(log: Path) -> list[str]:
    """The stub calls logged so far, one per line."""
    return log.read_text(encoding="utf-8").splitlines() if log.is_file() else []


def field(stdout: str, *keys: str) -> str:
    """The string under keys in the JSON object a hook printed; "" when absent or not text."""
    value = _decode(stdout)
    for key in keys:
        if not isinstance(value, dict):
            return ""
        value = cast("dict[str, object]", value).get(key)
    return value if isinstance(value, str) else ""


HOOK = Path(__file__).resolve().parents[1] / "hooks" / "check.mjs"
SCRIPT = "#!/usr/bin/env bash\necho hi\n"
# One more than the hook's MAX_FILES.
TOO_MANY = 21
BLOCKED = 2


class BashHookTest(unittest.TestCase):
    """What the hook checks, what it leaves alone, and that it never blocks without a finding."""

    def _run(
        self,
        tmp: Path,
        event: dict[str, object],
        *,
        tools: bool = True,
        data: bool = True,
        **extra: str,
    ) -> tuple[Outcome, list[str]]:
        """Run the hook in project tmp/work and return (outcome, stub calls).

        With data False, CLAUDE_PLUGIN_DATA is not in the environment at all.
        """
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
        if not data:
            del env["CLAUDE_PLUGIN_DATA"]
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

    def test_missing_tool_without_plugin_data_keeps_no_marker(self) -> None:
        """With no data folder the notice repeats and nothing is created in the temporary folder."""
        for data in (False, True):
            with self.subTest(data_set_but_empty=data), tempfile.TemporaryDirectory() as raw:
                tmp = Path(raw).resolve()
                write(tmp / "work" / "a.sh", SCRIPT)
                extra = {"CLAUDE_PLUGIN_DATA": ""} if data else {}
                runs = [
                    self._run(
                        tmp,
                        self._edit(tmp / "work" / "a.sh"),
                        tools=False,
                        data=data,
                        TMPDIR=str(tmp),
                        **extra,
                    )[0]
                    for _ in range(2)
                ]
                left = folders_named(tmp, "bash-lsp-intelligence")
                for outcome in runs:
                    self.assertEqual((outcome.code, outcome.stderr), (0, ""))
                    self.assertNotEqual(outcome.stdout, "")
                    self.assertIn("shfmt is not installed", field(outcome.stdout, "systemMessage"))
                self.assertEqual(left, [])

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

    def test_staged_edit_in_a_work_tree_is_checked(self) -> None:
        """A command that edits files and runs `git add` leaves none of them `--modified`."""
        for nested in (True, False):
            with self.subTest(nested=nested), tempfile.TemporaryDirectory() as raw:
                tmp = Path(raw).resolve()
                if nested:
                    repository(tmp / "origin", {"a.sh": SCRIPT, "b.sh": SCRIPT})
                    clone(tmp / "origin", tmp / "work" / "clone")
                    tree = tmp / "work" / "clone"
                else:
                    tree = tmp / "work"
                    repository(tree, {"a.sh": SCRIPT, "b.sh": SCRIPT})
                write(tree / "a.sh", f"{SCRIPT}echo more\n")
                write(tree / "c.sh", SCRIPT)
                git(tree, "add", "a.sh", "c.sh")
                # Modified again after staging, so Git lists a under both.
                write(tree / "a.sh", f"{SCRIPT}echo again\n")
                outcome, calls = self._run(tmp, self._bash(tmp))
                self.assertEqual((outcome.code, outcome.stderr), (0, ""))
                self.assertTrue(any(call.endswith("/a.sh") for call in calls), calls)
                self.assertTrue(any(call.endswith("/c.sh") for call in calls), calls)
                self.assertFalse(any(call.endswith("/b.sh") for call in calls), calls)
                # a is listed twice and c once; each is still checked once.
                once = [sum(call.endswith(f"/{name}.sh") for call in calls) for name in "ac"]
                self.assertEqual(once[0], once[1], calls)

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
