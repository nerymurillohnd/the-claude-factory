#!/usr/bin/env python3
"""github-operations hook handlers: read one hook input on stdin, print at most one JSON object.

Usage: github_hooks.py shell|mcp|files|compact

shell   (PreToolUse, Bash and PowerShell): reviewer agents' named writes, contract once.
mcp     (PreToolUse, GitHub MCP tools): reviewer agents' named writes, contract once.
files   (PreToolUse, Write, Edit and NotebookEdit): reviewer agents' writes in the project.
compact (SessionStart, compact): the session's lifecycle state as context.

Only the plugin's reviewer agents (pr-tracker, repo-auditor) are ever denied, and only the
write operations named below; the main session and every other agent pass. Every run exits 0.
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
    from collections.abc import Callable, Sequence

PREFIX = "github-operations: "
AGENTS = ("github-operations:pr-tracker", "github-operations:repo-auditor")
CONTRACT = (
    "This session is acting on GitHub. The github-operations plugin's rules for GitHub work"
    " (tool choice, approvals, evidence) are in the skill github-operations:github."
)
SESSION = re.compile(r"[A-Za-z0-9_-]+")
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
REVIEWER_INPUT = re.compile(r'"agent_type"\s*:\s*"github-operations:(?:pr-tracker|repo-auditor)"')
GUARDED_WORD = re.compile(r"(?<![A-Za-z0-9_.-])(git|gh)(?![A-Za-z0-9_-])")
HEREDOC = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
SHELL_WORD = re.compile(r"(?<![\w.-])(?:bash|sh|zsh)(?![\w.-])")
SUBSTITUTED = "SUBSTITUTION"
SUBSTITUTION_OPENERS = ("$(", "<(", ">(")
SOURCES = ("source", ".")
SHELL_VALUES = ("-o", "-O", "+o", "+O", "--rcfile", "--init-file")
ASSIGNERS = (
    "export",
    "declare",
    "typeset",
    "readonly",
    "local",
    "read",
    "mapfile",
    "readarray",
    "printf",
)
CONFIG_NAME = re.compile(r"HOME|XDG_CONFIG_HOME|GIT_CONFIG\w*|GIT_EXEC_PATH")
CONFIG_ASSIGNMENT = re.compile(rf"(?:{CONFIG_NAME.pattern})\+?=")
MUTATION = re.compile(r"\bmutation\b")
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
GIT_SETTINGS = ("-c", "--config-env")
GH_GLOBAL_VALUES = ("-R", "--repo", "--hostname")
API_SHORTS = ("-X", "-f", "-F")
SHORT_OPTION = 2
API_LONGS = ("--method", "--field", "--raw-field", "--input")
API_VALUES = ("-H", "--header", "-q", "--jq", "-t", "--template", "--cache", "-p", "--preview")

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
GIT_WRITE = frozenset(
    {
        "add",
        "am",
        "checkout",
        "cherry-pick",
        "commit",
        "commit-tree",
        "fetch",
        "filter-branch",
        "filter-repo",
        "gc",
        "init",
        "maintenance",
        "merge",
        "mv",
        "pack-refs",
        "prune",
        "pull",
        "push",
        "rebase",
        "repack",
        "replace",
        "reset",
        "restore",
        "revert",
        "rm",
        "sparse-checkout",
        "switch",
        "update-index",
        "update-ref",
        "write-tree",
    }
)
GH_WRITE_VERBS = frozenset(
    {
        "add",
        "archive",
        "cancel",
        "checkout",
        "close",
        "comment",
        "create",
        "delete",
        "develop",
        "disable",
        "edit",
        "enable",
        "fork",
        "install",
        "lock",
        "login",
        "logout",
        "merge",
        "pin",
        "ready",
        "refresh",
        "remove",
        "rename",
        "reopen",
        "rerun",
        "review",
        "revert",
        "run",
        "set",
        "setup-git",
        "sync",
        "transfer",
        "unarchive",
        "unlock",
        "unpin",
        "update-branch",
        "upgrade",
        "upload",
    }
)
MCP_WRITES = frozenset(
    {
        "actions_run_trigger",
        "add_automation_to_group",
        "add_comment_to_pending_review",
        "add_issue_comment",
        "add_reply_to_pull_request_comment",
        "assign_copilot_to_issue",
        "assign_copilot_to_issue_with_intent",
        "create_automation",
        "create_automation_group",
        "create_branch",
        "create_gist",
        "create_or_update_file",
        "create_pull_request",
        "create_pull_request_with_copilot",
        "create_repository",
        "create_repository_ruleset",
        "custom_properties_write",
        "delete_automation",
        "delete_file",
        "delete_repository",
        "discussion_comment_write",
        "dismiss_notification",
        "fork_repository",
        "issue_dependency_write",
        "issue_write",
        "label_write",
        "manage_notification_subscription",
        "manage_repository_notification_subscription",
        "mark_all_notifications_read",
        "merge_pull_request",
        "projects_write",
        "pull_request_review_write",
        "push_files",
        "remove_automation_from_group",
        "request_copilot_review",
        "run_automation",
        "run_secret_scanning",
        "star_repository",
        "sub_issue_write",
        "unstar_repository",
        "update_automation",
        "update_gist",
        "update_issue_comment",
        "update_pull_request",
        "update_pull_request_branch",
    }
)


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


class Command(NamedTuple):
    """One subcommand: the words it runs and the VAR=value assignments set for it."""

    words: list[str]
    env: list[str]


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
            if SHELL_WORD.search(line):
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
    """Return where the $(...), <(...), >(...) or `...` that starts at i ends."""
    end = text.find("`", i + 1) if text[i] == "`" else closing_paren(text, i + 2)
    if end < 0:
        raise LexError
    return end


def extract_substitutions(text: str) -> tuple[str, list[str]]:
    """Replace each $(...), <(...), >(...) and `...` outside single quotes with a word.

    Return the text and the bodies, which a shell runs as scripts of their own.
    """
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
        elif text.startswith(SUBSTITUTION_OPENERS, i) or ch == "`":
            end = substitution_end(text, i)
            bodies.append(text[i + (1 if ch == "`" else 2) : end])
            out.append(SUBSTITUTED)
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


def unwrap(words: list[str]) -> Command:
    """Set aside leading assignments and wrapper commands; return the command that really runs."""
    env: list[str] = []
    i = 0
    while i < len(words):
        word = words[i]
        name = posixpath.basename(word)
        if ASSIGNMENT.match(word):
            env.append(word)
            i += 1
        elif name in WRAPPERS:
            i += 1
            while i < len(words) and (words[i].startswith("-") or ASSIGNMENT.match(words[i])):
                env += [words[i]] if ASSIGNMENT.match(words[i]) else []
                i += 2 if words[i] in WRAPPERS[name] else 1
        else:
            break
    rest = words[i:]
    return Command([posixpath.basename(rest[0]), *rest[1:]] if rest else [], env)


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


def expand(words: list[str], depth: int) -> list[Command]:
    """Return the subcommands one word list runs, nested scripts included."""
    command = unwrap(words)
    if not command.words:
        return [command] if command.env else []
    script = nested_script(command.words)
    return [command] if script is None else [command, *lex_subcommands(script, depth + 1)]


def lex_subcommands(command: str, depth: int = 0) -> list[Command]:
    """Split a shell command into every subcommand it runs, with its assignments."""
    if depth > MAX_DEPTH:
        raise LexError
    text, scripts = split_heredocs(command)
    text, bodies = extract_substitutions(text)
    result: list[Command] = []
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


def git_parts(command: list[str]) -> tuple[str, list[str]]:
    """Return a git call's subcommand and its arguments, past git's own options."""
    i = 1
    while i < len(command) and command[i].startswith("-"):
        i += 2 if command[i] in (*GIT_GLOBAL_VALUES, *GIT_SETTINGS) else 1
    subcommand = command[i] if i < len(command) else ""
    return subcommand, command[i + 1 :]


def gh_split(command: list[str]) -> tuple[list[str], list[str]]:
    """Return a gh call's two command words and the rest of its arguments, in order."""
    words: list[str] = []
    rest: list[str] = []
    i = 1
    while i < len(command):
        arg = command[i]
        i += 1
        if arg in GH_GLOBAL_VALUES:
            rest += command[i - 1 : i + 1]
            i += 1
        elif len(words) < GH_COMMAND_WORDS and not arg.startswith("-"):
            words.append(arg)
        else:
            rest.append(arg)
    return words, rest


def gh_words(command: list[str]) -> list[str]:
    """Return a gh call's command words, such as pr and merge, skipping options and their values."""
    return gh_split(command)[0]


class ApiCall(NamedTuple):
    """A gh api call: its endpoint, method, fields and whether it reads a request body."""

    endpoint: str
    method: str
    fields: list[str]
    has_input: bool


def api_options(args: list[str]) -> list[tuple[str, str]]:
    """Pair each `gh api` option with its value; a positional word comes as ("", word)."""
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(args):
        arg = args[i]
        i += 1
        if arg.startswith("--") and "=" in arg:
            name, value = arg.split("=", 1)
        elif arg[:SHORT_OPTION] in API_SHORTS and len(arg) > SHORT_OPTION:
            name, value = arg[:SHORT_OPTION], arg[SHORT_OPTION:]
        elif arg in (*API_SHORTS, *API_LONGS, *API_VALUES):
            name, value = arg, args[i] if i < len(args) else ""
            i += 1
        else:
            name, value = ("", arg) if not arg.startswith("-") else (arg, "")
        pairs.append((name, value))
    return pairs


def gh_api(args: list[str]) -> ApiCall:
    """Parse the arguments after `gh api`."""
    pairs = api_options(args)
    endpoint = next((value for name, value in pairs if not name), "")
    methods = [value for name, value in pairs if name in ("-X", "--method")]
    fields = [value for name, value in pairs if name in ("-f", "-F", "--field", "--raw-field")]
    has_input = any(name == "--input" for name, _ in pairs)
    return ApiCall(endpoint, methods[-1].upper() if methods else "", fields, has_input)


# ── Rule 2: the plugin's reviewer agents do not write ───────────────────────────────────────


def deny(reason: str) -> Decision:
    """A deny with the plugin's prefix."""
    return Decision("deny", PREFIX + reason)


def branch_lists(args: list[str]) -> bool:
    """True when git branch only lists."""
    parsed = options(args, "", BRANCH_VALUES)
    lists = "--list" in parsed.longs or "l" in parsed.shorts
    flags_read = parsed.shorts <= set("arvl") and all(name in BRANCH_LONGS for name in parsed.longs)
    return flags_read and (lists or not parsed.positionals)


def tag_lists(args: list[str]) -> bool:
    """True when git tag only lists."""
    listing = {"-l", "--list", "-n", "--contains", "--no-contains", "--points-at", "--merged"}
    return not args or bool(listing & set(args)) or args[0].startswith("--sort")


def sets_git_config(command: Command) -> bool:
    """True when a subcommand points git at other configuration, which can run any program.

    That is -c or --config-env on a git call, or any assignment to a variable git reads its
    configuration from: VAR=, VAR+=, export and its kin, read, mapfile or printf -v.
    """
    words = command.words
    if any(CONFIG_ASSIGNMENT.match(w) for w in (*command.env, *words)):
        return True
    if words[:1] and words[0] in ASSIGNERS and any(CONFIG_NAME.fullmatch(w) for w in words):
        return True
    if words[:1] != ["git"]:
        return False
    subcommand, args = git_parts(words)
    flags = words[1 : len(words) - len(args) - (1 if subcommand else 0)]
    return any(f in GIT_SETTINGS or f.startswith("--config-env=") for f in flags)


def shell_script(command: list[str]) -> str:
    """Return the script word a shell, source or . runs, or "" when it reads stdin."""
    i = 1
    while i < len(command) and command[i][:1] in "-+" and command[i] not in ("-", "--"):
        option = command[i]
        short = option[:2] != "--"
        if command[0] in SHELLS and short and "s" in option[1:]:
            return ""
        takes_value = option in SHELL_VALUES or (short and bool(set(option[1:]) & set("oO")))
        i += 2 if takes_value else 1
    i += 1 if i < len(command) and command[i] == "--" else 0
    return command[i] if i < len(command) else ""


def hidden_script(command: list[str], cwd: str) -> bool:
    """True when a shell, source or . runs a script the hook cannot read.

    Anything but an existing regular file counts: stdin, a pipe, a here-string, a process
    substitution, a device, or a word that is no file at all.
    """
    if command[0] not in (*SHELLS, *SOURCES) or nested_script(command) is not None:
        return False
    script = shell_script(command)
    if script in ("", "-", SUBSTITUTED):
        return True
    target = (Path(cwd or ".") / script).resolve()
    return not target.is_file() or target.parts[1:2] in (("dev",), ("proc",))


def git_writes(command: list[str]) -> bool:
    """True when a git call is one of the named write operations."""
    subcommand, args = git_parts(command)
    if subcommand in GIT_WRITE:
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
        "lfs": first in ("ls-files", "status", "env"),
        "branch": branch_lists(args),
        "tag": tag_lists(args),
        "apply": bool({"--check", "--stat", "--numstat", "--summary"} & set(args)),
        "reflog": first in ("", "show", "exists"),
        "notes": first in ("", "list", "show"),
        "submodule": first in ("", "status", "summary"),
        "bisect": first in ("", "log", "view", "visualize"),
    }
    return not reads.get(subcommand, True)


def graphql_query(field: str) -> bool:
    """True when a field is an inline GraphQL query with no mutation in it."""
    document = field.removeprefix("query=").lstrip()
    return (
        field.startswith("query=")
        and document.startswith(("query", "{"))
        and not MUTATION.search(document)
    )


def api_reads(api: ApiCall) -> bool:
    """True when a gh api call only reads.

    gh sends a call with fields and no method as POST, so only the GraphQL endpoint with
    inline queries reads that way.
    """
    if api.has_input or api.method not in ("", "GET"):
        return False
    if api.method == "GET" or not api.fields:
        return True
    return api.endpoint == "graphql" and all(graphql_query(f) for f in api.fields)


def gh_writes(command: list[str]) -> bool:
    """True when a gh call is one of the named write operations."""
    words = gh_words(command)
    if words[:1] == ["api"]:
        return not api_reads(gh_api(command[command.index("api") + 1 :]))
    return len(words) == GH_COMMAND_WORDS and words[1] in GH_WRITE_VERBS


def rule_agents_shell(call: Call, subcommands: list[Command]) -> Decision | None:
    """Rule 2 for shell commands: the reviewer agents run no named git or gh write."""
    if call.agent not in AGENTS:
        return None
    for subcommand in subcommands:
        command = subcommand.words
        if command and hidden_script(command, call.cwd):
            reason = f"{call.agent} is read-only and cannot run `{command[0]}` on a hidden script;"
            return deny(reason + " run the commands directly.")
        if sets_git_config(subcommand):
            reason = (
                f"{call.agent} is read-only and cannot change where git reads its configuration;"
            )
            return deny(
                reason + " run git without -c, --config-env, GIT_CONFIG, HOME or XDG_CONFIG_HOME."
            )
        writes = {"git": git_writes, "gh": gh_writes}.get(command[0]) if command else None
        if writes and writes(command):
            shown = " ".join(command)[:80]
            reason = f"{call.agent} is read-only; `{shown}` changes state."
            return deny(reason + " Report it to the main session.")
    return None


def rule_agents_mcp(call: Call) -> Decision | None:
    """Rule 2 for MCP: the reviewer agents call no named write tool, on any GitHub server."""
    if call.agent in AGENTS and call.tool.rsplit("__", 1)[-1] in MCP_WRITES:
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


def reaches_github(command: list[str]) -> bool:
    """True when a subcommand is gh or git push."""
    return command[:1] == ["gh"] or (command[:1] == ["git"] and git_parts(command)[0] == "push")


def shell_decisions(call: Call) -> tuple[list[Decision | None], bool]:
    """Run the shell rules; return their decisions and whether the call reaches GitHub."""
    command = call.tool_input.get("command")
    command = command if isinstance(command, str) else ""
    try:
        subcommands = lex_subcommands(command)
    except LexError:
        if call.agent in AGENTS and GUARDED_WORD.search(command):
            reason = f"{call.agent} is read-only and this command could not be parsed;"
            return [deny(reason + " split it into simpler commands.")], False
        return [], False
    github = any(reaches_github(c.words) for c in subcommands)
    return [rule_agents_shell(call, subcommands)], github


def emit(decisions: Sequence[Decision | None], context: str | None, event: str) -> None:
    """Print the first deny with any context, or nothing."""
    output: dict[str, object] = {"hookEventName": event}
    chosen = next((d for d in decisions if d), None)
    if chosen:
        output |= {"permissionDecision": chosen.kind, "permissionDecisionReason": chosen.reason}
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
        if handler != "compact" and REVIEWER_INPUT.search(raw):
            reason = "a reviewer agent's call could not be read; try the call again."
            emit([deny(reason)], None, "PreToolUse")
        return 0
    if handler == "compact":
        emit([], rule_compact_state(call.session), "SessionStart")
        return 0
    if handler == "shell":
        decisions, github = shell_decisions(call)
    elif handler == "mcp":
        decisions, github = [rule_agents_mcp(call)], True
    elif handler == "files":
        decisions, github = [rule_agents_files(call)], False
    else:
        return 0
    emit(decisions, rule_contract_once(call.session, github=github), "PreToolUse")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
