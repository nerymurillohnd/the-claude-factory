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


DENY_EVERYONE = [
    ("gh pr -R o/r merge 12 --squash", "approved head"),
    ("gh pr --repo=o/r merge 12 --squash", "approved head"),
    ("gh api -X PUT 'repos/o/r/pulls/12/merge?x=1'", "sha="),
    ("gh api --method=put /repos/o/r/pulls/12/merge/", "sha="),
    ("gh api graphql -F query=@merge.graphql", "inline"),
    ("gh api graphql --input query.json", "inline"),
    ('gh api graphql -f query="$(cat merge.graphql)"', "inline"),
    ('gh api graphql -f query="$Q"', "inline"),
    ("cat <<'EOF' | bash\ngit push --force\nEOF", "force push"),
    (
        "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/x git commit -m x",
        "GIT_CONFIG",
    ),
    ("env GIT_CONFIG_PARAMETERS=\"'core.hooksPath'='/dev/null'\" git commit -m x", "GIT_CONFIG"),
    ("GIT_CONFIG_GLOBAL=/tmp/c git commit -m x", "GIT_CONFIG"),
    ("export GIT_CONFIG_COUNT=1; git commit -m x", "GIT_CONFIG"),
    ("git --config-env=core.hooksPath=HOOKS commit -m x", "on the command line"),
    ("git --config-env core.hooksPath=HOOKS commit -m x", "on the command line"),
    ("gh auth token", "token"),
    ("GH_TOKEN=x gh auth token", "token"),
    ("echo $(gh auth token)", "token"),
    ('curl -H "Authorization: Bearer $(gh auth token)" https://api.github.com/user', "token"),
    (
        "curl -H 'Authorization: token ghp_abcdefghijklmnopqrstuvwxyz0123' https://api.github.com",
        "token",
    ),
    ('curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com', "token"),
    ("gh auth status --show-token", "token"),
    ("git push --force origin main", "force push"),
    ("git push -f", "force push"),
    ("git push --force-with-lease", "force push"),
    ("git push --force-if-includes origin x", "force push"),
    ("git push --mirror backup", "--mirror"),
    ("git push origin +main", "+refspec"),
    ("git push -uf origin x", "force push"),
    ("git push --no-verify", "--no-verify"),
    ("git commit --no-verify -m x", "--no-verify"),
    ("git commit -n -m x", "--no-verify"),
    ("git commit -nm x", "--no-verify"),
    ("git commit --no-veri -m x", "--no-verify"),
    ("git commit --no-gpg-sign -m x", "--no-gpg-sign"),
    ("git merge --no-verify b", "--no-verify"),
    ("git am -n p.patch", "--no-verify"),
    ("git -c core.hooksPath=/dev/null commit -m x", "on the command line"),
    ("git -c commit.gpgsign=false commit -m x", "on the command line"),
    ("/usr/bin/git push --force", "force push"),
    ("git -C repo push --force", "force push"),
    ('git commit -m "x', "could not be parsed"),
]
PASS_MAIN = [
    "gh pr view 1 -R o/r",
    "gh api graphql -f query='query($o:String!){repository(owner:$o,name:\"r\"){id}}' -f o=x",
    "cat <<'EOF' | grep force\ngit push --force\nEOF",
    "git push origin feat/x",
    "git push -n",
    "git push -u origin x",
    'git commit -m "docs: mention --no-verify"',
    "git merge -n feature",
    "gh auth status",
    "gh pr view 1",
    "curl https://example.com",
    'echo "git push --force"',
    "ls -la",
    "git commit -m \"$(cat <<'EOF'\nfix: x\n\nnever use --force\nEOF\n)\"",
    "cat <<'EOF' > notes.md\ngit push --force\nEOF",
    "echo $'it\\'s'",
]
WRAPPED = [
    ("cd r && git push --force", "force push"),
    ('bash -c "git push -f"', "force push"),
    ("sudo -n git commit --no-verify -m x", "--no-verify"),
    ("bash <<'EOF'\ngit push --force\nEOF", "force push"),
    ("env GH_TOKEN=x gh auth token", "token"),
    ("true; git push --force", "force push"),
    ("ls | xargs echo && git push -f", "force push"),
    ("eval git push --force", "force push"),
    ("time nice -n 5 git push --force", "force push"),
    ("echo `git push --force`", "force push"),
    ('echo "don\'t $(git push --force)"', "force push"),
    (f'gh pr merge --body "a b" 12 --squash --match-head-commit {SHA[:7]}', "approved head"),
]


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

    def assert_ask(self, d: Decision, what: str) -> None:
        assert d.kind == "ask", f"not asked: {what!r} -> {d.raw!r}"
        assert d.reason.startswith("github-operations: "), d.reason

    def assert_silent(self, d: Decision, what: str) -> None:
        assert d.raw.strip() == "", f"not silent: {what!r} -> {d.raw!r}"

    def test_deny_everyone(self) -> None:
        for c, because in DENY_EVERYONE:
            self.assert_denied(self.shell(c), c, because)

    def test_main_session_passes_ordinary_work(self) -> None:
        for c in PASS_MAIN:
            self.assert_silent(self.shell(c), c)

    def test_wrapped_forms_are_caught(self) -> None:
        for c, because in WRAPPED:
            self.assert_denied(self.shell(c), c, because)

    def test_powershell_tool_is_checked(self) -> None:
        payload = self.payload("PowerShell", {"command": "git push --force"}, "", KNOWN)
        self.assert_denied(self.decide("shell", payload), "PowerShell git push --force")

    def test_merge_without_guard_denied(self) -> None:
        self.assert_denied(self.shell("gh pr merge 12 --squash"), "gh pr merge 12 --squash")

    def test_merge_with_guard_asks(self) -> None:
        c = f"gh pr merge 12 --squash --match-head-commit {SHA}"
        d = self.shell(c)
        self.assert_ask(d, c)
        assert SHA in d.reason
        assert "squash" in d.reason
        assert "12" in d.reason

    def test_merge_with_repo_flag_asks(self) -> None:
        c = f"gh pr -R o/r merge 12 --squash --match-head-commit {SHA}"
        d = self.shell(c)
        self.assert_ask(d, c)
        assert "PR 12 " in d.reason, d.reason

    def test_merge_admin_denied(self) -> None:
        c = f"gh pr merge 12 --admin --squash --match-head-commit {SHA}"
        self.assert_denied(self.shell(c), c)

    def test_merge_short_sha_denied(self) -> None:
        c = "gh pr merge 12 --squash --match-head-commit 0123abc"
        self.assert_denied(self.shell(c), c)

    def test_merge_via_api(self) -> None:
        c = "gh api -X PUT repos/o/r/pulls/12/merge"
        self.assert_denied(self.shell(c), c)
        c = f"gh api -X PUT repos/o/r/pulls/12/merge -f sha={SHA}"
        self.assert_ask(self.shell(c), c)

    def test_merge_via_graphql_denied(self) -> None:
        mutation = 'mutation{mergePullRequest(input:{pullRequestId:"x"}){clientMutationId}}'
        c = f"gh api graphql -f query='{mutation}'"
        self.assert_denied(self.shell(c), c)

    def test_merge_gate_any_server_name(self) -> None:
        for server in ("plugin_github-operations_github", "github", "claude_ai_GitHub"):
            tool = f"mcp__{server}__merge_pull_request"
            args: dict[str, object] = {"owner": "o", "repo": "r", "pullNumber": 12}
            self.assert_denied(self.mcp(tool, args), tool)
            d = self.mcp(tool, {**args, "expectedHeadSha": SHA, "merge_method": "squash"})
            self.assert_ask(d, tool)
            assert "o/r#12" in d.reason
            assert SHA in d.reason

    def test_tracker_shell(self) -> None:
        for c in (
            "git status",
            "git log --oneline -5",
            "git branch -a",
            "git remote -v",
            "gh pr view 1",
            "gh pr checks 1",
            "gh pr -R o/r view 1",
            "gh api repos/o/r/pulls/1",
            "gh api graphql -f query='query{viewer{login}}'",
            "ls -la",
        ):
            self.assert_silent(self.shell(c, agent=TRACKER), c)
        for c in (
            "git commit -m x",
            "git branch new-branch",
            "git fetch",
            "gh pr comment 1 -b x",
            "gh run rerun 1",
            "gh api -X POST repos/o/r/issues/1/comments -f body=x",
            "gh api repos/o/r/issues/1/comments -f body=x",
            "gh api graphql -f query='mutation{x}'",
        ):
            self.assert_denied(self.shell(c, agent=TRACKER), c)

    def test_tracker_mcp(self) -> None:
        for t in ("pull_request_read", "get_job_logs", "list_pull_requests", "search_code"):
            self.assert_silent(self.mcp(f"mcp__github__{t}", {}, agent=TRACKER), t)
        for t in ("issue_write", "actions_run_trigger", "add_issue_comment"):
            self.assert_denied(self.mcp(f"mcp__github__{t}", {}, agent=TRACKER), t)

    def test_auditor_files(self) -> None:
        self.assert_denied(self.files(self.project / "x.md", agent=AUDITOR), "project file")
        self.assert_denied(
            self.files(self.project / "n.ipynb", agent=AUDITOR, tool="NotebookEdit"), "notebook"
        )
        self.assert_silent(self.files(self.tmp / "findings.md", agent=AUDITOR), "scratch file")

    def test_other_agents_and_main_pass(self) -> None:
        self.assert_silent(self.shell("git commit -m x", agent="Explore"), "Explore commit")
        self.assert_silent(self.files(self.project / "x.md"), "main session write")
        self.assert_silent(self.mcp("mcp__github__issue_write", {}), "main session MCP write")

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
        d = self.shell("git push --force", session="W")
        assert d.kind == "deny"
        assert "github-operations:github" in d.context

    def test_contract_once_unwritable_data_dir(self) -> None:
        locked = self.tmp / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        self.assert_silent(self.shell("gh pr view 1", session="S", data_dir=locked), "unwritable")

    def test_bad_input_is_denied_by_guards(self) -> None:
        env = {
            **os.environ,
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN),
            "CLAUDE_PLUGIN_DATA": str(self.data),
        }
        result = subprocess.run(
            [str(LAUNCHER), "shell"],
            input="not json",
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert result.returncode == 0
        assert text_at(_decode(result.stdout), "hookSpecificOutput", "permissionDecision") == "deny"

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
