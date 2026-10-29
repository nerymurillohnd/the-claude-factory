#!/usr/bin/env python3
"""github-operations hook handlers: read one hook input on stdin, print at most one JSON object.

Usage: github_hooks.py shell|mcp|files|compact

shell   (PreToolUse, Bash and PowerShell): agents read-only, merge gate, credentials and
        history, contract once.
mcp     (PreToolUse, GitHub MCP tools and any merge_pull_request): agents read-only, merge gate,
        contract once.
files   (PreToolUse, Write, Edit and NotebookEdit): agents read-only.
compact (SessionStart, compact): the session's lifecycle state as context.

The strictest decision wins: deny, then ask, then context only. Every run exits 0.
Standard library only; Python 3.12 or later.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import posixpath
import re
import shlex
import sys
import time
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

PREFIX = "github-operations: "
AGENTS = ("github-operations:pr-tracker", "github-operations:repo-auditor")
CONTRACT = (
    "This session is acting on GitHub. The github-operations plugin's rules for GitHub work"
    " (tool choice, approvals, evidence) are in the skill github-operations:github."
)
SHA40 = re.compile(r"[0-9a-f]{40}")
SESSION = re.compile(r"[A-Za-z0-9_-]+")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
GUARDED_WORD = re.compile(r"(?<![A-Za-z0-9_.-])(git|gh|curl)(?![A-Za-z0-9_-])")
HEREDOC = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
FEEDS_SHELL = re.compile(r"(?:^|[\s;&|(/])(?:bash|sh|zsh)(?:\s+-\S+)*\s*$")
TOKEN = re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")
TOKEN_VARIABLES = ("$GH_TOKEN", "$GITHUB_TOKEN", "${GH_TOKEN}", "${GITHUB_TOKEN}")
PULL_MERGE = re.compile(r"(?:^|/)repos/([^/\s]+)/([^/\s]+)/pulls/(\d+)/merge$")
HISTORY_REASON = (
    "it rewrites published history or skips the repository's hooks or signing."
    " Run the command without it; if the user approved a history rewrite,"
    " give them the exact command to run in their own terminal."
)
HEAD_GUARD_REASON = (
    "merge only at the approved head: add --match-head-commit with the head's full"
    " 40-character SHA, read right before the merge."
)
GRAPHQL_MERGES = ("mergePullRequest", "enablePullRequestAutoMerge")
MAX_DEPTH = 8
GH_COMMAND_WORDS = 2
MARKER_DAYS = 7
SECONDS_PER_DAY = 86400

WRAPPERS: dict[str, frozenset[str]] = {
    "sudo": frozenset({"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-U"}),
    "env": frozenset({"-u", "-C"}),
    "time": frozenset(),
    "exec": frozenset({"-a"}),
    "command": frozenset(),
    "nice": frozenset({"-n"}),
    "nohup": frozenset(),
}
SHELLS = ("bash", "sh", "zsh")
GIT_GLOBAL_VALUES = ("-C", "--git-dir", "--work-tree", "--namespace")

GIT_READ = frozenset(
    {
        "status",
        "log",
        "diff",
        "show",
        "blame",
        "grep",
        "rev-list",
        "rev-parse",
        "for-each-ref",
        "cat-file",
        "ls-files",
        "ls-remote",
        "merge-base",
        "merge-tree",
        "cherry",
        "count-objects",
        "range-diff",
        "symbolic-ref",
    }
)
BRANCH_LONGS = frozenset(
    {
        "--all",
        "--remotes",
        "--verbose",
        "--list",
        "--merged",
        "--no-merged",
        "--contains",
        "--no-contains",
        "--points-at",
        "--sort",
        "--format",
        "--show-current",
        "--color",
        "--no-color",
        "--column",
        "--no-column",
        "--abbrev",
        "--no-abbrev",
        "--ignore-case",
    }
)
BRANCH_VALUES = frozenset(
    {
        "--merged",
        "--no-merged",
        "--contains",
        "--no-contains",
        "--points-at",
        "--sort",
        "--format",
    }
)
GH_READ: dict[str, frozenset[str]] = {
    "pr": frozenset({"view", "list", "checks", "diff", "status"}),
    "issue": frozenset({"view", "list", "status"}),
    "run": frozenset({"view", "list"}),
    "workflow": frozenset({"list", "view"}),
    "repo": frozenset({"view"}),
    "release": frozenset({"view", "list"}),
    "label": frozenset({"list"}),
    "auth": frozenset({"status"}),
    "secret": frozenset({"list"}),
    "variable": frozenset({"list"}),
    "ruleset": frozenset({"list", "view", "check"}),
    "cache": frozenset({"list"}),
}
COMMIT_VALUES = frozenset(
    {
        "--message",
        "--file",
        "--author",
        "--date",
        "--template",
        "--reuse-message",
        "--reedit-message",
        "--fixup",
        "--squash",
        "--trailer",
        "--cleanup",
        "--pathspec-from-file",
    }
)
MERGE_VALUES = frozenset({"--message", "--file", "--strategy", "--strategy-option", "--cleanup"})
PUSH_VALUES = frozenset({"--push-option", "--repo", "--receive-pack", "--exec"})
PR_MERGE_VALUES = frozenset(
    {
        "--match-head-commit",
        "--body",
        "--body-file",
        "--subject",
        "--repo",
        "--author-email",
        "-b",
        "-F",
        "-t",
        "-R",
        "-A",
    }
)
MERGE_METHODS = {
    "--squash": "squash",
    "-s": "squash",
    "--merge": "merge commit",
    "-m": "merge commit",
    "--rebase": "rebase",
    "-r": "rebase",
}


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


class LexError(Exception):
    """A command the lexer cannot split into words."""


@dataclass
class Decision:
    """One rule's verdict: deny or ask, with the reason shown to Claude or the user."""

    kind: str
    reason: str


class Options(NamedTuple):
    """The options and positional words of one git subcommand."""

    longs: list[str]
    shorts: set[str]
    positionals: list[str]


@dataclass
class Call:
    """One hook input, with the fields the rules read."""

    session: str
    agent: str
    tool: str
    tool_input: JsonObject
    cwd: str


# ── Lexing ──────────────────────────────────────────────────────────────────────────────────


def split_heredocs(command: str) -> tuple[str, list[str]]:
    """Remove heredoc bodies; return the text left and the bodies that a shell reads."""
    lines = command.split("\n")
    kept: list[str] = []
    scripts: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        for match in HEREDOC.finditer(line):
            body: list[str] = []
            while i < len(lines):
                candidate = lines[i].lstrip("\t") if match.group(1) else lines[i]
                i += 1
                if candidate == match.group(3):
                    break
                body.append(lines[i - 1])
            if FEEDS_SHELL.search(line[: match.start()]):
                scripts.append("\n".join(body))
    return "\n".join(kept), scripts


def closing_paren(text: str, start: int) -> int:
    """Return the index of the parenthesis that closes the one opened before start."""
    depth = 1
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        depth += {"(": 1, ")": -1}.get(ch, 0)
        if depth == 0:
            return i
        i += 1
    raise LexError


def substitution_end(text: str, i: int) -> int:
    """Return where the $(...) or `...` that starts at i ends."""
    end = closing_paren(text, i + 2) if text[i] == "$" else text.find("`", i + 1)
    if end < 0:
        raise LexError
    return end


def extract_substitutions(text: str) -> tuple[str, list[str]]:
    """Replace each $(...) and `...` outside single quotes with a word; return their bodies."""
    out: list[str] = []
    bodies: list[str] = []
    quote = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if quote == "'":
            quote = "" if ch == "'" else quote
            out.append(ch)
            i += 1
        elif ch == "\\":
            out.append(text[i : i + 2])
            i += 2
        elif text.startswith("$(", i) or ch == "`":
            end = substitution_end(text, i)
            bodies.append(text[i + (2 if ch == "$" else 1) : end])
            out.append("SUBSTITUTION")
            i = end + 1
        else:
            if ch in "'\"" and quote in ("", ch):
                quote = "" if quote else ch
            out.append(ch)
            i += 1
    return "".join(out), bodies


def tokens(text: str) -> list[str]:
    """Split text into words and operator tokens, as a POSIX shell would."""
    lexer = shlex.shlex(text, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError as error:
        raise LexError from error


def unwrap(words: list[str]) -> list[str]:
    """Drop leading assignments and wrapper commands; return the command that really runs."""
    i = 0
    while i < len(words):
        word = words[i]
        name = posixpath.basename(word)
        if ASSIGNMENT.match(word):
            i += 1
        elif name in WRAPPERS:
            i += 1
            while i < len(words) and (words[i].startswith("-") or ASSIGNMENT.match(words[i])):
                i += 2 if words[i] in WRAPPERS[name] else 1
        else:
            break
    rest = words[i:]
    return [posixpath.basename(rest[0]), *rest[1:]] if rest else []


def nested_script(command: list[str]) -> str | None:
    """Return the script a shell -c or eval runs, or None."""
    if command[0] == "eval":
        return " ".join(command[1:])
    if command[0] not in SHELLS:
        return None
    for i, word in enumerate(command[1:-1], start=1):
        if word.startswith("-") and not word.startswith("--") and "c" in word:
            return command[i + 1]
    return None


def expand(words: list[str], depth: int) -> list[list[str]]:
    """Return the subcommands one word list runs, nested scripts included."""
    command = unwrap(words)
    if not command:
        return []
    script = nested_script(command)
    return [command] if script is None else [command, *lex_subcommands(script, depth + 1)]


def lex_subcommands(command: str, depth: int = 0) -> list[list[str]]:
    """Split a shell command into the word lists of every subcommand it runs."""
    if depth > MAX_DEPTH:
        raise LexError
    text, scripts = split_heredocs(command)
    text, bodies = extract_substitutions(text)
    result: list[list[str]] = []
    for nested in (*scripts, *bodies):
        result.extend(lex_subcommands(nested, depth + 1))
    words: list[str] = []
    skip_target = False
    for token in tokens(text):
        if token and all(ch in "();<>|&\n" for ch in token):
            if any(ch in "<>" for ch in token):
                skip_target = True
                continue
            result.extend(expand(words, depth))
            words = []
        elif skip_target:
            skip_target = False
        else:
            words.append(token)
    result.extend(expand(words, depth))
    return result


# ── Command parsing ─────────────────────────────────────────────────────────────────────────


def options(args: list[str], short_values: str, long_values: frozenset[str]) -> Options:
    """Sort a subcommand's arguments into long options, short flags and positional words."""
    parsed = Options([], set(), [])
    i = 0
    while i < len(args):
        arg = args[i]
        i += 1
        if arg == "--":
            parsed.positionals.extend(args[i:])
            break
        if arg.startswith("--"):
            name = arg.split("=", 1)[0]
            parsed.longs.append(name)
            i += 1 if "=" not in arg and name in long_values else 0
        elif arg.startswith("-") and len(arg) > 1:
            i += short_cluster(arg, short_values, parsed.shorts)
        else:
            parsed.positionals.append(arg)
    return parsed


def short_cluster(arg: str, short_values: str, shorts: set[str]) -> int:
    """Add the flags of one -abc cluster; return 1 when the next word is a flag's value."""
    letters = arg[1:]
    for j, ch in enumerate(letters):
        shorts.add(ch)
        if ch in short_values:
            return 1 if j == len(letters) - 1 else 0
    return 0


def git_parts(command: list[str]) -> tuple[str, list[str], list[str]]:
    """Return a git call's subcommand, its arguments and its -c settings."""
    i = 1
    settings: list[str] = []
    while i < len(command) and command[i].startswith("-"):
        option = command[i]
        if option == "-c" and i + 1 < len(command):
            settings.append(command[i + 1])
        i += 2 if option in (*GIT_GLOBAL_VALUES, "-c") else 1
    subcommand = command[i] if i < len(command) else ""
    return subcommand, command[i + 1 :], settings


def gh_words(command: list[str]) -> list[str]:
    """Return a gh call's command words: the first two words that are not options."""
    return [word for word in command[1:] if not word.startswith("-")][:2]


def abbreviates(names: Iterable[str], full: str, shortest: str) -> bool:
    """True when one of names is full or an unambiguous git abbreviation of it."""
    return any(full.startswith(name) and len(name) >= len(shortest) for name in names)


class ApiCall(NamedTuple):
    """A gh api call: its method, endpoint and fields."""

    method: str
    endpoint: str
    fields: list[str]
    has_input: bool


def gh_api(args: list[str]) -> ApiCall:
    """Parse the arguments after `gh api`."""
    method = ""
    endpoint = ""
    fields: list[str] = []
    has_input = False
    i = 0
    while i < len(args):
        arg = args[i]
        value = args[i + 1] if i + 1 < len(args) else ""
        i += 1
        if arg in ("-X", "--method"):
            method, i = value, i + 1
        elif arg.startswith(("--method=", "-X")):
            method = arg.removeprefix("--method=").removeprefix("-X")
        elif arg in ("-f", "-F", "--field", "--raw-field"):
            fields.append(value)
            i += 1
        elif arg.startswith(("--field=", "--raw-field=", "-f", "-F")):
            fields.append(arg.split("=", 1)[1] if arg.startswith("--") else arg[2:])
        elif arg == "--input" or arg.startswith("--input="):
            has_input = True
        elif not arg.startswith("-") and not endpoint:
            endpoint = arg
    return ApiCall(method.upper(), endpoint, fields, has_input)


# ── Rule 4: credentials and history ─────────────────────────────────────────────────────────


def deny(reason: str) -> Decision:
    """A deny with the plugin's prefix."""
    return Decision("deny", PREFIX + reason)


def push_violation(args: list[str]) -> str | None:
    """Return the force or hook-skipping flag of a git push, or None."""
    parsed = options(args, "o", PUSH_VALUES)
    if any(name.startswith("--forc") for name in parsed.longs) or "f" in parsed.shorts:
        return "a force push"
    if abbreviates(parsed.longs, "--mirror", "--mir"):
        return "git push --mirror"
    if any(word.startswith("+") for word in parsed.positionals):
        return "a force push (a +refspec)"
    if abbreviates(parsed.longs, "--no-verify", "--no-veri"):
        return "git push --no-verify"
    return None


def commit_violation(subcommand: str, args: list[str]) -> str | None:
    """Return the hook- or signing-skipping flag of a commit, merge or am, or None."""
    short_values, long_values = {
        "commit": ("mFCct", COMMIT_VALUES),
        "merge": ("mFsX", MERGE_VALUES),
        "am": ("", frozenset[str]()),
    }[subcommand]
    parsed = options(args, short_values, long_values)
    skips_hooks = abbreviates(parsed.longs, "--no-verify", "--no-veri")
    if skips_hooks or (subcommand != "merge" and "n" in parsed.shorts):
        return f"git {subcommand} --no-verify"
    if subcommand == "commit" and abbreviates(parsed.longs, "--no-gpg-sign", "--no-g"):
        return "git commit --no-gpg-sign"
    return None


def git_violation(command: list[str]) -> str | None:
    """Return what a git call does that the history rule forbids, or None."""
    subcommand, args, settings = git_parts(command)
    for setting in settings:
        key = setting.split("=", 1)[0].lower()
        if key in ("commit.gpgsign", "core.hookspath"):
            return f"git -c {key}"
    if subcommand == "push":
        return push_violation(args)
    if subcommand in ("commit", "merge", "am"):
        return commit_violation(subcommand, args)
    return None


def credential_violation(command: list[str]) -> str | None:
    """Return how a gh or curl call exposes a token, or None."""
    if command[0] == "gh":
        words = gh_words(command)
        if words == ["auth", "token"]:
            return "gh auth token prints the token into the conversation"
        if words == ["auth", "status"] and ("-t" in command or "--show-token" in command):
            return "gh auth status --show-token prints the token into the conversation"
    if command[0] == "curl":
        text = " ".join(command[1:])
        if any(name in text for name in TOKEN_VARIABLES) or TOKEN.search(text):
            return "a GitHub token sent with curl passes through the conversation"
    return None


def rule_credentials_history(subcommands: list[list[str]]) -> Decision | None:
    """Rule 4: no token reads, tokens in curl, force pushes, --no-verify or unsigned commits."""
    for command in subcommands:
        if found := credential_violation(command):
            return deny(
                f"{found}; use gh or the GitHub MCP server, which authenticate on their own."
            )
        if command[0] == "git" and (found := git_violation(command)):
            return deny(f"{found} is not allowed: {HISTORY_REASON}")
    return None


# ── Rule 3: merge gate ──────────────────────────────────────────────────────────────────────


def pr_merge(args: list[str]) -> Decision:
    """Decide on `gh pr merge ARGS`."""
    if "--admin" in args:
        return deny("merging with --admin bypasses the repository's rules; merge without it.")
    sha = ""
    pr = ""
    method = "the default method"
    i = 0
    while i < len(args):
        arg = args[i]
        i += 1
        if arg == "--match-head-commit":
            sha = args[i] if i < len(args) else ""
        elif arg.startswith("--match-head-commit="):
            sha = arg.split("=", 1)[1]
        elif arg in MERGE_METHODS:
            method = MERGE_METHODS[arg]
        elif not arg.startswith("-") and not pr:
            pr = arg
        i += 1 if arg in PR_MERGE_VALUES else 0
    if not SHA40.fullmatch(sha):
        return deny(HEAD_GUARD_REASON)
    auto = ", auto-merge" if "--auto" in args else ""
    return Decision(
        "ask", f"{PREFIX}merge PR {pr or 'of the current branch'} at {sha} by {method}{auto}"
    )


def api_merge(api: ApiCall) -> Decision | None:
    """Decide on a gh api call that merges, or None when it does not merge."""
    if any(name in field for field in api.fields for name in GRAPHQL_MERGES):
        return deny("merge with gh pr merge --match-head-commit, not a GraphQL mutation.")
    target = PULL_MERGE.search(api.endpoint)
    if target is None or api.method != "PUT":
        return None
    shas = [f.split("=", 1)[1] for f in api.fields if f.startswith("sha=")]
    if not shas or not SHA40.fullmatch(shas[0]):
        return deny("a merge through the API needs -f sha=<the head's full 40-character SHA>.")
    owner, repo, number = target.groups()
    return Decision(
        "ask", f"{PREFIX}merge {owner}/{repo}#{number} at {shas[0]} through the REST API"
    )


def rule_merge_gate_shell(subcommands: list[list[str]]) -> Decision | None:
    """Rule 3 for shell commands: gh pr merge and merges through gh api."""
    for command in subcommands:
        if command[0] != "gh":
            continue
        words = gh_words(command)
        if words == ["pr", "merge"]:
            return pr_merge(command[command.index("merge") + 1 :])
        if words[:1] == ["api"]:
            decision = api_merge(gh_api(command[command.index("api") + 1 :]))
            if decision:
                return decision
    return None


def rule_merge_gate_mcp(call: Call) -> Decision | None:
    """Rule 3 for MCP: merge_pull_request needs the head SHA and the user's yes."""
    if call.tool.rsplit("__", 1)[-1] != "merge_pull_request":
        return None
    sha = call.tool_input.get("expectedHeadSha")
    if not isinstance(sha, str) or not SHA40.fullmatch(sha):
        return deny(
            "merge only at the approved head: pass expectedHeadSha with the full 40-character SHA."
        )
    owner, repo, number, method = (
        str(call.tool_input.get(key, "?"))
        for key in ("owner", "repo", "pullNumber", "merge_method")
    )
    by = method if method != "?" else "the default method"
    return Decision("ask", f"{PREFIX}merge {owner}/{repo}#{number} at {sha} by {by}")


# ── Rule 2: the plugin's agents stay read-only ──────────────────────────────────────────────


def branch_lists(args: list[str]) -> bool:
    """True when git branch only lists."""
    parsed = options(args, "", BRANCH_VALUES)
    lists = "--list" in parsed.longs or "l" in parsed.shorts
    flags_read = parsed.shorts <= set("arvl") and all(name in BRANCH_LONGS for name in parsed.longs)
    return flags_read and (lists or not parsed.positionals)


def git_reads(command: list[str]) -> bool:
    """True when a git call only reads."""
    subcommand, args, _ = git_parts(command)
    if subcommand in GIT_READ:
        return True
    first = args[0] if args else ""
    reads = {
        "fsck": "--lost-found" not in args,
        "worktree": first == "list" or (first == "prune" and bool({"-n", "--dry-run"} & set(args))),
        "stash": first in ("list", "show"),
        "bundle": first in ("verify", "list-heads"),
        "remote": first in ("", "-v", "--verbose", "get-url", "show"),
        "config": bool({"--get", "--get-all", "--get-regexp", "--list", "-l"} & set(args)),
        "clean": bool({"-n", "--dry-run"} & set(args)),
        "lfs": first == "ls-files",
        "branch": branch_lists(args),
    }
    return reads.get(subcommand, False)


def api_reads(api: ApiCall) -> bool:
    """True when a gh api call only reads."""
    if api.has_input or api.method not in ("", "GET"):
        return False
    return all(
        field.startswith("query=")
        and field.removeprefix("query=").lstrip().startswith(("query", "{"))
        for field in api.fields
    )


def gh_reads(command: list[str]) -> bool:
    """True when a gh call only reads."""
    words = gh_words(command)
    if words[:1] == ["search"]:
        return True
    if words[:1] == ["api"]:
        return api_reads(gh_api(command[command.index("api") + 1 :]))
    return len(words) == GH_COMMAND_WORDS and words[1] in GH_READ.get(words[0], frozenset())


def rule_agents_shell(call: Call, subcommands: list[list[str]]) -> Decision | None:
    """Rule 2 for shell commands: the agents run only reading git and gh commands."""
    if call.agent not in AGENTS:
        return None
    for command in subcommands:
        reads = {"git": git_reads, "gh": gh_reads}.get(command[0])
        if reads and not reads(command):
            shown = " ".join(command)[:80]
            reason = f"{call.agent} is read-only; `{shown}` changes state."
            return deny(reason + " Report it to the main session.")
    return None


def mcp_reads(tool: str) -> bool:
    """True when an MCP tool's bare name says it only reads."""
    name = tool.rsplit("__", 1)[-1]
    return name.startswith(("get_", "list_", "search_")) or name.endswith(
        ("_read", "_get", "_list")
    )


def rule_agents_mcp(call: Call) -> Decision | None:
    """Rule 2 for MCP: the agents call only reading tools."""
    if call.agent in AGENTS and not mcp_reads(call.tool):
        return deny(
            f"{call.agent} is read-only and cannot call {call.tool}. Report it to the main session."
        )
    return None


def rule_agents_files(call: Call) -> Decision | None:
    """Rule 2 for file tools: the agents never write inside the project."""
    if call.agent not in AGENTS:
        return None
    path = call.tool_input.get("file_path") or call.tool_input.get("notebook_path")
    if not isinstance(path, str):
        return None
    base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or call.cwd or ".").resolve()
    target = (Path(call.cwd or ".") / path).resolve()
    if target == base or base in target.parents:
        where = "write to the scratch folder the brief names."
        return deny(
            f"{call.agent} is read-only and cannot write {path} inside the project; {where}"
        )
    return None


# ── Rules 5 and 6: context ──────────────────────────────────────────────────────────────────


def prune(sessions: Path) -> None:
    """Remove session markers older than the retention period."""
    limit = time.time() - MARKER_DAYS * SECONDS_PER_DAY
    for marker in sessions.iterdir():
        try:
            if marker.stat().st_mtime < limit:
                marker.rmdir()
        except OSError:
            continue


def rule_contract_once(session: str, *, github: bool) -> str | None:
    """Rule 5: name the contract skill on the session's first GitHub call."""
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not github or not data or not SESSION.fullmatch(session):
        return None
    sessions = Path(data) / "sessions"
    try:
        sessions.mkdir(parents=True, exist_ok=True)
        (sessions / session).mkdir()
        prune(sessions)
    except OSError:
        return None
    return CONTRACT


def rule_compact_state(session: str) -> str | None:
    """Rule 6: the session's lifecycle state, as one line of facts."""
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not data or not SESSION.fullmatch(session):
        return None
    try:
        record = _decode((Path(data) / "state" / f"{session}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, JsonObject):
        return None
    labels = (
        ("kind", "{}"),
        ("repository", "repository {}"),
        ("pr", "PR #{}"),
        ("phase", "phase {}"),
        ("head", "head {}"),
        ("approval", "approval {}"),
        ("next_reference", "next reference {}"),
        ("scratch", "scratch folder {}"),
        ("backup", "backup folder {}"),
    )
    facts = [label.format(record[key]) for key, label in labels if isinstance(record.get(key), str)]
    if "approval" not in record:
        facts.insert(min(5, len(facts)), "approval none")
    return "github-operations state for this session: " + ", ".join(facts) + "."


# ── Entry point ─────────────────────────────────────────────────────────────────────────────


def read_call(raw: str) -> Call:
    """Parse the hook input; raise ValueError when it is not a hook input object."""
    payload = _decode(raw)
    if not isinstance(payload, JsonObject):
        raise TypeError
    tool_input = payload.get("tool_input")

    def text(key: str) -> str:
        value = payload.get(key)
        return value if isinstance(value, str) else ""

    return Call(
        text("session_id"),
        text("agent_type"),
        text("tool_name"),
        tool_input if isinstance(tool_input, JsonObject) else JsonObject(),
        text("cwd"),
    )


def shell_decisions(call: Call) -> tuple[list[Decision | None], bool]:
    """Run the shell rules; return their decisions and whether the call reaches GitHub."""
    command = call.tool_input.get("command")
    command = command if isinstance(command, str) else ""
    try:
        subcommands = lex_subcommands(command)
    except LexError:
        if GUARDED_WORD.search(command):
            return [
                deny("this command could not be parsed; split it into simpler commands.")
            ], False
        return [], False
    github = any(c[0] == "gh" or (c[0] == "git" and git_parts(c)[0] == "push") for c in subcommands)
    rules = [
        rule_credentials_history(subcommands),
        rule_merge_gate_shell(subcommands),
        rule_agents_shell(call, subcommands),
    ]
    return rules, github


def emit(decisions: Sequence[Decision | None], context: str | None, event: str) -> None:
    """Print the strictest decision with any context, or nothing."""
    output: dict[str, object] = {"hookEventName": event}
    for kind in ("deny", "ask"):
        chosen = next((d for d in decisions if d and d.kind == kind), None)
        if chosen:
            output |= {"permissionDecision": kind, "permissionDecisionReason": chosen.reason}
            break
    if context:
        output["additionalContext"] = context
    if len(output) > 1:
        _ = sys.stdout.write(json.dumps({"hookSpecificOutput": output}) + "\n")


def main(handler: str) -> int:
    """Run one handler on the hook input from stdin."""
    raw = sys.stdin.read()
    try:
        call = read_call(raw)
    except (ValueError, TypeError):
        if handler != "compact":
            emit(
                [deny("the hook could not read its input; try the call again.")], None, "PreToolUse"
            )
        return 0
    if handler == "compact":
        emit([], rule_compact_state(call.session), "SessionStart")
        return 0
    if handler == "shell":
        decisions, github = shell_decisions(call)
    elif handler == "mcp":
        decisions, github = [rule_merge_gate_mcp(call), rule_agents_mcp(call)], True
    elif handler == "files":
        decisions, github = [rule_agents_files(call)], False
    else:
        decisions, github = [deny(f"unknown hook handler {handler!r}.")], False
    emit(decisions, rule_contract_once(call.session, github=github), "PreToolUse")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
