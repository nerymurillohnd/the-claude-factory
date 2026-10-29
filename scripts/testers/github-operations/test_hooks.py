#!/usr/bin/env python3
"""Tests for github-operations' hooks, run through hooks/run-hook.sh as Claude Code runs them.

Run: python3 -m unittest discover -s scripts/testers/github-operations -v
Standard library only; runs on the python3 on PATH.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import TYPE_CHECKING, override
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / "plugins" / "github-operations"
LAUNCHER = PLUGIN / "hooks" / "run-hook.sh"
SHA = "0123456789abcdef0123456789abcdef01234567"
TRACKER = "github-operations:pr-tracker"
AUDITOR = "github-operations:repo-auditor"
KNOWN = "known-session"


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def text_at(value: object, *keys: str) -> str:
    """Return the string under keys in nested JSON objects, or "" when absent."""
    for key in keys:
        if not isinstance(value, JsonObject):
            return ""
        value = value.get(key)
    return value if isinstance(value, str) else ""


@dataclass
class Decision:
    """What one hook run decided: deny, ask or nothing, its reason and any added context."""

    kind: str
    reason: str
    context: str
    raw: str


PASS_MAIN = [
    "git push --force origin main",
    "git push -uf origin x",
    "git commit --no-verify -m x",
    "git -c commit.gpgsign=false commit -m x",
    "GIT_CONFIG_GLOBAL=/tmp/c git commit -m x",
    "gh pr merge 12 --squash",
    f"gh pr merge 12 --admin --squash --match-head-commit {SHA}",
    "gh api -X PUT repos/o/r/pulls/12/merge",
    "gh auth token",
    'git commit -m "x',
    "gh pr view 1 -R o/r",
    "git push origin feat/x",
    "curl https://example.com",
    "ls -la",
]
REVIEWER_DENIED = [
    "git commit -m x",
    "git push origin x",
    "git push --force",
    "git branch new-branch",
    "git branch -D old",
    "git tag v1.0.0",
    "git fetch",
    "git reset --hard HEAD~1",
    "git checkout main",
    "git switch -c x",
    "git stash",
    "git merge feature",
    "git rebase main",
    "git cherry-pick abc",
    "git clean -fd",
    "git config user.name x",
    "git remote add up https://example.com/r.git",
    "git worktree add ../wt",
    "git gc",
    "gh pr merge 12 --squash",
    "gh pr comment 1 -b x",
    "gh pr create --title x --body y",
    "gh issue close 3",
    "gh label create x",
    "gh run rerun 1",
    "gh workflow enable ci.yml",
    "gh api -X POST repos/o/r/issues/1/comments -f body=x",
    "gh api repos/o/r/issues/1/comments -f body=x",
    "gh api graphql -f query='mutation{x}'",
    'git commit -m "x',
]
REVIEWER_WRAPPED = [
    "cd r && git commit -m x",
    'bash -c "git push"',
    "echo $(git commit -m x)",
    "bash <<'EOF'\ngit tag v1\nEOF",
    "GIT_OPTIONAL_LOCKS=0 git -C r commit -m x",
    "sudo -n git push",
    "git -c alias.x='!git push' x",
    "git -c core.hooksPath=/tmp/h status",
    "git --config-env=alias.x=CMD x",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.x GIT_CONFIG_VALUE_0=push git x",
    "env GIT_CONFIG_PARAMETERS=\"'alias.x=push'\" git x",
    "gh api repos/o/r/issues/1/comments -f query=x",
    "gh api graphql -f query='query{a} mutation{b}'",
    "gh api graphql -F query=@q.graphql",
    "bash <(echo git push)",
    "bash <<< 'git push'",
    "echo git push | bash",
    "echo git push | sh -s",
    "cat s.sh | zsh",
    "source <(echo git push)",
    ". <(echo git push)",
    "echo git push | bash -s x",
    "echo git push | bash -xs",
    "echo git push | bash -o pipefail",
    "echo git push | bash +x",
    "echo git push | bash /dev/stdin",
    "echo git push | sh -",
    "bash --rcfile r /dev/fd/0",
    "HOME=/tmp/h git x",
    "XDG_CONFIG_HOME=/tmp/c git x",
    "export GIT_CONFIG_GLOBAL=/tmp/g; git x",
    "export HOME=/tmp/h && git x",
    "echo git push | bash -eo pipefail",
    "echo git push | bash //dev/stdin",
    "echo git push | bash ../../dev/stdin",
    "bash no-such-script.sh",
    "HOME+=x; git x",
    "read HOME <<< /tmp/h; git x",
    "printf -v HOME /tmp/h; git x",
]
REVIEWER_PASS = [
    "git status",
    "git log --oneline -5",
    "git branch -a",
    "git tag -l",
    "git remote -v",
    "git stash list",
    "git worktree list",
    "git config --get user.name",
    "git clean -n",
    "git bundle verify all.bundle",
    "git whatchanged -1",
    "GIT_OPTIONAL_LOCKS=0 git -C r for-each-ref refs/heads",
    "gh pr view 1",
    "gh pr checks 1",
    "gh pr -R o/r view 1",
    "gh api repos/o/r/pulls/1",
    "gh api graphql -f query='query{viewer{login}}'",
    "ls -la",
    "awk '{print $1}' f.txt",
    "sed -n '1,5p' f.txt",
    "cat f.txt",
    "echo found > /tmp/scratch/findings.md",
    "/path/to/branch-states.sh repo main out.tsv",
    "bash RUN/branch-states.sh repo main out.tsv",
    "bash -o pipefail RUN/branch-states.sh repo main out.tsv",
    "ls $HOME/repo",
    "export LC_ALL=C; git log -1",
    "diff <(git log a) <(git log b)",
    "gh api -X GET repos/o/r/pulls -f per_page=100",
]
MCP_WRITES = (
    "merge_pull_request",
    "push_files",
    "create_or_update_file",
    "create_pull_request",
    "issue_write",
    "actions_run_trigger",
    "add_issue_comment",
    "pull_request_review_write",
    "label_write",
)
MCP_OTHERS = (
    "pull_request_read",
    "get_job_logs",
    "list_pull_requests",
    "search_code",
    "github_support_docs_search",
    "semantic_issue_similarity_search",
    "web_search",
)


class Hooks(unittest.TestCase):
    """Runs the launcher with a temporary plugin data folder and project."""

    tmp: Path = Path()
    data: Path = Path()
    project: Path = Path()

    @override
    def setUp(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        self.tmp = Path(handle.name)
        self.data = self.tmp / "data"
        self.project = self.tmp / "project"
        (self.data / "sessions" / KNOWN).mkdir(parents=True)
        self.project.mkdir()

    def fire(self, handler: str, payload: dict[str, object], data_dir: Path | None = None) -> str:
        """Run the launcher for one handler and return its stdout."""
        env = {
            **os.environ,
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
            "CLAUDE_PLUGIN_DATA": str(data_dir or self.data),
            "CLAUDE_PROJECT_DIR": str(self.project),
        }
        result = subprocess.run(
            [str(LAUNCHER), handler],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=env,
            check=False,
            timeout=20,
        )
        assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
        return result.stdout

    def decide(
        self, handler: str, payload: dict[str, object], data_dir: Path | None = None
    ) -> Decision:
        """Run one PreToolUse handler and parse what it printed."""
        out = self.fire(handler, payload, data_dir)
        if not out.strip():
            return Decision("", "", "", out)
        value = _decode(out)
        kind = text_at(value, "hookSpecificOutput", "permissionDecision")
        reason = text_at(value, "hookSpecificOutput", "permissionDecisionReason")
        context = text_at(value, "hookSpecificOutput", "additionalContext")
        return Decision(kind, reason, context, out)

    def payload(
        self, tool: str, tool_input: dict[str, object], agent: str, session: str
    ) -> dict[str, object]:
        """Return the PreToolUse input Claude Code sends for one call."""
        base: dict[str, object] = {
            "session_id": session,
            "hook_event_name": "PreToolUse",
            "cwd": str(self.project),
            "tool_name": tool,
            "tool_input": tool_input,
        }
        if agent:
            base |= {"agent_id": "agent-1", "agent_type": agent}
        return base

    def shell(
        self, command: str, agent: str = "", session: str = KNOWN, data_dir: Path | None = None
    ) -> Decision:
        payload = self.payload("Bash", {"command": command}, agent, session)
        return self.decide("shell", payload, data_dir)

    def mcp(self, tool: str, tool_input: dict[str, object], agent: str = "") -> Decision:
        return self.decide("mcp", self.payload(tool, tool_input, agent, KNOWN))

    def files(self, path: Path, agent: str = "", tool: str = "Write") -> Decision:
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        return self.decide("files", self.payload(tool, {key: str(path)}, agent, KNOWN))

    def compact(self, session: str) -> str:
        out = self.fire(
            "compact",
            {"session_id": session, "hook_event_name": "SessionStart", "source": "compact"},
        )
        return (
            text_at(_decode(out), "hookSpecificOutput", "additionalContext") if out.strip() else ""
        )

    def write_state(self, session: str, **values: str) -> None:
        state = self.data / "state"
        state.mkdir(parents=True, exist_ok=True)
        _ = (state / f"{session}.json").write_text(json.dumps(values), encoding="utf-8")

    def assert_denied(self, d: Decision, what: str, because: str = "") -> None:
        assert d.kind == "deny", f"not denied: {what!r} -> {d.raw!r}"
        assert d.reason.startswith("github-operations: "), d.reason
        assert because in d.reason, f"denied for another reason: {what!r} -> {d.reason!r}"

    def assert_silent(self, d: Decision, what: str) -> None:
        assert d.raw.strip() == "", f"not silent: {what!r} -> {d.raw!r}"

    def test_main_session_is_never_blocked(self) -> None:
        for c in PASS_MAIN:
            self.assert_silent(self.shell(c), c)
            self.assert_silent(self.shell(c, agent="executor"), c)

    def test_main_session_mcp_is_never_blocked(self) -> None:
        for t in (*MCP_WRITES, *MCP_OTHERS):
            self.assert_silent(self.mcp(f"mcp__github__{t}", {}), t)

    def test_reviewers_denied_named_writes(self) -> None:
        for agent in (TRACKER, AUDITOR):
            for c in (*REVIEWER_DENIED, *REVIEWER_WRAPPED):
                self.assert_denied(self.shell(c, agent=agent), c, "read-only")

    def test_reviewers_keep_everything_else(self) -> None:
        for agent in (TRACKER, AUDITOR):
            for c in REVIEWER_PASS:
                command = c.replace("RUN", str(PLUGIN / "skills" / "github" / "scripts"))
                self.assert_silent(self.shell(command, agent=agent), command)

    def test_reviewer_powershell_is_checked(self) -> None:
        payload = self.payload("PowerShell", {"command": "git commit -m x"}, TRACKER, KNOWN)
        self.assert_denied(self.decide("shell", payload), "PowerShell git commit")

    def test_reviewers_mcp(self) -> None:
        for server in ("plugin_github-operations_github", "github", "claude_ai_GitHub"):
            for t in MCP_WRITES:
                tool = f"mcp__{server}__{t}"
                self.assert_denied(self.mcp(tool, {}, agent=TRACKER), tool, "read-only")
            for t in MCP_OTHERS:
                tool = f"mcp__{server}__{t}"
                self.assert_silent(self.mcp(tool, {}, agent=TRACKER), tool)

    def test_auditor_files(self) -> None:
        self.assert_denied(self.files(self.project / "x.md", agent=AUDITOR), "project file")
        self.assert_denied(
            self.files(self.project / "n.ipynb", agent=AUDITOR, tool="NotebookEdit"), "notebook"
        )
        self.assert_silent(self.files(self.tmp / "findings.md", agent=AUDITOR), "scratch file")

    def test_other_agents_and_main_pass(self) -> None:
        self.assert_silent(self.shell("git commit -m x", agent="Explore"), "Explore commit")
        self.assert_silent(self.files(self.project / "x.md"), "main session write")
        self.assert_silent(self.files(self.project / "x.md", agent="executor"), "executor write")

    def test_contract_once(self) -> None:
        d = self.shell("gh pr view 1", session="S")
        assert "github-operations:github" in d.context, d.raw
        assert d.kind == ""
        self.assert_silent(self.shell("gh pr view 2", session="S"), "second call")
        self.assert_silent(self.shell("ls", session="T"), "not GitHub")
        assert "github-operations:github" in self.shell("git push origin x", session="U").context
        d = self.decide("mcp", self.payload("mcp__github__get_me", {}, "", "V"))
        assert "github-operations:github" in d.context

    def test_contract_rides_with_a_denial(self) -> None:
        d = self.shell("git push origin x", agent=TRACKER, session="W")
        assert d.kind == "deny"
        assert "github-operations:github" in d.context

    def test_contract_once_unwritable_data_dir(self) -> None:
        locked = self.tmp / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        self.assert_silent(self.shell("gh pr view 1", session="S", data_dir=locked), "unwritable")

    def raw(self, text: str) -> str:
        """Run the shell handler on raw stdin text and return its stdout."""
        env = {
            **os.environ,
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
            "CLAUDE_PLUGIN_DATA": str(self.data),
        }
        result = subprocess.run(
            [str(LAUNCHER), "shell"],
            input=text,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert result.returncode == 0
        return result.stdout

    def test_bad_input_passes(self) -> None:
        out = self.raw("not json")
        assert out.strip() == "", out

    def test_bad_input_from_a_reviewer_is_denied(self) -> None:
        out = self.raw(f'{{"agent_type": "{TRACKER}", "tool_input": {{"command": ')
        assert text_at(_decode(out), "hookSpecificOutput", "permissionDecision") == "deny"

    def test_compact_restores_state(self) -> None:
        self.write_state("S", kind="pr", pr="12", phase="observe", head=SHA)
        c = self.compact("S")
        assert "PR #12" in c, c
        assert "phase observe" in c, c
        assert SHA in c, c

    def test_compact_without_state_is_silent(self) -> None:
        assert self.compact("none") == ""


if __name__ == "__main__":
    _ = unittest.main()
