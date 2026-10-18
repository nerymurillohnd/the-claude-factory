"""Tests for the git-cleanup guard, hooks/git_cleanup_guard.py, run as Claude Code runs it.

The hook event goes on stdin and the permission decision comes back on stdout.

Run: python3 -m unittest discover -s .github/scripts/tests/github-operations -v
Standard library only; runs on Python 3.9+.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable
REPO = Path(__file__).resolve().parents[4]
GUARD = REPO / "plugins" / "github-operations" / "hooks" / "git_cleanup_guard.py"


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


def run_guard(event: dict[str, object] | str) -> tuple[int, str, str]:
    """Run the guard by path with an event; return (exit code, decision or "", reason or "")."""
    payload = event if isinstance(event, str) else json.dumps(event)
    done = subprocess.run(
        [sys.executable, str(GUARD)], input=payload, capture_output=True, text=True, check=False
    )
    if not done.stdout:
        return (done.returncode, "", "")
    parsed = _decode(done.stdout)
    decision = text_at(parsed, "hookSpecificOutput", "permissionDecision")
    return (
        done.returncode,
        decision,
        text_at(parsed, "hookSpecificOutput", "permissionDecisionReason"),
    )


def verdict(command: str) -> str:
    """Return the guard's decision for a Bash command: deny, ask or "" (no objection)."""
    code, decision, _ = run_guard({"tool_name": "Bash", "tool_input": {"command": command}})
    assert code == 0
    return decision


class GuardTests(unittest.TestCase):
    """The guard denies, asks or stays silent according to what a command would do."""

    def check(self, expected: str, commands: list[str]) -> None:
        """Assert every command gets the expected decision."""
        for command in commands:
            with self.subTest(command=command):
                assert verdict(command) == expected

    def test_read_only_commands_pass(self) -> None:
        self.check(
            "",
            [
                "git status --short --branch",
                "git log --oneline -20 origin/main",
                "git branch -a",
                "git branch --merged origin/main",
                "git branch -vv",
                "git tag --list",
                "git stash list",
                "git stash show --stat stash@{0}",
                "git worktree list --porcelain",
                "git reflog show HEAD",
                "git merge-tree --write-tree main feat/x",
                "git range-diff a...b c...d",
                "git cherry origin/main feat/x",
                "git rev-list --left-right --count a...b",
                "git for-each-ref refs/heads",
                "git ls-remote --heads origin",
                "git remote",
                "git worktree prune --dry-run --verbose",
                "git clean -fdn",
                "git push --dry-run origin feat/x",
                "git fetch --dry-run",
                "git bundle verify /tmp/b.bundle",
                "git bisect log",
                "git -C /some/repo status",
                "git config user.name",
                "git reflog HEAD",
                "git log main..feat/secrets",
                "git log --stat origin/main..hotfix/credentials",
                "git diff --stat origin/main...feat/x",
                "git diff --name-status origin/main...feat/x",
                "git show --stat HEAD",
                "git show -s --format=%s HEAD",
                "git stash show --stat stash@{0}",
                "git grep -l password",
                "git cat-file -t HEAD",
                "git diff origin/main...feat/x -- . ':(exclude).env'",
                "git show feat/id_rsa --stat",
                "git log -- src/secrets.py",
                "cat secrets.py",
                "gh -R o/r pr view 4",
                "gh --repo o/r pr list",
                "gh search repos tools",
                "gh pr list --state open",
                "gh pr view 4",
                "gh api repos/o/r/branches",
                "gh auth status",
                "echo hello",
                "ls -la",
                "cat README.md",
                "cat .env.example",
                "cat *",
                "grep -rn credentials .",
                "grep -rn secret src/",
                r"git ls-files | grep '\.env'",
                "python3 script.py -e foo",
                "echo git push -f",
                r"git config --get-regexp '^branch\.'",
                "git config --show-origin user.name",
                "git log 2>&1",
                "git status 2>/dev/null",
                "git diff --stat origin/main...feat/x -U0 --no-patch",
            ],
        )

    def test_state_changing_commands_ask(self) -> None:
        self.check(
            "ask",
            [
                "git fetch --all --prune",
                "git push origin feat/x",
                "git push origin --delete feat/x",
                "git push origin :feat/x",
                "git branch -D feat/x",
                "git branch -d feat/x",
                "git branch newbranch",
                "git tag -d v1",
                "git stash drop stash@{0}",
                "git stash",
                "git worktree remove ../wt",
                "git worktree prune",
                "git reset --hard origin/main",
                "git clean -fd",
                "git gc --prune=now",
                "git reflog expire --expire=now --all",
                "git merge feat/x",
                "git rebase main",
                "git checkout main",
                "git switch main",
                "git commit -m wip",
                "git remote prune origin",
                "git remote set-url origin https://example.com/o/r.git",
                "git bundle create /tmp/b.bundle --all",
                "git bisect start",
                "git config user.name Someone",
                "git -c core.sshCommand=./x fetch",
                "gh pr close 4",
                "gh pr merge 4",
                "gh api repos/o/r/git/refs/heads/x -X DELETE",
                "rm -rf /tmp/backup",
                "ls && git stash drop",
                "git status; git clean -fd",
                "FOO=1 git reset --hard",
                "sudo git gc",
                "echo $(git clean -fd)",
                'bash -c "git fetch"',
                "git unknown-subcommand",
                "for b in a b; do git branch -D $b; done",
                'git branch --merged | while read b; do git branch -d "$b"; done',
                "if true; then git reset --hard; fi",
                "{ git reset --hard; }",
                "sudo -u root git reset --hard",
                "env -u FOO git reset --hard",
                "timeout 10 git reset --hard",
                "nice -n 10 git reset --hard",
                "git branch --merged | xargs -n 1 git branch -d",
                "git branch --merged | xargs -L 1 git branch -D",
                "git branch --merged | xargs git branch -d",
                "git diff origin/main...feat/x",
                "git log -p origin/main..feat/x",
                "git show HEAD",
                "git stash show -p stash@{0}",
                "git grep -n password",
                "git cat-file blob abc123",
                "git diff --output=/tmp/x HEAD",
                "git -ccore.pager=x log",
                "git symbolic-ref HEAD refs/heads/x",
                "git merge-file a b c",
                "git branch --unset-upstream",
                "git push --prune origin 'refs/heads/*:refs/heads/*'",
                "find . -name '*.orig' -delete",
                "find . -type f -exec rm {} +",
                "git branch --merged | xargs rm",
                "git diff --stat -p",
                "git show --stat -p HEAD",
                "git log -L1,5:f.txt",
                "git log --word-diff",
                "git log -U5",
                "git reflog show -p",
                "git log --binary",
                "echo hi > out.txt",
                "touch f",
                "cp a b",
                "chmod 600 f",
                "gh api -X DELETE repos/o/r/git/refs/heads/main-old",
                "mv a b",
                "sed -i s/a/b/ file",
                "python3 -c 'import os'",
                "node -e 'process.exit()'",
                "curl -X DELETE https://api.github.com/repos/o/r/git/refs/heads/x",
                "gh api -XDELETE repos/o/r/git/refs/heads/feature",
                'unterminated "quote',
            ],
        )

    def test_dangerous_commands_are_denied(self) -> None:
        self.check(
            "deny",
            [
                "git push --force origin feat/x",
                "git push -f origin feat/x",
                "git push --dry-run --force origin feat/x",
                "git push --force-with-lease origin feat/x",
                "git push origin +main",
                "git push --mirror backup",
                "git push origin --delete main",
                "git push origin :master",
                "git filter-branch --all",
                "git filter-repo --path x",
                "git remote -v",
                "git remote -vv",
                "git ls-remote --get-url origin",
                "git credential fill",
                "git clean -fdx",
                "git clean -fdX",
                "git filter-repo --path x",
                "bfg --delete-files x",
                "gh api -XDELETE repos/o/r/git/refs/heads/main",
                "gh api repos/o/r/git/refs/heads/main -XDELETE",
                "gh api -XPATCH repos/o/r --field=default_branch=trunk",
                "gh api repos/o/r --raw-field=default_branch=trunk",
                "gh -R o/r repo edit --default-branch trunk",
                "cat <.env",
                "cat<.env",
                "cat < .env",
                "cat .env*",
                "cat .e*",
                "less .env",
                "vim .env",
                "diff .env .env.example",
                "cat ~/.docker/config.json",
                "cat .git/config",
                "cat .envrc",
                "git var -l",
                "cat ~/.config/gh/hosts.yml",
                "echo $GITHUB_TOKEN",
                'echo "$GITHUB_PAT"',
                "echo ${GITHUB_PAT}",
                "echo $GH_PAT",
                "export",
                "declare -p",
                "cat ~/.pgpass",
                "cat ~/.config/gcloud/credentials.db",
                "git config --get-regexp .",
                "cat service-account.json",
                "git log -p -- .env",
                "git remote get-url origin",
                "git remote show origin",
                "git config --list",
                "git config --get remote.origin.url",
                "git config --get-regexp 'remote.*'",
                "gh repo edit --default-branch trunk",
                "gh api repos/o/r -X PATCH -f default_branch=trunk",
                "gh auth token",
                "gh auth status --show-token",
                "cat .env",
                "cat ~/.ssh/id_rsa",
                "head -5 config/secrets.yml",
                "grep password .npmrc",
                "git show HEAD:.env",
                "git diff -- server.pem",
                "printenv",
                "env",
                'bash -c "git push -f"',
                "echo ok && git push --force",
            ],
        )

    def test_variables_that_only_resemble_a_token_name_pass(self) -> None:
        self.check("", ['echo "$PATH"', "echo $PATHS", "echo $MY_PATTERN", "echo ${HOME}/path"])

    def test_secret_example_files_are_not_secrets(self) -> None:
        self.check("", ["cat .env.sample", "cat config/credentials.example", "cat id_rsa.pub"])

    def test_read_tool_is_guarded(self) -> None:
        _, denied, _ = run_guard({"tool_name": "Read", "tool_input": {"file_path": "/home/u/.env"}})
        _, allowed, _ = run_guard(
            {"tool_name": "Read", "tool_input": {"file_path": "/home/u/a.md"}}
        )
        _, grep, _ = run_guard(
            {"tool_name": "Grep", "tool_input": {"pattern": "x", "path": ".env"}}
        )
        assert (denied, allowed, grep) == ("deny", "", "deny")

    def test_writes_and_mcp_actions_ask_but_reads_pass(self) -> None:
        def decision(tool: str) -> str:
            return run_guard({"tool_name": tool, "tool_input": {}})[1]

        assert decision("Write") == "ask"
        assert decision("Edit") == "ask"
        assert decision("NotebookEdit") == "ask"
        assert decision("mcp__github__delete_file") == "ask"
        assert decision("mcp__github__push_files") == "ask"
        assert decision("mcp__github__get_file_contents") == ""
        assert decision("mcp__github__list_branches") == ""
        assert decision("mcp__github__search_code") == ""

    def test_other_tools_are_ignored(self) -> None:
        _, decision, _ = run_guard({"tool_name": "WebSearch", "tool_input": {"query": ".env"}})
        assert decision == ""

    def test_broken_input_asks_instead_of_passing(self) -> None:
        code, decision, reason = run_guard("not json")
        assert (code, decision) == (0, "ask")
        assert "git-cleanup" in reason

    def test_reasons_explain_and_guide(self) -> None:
        _, _, deny_reason = run_guard(
            {"tool_name": "Bash", "tool_input": {"command": "git push -f origin x"}}
        )
        _, _, ask_reason = run_guard(
            {"tool_name": "Bash", "tool_input": {"command": "git clean -fd"}}
        )
        assert "never" in deny_reason
        assert "approved in the cleanup plan" in ask_reason


if __name__ == "__main__":
    _ = unittest.main()
