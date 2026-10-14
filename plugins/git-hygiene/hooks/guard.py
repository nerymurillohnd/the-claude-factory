#!/usr/bin/env python3
"""PreToolUse hook for git-hygiene's cleanup skill: the guard rails that must hold every time.

Registered by the skill's frontmatter, so it only runs after /git-hygiene:cleanup was invoked.
Reads the hook event on stdin and answers with a permission decision on stdout:

- deny: force-pushes, deleting main on the remote, history rewriting tools, changing the
  remote default branch, and anything that would print a credential or a secret file.
- ask: every other command that changes the repository, its remotes, its pull requests or
  files, so the user confirms each one in Claude Code's own permission prompt.
- nothing: read-only commands and everything unrelated to git, left to the normal flow.

A command it cannot parse or does not recognize asks instead of passing silently.
Requires Python 3.9+, standard library only.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

DENY = "deny"
ASK = "ask"
Verdict = tuple[str, str]

MAX_DEPTH = 3
SEPARATORS = ";&|()\n"
WRAPPERS = frozenset(
    {"sudo", "command", "time", "nohup", "exec", "xargs", "env", "nice", "builtin"}
)
SHELLS = frozenset({"bash", "sh", "zsh", "dash", "ksh"})
PROTECTED = frozenset({"main", "master", "trunk", "develop", "head"})

GIT_GLOBAL_WITH_VALUE = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"},
)
RISKY_CONFIG = re.compile(
    r"^(alias\.|core\.(sshcommand|pager|editor|fsmonitor|hookspath)|.*helper)"
)

DEFAULT_BRANCH = "Changing the repository's default branch is never done automatically."
REWRITES = "rewrites history; cleanup never rewrites published history."
DRY_RUN_GIT = frozenset({"fetch", "clean", "worktree", "remote", "gc", "prune"})
DENY_GIT = {
    "filter-branch": f"git filter-branch {REWRITES}",
    "filter-repo": f"git filter-repo {REWRITES}",
}
READ_ONLY_GIT = frozenset(
    {
        "status",
        "log",
        "diff",
        "show",
        "rev-parse",
        "rev-list",
        "for-each-ref",
        "cherry",
        "merge-base",
        "merge-tree",
        "range-diff",
        "ls-files",
        "ls-tree",
        "ls-remote",
        "cat-file",
        "blame",
        "annotate",
        "grep",
        "describe",
        "shortlog",
        "count-objects",
        "check-ignore",
        "diff-tree",
        "diff-index",
        "diff-files",
        "name-rev",
        "show-ref",
        "show-branch",
        "var",
        "version",
        "help",
        "whatchanged",
        "verify-commit",
        "verify-tag",
        "fsck",
        "symbolic-ref",
        "check-ref-format",
        "merge-file",
        "get-tar-commit-id",
    },
)
SECRET_REVEALING_GIT = frozenset(
    {"show", "diff", "log", "blame", "annotate", "grep", "cat-file", "diff-tree", "whatchanged"},
)
SAFE_FIRST_ARG = {
    "stash": frozenset({"list", "show"}),
    "worktree": frozenset({"list"}),
    "reflog": frozenset({"show", "exists", ""}),
    "bisect": frozenset({"log", "view", "visualize"}),
    "submodule": frozenset({"status", "summary"}),
    "bundle": frozenset({"verify", "list-heads"}),
    "notes": frozenset({"list", "show"}),
}
ASK_GIT_REASON = {
    "push": "git push changes the remote.",
    "fetch": "git fetch updates remote-tracking references.",
    "reset": "git reset moves a branch and can discard work.",
    "clean": "git clean deletes untracked files.",
    "gc": "git gc prunes unreachable objects.",
    "prune": "git prune deletes unreachable objects.",
    "reflog": "git reflog expire/delete removes recovery entries.",
}

SECRET_NAME = re.compile(
    r"^(\.env(\..+)?|.+\.(pem|key|p12|pfx|keystore|kdbx|tfstate)|id_(rsa|dsa|ecdsa|ed25519)"
    r"|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd|credentials(\..+)?|secrets?(\..+)?"
    r"|terraform\.tfvars)$",
    re.IGNORECASE,
)
SECRET_EXAMPLE = re.compile(r"\.(example|sample|template|dist|pub)$", re.IGNORECASE)
SECRET_DIRS = frozenset({".ssh", ".aws", ".gnupg"})
FILE_READERS = frozenset(
    {
        "cat",
        "head",
        "tail",
        "less",
        "more",
        "bat",
        "nl",
        "tac",
        "sed",
        "awk",
        "grep",
        "egrep",
        "fgrep",
        "rg",
        "ag",
        "xxd",
        "od",
        "hexdump",
        "strings",
        "base64",
        "cp",
        "jq",
        "source",
        ".",
    },
)
FILE_DELETERS = frozenset({"rm", "rmdir", "unlink", "shred"})
GH_READ = frozenset(
    {"view", "list", "status", "diff", "checks", "get", "show", "watch", "browse", "help"},
)
GH_SENSITIVE = frozenset({"secret", "variable", "ssh-key", "gpg-key"})
GH_BODY_FLAGS = frozenset({"-f", "-F", "--field", "--raw-field", "--input"})


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


def basename(token: str) -> str:
    """Return the last path segment of a token, without a Windows .exe suffix."""
    name = re.split(r"[\\/]", token.rstrip("/\\"))[-1].lower()
    return name.removesuffix(".exe")


def positionals(args: list[str]) -> list[str]:
    """Return the arguments that are not options."""
    return [arg for arg in args if not arg.startswith("-")]


def is_secret_path(token: str) -> bool:
    """True when a token names a file or folder that usually holds secrets."""
    parts = [part for part in re.split(r"[\\/:]", token) if part]
    if any(part in SECRET_DIRS for part in parts[:-1]):
        return True
    name = parts[-1] if parts else ""
    return bool(SECRET_NAME.match(name)) and not SECRET_EXAMPLE.search(name)


def secret_verdict(tokens: list[str]) -> Verdict | None:
    """Deny when any token names a secret-bearing file."""
    for token in tokens:
        if not token.startswith("-") and is_secret_path(token):
            return DENY, (
                f"'{token}' looks like a secret-bearing file; the audit reports its name only "
                "and never reads or prints its contents."
            )
    return None


def check_push(args: list[str]) -> Verdict | None:
    """Deny force pushes and deleting a protected branch; ask for any other real push."""
    plain = positionals(args)
    longs = [arg for arg in args if arg.startswith("--")]
    shorts = [arg for arg in args if arg.startswith("-") and not arg.startswith("--")]
    forced = (
        any(arg in {"--force", "--mirror", "--force-if-includes"} for arg in longs)
        or any(arg.startswith("--force-with-lease") for arg in longs)
        or any("f" in arg[1:] for arg in shorts)
        or any(ref.startswith("+") for ref in plain)
    )
    if forced:
        return DENY, "Force-pushing rewrites published history; cleanup never does that."
    if "--dry-run" in longs or "-n" in shorts:
        return None
    deleting = (
        "--delete" in longs
        or any("d" in arg[1:] for arg in shorts)
        or any(ref.startswith(":") for ref in plain)
    )
    targets = [ref.lstrip(":").removeprefix("refs/heads/").lower() for ref in plain[1:]]
    if deleting and any(target in PROTECTED for target in targets):
        return (
            DENY,
            "Deleting main (or another protected branch) on the remote is never part of cleanup.",
        )
    verb = "deletes a remote branch" if deleting else "changes the remote"
    return ASK, f"git push {verb}."


def check_branch(args: list[str]) -> Verdict | None:
    """Ask for branch deletion, renames and creation; listing passes."""
    changing = {"-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy", "-f", "--force"}
    if any(arg in changing or arg.startswith("--set-upstream") for arg in args):
        return ASK, "git branch deletes, renames or reconfigures a branch."
    listing = {"-l", "--list", "--contains", "--merged", "--no-merged", "--points-at"}
    if positionals(args) and not any(arg in listing for arg in args):
        return ASK, "git branch with a name creates a branch."
    return None


def check_tag(args: list[str]) -> Verdict | None:
    """Ask for tag creation and deletion; listing passes."""
    changing = {"-d", "--delete", "-f", "--force", "-a", "-s", "-m"}
    listing = {"-l", "--list", "--contains", "--merged", "--no-merged", "--points-at"}
    if any(arg in changing for arg in args):
        return ASK, "git tag creates or deletes a tag."
    if positionals(args) and not any(arg in listing for arg in args):
        return ASK, "git tag with a name creates a tag."
    return None


def check_remote(args: list[str]) -> Verdict | None:
    """Deny commands that print remote URLs (they can embed credentials); ask for changes."""
    plain = positionals(args)
    action = plain[0] if plain else ""
    if "-v" in args or "--verbose" in args or action in {"get-url", "show"}:
        return DENY, (
            "This prints remote URLs, which can embed credentials. "
            "Run the plugin's inventory.py: it redacts them."
        )
    if action in {
        "add",
        "remove",
        "rm",
        "rename",
        "set-url",
        "set-head",
        "set-branches",
        "prune",
        "update",
    }:
        return ASK, f"git remote {action} changes the repository's remotes."
    return None


def check_config(args: list[str]) -> Verdict | None:
    """Deny config reads that can print credentials; ask for writes."""
    writing = {
        "--unset",
        "--unset-all",
        "--add",
        "--replace-all",
        "--edit",
        "-e",
        "--remove-section",
        "--rename-section",
    }
    plain = positionals(args)
    if any(arg in writing for arg in args) or len(plain) > 1:
        return ASK, "git config changes the repository's configuration."
    listing = {"-l", "--list", "--get-regexp", "--show-origin"}
    sensitive = re.compile(r"url|credential|token|password|extraheader", re.IGNORECASE)
    if any(arg in listing for arg in args) or any(sensitive.search(key) for key in plain):
        return DENY, (
            "This can print remote URLs or credentials. "
            "Run the plugin's inventory.py: it redacts them."
        )
    return None


SPECIAL_GIT: dict[str, Callable[[list[str]], Verdict | None]] = {
    "push": check_push,
    "branch": check_branch,
    "tag": check_tag,
    "remote": check_remote,
    "config": check_config,
}


def parse_git(args: list[str]) -> tuple[str, list[str], list[str]]:
    """Split git's arguments into the subcommand, its arguments and the -c settings."""
    configs: list[str] = []
    index = 0
    while index < len(args) and args[index].startswith("-"):
        takes_value = args[index] in GIT_GLOBAL_WITH_VALUE
        if args[index] == "-c" and index + 1 < len(args):
            configs.append(args[index + 1])
        index += 2 if takes_value else 1
    if index >= len(args):
        return "", [], configs
    return args[index], args[index + 1 :], configs


def dry_run(sub: str, args: list[str]) -> bool:
    """True when the arguments ask for a preview (-n means something else for fetch)."""
    short_n = any(a.startswith("-") and not a.startswith("--") and "n" in a[1:] for a in args)
    return "--dry-run" in args or (sub != "fetch" and short_n)


def classify_subcommand(sub: str, rest: list[str]) -> Verdict | None:
    """Return the verdict for a git subcommand and its arguments."""
    if sub in DRY_RUN_GIT and dry_run(sub, rest):
        return None
    if sub in SPECIAL_GIT:
        return SPECIAL_GIT[sub](rest)
    if sub in SAFE_FIRST_ARG:
        first = rest[0] if rest and not rest[0].startswith("-") else ""
        if first in SAFE_FIRST_ARG[sub]:
            return None
        return ASK, f"git {sub} {first} changes repository state."
    if sub in READ_ONLY_GIT and not (sub == "fsck" and "--lost-found" in rest):
        return None
    return ASK, ASK_GIT_REASON.get(sub, f"git {sub} can change repository state.")


def classify_git(args: list[str]) -> Verdict | None:
    """Return the verdict for one git invocation, or None when it only reads."""
    sub, rest, configs = parse_git(args)
    if any(RISKY_CONFIG.match(setting.lower()) for setting in configs):
        return ASK, "git -c sets a configuration that can run another program."
    if not sub:
        return None
    if sub in DENY_GIT:
        return DENY, DENY_GIT[sub]
    if sub in SECRET_REVEALING_GIT:
        verdict = secret_verdict(rest)
        if verdict:
            return verdict
    return classify_subcommand(sub, rest)


def gh_api_method(args: list[str]) -> str:
    """Return the HTTP method a `gh api` call will use."""
    for index, arg in enumerate(args):
        if arg in {"-X", "--method"} and index + 1 < len(args):
            return args[index + 1].upper()
        if arg.startswith("--method="):
            return arg.split("=", 1)[1].upper()
    return "POST" if any(arg in GH_BODY_FLAGS for arg in args) else "GET"


def check_gh_api(args: list[str]) -> Verdict | None:
    """Deny default-branch changes; ask for any non-GET call."""
    joined = " ".join(args)
    if "graphql" in args:
        return (ASK, "A GraphQL mutation changes GitHub state.") if "mutation" in joined else None
    method = gh_api_method(args)
    if method == "GET":
        return None
    if "default_branch" in joined:
        return DENY, DEFAULT_BRANCH
    return ASK, f"gh api {method} changes GitHub state."


def classify_gh_auth(action: str, args: list[str]) -> Verdict | None:
    """Deny commands that print a token; ask for account changes."""
    if action == "token" or "--show-token" in args or "-t" in args:
        return DENY, "This prints an authentication token."
    return None if action == "status" else (ASK, "gh auth changes the signed-in account.")


def classify_gh(args: list[str]) -> Verdict | None:
    """Return the verdict for one gh invocation, or None when it only reads."""
    plain = positionals(args)
    group = plain[0] if plain else ""
    action = plain[1] if len(plain) > 1 else ""
    if group == "auth":
        return classify_gh_auth(action, args)
    if group == "api":
        return check_gh_api(args)
    if group == "repo" and any(arg.startswith("--default-branch") for arg in args):
        return DENY, DEFAULT_BRANCH
    if group in GH_SENSITIVE:
        return None if action == "list" else (ASK, f"gh {group} {action} touches credentials.")
    if not group or action in GH_READ or group in GH_READ:
        return None
    return ASK, f"gh {group} {action} changes GitHub state."


def at_command_position(segment: list[str], index: int) -> bool:
    """True when every token before index is an assignment, a wrapper or an option of one."""
    for token in segment[:index]:
        assignment = "=" in token and "/" not in token.split("=", 1)[0]
        if not (assignment or basename(token) in WRAPPERS or token.startswith("-")):
            return False
    return True


def classify_command(name: str, rest: list[str]) -> Verdict | None:
    """Return the verdict for one command name and its arguments."""
    if name == "git":
        return classify_git(rest)
    if name == "gh":
        return classify_gh(rest)
    if name in FILE_READERS:
        return secret_verdict(rest)
    if name in FILE_DELETERS:
        return ASK, f"{name} deletes files."
    if name == "printenv" or (name == "env" and not rest):
        return DENY, "This prints the environment, which can hold secrets."
    return None


def classify_segment(segment: list[str]) -> list[Verdict]:
    """Return the verdicts for one command segment (no pipes or separators)."""
    verdicts: list[Verdict] = []
    for index, token in enumerate(segment):
        if not at_command_position(segment, index):
            break
        found = classify_command(basename(token), segment[index + 1 :])
        if found:
            verdicts.append(found)
    return verdicts


def split_segments(command: str) -> list[list[str]]:
    """Split a command line into segments on ; & | ( ) and newlines."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=SEPARATORS)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    segments: list[list[str]] = []
    current: list[str] = []
    for token in lexer:
        if set(token) <= set(SEPARATORS):
            if current:
                segments.append(current)
            current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def nested_commands(segment: list[str]) -> list[str]:
    """Return command strings hidden in `bash -c`, `eval`, `$(...)` and backticks."""
    found: list[str] = []
    for index, token in enumerate(segment):
        name = basename(token)
        if name in SHELLS and "-c" in segment[index + 1 :]:
            position = segment.index("-c", index + 1)
            found.extend(segment[position + 1 : position + 2])
        elif name == "eval":
            found.append(" ".join(segment[index + 1 :]))
        found.extend(re.findall(r"\$\(([^()]*)\)", token))
        found.extend(re.findall(r"`([^`]*)`", token))
    return found


def analyze(command: str, depth: int = 0) -> list[Verdict]:
    """Return every verdict for a command line, including the commands nested in it."""
    verdicts: list[Verdict] = []
    for segment in split_segments(command):
        verdicts.extend(classify_segment(segment))
        if depth < MAX_DEPTH:
            for inner in nested_commands(segment):
                verdicts.extend(analyze(inner, depth + 1))
    return verdicts


def decide(event: object) -> Verdict | None:
    """Return the single verdict for a hook event: deny beats ask, nothing means no objection."""
    tool = text_at(event, "tool_name")
    if tool == "Read":
        return secret_verdict([text_at(event, "tool_input", "file_path")])
    if tool != "Bash":
        return None
    try:
        verdicts = analyze(text_at(event, "tool_input", "command"))
    except ValueError:
        return (
            ASK,
            "git-hygiene could not parse this command, so it cannot tell whether it is safe.",
        )
    for kind in (DENY, ASK):
        for found in verdicts:
            if found[0] == kind:
                return found
    return None


def emit(verdict: Verdict) -> None:
    """Print the permission decision Claude Code reads."""
    kind, reason = verdict
    suffix = (
        " Approve only if it matches an action you approved in the cleanup plan."
        if kind == ASK
        else " Cleanup stops here: ask the user how to proceed."
    )
    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": kind,
            "permissionDecisionReason": f"git-hygiene: {reason}{suffix}",
        },
    }
    sys.stdout.write(json.dumps(decision) + "\n")


def main() -> int:
    """Run the hook; any internal error asks instead of letting the call through unchecked."""
    try:
        verdict = decide(_decode(sys.stdin.read()))
    except (ValueError, OSError, RecursionError):
        verdict = ASK, "git-hygiene's guard could not read this tool call."
    if verdict:
        emit(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
