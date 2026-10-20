#!/usr/bin/env python3
"""Tests for block-no-verify's hooks/block_no_verify.py.

Run: python3 -m unittest discover -s .github/scripts/tests/block-no-verify -v
Standard library only. Each case runs the hook the way Claude Code does: one JSON event on
stdin, and on stdout either one JSON deny object or nothing.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time
from typing import cast
import unittest

REPO = Path(__file__).resolve().parents[4]
HOOK = REPO / "plugins" / "block-no-verify" / "hooks" / "block_no_verify.py"
SLOWEST = 5.0  # seconds; the hook's own timeout is 10
BIG_MESSAGE = 500_000  # characters


def run_hook(stdin: bytes) -> tuple[int, str]:
    """Run the hook once; return its exit code and its stdout."""
    done = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        check=False,
        timeout=30,
    )
    return done.returncode, done.stdout.decode("utf-8")


def event(command: object) -> bytes:
    """Build the PreToolUse payload Claude Code sends for one Bash call."""
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }
    return json.dumps(payload).encode("utf-8")


def deny_reason(stdout: str) -> str:
    """Return the reason of the one deny object that `stdout` must hold, and nothing else."""
    parsed = cast("object", json.loads(stdout))
    if not isinstance(parsed, dict):
        raise TypeError(stdout)
    outer = cast("dict[str, object]", parsed)
    inner = outer["hookSpecificOutput"]
    if set(outer) != {"hookSpecificOutput"} or not isinstance(inner, dict):
        raise TypeError(stdout)
    fields = cast("dict[str, object]", inner)
    reason = fields["permissionDecisionReason"]
    if fields["hookEventName"] != "PreToolUse" or fields["permissionDecision"] != "deny":
        raise ValueError(stdout)
    if not isinstance(reason, str):
        raise TypeError(stdout)
    return reason


class HookCase(unittest.TestCase):
    """Two verdicts: the command is denied with a reason, or the hook stays silent."""

    def assert_denied(self, command: str, names: str | None = None) -> None:
        """Assert a deny for `command`; when given, the reason must name `names`."""
        code, out = run_hook(event(command))
        assert code == 0, command
        assert out != "", f"expected a deny for: {command!r}"
        reason = deny_reason(out)
        if names is not None:
            assert names in reason, command

    def assert_allowed(self, command: str) -> None:
        """Assert the hook exits 0 and prints nothing for `command`."""
        assert run_hook(event(command)) == (0, ""), command


class DirectBypassTests(HookCase):
    """A git command that carries a bypass is denied, and the reason names it."""

    def test_each_named_bypass_is_denied(self) -> None:
        """Break caught: a bypass flag or gpgsign override that stops being recognised."""
        cases = (
            ('git commit -m "x" --no-verify', "--no-verify"),
            ('git commit --no-gpg-sign -m "x"', "--no-gpg-sign"),
            ('git commit -m "x" -c commit.gpgsign=false', "commit.gpgsign"),
            ('git -c commit.gpgsign=false commit -m "x"', "commit.gpgsign"),
            ('git --config commit.gpgsign=false commit -m "x"', "commit.gpgsign"),
        )
        for command, names in cases:
            with self.subTest(command=command):
                self.assert_denied(command, names)

    def test_every_falsy_gpgsign_value_is_denied_in_any_case(self) -> None:
        """Break caught: a falsy spelling of commit.gpgsign that slips through."""
        for value in ("false", "no", "off", "0", "False", "FALSE", "NO", "OFF"):
            with self.subTest(value=value):
                self.assert_denied(f'git -c commit.gpgsign={value} commit -m "x"', "commit.gpgsign")

    def test_an_abbreviation_that_git_accepts_is_denied(self) -> None:
        """Break caught: git runs `--no-veri` and `--no-g` as the full flags (git 2.56.0)."""
        cases = (
            ('git commit --no-veri -m "x"', "--no-verify"),
            ('git commit --no-verif -m "x"', "--no-verify"),
            ("git push --no-veri", "--no-verify"),
            ('git commit --no-gpg-s -m "x"', "--no-gpg-sign"),
            ('git commit --no-gpg -m "x"', "--no-gpg-sign"),
            ('git commit --no-g -m "x"', "--no-gpg-sign"),
            ('git commit --no-v -m "x"', "--no-verify"),  # ambiguous in git, so it only errors
        )
        for command, names in cases:
            with self.subTest(command=command):
                self.assert_denied(command, names)


class RouteTests(HookCase):
    """The same bypass is found through every way a shell can wrap or spell the command."""

    def test_each_wrapper_is_stripped(self) -> None:
        """Break caught: a wrapper that hides the git call behind it."""
        wrappers = (
            "sudo",
            "env",
            "nice",
            "nohup",
            "timeout 5",
            "xargs",
            "command",
            "builtin",
            "noglob",
            "watch",
        )
        for wrapper in wrappers:
            with self.subTest(wrapper=wrapper):
                self.assert_denied(f'{wrapper} git commit -m "x" --no-verify', "--no-verify")

    def test_assignments_and_stacked_wrappers_are_stripped(self) -> None:
        """Break caught: leading VAR=value, or two wrappers in a row, hiding the git call."""
        self.assert_denied('GIT_AUTHOR_NAME=x git commit -m "x" --no-verify', "--no-verify")
        self.assert_denied(
            'sudo env GIT_AUTHOR_NAME=x nice git commit -m "x" --no-verify', "--no-verify"
        )

    def test_each_command_in_a_list_is_checked(self) -> None:
        """Break caught: only the first command of a chain being inspected."""
        self.assert_denied('ls && git commit -m "x" --no-verify', "--no-verify")
        self.assert_denied('ls; sudo git commit -m "x" --no-verify', "--no-verify")
        self.assert_denied('true || git commit --no-gpg-sign -m "x"', "--no-gpg-sign")

    def test_the_git_name_is_matched_in_any_case(self) -> None:
        """Break caught: a case-sensitive match, which a case-insensitive disk runs anyway."""
        self.assert_denied('GIT commit -m "x" --no-verify', "--no-verify")
        self.assert_denied('Git commit --no-gpg-sign -m "x"', "--no-gpg-sign")
        self.assert_denied('sudo GIT commit -m "x" --no-verify', "--no-verify")

    def test_a_line_continuation_does_not_hide_a_flag(self) -> None:
        """Break caught: the shell joins backslash-newline, so the flag is not in its own word."""
        self.assert_denied('git commit \\\n--no-verify -m "x"', "--no-verify")
        self.assert_denied('git commit -m "x" \\\n  --no-gpg-sign', "--no-gpg-sign")
        self.assert_denied('git commit \\\n-m "x" \\\n--no-verify', "--no-verify")


class AllowedTests(HookCase):
    """Ordinary git, and words that only mention a bypass, are left alone."""

    def test_flags_that_only_resemble_a_bypass_pass(self) -> None:
        """Break caught: the abbreviation rule reaching flags that are not prefixes of the two."""
        commands = (
            'git commit --no-edit -m "x"',
            'git commit --no-status -m "x"',
            'git commit --verbose -m "x"',
            "git merge --no-verify-signatures b",
            "git log --no-walk",
            'git commit \\\n-m "docs: mention --no-verify"',
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_allowed(command)

    def test_ordinary_commands_pass(self) -> None:
        """Break caught: a false positive on everyday git and wrapper use."""
        commands = (
            "git status",
            'git commit -m "x"',
            "git push origin main",
            "sudo git log",
            "env FOO=bar git status",
            "timeout 5 git status",
            "git -c color.ui=always status",
            'git -c commit.gpgsign=funky-not-a-bool commit -m "x"',
            "GIT status",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_allowed(command)

    def test_a_message_that_mentions_the_flag_passes(self) -> None:
        """Break caught: a commit message being read as options."""
        self.assert_allowed('git commit -m "docs: explain --no-verify blocking"')
        self.assert_allowed('git commit -m "say \\"hello\\""')
        self.assert_allowed('git commit --message="docs: explain --no-verify"')
        self.assert_allowed('git commit -m"docs: explain --no-verify"')


class SubcommandTests(HookCase):
    """`-n` means --no-verify only in `git commit` and `git am`; elsewhere it is something else."""

    def test_short_n_is_denied_on_commit_and_am(self) -> None:
        """Break caught: `git commit -n`, the short spelling of --no-verify, passing."""
        commands = (
            "git commit -n",
            'git commit -nm "x"',
            'git commit -anm "x"',
            'git commit -m "x" -n',
            'git commit -am "x" -n',
            "git commit -S -n",
            "git commit -C HEAD -n",
            "git am -n p.patch",
            "git am -3 -n p.patch",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_denied(command, "-n")

    def test_short_n_is_found_behind_global_options(self) -> None:
        """Break caught: global options before the subcommand hiding it from the `-n` rule."""
        commands = (
            "git -C /tmp/r commit -n",
            "git -c user.name=x commit -n",
            "git -c user.name=x -C /r commit -n",
            "git --git-dir=/x commit -n",
            "git --git-dir /x --no-pager commit -n",
            "git --no-pager commit -n",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_denied(command, "-n")

    def test_short_n_passes_where_it_means_something_else(self) -> None:
        """Break caught: a false positive on `-n` of push, merge, pull, cherry-pick or rebase."""
        commands = (
            "git push -n",
            "git merge -n b",
            "git pull -n",
            "git cherry-pick -n abc",
            "git revert -n abc",
            "git rebase -n",
            "git status -n",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_allowed(command)

    def test_short_n_passes_when_it_is_part_of_a_value(self) -> None:
        """Break caught: a message or key id that starts with `n` read as a flag cluster."""
        commands = (
            "git commit -mn",
            'git commit -m "n"',
            'git commit -am "n"',
            'git commit -m "-n"',
            "git commit -S",
            "git commit -Sn",
            "git commit -Fn.txt",
            "git am -3",
            "git am -Cn",
        )
        for command in commands:
            with self.subTest(command=command):
                self.assert_allowed(command)

    def test_a_bypass_flag_is_denied_on_every_subcommand(self) -> None:
        """Break caught: the long flags being checked for commit only."""
        cases = (
            ("git push --no-verify", "--no-verify"),
            ("git merge --no-verify b", "--no-verify"),
            ("git rebase --no-verify", "--no-verify"),
            ("git am --no-verify p.patch", "--no-verify"),
            ("git tag --no-gpg-sign v1", "--no-gpg-sign"),
            ("git merge --no-gpg-sign b", "--no-gpg-sign"),
            ("git cherry-pick --no-gpg-sign abc", "--no-gpg-sign"),
        )
        for command, names in cases:
            with self.subTest(command=command):
                self.assert_denied(command, names)

    def test_tag_signing_overrides_are_denied_like_commit_ones(self) -> None:
        """Break caught: an unsigned tag through `-c tag.gpgsign=false`."""
        for command in (
            "git -c tag.gpgsign=false tag v1",
            "git --config=tag.gpgsign=off tag v1",
            "git -c TAG.GPGSIGN=No tag v1",
        ):
            with self.subTest(command=command):
                self.assert_denied(command, "tag.gpgsign")

    def test_windows_spellings_of_git_are_found(self) -> None:
        """Break caught: `git.exe`, or a quoted path to it, hiding the call."""
        cases = (
            "git.exe commit --no-verify",
            '"C:/Program Files/Git/cmd/git.exe" commit -n',
            "/usr/bin/git commit --no-verify",
        )
        for command in cases:
            with self.subTest(command=command):
                self.assert_denied(command)

    def test_crlf_line_ends_do_not_hide_a_command(self) -> None:
        """Break caught: a carriage return gluing the flag to the word before the newline."""
        self.assert_denied("git commit -m x\r\ngit commit --no-verify\r\n", "--no-verify")
        self.assert_allowed("git commit -m x\r\ngit status\r\n")


class ContractTests(HookCase):
    """What the hook prints and returns for payloads Claude Code or a caller could send."""

    def test_a_deny_is_one_json_object_with_exit_zero(self) -> None:
        """Break caught: a second line on stdout, which Claude Code would read as plain text."""
        code, out = run_hook(event('git commit -m "x" --no-verify'))
        assert code == 0
        reason = deny_reason(out)  # parses the whole of stdout as one object
        assert "--no-verify" in reason
        assert "fix the cause" in reason

    def test_unreadable_input_is_denied_with_the_reason(self) -> None:
        """Break caught: a guard that lets everything through when it cannot read its input."""
        for stdin in (b"", b"not json", b"[]", b'"text"', b"\xff\xfe"):
            with self.subTest(stdin=stdin):
                code, out = run_hook(stdin)
                assert code == 0
                assert "could not read" in deny_reason(out)

    def test_an_event_without_a_command_passes(self) -> None:
        """Break caught: denying calls that carry no Bash command at all."""
        for stdin in (
            b'{"tool_name":"Bash"}',
            b'{"tool_name":"Bash","tool_input":{}}',
            b'{"tool_input":[]}',
            event(5),
            event(None),
        ):
            with self.subTest(stdin=stdin):
                assert run_hook(stdin) == (0, "")

    def test_a_command_it_cannot_lex_is_denied_with_the_reason(self) -> None:
        """Break caught: an unterminated quote passing because the parser gave up."""
        for command in ("echo \"it's", "echo 'x", "echo x\\"):
            with self.subTest(command=command):
                code, out = run_hook(event(command))
                assert code == 0
                assert "could not inspect" in deny_reason(out)

    def test_a_very_long_message_passes_quickly(self) -> None:
        """Break caught: quadratic parsing that would hit the hook's timeout."""
        command = 'git commit -m "' + "a" * BIG_MESSAGE + '"'
        started = time.monotonic()
        assert run_hook(event(command)) == (0, "")
        assert time.monotonic() - started < SLOWEST


if __name__ == "__main__":
    _ = unittest.main()
