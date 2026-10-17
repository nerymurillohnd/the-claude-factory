#!/usr/bin/env python3
"""PreToolUse hook for the git-cleanup skill: the guard rails that must hold every time.

Registered by the skill's frontmatter, so it only runs after /github-operations:git-cleanup
was invoked.
Reads the hook event on stdin and answers with a permission decision on stdout:

- deny: force-pushes, deleting main on the remote, history rewriting tools, changing the remote
  default branch, `git clean -x`, and anything that would print a credential or a secret file.
- ask: every other git or gh command that changes the repository, its remotes or its pull
  requests, file deletions and moves, commands that print file contents (which can include
  committed secrets), and inline interpreter code, so the user confirms each one.
- nothing: read-only commands and everything unrelated, left to the normal permission flow.

A git or gh command is recognized anywhere in a command line (loops, pipes, xargs, wrappers,
`bash -c`, `$(...)`). A command it cannot parse asks instead of passing silently. The guard is
best effort against honest mistakes, not a sandbox: shell tricks it cannot see still pass.
Requires Python 3.9+, standard library only.
"""

from __future__ import annotations

import fnmatch
import json
import re
import shlex
import sys

# Not imported from typing: that import costs about 1 ms on every hook call.
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable

DENY = "deny"
ASK = "ask"
Verdict = tuple[str, str]

MAX_DEPTH = 3
SEPARATORS = ";&|()\n"
WRAPPERS = frozenset(
    {"sudo", "command", "time", "nohup", "exec", "xargs", "env", "nice", "builtin", "timeout"},
)
KEYWORDS = frozenset({"do", "then", "else", "elif", "if", "while", "until", "{", "!"})
SHELLS = frozenset({"bash", "sh", "zsh", "dash", "ksh"})
INTERPRETERS = frozenset({"python", "python3", "node", "perl", "ruby", "php", "deno", "bun", "lua"})
INLINE_FLAGS = frozenset({"-c", "-e", "-E", "-p", "--eval", "--command"})
PROTECTED = frozenset({"main", "master", "trunk", "develop", "head"})

DEFAULT_BRANCH = "Changing the repository's default branch is never done automatically."
PROTECTED_DELETE = (
    "Deleting main (or another protected branch) on the remote is never part of cleanup."
)
REWRITES = "rewrites history; cleanup never rewrites published history."
CREDENTIALS = (
    "This can print remote URLs or credentials. Run the plugin's inventory.py: it redacts them."
)
CONTENT = (
    "This prints file contents, which can include secrets committed to the repository. "
    "Audit with --stat, --name-status or --name-only, or exclude secret-like paths with "
    "':(exclude)' pathspecs."
)

GIT_GLOBAL_WITH_VALUE = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"},
)
RISKY_CONFIG = re.compile(
    r"^(alias\.|core\.(sshcommand|pager|editor|fsmonitor|hookspath)|.*helper)"
)

DENY_GIT = {
    "filter-branch": f"git filter-branch {REWRITES}",
    "filter-repo": f"git filter-repo {REWRITES}",
    "credential": "git credential prints stored passwords.",
}
READ_ONLY_GIT = frozenset(
    {
        "status", "log", "diff", "show", "rev-parse", "rev-list", "for-each-ref", "cherry",
        "merge-base", "merge-tree", "range-diff", "ls-files", "ls-tree", "ls-remote",
        "cat-file", "blame", "annotate", "grep", "describe", "shortlog", "count-objects",
        "check-ignore", "diff-tree", "diff-index", "diff-files", "name-rev", "show-ref",
        "show-branch", "var", "version", "help", "whatchanged", "verify-commit",
        "verify-tag", "fsck", "check-ref-format", "get-tar-commit-id",
    },
)  # fmt: skip
PATCH_FLAGS = frozenset(
    {
        "-p", "--patch", "-u", "-c", "--cc", "--patch-with-stat", "--patch-with-raw", "-W",
        "--function-context", "--binary", "--ext-diff",
    },
)  # fmt: skip
PATCH_PREFIXES = ("-L", "-U", "--unified", "--word-diff", "--color-words")
SEARCH_TOOLS = frozenset({"grep", "egrep", "fgrep", "rg", "ag", "sed", "awk"})
SECRET_VARIABLE = re.compile(
    r"\$\{?(?:\w*(?:token|secret|passw|api_?key|credential|private_?key)|(?:\w*_)?pat\b)",
    re.IGNORECASE,
)
ENV_PRINTERS = frozenset({"export", "declare", "typeset", "set", "env"})
WRITE_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})
READ_MCP = re.compile(r"__(get|list|search|read|query|find|fetch|describe|show)_", re.IGNORECASE)
STAT_FLAGS = frozenset(
    {
        "--stat", "--shortstat", "--numstat", "--name-only", "--name-status", "--summary",
        "--check", "--quiet", "-s", "--raw", "--dirstat", "-q",
    },
)  # fmt: skip
GREP_SAFE_FLAGS = frozenset(
    {"-l", "--files-with-matches", "-L", "-c", "--count", "-q", "--quiet", "--name-only"},
)
CAT_FILE_SAFE_FLAGS = frozenset({"-t", "-s", "-e", "--batch-check"})
SAFE_FIRST_ARG = {
    "stash": frozenset({"list", "show"}),
    "worktree": frozenset({"list"}),
    "bisect": frozenset({"log", "view", "visualize"}),
    "submodule": frozenset({"status", "summary"}),
    "bundle": frozenset({"verify", "list-heads"}),
    "notes": frozenset({"list", "show"}),
}
ASK_GIT_REASON = {
    "fetch": "git fetch updates remote-tracking references.",
    "reset": "git reset moves a branch and can discard work.",
    "gc": "git gc prunes unreachable objects.",
    "prune": "git prune deletes unreachable objects.",
}
MUTATING_GIT = frozenset(
    {
        "add", "rm", "mv", "commit", "merge", "rebase", "cherry-pick", "revert", "checkout",
        "switch", "restore", "am", "apply", "pull", "init", "clone", "update-ref",
        "replace", "maintenance", "sparse-checkout", "lfs", "format-patch", "archive",
        "merge-file", "update-index", "repack", "pack-refs", "fetch", "reset", "gc", "prune",
    },
)  # fmt: skip
DRY_RUN_GIT = frozenset({"fetch", "clean", "worktree", "remote", "gc", "prune"})
DRY_RUN_LETTERS = frozenset("nfdqxXvi")

STRONG_SECRET = re.compile(
    (
        r"^(\.env(\..+)?|\.envrc|.+\.(pem|p12|pfx|keystore|jks|kdbx|tfstate|tfvars)"
        r"|id_(rsa|dsa|ecdsa|ed25519)|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd"
        r"|\.vault_pass|\.dockerconfigjson|kubeconfig|\.pgpass|\.my\.cnf)$"
    ),
    re.IGNORECASE,
)
WEAK_SECRET = re.compile(
    (
        r"^(.+\.key|\.secrets?|service-account.*\.json"
        r"|(secrets?|credentials)(\.(json|ya?ml|txt|toml|ini|conf|cfg|xml|properties|env))?)$"
    ),
    re.IGNORECASE,
)
SECRET_EXAMPLE = re.compile(r"\.(example|sample|template|dist|pub)$", re.IGNORECASE)
SECRET_DIRS = frozenset({".ssh", ".aws", ".gnupg", ".docker", ".kube"})
SECRET_PAIRS = frozenset({(".git", "config"), (".config", "gh"), (".config", "gcloud")})
GLOB_SAMPLES = (
    ".env", ".envrc", ".netrc", ".npmrc", "id_rsa", "server.pem", "secrets", "credentials",
)  # fmt: skip
FILE_READERS = frozenset(
    {
        "cat", "head", "tail", "less", "more", "bat", "nl", "tac", "sed", "awk", "grep",
        "egrep", "fgrep", "rg", "ag", "xxd", "od", "hexdump", "strings", "base64", "cp",
        "jq", "source", ".", "view", "vi", "vim", "nano", "sort", "wc", "diff", "cut", "tr",
        "paste", "column", "fold", "rev", "tee", "uniq", "comm",
    },
)  # fmt: skip
FILE_CHANGERS = frozenset(
    {
        "rm", "rmdir", "unlink", "shred", "mv", "truncate", "touch", "cp", "tee", "chmod",
        "chown", "ln", "install", "dd",
    },
)  # fmt: skip
NETWORK_TOOLS = frozenset({"curl", "wget", "http", "https"})
GH_READ = frozenset(
    {
        "view", "list", "status", "diff", "checks", "get", "show", "watch", "browse", "help",
        "search",
    },
)  # fmt: skip
GH_SENSITIVE = frozenset({"secret", "variable", "ssh-key", "gpg-key"})
GH_BODY_FLAGS = frozenset({"-f", "-F", "--field", "--raw-field", "--input"})
GH_GLOBAL_WITH_VALUE = frozenset({"-R", "--repo", "--hostname"})


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


def is_cluster(arg: str, letters: str) -> bool:
    """True for a short-option cluster such as -fd that contains any of the letters."""
    return arg.startswith("-") and not arg.startswith("--") and any(c in arg[1:] for c in letters)


def glob_hits_secret(name: str) -> bool:
    """True when a wildcard pattern could expand to a secret-bearing file name."""
    if not name.strip("*?[]") or not any(char in name for char in "*?["):
        return False
    dotted = name.startswith(".")
    return any(
        fnmatch.fnmatchcase(sample, name)
        for sample in GLOB_SAMPLES
        if sample.startswith(".") == dotted
    )


def is_secret_path(token: str, *, strong_only: bool = False) -> bool:
    """True when a token names a file or folder that usually holds secrets."""
    parts = [part for part in re.split(r"[\\/]", token) if part]
    if any(part in SECRET_DIRS for part in parts[:-1]):
        return True
    if any((parts[i], parts[i + 1]) in SECRET_PAIRS for i in range(len(parts) - 1)):
        return True
    name = parts[-1] if parts else ""
    if SECRET_EXAMPLE.search(name):
        return False
    if STRONG_SECRET.match(name) or glob_hits_secret(name):
        return True
    return not strong_only and bool(WEAK_SECRET.match(name))


def secret_verdict(tokens: list[str], *, strong_only: bool = False) -> Verdict | None:
    """Deny when any token names a secret-bearing file."""
    for token in tokens:
        candidate = token.lstrip("<")
        if (
            candidate
            and not candidate.startswith("-")
            and is_secret_path(candidate, strong_only=strong_only)
        ):
            return DENY, (
                f"'{candidate}' looks like a secret-bearing file; the audit reports its name only "
                "and never reads or prints its contents."
            )
    return None


def git_path_arguments(args: list[str]) -> list[str]:
    """Return the path-like arguments of a git command: after `--` and the part after `rev:`."""
    paths = args[args.index("--") + 1 :] if "--" in args else []
    paths += [arg.split(":", 1)[1] for arg in args if ":" in arg and not arg.startswith(("-", ":"))]
    return paths


SAFE_WITH = {
    **dict.fromkeys(("diff", "diff-tree", "diff-index", "diff-files", "show"), STAT_FLAGS),
    "grep": GREP_SAFE_FLAGS,
    "cat-file": CAT_FILE_SAFE_FLAGS,
}
PATCH_PRINTERS = frozenset({"log", "whatchanged", "reflog"})


def has_patch_flag(args: list[str]) -> bool:
    """True when the arguments ask git to print a patch or file content."""
    return any(arg in PATCH_FLAGS or arg.startswith(PATCH_PREFIXES) for arg in args)


def prints_content(sub: str, args: list[str]) -> bool:
    """True when a read-only git command would print file contents rather than names or stats."""
    if "--no-patch" in args or any(arg.startswith((":(exclude)", ":!", ":^")) for arg in args):
        return False
    if sub in SAFE_WITH:
        return has_patch_flag(args) or SAFE_WITH[sub].isdisjoint(args)
    if sub == "stash":
        return args[:1] == ["show"] and has_patch_flag(args)
    if sub in PATCH_PRINTERS:
        return has_patch_flag(args)
    return sub in {"blame", "annotate"}


def check_push(args: list[str]) -> Verdict | None:
    """Deny force pushes and deleting a protected branch; ask for any other real push."""
    plain = positionals(args)
    forced = (
        any(arg in {"--force", "--mirror", "--force-if-includes"} for arg in args)
        or any(arg.startswith("--force-with-lease") for arg in args)
        or any(is_cluster(arg, "f") for arg in args)
        or any(ref.startswith("+") for ref in plain)
    )
    if forced:
        return DENY, "Force-pushing rewrites published history; cleanup never does that."
    if "--dry-run" in args or "-n" in args:
        return None
    deleting = (
        "--delete" in args
        or any(is_cluster(arg, "d") for arg in args)
        or any(r.startswith(":") for r in plain)
    )
    targets = [ref.lstrip(":").removeprefix("refs/heads/").lower() for ref in plain[1:]]
    if deleting and any(target in PROTECTED for target in targets):
        return DENY, PROTECTED_DELETE
    verb = "deletes a remote branch" if deleting else "changes the remote"
    if "--prune" in args:
        verb = "can delete remote branches (--prune)"
    return ASK, f"git push {verb}."


LISTING_FLAGS = frozenset({"-l", "--list", "--contains", "--merged", "--no-merged", "--points-at"})


def names_without_listing(args: list[str]) -> bool:
    """True when a branch or tag command names something and has no listing option."""
    return bool(positionals(args)) and LISTING_FLAGS.isdisjoint(args)


def check_branch(args: list[str]) -> Verdict | None:
    """Ask for branch deletion, renames and creation; listing passes."""
    changing = {
        "-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy", "-f", "--force",
        "-u", "--edit-description", "--unset-upstream",
    }  # fmt: skip
    if any(arg in changing or arg.startswith("--set-upstream") for arg in args):
        return ASK, "git branch deletes, renames or reconfigures a branch."
    if names_without_listing(args):
        return ASK, "git branch with a name creates a branch."
    return None


def check_tag(args: list[str]) -> Verdict | None:
    """Ask for tag creation and deletion; listing passes."""
    changing = {"-d", "--delete", "-f", "--force", "-a", "-s", "-m"}
    if any(arg in changing for arg in args):
        return ASK, "git tag creates or deletes a tag."
    if names_without_listing(args):
        return ASK, "git tag with a name creates a tag."
    return None


def check_remote(args: list[str]) -> Verdict | None:
    """Deny commands that print remote URLs (they can embed credentials); ask for changes."""
    plain = positionals(args)
    action = plain[0] if plain else ""
    if (
        "--verbose" in args
        or any(is_cluster(arg, "v") for arg in args)
        or action in {"get-url", "show"}
    ):
        return DENY, CREDENTIALS
    changing = {
        "add", "remove", "rm", "rename", "set-url", "set-head", "set-branches", "prune", "update",
    }  # fmt: skip
    if action in changing:
        return ASK, f"git remote {action} changes the repository's remotes."
    return None


def check_config(args: list[str]) -> Verdict | None:
    """Deny config reads that can print credentials; ask for writes."""
    writing = {
        "--unset", "--unset-all", "--add", "--replace-all", "--edit", "-e", "--remove-section",
        "--rename-section",
    }  # fmt: skip
    plain = positionals(args)
    regexp = "--get-regexp" in args
    if any(arg in writing for arg in args) or (len(plain) > 1 and not regexp):
        return ASK, "git config changes the repository's configuration."
    wide = re.compile(r"remote|http|^\.\*?$", re.IGNORECASE)
    named = re.compile(r"url|credential|token|password|extraheader", re.IGNORECASE)
    risky = (
        any(arg in {"-l", "--list"} for arg in args)
        or (regexp and (not plain or any(wide.search(key) for key in plain)))
        or any(named.search(key) for key in plain)
    )
    return (DENY, CREDENTIALS) if risky else None


def check_var(args: list[str]) -> Verdict | None:
    """Deny git var -l, which lists every config value including remote URLs."""
    return (DENY, CREDENTIALS) if "-l" in args else None


def check_clean(args: list[str]) -> Verdict | None:
    """Deny git clean -x/-X (it deletes ignored files such as .env); ask for the rest."""
    if "--dry-run" in args or any(is_cluster(arg, "n") for arg in args):
        return None
    if any(is_cluster(arg, "xX") for arg in args):
        return DENY, (
            "git clean -x/-X deletes ignored files such as .env that no backup holds. "
            "Delete the listed paths explicitly after a git clean -n preview."
        )
    return ASK, "git clean deletes untracked files."


def check_ls_remote(args: list[str]) -> Verdict | None:
    """Deny ls-remote --get-url, which prints the URL with its credentials."""
    return (DENY, CREDENTIALS) if "--get-url" in args else None


def check_symbolic_ref(args: list[str]) -> Verdict | None:
    """Ask when symbolic-ref would write; reading passes."""
    if len(positionals(args)) > 1 or "-d" in args or "--delete" in args:
        return ASK, "git symbolic-ref changes a symbolic reference."
    return None


def check_reflog(args: list[str]) -> Verdict | None:
    """Ask for reflog expire and delete; reading passes."""
    plain = positionals(args)
    if plain and plain[0] in {"expire", "delete"}:
        return ASK, "git reflog expire/delete removes recovery entries."
    return None


SPECIAL_GIT: dict[str, Callable[[list[str]], Verdict | None]] = {
    "push": check_push,
    "branch": check_branch,
    "tag": check_tag,
    "remote": check_remote,
    "config": check_config,
    "clean": check_clean,
    "ls-remote": check_ls_remote,
    "var": check_var,
    "symbolic-ref": check_symbolic_ref,
    "reflog": check_reflog,
}
KNOWN_GIT = READ_ONLY_GIT | MUTATING_GIT


def parse_git(args: list[str]) -> tuple[str, list[str], list[str]]:
    """Split git's arguments into the subcommand, its arguments and the -c settings."""
    configs: list[str] = []
    index = 0
    while index < len(args) and args[index].startswith("-"):
        arg = args[index]
        if arg == "-c" and index + 1 < len(args):
            configs.append(args[index + 1])
        elif arg.startswith("-c") and not arg.startswith("--"):
            configs.append(arg[2:])
        elif arg.startswith("--config-env="):
            configs.append(arg.split("=", 1)[1])
        index += 2 if arg in GIT_GLOBAL_WITH_VALUE else 1
    if index >= len(args):
        return "", [], configs
    return args[index], args[index + 1 :], configs


def dry_run(sub: str, args: list[str]) -> bool:
    """True when the arguments ask for a preview (-n means something else for fetch)."""
    short_n = any(is_cluster(arg, "n") and set(arg[1:]) <= DRY_RUN_LETTERS for arg in args)
    return "--dry-run" in args or (sub != "fetch" and short_n)


def classify_subcommand(sub: str, rest: list[str], *, strict: bool) -> Verdict | None:
    """Return the verdict for a git subcommand and its arguments."""
    if sub in DRY_RUN_GIT and dry_run(sub, rest):
        return None
    if sub in SPECIAL_GIT:
        return SPECIAL_GIT[sub](rest)
    if sub in SAFE_FIRST_ARG:
        first = rest[0] if rest and not rest[0].startswith("-") else ""
        return (
            None
            if first in SAFE_FIRST_ARG[sub]
            else (ASK, f"git {sub} {first} changes repository state.")
        )
    reads_only = sub in READ_ONLY_GIT and not (sub == "fsck" and "--lost-found" in rest)
    if reads_only or (sub not in KNOWN_GIT and not strict):
        return None
    return ASK, ASK_GIT_REASON.get(sub, f"git {sub} can change repository state.")


def inspect_arguments(sub: str, rest: list[str]) -> Verdict | None:
    """Check what a command would print or write: secret paths, file contents, --output."""
    if sub in READ_ONLY_GIT or sub == "stash":
        verdict = secret_verdict(git_path_arguments(rest), strong_only=True)
        if verdict:
            return verdict
    if any(arg.startswith("--output") for arg in rest):
        return ASK, f"git {sub} --output writes a file."
    if prints_content(sub, rest):
        return ASK, CONTENT
    return None


def classify_git(args: list[str], *, strict: bool = True) -> Verdict | None:
    """Return the verdict for one git invocation, or None when it only reads.

    strict is False when git is found away from the start of a command (after a pipe's xargs,
    a loop keyword or a wrapper); an unknown subcommand then passes, because the token may not
    be the git program at all.
    """
    sub, rest, configs = parse_git(args)
    if any(RISKY_CONFIG.match(setting.lower()) for setting in configs):
        return ASK, "git -c sets a configuration that can run another program."
    if not sub:
        return None
    if sub in DENY_GIT:
        return DENY, DENY_GIT[sub]
    return inspect_arguments(sub, rest) or classify_subcommand(sub, rest, strict=strict)


def gh_api_method(args: list[str]) -> str:
    """Return the HTTP method a `gh api` call will use."""
    for index, arg in enumerate(args):
        if arg in {"-X", "--method"} and index + 1 < len(args):
            return args[index + 1].upper()
        if arg.startswith("--method="):
            return arg.split("=", 1)[1].upper()
        if arg.startswith("-X") and arg[2:]:
            return arg[2:].upper()
    body = any(arg.split("=", 1)[0] in GH_BODY_FLAGS or re.match(r"^-[fF].", arg) for arg in args)
    return "POST" if body else "GET"


def check_gh_api(args: list[str]) -> Verdict | None:
    """Deny default-branch changes and deleting main; ask for any other non-GET call."""
    joined = " ".join(args)
    if "graphql" in args:
        return (ASK, "A GraphQL mutation changes GitHub state.") if "mutation" in joined else None
    method = gh_api_method(args)
    if method == "GET":
        return None
    if "default_branch" in joined:
        return DENY, DEFAULT_BRANCH
    if method == "DELETE" and re.search(
        r"(refs/heads|branches)/(main|master|trunk|develop)(?![\w.\-/])", joined, re.IGNORECASE
    ):
        return DENY, PROTECTED_DELETE
    return ASK, f"gh api {method} changes GitHub state."


def strip_gh_globals(args: list[str]) -> list[str]:
    """Drop gh's global -R/--repo/--hostname options and their values."""
    kept: list[str] = []
    skip = False
    for arg in args:
        if skip:
            skip = False
        elif arg in GH_GLOBAL_WITH_VALUE:
            skip = True
        elif not arg.startswith(("--repo=", "--hostname=")):
            kept.append(arg)
    return kept


def classify_gh_auth(action: str, args: list[str]) -> Verdict | None:
    """Deny commands that print a token; ask for account changes."""
    if action == "token" or "--show-token" in args or "-t" in args:
        return DENY, "This prints an authentication token."
    return None if action == "status" else (ASK, "gh auth changes the signed-in account.")


def classify_gh(args: list[str]) -> Verdict | None:
    """Return the verdict for one gh invocation, or None when it only reads."""
    args = strip_gh_globals(args)
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


def is_command_prefix(token: str) -> bool:
    """True for a token that can precede a command: an assignment, keyword, wrapper or option."""
    assignment = "=" in token and "/" not in token.split("=", 1)[0]
    return assignment or token in KEYWORDS or basename(token) in WRAPPERS or token.startswith("-")


def classify_file_change(name: str, rest: list[str]) -> Verdict | None:
    """Ask for commands that delete, move or edit files."""
    if name in FILE_CHANGERS:
        return ASK, f"{name} deletes or moves files."
    if name == "find" and any(arg in {"-delete", "-exec", "-execdir", "-ok"} for arg in rest):
        return ASK, "find with -delete or -exec changes files."
    if name == "sed" and any(arg.startswith("-i") or arg == "--in-place" for arg in rest):
        return ASK, "sed -i edits files in place."
    return None


def classify_runner(name: str, rest: list[str]) -> Verdict | None:
    """Ask for inline interpreter code."""
    for arg in rest:
        if arg in INLINE_FLAGS:
            return (
                ASK,
                f"{name} with inline code can do anything; put it in a file the user can read.",
            )
        if not arg.startswith("-"):
            break
    return None


def reader_arguments(name: str, rest: list[str]) -> list[str]:
    """Return the arguments of a file-reading command that are file names, not patterns."""
    if name not in SEARCH_TOOLS:
        return rest
    kept: list[str] = []
    skip_next = False
    pattern_given = any(arg in {"-e", "--regexp", "-f", "--file"} for arg in rest)
    for arg in rest:
        if skip_next:
            skip_next = False
        elif arg in {"-e", "--regexp"}:
            skip_next = True
        elif not arg.startswith("-") and not pattern_given:
            pattern_given = True
        else:
            kept.append(arg)
    return kept


def classify_other(name: str, rest: list[str]) -> Verdict | None:
    """Return the verdict for commands that are neither git nor gh."""
    if name in {"git-filter-repo", "bfg"}:
        return DENY, f"{name} {REWRITES}"
    if name in FILE_READERS:
        return secret_verdict(reader_arguments(name, rest)) or classify_file_change(name, rest)
    if name in FILE_CHANGERS or name == "find":
        return classify_file_change(name, rest)
    if name in NETWORK_TOOLS:
        return ASK, f"{name} can change GitHub or other services."
    if name in INTERPRETERS:
        return classify_runner(name, rest)
    prints_env = name == "printenv" or (name in ENV_PRINTERS and rest in ([], ["-p"], ["-x"]))
    return (DENY, "This prints the environment, which can hold secrets.") if prints_env else None


def redirect_verdict(segment: list[str]) -> Verdict | None:
    """Ask when the command redirects output into a file other than /dev/null."""
    for index, token in enumerate(segment):
        match = re.match(r"^\d*>>?(?!&)(.*)$", token)
        if not match:
            continue
        target = match.group(1) or (segment[index + 1] if index + 1 < len(segment) else "")
        if target != "/dev/null":
            return ASK, "Output redirection writes a file."
    return None


def classify_segment(segment: list[str]) -> list[Verdict]:
    """Return the verdicts for one command segment: every token may start a command."""
    verdicts: list[Verdict] = []
    variable = next((t for t in segment if SECRET_VARIABLE.search(t)), None)
    if variable:
        verdicts.append(
            (DENY, f"'{variable}' would expose a secret held in an environment variable.")
        )
    redirect = redirect_verdict(segment)
    if redirect:
        verdicts.append(redirect)
    if basename(segment[0]) in {"echo", "printf"}:
        return verdicts
    at_start = True
    for index, token in enumerate(segment):
        name, rest = basename(token), segment[index + 1 :]
        if name == "git":
            found = classify_git(rest, strict=at_start)
        elif name == "gh":
            found = classify_gh(rest)
        else:
            found = classify_other(name, rest)
        if found:
            verdicts.append(found)
        at_start = at_start and is_command_prefix(token)
    return verdicts


def split_segments(command: str) -> list[list[str]]:
    """Split a command line into segments on ; & | ( ) and newlines."""
    command = re.sub(r"&>>?", " > ", command)
    command = re.sub(r"\d*>&\d*-?", " ", command)  # 2>&1 only merges streams
    command = re.sub(r"(?<![<(])<(?![<(])", " < ", command)
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


def decide_tool(tool: str, event: object) -> Verdict | None:
    """Verdict for the non-Bash tools: secret reads, file writes and MCP actions."""
    if tool in {"Read", "Grep"}:
        paths = [text_at(event, "tool_input", key) for key in ("file_path", "path", "glob")]
        return secret_verdict([path for path in paths if path])
    if tool in WRITE_TOOLS or (tool.startswith("mcp__") and not READ_MCP.search(tool)):
        return ASK, f"{tool} may change files or a service; the audit phase is read-only."
    return None


def decide(event: object) -> Verdict | None:
    """Return the single verdict for a hook event: deny beats ask, nothing means no objection."""
    tool = text_at(event, "tool_name")
    if tool != "Bash":
        return decide_tool(tool, event)
    try:
        verdicts = analyze(text_at(event, "tool_input", "command"))
    except ValueError:
        return (
            ASK,
            "git-cleanup could not parse this command, so it cannot tell whether it is safe.",
        )
    return next((found for kind in (DENY, ASK) for found in verdicts if found[0] == kind), None)


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
            "permissionDecisionReason": f"git-cleanup: {reason}{suffix}",
        },
    }
    _ = sys.stdout.write(json.dumps(decision) + "\n")


def main() -> int:
    """Run the hook; any internal error asks instead of letting the call through unchecked."""
    try:
        verdict = decide(_decode(sys.stdin.read()))
    except (ValueError, OSError, RecursionError):
        verdict = ASK, "git-cleanup's guard could not read this tool call."
    if verdict:
        emit(verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
