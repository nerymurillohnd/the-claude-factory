#!/usr/bin/env python3
"""Read-only checker for Claude Code instruction files.

Inventories CLAUDE.md, CLAUDE.local.md, .claude/CLAUDE.md, AGENTS.md and
.claude/rules/**/*.md at project and user scope, then reports deterministic
findings: rule frontmatter problems, path globs that match nothing, imports
that do not resolve, package scripts that do not exist, duplicate lines,
emphasis written for older models, and size limits.

It never edits, executes or uploads anything. It reads the instruction files
of the project, its ancestor directories and the user configuration directory,
the files they import inside those directories (imports elsewhere are only
checked for existence), and package.json files. To check whether
CLAUDE.local.md is git-ignored it runs `git check-ignore` once.
Standard library only, Python 3.12 or later.

Exit codes: 0 no error-level finding, 1 at least one error-level finding,
2 bad arguments.

Loader facts encoded here were checked against
https://code.claude.com/docs/en/memory and the Claude Code changelog through
v2.1.312 (2026-10-28). The glob matcher approximates Claude Code's: treat a
match result as strong evidence and confirm loading in a session with
/context or an InstructionsLoaded hook.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import NoReturn, cast
import warnings

CHECKED_AGAINST = (
    "code.claude.com/docs/en/memory and changelog through Claude Code v2.1.312 (2026-10-28)"
)
# Never instruction or source files Claude Code would scope rules to.
SKIP_DIRS = {".git", "node_modules"}
MAX_WALK_FILES = 300_000
CLAUDE_MD_LINE_TARGET = 200  # documented guidance, not a loader limit
MAX_FILE_BYTES = 4 * 1024 * 1024  # documented for CLAUDE.md files that load at launch
ON_DEMAND_CHAR_LIMIT_200K = 40_000  # per-file limit for on-demand files, 200K window
BRACE_BUDGET = 1_000  # expanded patterns per rule's whole paths list
IMPORT_MAX_HOPS = 4
MIN_DUPLICATE_CHARS = 30
EMPHASIS_THRESHOLD = 3
FOREIGN_SCOPING_KEYS = {"globs", "glob", "include", "files", "applyTo", "alwaysApply"}
KNOWN_FOREIGN_KEYS = {
    "globs": "Cursor-style key",
    "glob": "Cursor-style key",
    "include": "generator key",
    "files": "generator key",
    "alwaysApply": "Cursor-style key",
    "applyTo": "Copilot-style key",
    "description": "skill/agent key",
    "name": "skill/agent key",
    "priority": "invented key",
    "tools": "agent key",
    "model": "agent key",
}
YAML_DQ_ESCAPES = set('0abt\tnvfre "/\\N_LPxuU')
EMPHASIS_RE = re.compile(r"\b(IMPORTANT|CRITICAL|MUST|NEVER|ALWAYS|MANDATORY|REQUIRED)\b|!!+")
NUDGE_RE = re.compile(
    (
        r"\b(think (step[- ]by[- ]step|hard|harder|carefully)|be thorough|don'?t be lazy"
        r"|take a deep breath)\b"
    ),
    re.IGNORECASE,
)
PM_COMMAND_RE = re.compile(r"(?:^|[\s;&|(`])(npm|pnpm|yarn|bun)\s+(run\s+)?([A-Za-z0-9:_.@/\-]+)")
SHELL_FENCES = {"", "bash", "sh", "shell", "zsh", "console", "shell-session", "terminal"}
NPM_BUILTINS = frozenset(
    [
        "install",
        "i",
        "ci",
        "add",
        "remove",
        "rm",
        "uninstall",
        "update",
        "up",
        "upgrade",
        "exec",
        "x",
        "create",
        "init",
        "publish",
        "link",
        "unlink",
        "outdated",
        "audit",
        "why",
        "list",
        "ls",
        "view",
        "info",
        "pack",
        "version",
        "config",
        "set",
        "get",
        "login",
        "logout",
        "whoami",
        "cache",
        "rebuild",
        "prune",
        "dedupe",
        "help",
        "fund",
        "doctor",
        "start",
        "test",
        "t",
        "restart",
        "stop",
        "run",
        "run-script",
        "explain",
        "query",
        "pkg",
        "sbom",
        "search",
        "ping",
        "owner",
        "access",
        "deprecate",
        "dist-tag",
        "edit",
        "explore",
        "diff",
        "bugs",
        "docs",
        "repo",
        "root",
        "prefix",
        "bin",
        "token",
        "team",
        "star",
        "stars",
        "unstar",
        "shrinkwrap",
    ]
)
OTHER_PM_BUILTINS = NPM_BUILTINS | frozenset(
    [
        "dlx",
        "store",
        "import",
        "patch",
        "patch-commit",
        "workspace",
        "workspaces",
        "recursive",
        "-r",
        "--filter",
        "-w",
        "-C",
        "--dir",
        "env",
        "setup",
        "self-update",
        "licenses",
        "fetch",
        "deploy",
        "plugin",
        "constraints",
        "dedupe",
        "node",
        "set",
        "global",
        "upgrade-interactive",
        "x",
        "pm",
        "create",
    ]
)
BACKUP_DIR_NAMES = {"backup", "backups", "old", "archive", "deprecated", "_old"}
BACKUP_NAME_RE = re.compile(r"(\.bak|\.old|[-_.](old|backup|copy))\.md$", re.IGNORECASE)
IMPORT_RE = re.compile(r"(?:^|(?<=\s))@((?:\\ |[^\s`\"'])+)")


@dataclass
class Finding:
    """One deterministic finding about an instruction file."""

    severity: str  # error | warning | info
    code: str
    path: str
    message: str
    line: int | None = None

    def as_dict(self) -> dict[str, str | int]:
        """Return the finding without empty fields."""
        out: dict[str, str | int] = {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
        }
        if self.line is not None:
            out["line"] = self.line
        return out


@dataclass
class InstructionFile:
    """A discovered instruction file and what is known about its loading."""

    path: Path
    # user-claude-md, user-rule, ancestor, project-root, project-local, nested, *-rule, agents-md
    kind: str
    loads: str  # launch, on-demand, conditional, not-by-default
    lines: int = 0
    chars: int = 0
    sha256: str = ""
    paths: list[str] | None = None
    text: str = ""
    imports: list[str] = field(default_factory=list[str])

    def as_dict(self) -> dict[str, str | int | list[str]]:
        """Return the inventory row."""
        out: dict[str, str | int | list[str]] = {
            "path": str(self.path),
            "kind": self.kind,
            "loads": self.loads,
            "lines": self.lines,
            "chars": self.chars,
        }
        if self.paths is not None:
            out["paths"] = self.paths
        if self.imports:
            out["imports"] = self.imports
        return out


@dataclass
class Context:
    """What every check needs to know about the session being simulated."""

    project: Path
    user_dir: Path | None  # None when user scope is skipped
    # The user configuration directory, excluded from ancestor discovery either way.
    config_dir: Path
    all_rel: list[str]
    findings: list[Finding]


class JsonObject(dict[str, object]):
    """A decoded JSON object; used as object_pairs_hook so keys stay typed."""


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    project: Path = Path()
    user_dir: Path | None = None
    no_user: bool = False
    match: list[str] | None = None
    json: bool = False


# ---------------------------------------------------------------------------
# Glob matching (approximation of Claude Code's matcher)
# ---------------------------------------------------------------------------


def split_top_level_commas(body: str) -> list[str]:
    """Split on commas that are not inside braces or escaped."""
    parts: list[str] = []
    depth = 0
    cur = ""
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            cur += body[i : i + 2]
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    parts.append(cur)
    return parts


def find_brace_group(pattern: str) -> tuple[int, int] | None:
    """Return the span of the first top-level, unescaped {...} group with a comma."""
    depth = 0
    start = -1
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and len(split_top_level_commas(pattern[start + 1 : i])) > 1:
                return start, i
        i += 1
    return None


def expand_braces(pattern: str, limit: int) -> list[str] | None:
    """Expand {a,b} groups combinatorially; None once more than `limit` patterns would result.

    Escaped braces stay literal. Stopping at the limit keeps a hostile pattern such as
    '{a,b}' repeated 30 times from building a billion strings before the budget is checked.
    """
    span = find_brace_group(pattern)
    if span is None:
        return [pattern] if limit >= 1 else None
    start, end = span
    out: list[str] = []
    for part in split_top_level_commas(pattern[start + 1 : end]):
        sub = expand_braces(pattern[:start] + part + pattern[end + 1 :], limit - len(out))
        if sub is None:
            return None
        out.extend(sub)
    return out


def bracket_is_valid(pattern: str) -> bool:
    """Every unescaped '[' must close with ']' inside the same path segment."""
    i = 0
    while i < len(pattern):
        if pattern[i] == "\\":
            i += 2
            continue
        if pattern[i] == "[":
            j = i + 1
            if j < len(pattern) and pattern[j] in "!^":
                j += 1
            if j < len(pattern) and pattern[j] == "]":
                j += 1
            while j < len(pattern) and pattern[j] not in "]/":
                j += 1
            if j >= len(pattern) or pattern[j] == "/":
                return False
            i = j
        i += 1
    return True


@dataclass(frozen=True)
class Token:
    """One step of a compiled glob: a literal, one character, '*', '**/' or a trailing '**'."""

    kind: str  # lit | one | star | segs | any
    text: str = ""
    cls: re.Pattern[str] | None = None  # the single-character class of a 'one' token


ONE_CHAR = re.compile(r"[^/]")


def star_token(pattern: str, i: int) -> tuple[Token, int]:
    """Read '*' or '**' at index i: '**' alone in its segment spans directories."""
    n = len(pattern)
    if i + 1 < n and pattern[i + 1] == "*":
        at_segment_start = i == 0 or pattern[i - 1] == "/"
        after = i + 2
        if at_segment_start and after == n:
            return Token("any"), after
        if at_segment_start and pattern[after] == "/":
            return Token("segs"), after + 1
    return Token("star"), i + 1


def bracket_token(pattern: str, i: int) -> tuple[Token, int]:
    """Read a bracket expression at index i; an unclosed '[' is a literal."""
    n = len(pattern)
    j = i + 1
    negate = j < n and pattern[j] in "!^"
    if negate:
        j += 1
    k = j + 1 if j < n and pattern[j] == "]" else j
    while k < n and pattern[k] != "]":
        k += 1
    if k >= n:
        return Token("lit", "["), i + 1
    body = pattern[j:k].replace("\\", "\\\\")
    with warnings.catch_warnings():  # '[[' or '--' in a class is literal; re warns about it
        warnings.simplefilter("ignore", FutureWarning)
        cls = re.compile("[" + ("^" if negate else "") + body + "]")  # re.error: e.g. '[z-a]'
    return Token("one", cls=cls), k + 1


def glob_tokens(pattern: str) -> tuple[Token, ...]:
    """Compile one brace-free glob into tokens."""
    tokens: list[Token] = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "\\" and i + 1 < len(pattern):
            tokens.append(Token("lit", pattern[i + 1]))
            i += 2
        elif ch == "*":
            token, i = star_token(pattern, i)
            tokens.append(token)
        elif ch == "?":
            tokens.append(Token("one", cls=ONE_CHAR))
            i += 1
        elif ch == "[":
            token, i = bracket_token(pattern, i)
            tokens.append(token)
        else:
            tokens.append(Token("lit", ch))
            i += 1
    return tuple(tokens)


State = tuple[int, int]  # (token index, 1 while inside a segment that '**/' is consuming)


def epsilon_closure(tokens: tuple[Token, ...], states: set[State]) -> set[State]:
    """Add every state reachable without reading a character: skipping '*', '**/' and '**'."""
    out = set(states)
    stack = list(states)
    while stack:
        k, inside = stack.pop()
        if k == len(tokens):
            continue
        kind = tokens[k].kind
        if kind in ("star", "any") or (kind == "segs" and not inside):
            nxt = (k + 1, 0)
            if nxt not in out:
                out.add(nxt)
                stack.append(nxt)
    return out


def step(token: Token, state: State, ch: str) -> State | None:
    """The state after reading one character, or None when the token cannot take it."""
    k, inside = state
    kind = token.kind
    if kind == "lit":
        return (k + 1, 0) if ch == token.text else None
    if kind == "one":
        return (k + 1, 0) if token.cls is not None and token.cls.fullmatch(ch) else None
    if kind == "star":
        return (k, 0) if ch != "/" else None
    if kind == "any":
        return (k, 0) if ch != "\n" else None
    if ch != "/":  # segs: a non-empty directory name ...
        return (k, 1)
    return (k, 0) if inside else None  # ... ended by '/'


@dataclass(frozen=True)
class Glob:
    """A brace-free glob matched in time linear in path length times pattern length.

    It matches what the anchored regex '^...$' of the same glob would ('*' within a segment,
    '**/' as zero or more directories, a trailing '**' as anything), without the backtracking
    that lets a pattern such as '*a*a*a...b' run for minutes.
    """

    tokens: tuple[Token, ...]

    def match(self, path: str) -> bool:
        """True when the whole path matches."""
        states = epsilon_closure(self.tokens, {(0, 0)})
        for ch in path:
            moved = {
                nxt
                for state in states
                if state[0] < len(self.tokens)
                and (nxt := step(self.tokens[state[0]], state, ch)) is not None
            }
            if not moved:
                return False
            states = epsilon_closure(self.tokens, moved)
        return (len(self.tokens), 0) in states


def compile_glob(pattern: str) -> Glob:
    """Compile one brace-free glob."""
    return Glob(glob_tokens(pattern))


@dataclass
class CompiledPattern:
    """One `paths` pattern after brace expansion."""

    pattern: str
    globs: list[Glob]
    invalid: bool = False  # a '[' that is not a bracket expression: it matches nothing
    over_budget: bool = False  # past the rule's brace budget: used unexpanded, matches nothing

    def matches(self, rel: str) -> bool:
        """True when any expansion matches the relative path."""
        return any(g.match(rel) for g in self.globs)


def compile_expansions(expanded: list[str]) -> list[Glob] | None:
    """Compile every expansion of a pattern; None when a bracket expression is invalid."""
    if not all(bracket_is_valid(x) for x in expanded):
        return None
    try:
        return [compile_glob(x) for x in expanded]
    except re.error:  # a class re rejects, such as '[z-a]'
        return None


def compile_paths(patterns: list[str]) -> list[CompiledPattern]:
    """Compile a rule's patterns, sharing one brace budget across the whole `paths` list."""
    left = BRACE_BUDGET
    out: list[CompiledPattern] = []
    for pat in patterns:
        if "{" not in pat:
            expanded: list[str] | None = [pat]
        else:
            expanded = expand_braces(pat, left) if left > 0 else None
            if expanded is None:
                left = 0
                out.append(CompiledPattern(pat, [], over_budget=True))
                continue
            left -= len(expanded)
        globs = compile_expansions(expanded)
        out.append(CompiledPattern(pat, globs or [], invalid=globs is None))
    return out


# ---------------------------------------------------------------------------
# Frontmatter: strict subset parser for what a rule can meaningfully hold
# ---------------------------------------------------------------------------


class FrontmatterError(Exception):
    """The frontmatter is not valid YAML: Claude Code would ignore it."""


class UnsupportedYamlError(Exception):
    """Valid or possibly valid YAML that this subset parser does not interpret."""


def split_quoted(s: str, lineno: int) -> tuple[str, str]:
    """Split a value that starts with a quote into (quoted token, rest)."""
    quote = s[0]
    i = 1
    while i < len(s):
        if quote == '"' and s[i] == "\\":
            i += 2
            continue
        if s[i] == quote:
            if quote == "'" and i + 1 < len(s) and s[i + 1] == "'":
                i += 2
                continue
            return s[: i + 1], s[i + 1 :]
        i += 1
    kind = "double" if quote == '"' else "single"
    msg = f"line {lineno}: unterminated {kind}-quoted string"
    raise FrontmatterError(msg)


def unescape_double_quoted(body: str, lineno: int) -> str:
    """Validate YAML double-quoted escapes; return the text with the simple ones resolved."""
    simple = {'"': '"', "\\": "\\", "/": "/", "t": "\t", "n": "\n", " ": " "}
    out = ""
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\":
            nxt = body[i + 1] if i + 1 < len(body) else ""
            if not nxt or nxt not in YAML_DQ_ESCAPES:
                msg = (
                    f"line {lineno}: '\\{nxt}' is not a valid escape inside double quotes in YAML; "
                    "put a glob that escapes '[' or '{' in single quotes instead"
                )
                raise FrontmatterError(msg)
            out += simple.get(nxt, "\\" + nxt)
            i += 2
            continue
        out += ch
        i += 1
    return out


UNQUOTED_INDICATORS = {
    "*": "an alias",
    "@": "a reserved indicator",
    "`": "a reserved indicator",
    "%": "a directive indicator",
    "!": "a tag",
}
BLOCK_SCALAR_RE = re.compile(r"^[|>][-+0-9]*(\s+#.*)?$")
KEY_LINE_RE = re.compile(r"^([A-Za-z_][\w.\-]*)\s*:(?:\s+(.*))?$")


def parse_quoted_scalar(s: str, lineno: int) -> str:
    """Parse a scalar that starts with a quote; only a comment may follow it."""
    token, rest = split_quoted(s, lineno)
    rest = rest.strip()
    if rest and not rest.startswith("#"):
        msg = f"line {lineno}: unexpected text {rest!r} after a quoted string"
        raise FrontmatterError(msg)
    if token[0] == '"':
        return unescape_double_quoted(token[1:-1], lineno)
    return token[1:-1].replace("''", "'")


def reject_plain_indicator(s: str, lineno: int) -> None:
    """Raise when an unquoted scalar starts with a character YAML reads as syntax."""
    first = s[0]
    if first in UNQUOTED_INDICATORS:
        msg = (
            f"line {lineno}: unquoted value starts with '{first}', "
            f"which YAML reads as {UNQUOTED_INDICATORS[first]}"
        )
        raise FrontmatterError(msg)
    if first == "{":
        msg = f"line {lineno}: unquoted value starts with '{{', which YAML reads as a mapping"
        raise FrontmatterError(msg)
    if first in "&[|>":
        msg = f"line {lineno}: value starts with '{first}'"
        raise UnsupportedYamlError(msg)


def parse_scalar(raw: str, lineno: int) -> str:
    """Parse one inline scalar value, rejecting what YAML would read as syntax."""
    s = raw.strip()
    if not s:
        return ""
    if s[0] in "\"'":
        return parse_quoted_scalar(s, lineno)
    reject_plain_indicator(s, lineno)
    if " #" in s:
        s = s.split(" #", 1)[0].rstrip()
    if ": " in s or s.endswith(":"):
        msg = f"line {lineno}: unquoted value contains ': ', which YAML reads as a mapping"
        raise FrontmatterError(msg)
    return s


def flow_list_items(s: str, lineno: int) -> tuple[list[str], str]:
    """Split a one-line flow list that starts with '[' into raw items and the text after ']'."""
    items: list[str] = []
    cur = ""
    quote = ""
    i = 1
    while i < len(s):
        ch = s[i]
        if quote:
            step = 2 if ch == "\\" and quote == '"' and i + 1 < len(s) else 1
            cur += s[i : i + step]
            if step == 1 and ch == quote:
                quote = ""
            i += step
            continue
        if ch == "]":
            items.append(cur)
            return items, s[i + 1 :]
        if ch in "[{":
            msg = f"line {lineno}: an unquoted '{ch}' inside [ ] is YAML syntax; quote each glob"
            raise FrontmatterError(msg)
        if ch in "\"'":
            quote = ch
        if ch == ",":
            items.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    msg = f"line {lineno}: flow list opened with '[' but never closed on this line"
    raise FrontmatterError(msg)


def parse_flow_list(raw: str, lineno: int) -> list[str]:
    """Parse ["a", "b"] with an optional trailing comment."""
    items, rest = flow_list_items(raw.strip(), lineno)
    rest = rest.strip()
    if rest and not rest.startswith("#"):
        msg = f"line {lineno}: unexpected text {rest!r} after a flow list"
        raise FrontmatterError(msg)
    return [parse_scalar(item, lineno) for item in items if item.strip()]


def empty_frontmatter() -> dict[str, str | list[str]]:
    """A new, empty frontmatter mapping."""
    return {}


@dataclass
class FrontmatterState:
    """What parse_frontmatter has read so far."""

    data: dict[str, str | list[str]] = field(default_factory=empty_frontmatter)
    current_key: str | None = None  # the key whose block list is open
    block_scalar_key: str | None = None  # the key whose | or > scalar is open


def continue_block_scalar(state: FrontmatterState, stripped: str, indent: int) -> bool:
    """Append a line to an open block scalar; return False once the scalar has ended."""
    key = state.block_scalar_key
    if key is None:
        return False
    if not stripped or indent > 0:
        state.data[key] = (str(state.data[key]) + "\n" + stripped).strip()
        return True
    state.block_scalar_key = None
    return False


def add_list_item(state: FrontmatterState, stripped: str, lineno: int) -> None:
    """Append a '- item' line to the open block list."""
    target = state.data.get(state.current_key) if state.current_key is not None else None
    if not isinstance(target, list):
        msg = f"line {lineno}: list item outside a list"
        raise FrontmatterError(msg)
    target.append(parse_scalar(stripped[1:], lineno))


def reject_indented(state: FrontmatterState, lineno: int) -> NoReturn:
    """Raise for an indented line that is neither a list item nor block-scalar text."""
    if state.current_key is None:
        msg = f"line {lineno}: unexpected indentation"
        raise FrontmatterError(msg)
    msg = f"line {lineno}: nested mapping under '{state.current_key}'"
    raise UnsupportedYamlError(msg)


def add_key(state: FrontmatterState, line: str, stripped: str, lineno: int) -> None:
    """Read a top-level `key: value` line."""
    m = KEY_LINE_RE.match(line.rstrip())
    if not m:
        msg = f"line {lineno}: expected 'key: value', got {stripped!r}"
        raise FrontmatterError(msg)
    key, value = m.group(1), (m.group(2) or "").strip()
    if key in state.data:
        msg = f"line {lineno}: duplicate key '{key}'"
        raise UnsupportedYamlError(msg)
    state.current_key = None
    if not value or value.startswith("#"):
        state.data[key] = []
        state.current_key = key
    elif value.startswith("["):
        state.data[key] = parse_flow_list(value, lineno)
    elif BLOCK_SCALAR_RE.match(value):
        state.data[key] = ""
        state.block_scalar_key = key
    else:
        state.data[key] = parse_scalar(value, lineno)


def parse_frontmatter(block: list[str], first_lineno: int) -> dict[str, str | list[str]]:
    """Parse top-level `key: value` pairs, block lists, flow lists and block scalars.

    Raise FrontmatterError for what YAML rejects, UnsupportedYamlError for valid
    constructs this subset does not interpret (nested maps, anchors, duplicate keys).
    """
    state = FrontmatterState()
    for offset, line in enumerate(block):
        lineno = first_lineno + offset
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if continue_block_scalar(state, stripped, indent):
            continue
        if "\t" in line[: len(line) - len(line.lstrip())]:
            msg = f"line {lineno}: tab indentation is not valid YAML"
            raise FrontmatterError(msg)
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") or stripped == "-":
            add_list_item(state, stripped, lineno)
        elif indent > 0:
            reject_indented(state, lineno)
        else:
            add_key(state, line, stripped, lineno)
    return state.data


def split_frontmatter(text: str) -> tuple[list[str] | None, str | None]:
    """Return (frontmatter lines, error). Lines are None when there is no frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None, None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return lines[1:i], None
    return None, "frontmatter opened with '---' but never closed"


def paths_from_value(value: str | list[str]) -> list[str]:
    """Normalize a YAML list or a comma-separated string into patterns."""
    if isinstance(value, list):
        return [v.strip() for v in value if v.strip()]
    return [p.strip() for p in split_top_level_commas(value) if p.strip()]


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def walk_files(root: Path, findings: list[Finding]) -> list[Path]:
    """List files under root, skipping .git, node_modules and Claude worktrees."""
    files: list[Path] = []
    worktrees = root / ".claude" / "worktrees"
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and Path(base) / d != worktrees)
        for name in names:
            files.append(Path(base) / name)
            if len(files) >= MAX_WALK_FILES:
                msg = (
                    f"stopped listing files at {MAX_WALK_FILES}; "
                    "glob and nested-file results may be incomplete"
                )
                findings.append(Finding("info", "walk-truncated", str(root), msg))
                return files
    return files


def rule_files(rules_dir: Path) -> list[Path]:
    """Every .md under a rules directory, following symlinked directories with loop protection."""
    out: list[Path] = []
    seen: set[str] = set()
    for base, dirs, names in os.walk(rules_dir, followlinks=True):
        real = os.path.realpath(base)
        if real in seen:
            dirs[:] = []
            continue
        seen.add(real)
        dirs.sort()
        out.extend(Path(base) / n for n in sorted(names) if n.endswith(".md"))
    return out


def rules_base(rule: Path) -> Path:
    """Return the directory that contains the rule's .claude folder."""
    cur = rule.parent
    while cur.name != ".claude" and cur != cur.parent:
        cur = cur.parent
    return cur.parent


@dataclass
class Discovery:
    """Instruction files found so far, keyed by resolved path in discovery order."""

    ctx: Context
    found: dict[Path, InstructionFile] = field(default_factory=dict[Path, InstructionFile])

    def add(self, path: Path, kind: str, loads: str) -> None:
        """Record a file once; the user configuration directory is never a project file."""
        if not path.is_file() or path.resolve() in self.found:
            return
        config_real = self.ctx.config_dir.resolve()
        if path.parent.resolve() == config_real or path.resolve().parent == config_real:
            return
        self.found[path.resolve()] = InstructionFile(path=path, kind=kind, loads=loads)


def discover_user(d: Discovery, user_dir: Path) -> None:
    """User CLAUDE.md and user rules, which load at launch in every project."""
    user_md = user_dir / "CLAUDE.md"
    if user_md.is_file():
        d.found[user_md.resolve()] = InstructionFile(
            path=user_md, kind="user-claude-md", loads="launch"
        )
        if user_md.is_symlink():
            msg = (
                "a symlink; Cowork desktop sessions skip a symlinked or hard-linked "
                "~/.claude/CLAUDE.md"
            )
            d.ctx.findings.append(Finding("info", "user-claude-md-symlink", str(user_md), msg))
    if (user_dir / "rules").is_dir():
        for p in rule_files(user_dir / "rules"):
            _ = d.found.setdefault(
                p.resolve(), InstructionFile(path=p, kind="user-rule", loads="launch")
            )


def discover_ancestors(d: Discovery) -> None:
    """CLAUDE.md, AGENTS.md and rules of every directory above the project."""
    user_rules = (d.ctx.config_dir.resolve() / "rules").resolve()
    for parent in reversed(d.ctx.project.parents):
        for rel in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md"):
            d.add(parent / rel, "ancestor", "launch")
        for rel in ("AGENTS.md", ".claude/AGENTS.md"):
            d.add(parent / rel, "agents-md", "depends")
        ancestor_rules = parent / ".claude" / "rules"
        if ancestor_rules.is_dir() and ancestor_rules.resolve() != user_rules:
            for p in rule_files(ancestor_rules):
                d.add(p, "ancestor-rule", "launch")


def rules_dir_index(parts: tuple[str, ...]) -> int | None:
    """Index of the '.claude' part of a '.claude/rules' pair in a relative path, if any."""
    return next(
        (i for i in range(len(parts) - 1) if parts[i : i + 2] == (".claude", "rules")), None
    )


def is_nested_claude_md(p: Path, parts: tuple[str, ...]) -> bool:
    """A CLAUDE.md or CLAUDE.local.md below the project root, other than .claude/CLAUDE.md."""
    return (
        p.name in ("CLAUDE.md", "CLAUDE.local.md")
        and len(parts) > 1
        and parts[:2] != (".claude", "CLAUDE.md")
    )


def is_nested_agents_md(p: Path, parts: tuple[str, ...]) -> bool:
    """A subdirectory AGENTS.md with no CLAUDE.md beside it."""
    return (
        p.name == "AGENTS.md"
        and len(parts) > 1
        and parts[0] != ".claude"
        and not any((p.parent / n).is_file() for n in ("CLAUDE.md", "CLAUDE.local.md"))
    )


def scan_project_files(d: Discovery, all_files: list[Path]) -> set[Path]:
    """Record nested CLAUDE.md and AGENTS.md files; return the rules directories found."""
    project = d.ctx.project
    rules_dirs: set[Path] = {project / ".claude" / "rules"}
    for p in all_files:
        parts = p.relative_to(project).parts
        rule_at = rules_dir_index(parts)
        if rule_at is not None:
            rules_dirs.add(project.joinpath(*parts[: rule_at + 2]))
        elif is_nested_claude_md(p, parts):
            d.add(p, "nested", "on-demand")
        elif is_nested_agents_md(p, parts):
            d.add(p, "nested-agents-md", "on-demand")
    rules_dirs.update(  # symlinked rules directories are not walked above
        p.parent
        for p in all_files
        if p.is_symlink() and p.parent.name == "rules" and p.parent.parent.name == ".claude"
    )
    rules_dirs.update(p.parent for p in all_files if p.parent.name == "rules")
    return rules_dirs


def discover_rules(d: Discovery, rules_dirs: set[Path]) -> None:
    """Rules of the project (launch) and of its subdirectories (on demand)."""
    project = d.ctx.project
    for rules_dir in sorted(rules_dirs):
        if rules_dir.parent.name != ".claude" or not rules_dir.is_dir():
            continue
        top = rules_dir.parent.parent == project
        for p in rule_files(rules_dir):
            d.add(p, "project-rule" if top else "nested-rule", "launch" if top else "on-demand")
            if p.resolve() in d.found and not is_within(p, project):
                msg = (
                    "resolves outside the project through a symlink: it loads only after the "
                    "one-time external-import approval, and then only if it has no `paths`"
                )
                d.ctx.findings.append(Finding("info", "rule-symlink-external", str(p), msg))


def discover(ctx: Context, all_files: list[Path]) -> list[InstructionFile]:
    """Find instruction files the way Claude Code would discover them."""
    d = Discovery(ctx)
    if ctx.user_dir is not None:
        discover_user(d, ctx.user_dir)
    discover_ancestors(d)
    d.add(ctx.project / "CLAUDE.md", "project-root", "launch")
    d.add(ctx.project / ".claude" / "CLAUDE.md", "project-root", "launch")
    d.add(ctx.project / "CLAUDE.local.md", "project-local", "launch")
    d.add(ctx.project / "AGENTS.md", "agents-md", "depends")
    d.add(ctx.project / ".claude" / "AGENTS.md", "agents-md", "depends")
    discover_rules(d, scan_project_files(d, all_files))
    return list(d.found.values())


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def read_text(path: Path, findings: list[Finding], *, launch_claude_md: bool = False) -> str | None:
    """Read a UTF-8 instruction file."""
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            if launch_claude_md:
                msg = "over 4 MiB; Claude Code skips the whole file"
                findings.append(Finding("error", "over-4mib", str(path), msg))
            else:
                msg = (
                    "over 4 MiB; the docs state the skip only for CLAUDE.md loaded at launch, "
                    "so treat as unverified"
                )
                findings.append(Finding("warning", "over-4mib", str(path), msg))
            return None
        return path.read_bytes().decode("utf-8-sig")
    except OSError as exc:
        findings.append(Finding("error", "unreadable", str(path), f"cannot read: {exc}"))
    except UnicodeDecodeError:
        findings.append(Finding("error", "not-utf8", str(path), "not valid UTF-8"))
    return None


def strip_html_comments(text: str) -> str:
    """Drop block-level HTML comments, which Claude Code strips before injection."""
    return re.sub(r"(?m)^[ \t]*<!--.*?-->[ \t]*$", "", text, flags=re.DOTALL)


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Return (line number, line) outside fenced blocks, with inline code removed."""
    out: list[tuple[int, str]] = []
    fence = ""
    for i, line in enumerate(text.splitlines(), 1):
        s = line.lstrip()
        if fence:
            if s.startswith(fence):
                fence = ""
            continue
        if s.startswith(("```", "~~~")):
            fence = s[:3]
            continue
        out.append((i, re.sub(r"`[^`]*`", "", line)))
    return out


def command_snippets(text: str) -> list[tuple[int, str]]:
    """Return (line number, text) for inline code spans and lines inside shell code fences."""
    out: list[tuple[int, str]] = []
    fence = ""
    fence_lang = ""
    for i, line in enumerate(text.splitlines(), 1):
        s = line.lstrip()
        if fence:
            if s.startswith(fence):
                fence = ""
            elif fence_lang in SHELL_FENCES:
                out.append((i, s.removeprefix("$ ")))
            continue
        if s.startswith(("```", "~~~")):
            fence = s[:3]
            fence_lang = s[3:].strip().split(" ")[0].lower()
            continue
        out.extend((i, m.group(1)) for m in re.finditer(r"`([^`]+)`", line))
    return out


def find_imports(text: str) -> list[tuple[int, str]]:
    """Find @path imports outside code spans and fences."""
    found: list[tuple[int, str]] = []
    for lineno, line in prose_lines(strip_html_comments(text)):
        for m in IMPORT_RE.finditer(line):
            target = m.group(1).rstrip(".,;:)")
            if (
                "/" not in target and "." not in target and target != "README"
            ) or target.startswith("http"):
                continue  # @team mentions and URLs are not imports worth checking
            found.append((lineno, target.replace("\\ ", " ")))
    return found


def resolve_import(base_file: Path, target: str) -> Path:
    """Resolve an import the way Claude Code does: relative to the importing file."""
    if target.startswith("~/"):
        return Path.home() / target[2:]
    p = Path(target)
    return p if p.is_absolute() else base_file.parent / p


def is_within(path: Path, root: Path) -> bool:
    """True when path resolves inside root."""
    try:
        _ = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


@dataclass
class ImportWalk:
    """State of one recursive import check."""

    root: InstructionFile
    seen: set[Path]
    total_lines: int = 0


def note_external_import(
    ctx: Context, walk: ImportWalk, where: tuple[Path, int], target: str, *, inside_project: bool
) -> None:
    """Explain what happens to an import that resolves outside the project."""
    if inside_project:
        return
    path, lineno = where
    if walk.root.kind.startswith("user"):
        msg = (
            f"@{target} resolves outside the working directory; "
            "Cowork desktop sessions skip such imports"
        )
        ctx.findings.append(Finding("info", "import-skipped-in-cowork", str(path), msg, lineno))
    else:
        msg = (
            f"@{target} resolves outside the project; Claude Code asks once per project to "
            "approve external imports, and declining disables them"
        )
        ctx.findings.append(Finding("info", "import-external", str(path), msg, lineno))


def read_import(ctx: Context, walk: ImportWalk, dest: Path) -> str | None:
    """Read an imported file once, count its lines and check the on-demand limit."""
    walk.seen.add(dest.resolve())
    sub_text = read_text(dest, ctx.findings)
    if sub_text is None:
        return None
    walk.total_lines += len(sub_text.splitlines())
    if (
        walk.root.loads in ("on-demand", "conditional")
        and len(sub_text) > ON_DEMAND_CHAR_LIMIT_200K
    ):
        msg = (
            f"{len(sub_text)} characters, imported by a file that loads on demand; such imports "
            "are cut at 40,000 characters on a 200K context window "
            "(150,000 on current 1M-window models)"
        )
        ctx.findings.append(Finding("warning", "on-demand-over-limit", str(dest), msg))
    return sub_text


def check_imports(ctx: Context, walk: ImportWalk, path: Path, text: str, hop: int = 1) -> None:
    """Validate imports recursively; count imported lines into walk.total_lines.

    Files outside the project and the user configuration directory are only
    checked for existence, never read.
    """
    for lineno, target in find_imports(text):
        dest = resolve_import(path, target)
        if not dest.exists():
            msg = f"@{target} does not resolve ({dest}); the import loads nothing"
            ctx.findings.append(Finding("error", "import-missing", str(path), msg, lineno))
            continue
        if hop > IMPORT_MAX_HOPS:
            msg = (
                f"@{target} is import hop {hop}; the docs allow at most four hops, "
                "so it does not load"
            )
            ctx.findings.append(Finding("warning", "import-depth", str(path), msg, lineno))
            continue
        inside_project = is_within(dest, ctx.project)
        note_external_import(ctx, walk, (path, lineno), target, inside_project=inside_project)
        readable = inside_project or is_within(dest, ctx.config_dir)
        if dest.resolve() in walk.seen or not dest.is_file() or not readable:
            continue
        sub_text = read_import(ctx, walk, dest)
        if sub_text is not None:
            check_imports(ctx, walk, dest, sub_text, hop + 1)


@dataclass
class RuleScope:
    """The files a rule's patterns are tested against, relative to the rule's base."""

    base: Path
    rel_files: list[str]
    ancestor: bool = False  # a rule above the project: only the project's files were listed


def rule_frontmatter(
    f: InstructionFile, findings: list[Finding]
) -> dict[str, str | list[str]] | None:
    """Parse a rule's frontmatter, reporting what makes it invalid or unreadable here."""
    where = str(f.path)
    block, err = split_frontmatter(f.text)
    if err:
        msg = f"{err}; Claude Code ignores invalid frontmatter and loads the rule unconditionally"
        findings.append(Finding("error", "frontmatter-invalid", where, msg))
        return None
    if block is None:
        return None
    try:
        return parse_frontmatter(block, 2)
    except FrontmatterError as exc:
        msg = (
            f"{exc}. Invalid YAML makes Claude Code ignore the frontmatter and load this rule "
            "in every session (`claude --debug` shows the parse error)"
        )
        findings.append(Finding("error", "frontmatter-invalid", where, msg))
    except UnsupportedYamlError as exc:
        msg = (
            f"{exc}: this checker cannot interpret it; "
            "confirm the rule's scope with `claude --debug`"
        )
        findings.append(Finding("warning", "frontmatter-unchecked", where, msg))
    return None


def report_ignored_keys(
    where: str, data: dict[str, str | list[str]], findings: list[Finding]
) -> None:
    """Every key but `paths` is ignored; a scoping key without `paths` leaves the rule global."""
    for key in data:
        if key == "paths":
            continue
        scoping = key in FOREIGN_SCOPING_KEYS and "paths" not in data
        label = KNOWN_FOREIGN_KEYS.get(key, "unknown key")
        msg = f"'{key}' ({label}) is ignored: `paths` is the only field read"
        if scoping:
            msg += "; without `paths` this rule loads in every session"
        findings.append(
            Finding("error" if scoping else "warning", "frontmatter-ignored-key", where, msg)
        )


def report_no_match(where: str, pat: str, scope: RuleScope, findings: list[Finding]) -> None:
    """A pattern that matches none of the listed files never loads the rule through it."""
    skipped = "(.git, node_modules and .claude/worktrees are not searched)"
    if scope.ancestor:
        msg = (
            f"'{pat}' matches no file of this project {skipped}, so in sessions started here "
            f"the rule never loads through it; patterns are relative to {scope.base}, and files "
            "there outside this project were not listed"
        )
        findings.append(Finding("info", "glob-no-match", where, msg))
        return
    msg = (
        f"'{pat}' matches no file under {scope.base} {skipped}, so the rule never loads "
        "through it: renamed directory, wrong base, or '*' where '**' was meant"
    )
    findings.append(Finding("warning", "glob-no-match", where, msg))


def check_pattern(
    where: str, compiled: CompiledPattern, scope: RuleScope, findings: list[Finding]
) -> None:
    """Check one compiled `paths` pattern against the files under the rule's base."""
    pat = compiled.pattern
    if compiled.over_budget:
        return
    if compiled.invalid:
        msg = (
            f"'{pat}' has a '[' that is not a valid bracket expression, so it matches nothing; "
            "escape it as '\\['"
        )
        findings.append(Finding("error", "glob-invalid-bracket", where, msg))
        return
    if pat.startswith(("./", "/")):
        msg = (
            f"'{pat}' starts with a path prefix; "
            "the docs show patterns relative to the base with no prefix"
        )
        findings.append(Finding("info", "glob-leading-slash", where, msg))
    if not any(compiled.matches(rel) for rel in scope.rel_files):
        report_no_match(where, pat, scope, findings)
    if pat.startswith("*.") and "/" not in pat:
        deeper_glob = compile_glob("**/" + pat)
        deeper = sum(1 for rel in scope.rel_files if "/" in rel and deeper_glob.match(rel))
        if deeper:
            msg = (
                f"'{pat}' matches only the base directory; "
                f"{deeper} file(s) in subdirectories need '**/{pat}'"
            )
            findings.append(Finding("info", "glob-root-only", where, msg))


def check_rule(f: InstructionFile, scope: RuleScope, findings: list[Finding]) -> None:
    """Validate a rule's frontmatter and its path patterns against the files under its base."""
    where = str(f.path)
    data = rule_frontmatter(f, findings)
    if data is None:
        return
    report_ignored_keys(where, data, findings)
    if "paths" not in data:
        return
    patterns = paths_from_value(data["paths"])
    f.paths = patterns
    if not patterns:
        msg = "`paths` is present but holds no pattern"
        findings.append(Finding("error", "paths-empty", where, msg))
        return
    compiled = compile_paths(patterns)
    for c in compiled:
        check_pattern(where, c, scope, findings)
    over = [c.pattern for c in compiled if c.over_budget]
    if over:
        msg = (
            f"brace expansion of `paths` yields more than the 1,000-pattern budget; "
            f"over-budget patterns are used unexpanded and match nothing: {', '.join(over)}"
        )
        findings.append(Finding("error", "brace-budget", where, msg))


def nearest_package_scripts(
    start: Path, project: Path, cache: dict[Path, set[str] | None]
) -> set[str] | None:
    """Scripts of the nearest package.json from start up to the project root."""
    cur = start
    while True:
        if cur not in cache:
            cache[cur] = load_scripts(cur / "package.json")
        if cache[cur] is not None or cur in {project, cur.parent} or not is_within(cur, project):
            return cache[cur]
        cur = cur.parent


def check_pm_command(
    ctx: Context, m: re.Match[str], scripts: set[str], where: tuple[str, int]
) -> None:
    """Check one package-manager command against package.json scripts and local binaries."""
    path, lineno = where
    pm, has_run, name = m.group(1), bool(m.group(2)), m.group(3)
    command = m.group(0).strip()
    if has_run:
        if name not in scripts:
            msg = (
                f"`{command}` runs script '{name}', which the nearest package.json does not define"
            )
            ctx.findings.append(Finding("error", "script-missing", path, msg, lineno))
        return
    builtins = NPM_BUILTINS if pm == "npm" else OTHER_PM_BUILTINS
    if name in builtins or name.startswith("-"):
        return
    if pm == "npm":
        msg = f"`{command}`: npm needs `npm run {name}` for a package.json script"
        ctx.findings.append(Finding("warning", "npm-needs-run", path, msg, lineno))
    elif name not in scripts and not (ctx.project / "node_modules" / ".bin" / name).exists():
        msg = (
            f"`{command}`: '{name}' is not a package.json script and not an installed local "
            "binary; fine if it is a package-manager command or a binary installed later"
        )
        ctx.findings.append(Finding("info", "command-unverified", path, msg, lineno))


def check_scripts(f: InstructionFile, ctx: Context, cache: dict[Path, set[str] | None]) -> None:
    """Flag package-manager commands that name scripts the nearest package.json does not define."""
    if not is_within(f.path, ctx.project):
        return
    scripts = nearest_package_scripts(f.path.parent, ctx.project, cache)
    if scripts is None:
        return
    for lineno, snippet in command_snippets(f.text):
        for m in PM_COMMAND_RE.finditer(snippet):
            check_pm_command(ctx, m, scripts, (str(f.path), lineno))


def check_wording(f: InstructionFile, findings: list[Finding]) -> None:
    """Flag emphasis and reasoning nudges that current models over-apply or ignore."""
    caps = 0
    first_line: int | None = None
    for lineno, line in prose_lines(strip_html_comments(f.text)):
        hits = len(EMPHASIS_RE.findall(line))
        if hits:
            caps += hits
            first_line = first_line or lineno
        if NUDGE_RE.search(line):
            msg = (
                "'think step by step', 'be thorough' and similar are ordinary text; "
                "effort controls depth"
            )
            findings.append(Finding("warning", "reasoning-nudge", str(f.path), msg, lineno))
    if caps >= EMPHASIS_THRESHOLD:
        msg = (
            f"{caps} emphasis markers (IMPORTANT, MUST, NEVER in capitals, '!!'); "
            "current models over-apply emphasized lines. "
            "Write plain lines; move zero-exception rules to a hook or deny rule"
        )
        findings.append(Finding("warning", "emphasis", str(f.path), msg, first_line))


def check_local_ignored(f: InstructionFile, project: Path, findings: list[Finding]) -> None:
    """CLAUDE.local.md must stay out of git."""
    git = shutil.which("git")
    if git is None:
        msg = "could not run git check-ignore: git is not on PATH"
        findings.append(Finding("info", "git-check-skipped", str(f.path), msg))
        return
    try:
        res = subprocess.run(
            [git, "check-ignore", "-q", str(f.path)],
            cwd=project,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        msg = f"could not run git check-ignore: {exc}"
        findings.append(Finding("info", "git-check-skipped", str(f.path), msg))
        return
    if res.returncode == 1:
        msg = (
            "CLAUDE.local.md is not git-ignored; "
            "add it to .gitignore so personal notes are not committed"
        )
        findings.append(Finding("warning", "local-not-ignored", str(f.path), msg))
    elif res.returncode != 0:
        msg = "git check-ignore failed (not a git repository?); ignore status not checked"
        findings.append(Finding("info", "git-check-skipped", str(f.path), msg))


def normalize(line: str) -> str:
    """Normalize a line for duplicate detection."""
    s = re.sub(r"^[\s>*\-+\d.)#]+", "", line).strip().lower()
    return re.sub(r"\s+", " ", s)


def check_duplicates(files: list[InstructionFile], findings: list[Finding]) -> None:
    """Flag identical instructions in two homes and identical files."""
    seen: dict[str, tuple[str, int]] = {}
    for f in files:
        for lineno, line in prose_lines(strip_html_comments(f.text)):
            key = normalize(line)
            if len(key) < MIN_DUPLICATE_CHARS:
                continue
            first = seen.setdefault(key, (str(f.path), lineno))
            if first[0] != str(f.path):
                msg = f"same instruction as {first[0]}:{first[1]}; keep one canonical home"
                findings.append(Finding("warning", "duplicate-line", str(f.path), msg, lineno))
    by_hash: dict[str, list[str]] = {}
    for f in files:
        if f.sha256:
            by_hash.setdefault(f.sha256, []).append(str(f.path))
    findings.extend(
        Finding(
            "warning", "duplicate-file", group[0], "identical content in: " + ", ".join(group[1:])
        )
        for group in by_hash.values()
        if len(group) > 1
    )


def load_scripts(pkg: Path) -> set[str] | None:
    """Return a package.json's script names, or None when it is absent or unreadable."""
    if not pkg.is_file():
        return None
    try:
        text = pkg.read_text(encoding="utf-8")
        data = cast("object", json.loads(text, object_pairs_hook=JsonObject))
    except (ValueError, OSError):  # ValueError covers invalid JSON and invalid UTF-8
        return None
    if isinstance(data, JsonObject):
        scripts = data.get("scripts")
        if isinstance(scripts, JsonObject):
            return set(scripts)
    return set()


# ---------------------------------------------------------------------------
# Heuristics: leads for the reader, never verdicts
# ---------------------------------------------------------------------------

STOPWORDS = frozenset(
    [
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "by",
        "from",
        "at",
        "as",
        "is",
        "are",
        "be",
        "been",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "use",
        "using",
        "always",
        "never",
        "must",
        "should",
        "can",
        "do",
        "does",
        "don't",
        "not",
        "no",
        "all",
        "any",
        "each",
        "every",
        "when",
        "if",
        "then",
        "than",
        "into",
        "only",
        "also",
        "our",
        "your",
        "you",
        "we",
        "they",
        "them",
        "their",
        "there",
        "here",
        "new",
        "file",
        "files",
        "code",
    ]
)
NEAR_DUPLICATE_THRESHOLD = 0.6
MIN_CONTENT_TOKENS = 5
CHOICE_GROUPS: dict[str, list[str]] = {
    "package manager": ["npm", "pnpm", "yarn", "bun"],
    "JavaScript test runner": ["jest", "vitest", "mocha", "ava"],
    "Python test runner": ["pytest", "unittest", "nose"],
    "formatter": ["prettier", "biome", "dprint"],
    "validation library": ["zod", "joi", "yup", "valibot"],
    "ORM": ["prisma", "drizzle", "typeorm", "sequelize"],
    "Python environment tool": ["uv", "poetry", "pipenv", "conda"],
    "quote style": ["single quotes", "double quotes"],
    "indentation": ["2 spaces", "4 spaces", "tabs"],
}
PRESCRIPTIVE_RE = re.compile(
    r"\b(use|uses|using|prefer|prefers|with|run|runs|write|written|choose|go with)\b", re.IGNORECASE
)
NEGATION_BEFORE_RE = re.compile(
    (
        r"\b(not|never|don'?t|do not|no|avoid|instead of|rather than|over|replace|replacing"
        r"|migrate from|not use)\b(?:\s+\S+){0,3}\s*$"
    ),
    re.IGNORECASE,
)
PROCEDURE_HEADING_RE = re.compile(
    (
        r"^#+\s.*\b(release|deploy|deployment|rollout|runbook|procedure|steps|checklist|process"
        r"|onboarding|setup|incident|how to)\b"
    ),
    re.IGNORECASE,
)
GENERIC_LINE_RE = re.compile(
    (
        r"\b(clean,? (and )?(maintainable|readable)|production[- ]ready|best practices"
        r"|high[- ]quality code|meaningful (variable |function )?names|self-documenting"
        r"|handle errors (properly|gracefully|appropriately)|keep (the )?code (dry|simple|clean)"
        r"|follow (the )?solid|be careful|write good code|readable code)\b"
    ),
    re.IGNORECASE,
)
PATH_TOKEN_RE = re.compile(r"(?<![\w@./-])((?:[\w.-]+/)+[\w.*{},-]*)")
FORMATTER_CONFIGS = (
    "biome.json",
    "biome.jsonc",
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.json5",
    ".prettierrc.yaml",
    ".prettierrc.yml",
    ".prettierrc.toml",
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.mjs",
    "prettier.config.js",
    "prettier.config.cjs",
    "prettier.config.mjs",
    "prettier.config.ts",
    ".editorconfig",
    "dprint.json",
    "ruff.toml",
    ".ruff.toml",
    "rustfmt.toml",
    ".rustfmt.toml",
    ".clang-format",
)
PYPROJECT_FORMATTER_RE = re.compile(r"^\[tool\.(ruff|black)(\.format)?\]", re.MULTILINE)
STYLE_LINE_RE = re.compile(
    (
        r"\b(\d+[- ]space|indent(ation|ed)?\b.*\b(spaces?|tabs?)\b"
        r"|tabs? (for|instead of) (indent|spaces)|(single|double) quotes|semicolons?"
        r"|trailing commas?|(max(imum)?|line) (line )?(length|width)"
        r"|lines? (under|at most|no longer than) \d+ (char|column))"
    ),
    re.IGNORECASE,
)


NEGATIVE_START_RE = re.compile(
    r"^(?:[-*+]\s+|\d+[.)]\s+)?(?:\*\*)?(?:never|don'?t|do not|avoid|no)\b", re.IGNORECASE
)
ALTERNATIVE_RE = re.compile(
    (
        r"\b(prefer|instead|rather|through|via|unless|except|because|since|so that|only)\b"
        r"|,\s*(use|run|call)\b|[;:—]|\s-\s"
    ),
    re.IGNORECASE,
)

REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"
REFERENCE_FOR_CODE: dict[str, str] = {
    "procedure-candidate": "procedures-to-skills.md",
    "near-duplicate": "cross-file-analysis.md",
    "duplicate-line": "cross-file-analysis.md",
    "duplicate-file": "cross-file-analysis.md",
    "conflicting-choice": "cross-file-analysis.md",
    "no-op-candidate": "placement.md",
    "formatter-enforced": "placement.md",
    "discoverable-layout": "placement.md",
    "local-not-ignored": "placement.md",
    "negative-only": "writing-guide.md",
    "time-sensitive": "writing-guide.md",
    "exact-version": "writing-guide.md",
    "table-padding": "format-and-links.md",
    "reasoning-nudge": "writing-guide.md",
    "emphasis": "escalation.md",
    "scope-candidate": "rules-architecture.md",
    "claude-md-long": "rules-architecture.md",
    "rule-symlink-external": "rules-architecture.md",
}
LOADER_CODE_PREFIXES = (
    "frontmatter-",
    "glob-",
    "paths-",
    "brace-",
    "import-",
    "agents-md-",
    "on-demand-",
    "over-4mib",
)


def references_for(findings: list[Finding]) -> list[tuple[str, list[str]]]:
    """The skill references to read before reporting these findings, in first-seen order."""
    by_ref: dict[str, list[str]] = {}
    for x in findings:
        name = REFERENCE_FOR_CODE.get(x.code)
        if name is None and x.code.startswith(LOADER_CODE_PREFIXES):
            name = "loading-semantics.md"
        if name is None:
            continue
        codes = by_ref.setdefault(str(REFERENCES_DIR / name), [])
        if x.code not in codes:
            codes.append(x.code)
    return list(by_ref.items())


MONTHS = (
    r"(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sep(t(ember)?)?"
    r"|oct(ober)?|nov(ember)?|dec(ember)?)"
)
TIME_SENSITIVE_RE = re.compile(
    (
        rf"\b(20\d\d-\d\d(-\d\d)?|{MONTHS}\.? 20\d\d|q[1-4] 20\d\d|as of"
        rf"|last (updated|checked|reviewed)|(until|before|after|since) {MONTHS}\b"
        rf"|recently (added|changed|migrated|upgraded))"
    ),
    re.IGNORECASE,
)
EXACT_VERSION_RE = re.compile(r"(?<![\w./-])v?\d+\.\d+\.\d+(?!\w|\.\w)")


def check_time_sensitive(f: InstructionFile, findings: list[Finding]) -> None:
    """Flag dates, 'as of' statements and exact versions: they go stale or copy the manifest."""
    for lineno, line in instruction_lines(f):
        if TIME_SENSITIVE_RE.search(line):
            msg = (
                "time-sensitive wording (a date, 'as of', 'until <month>'); state the current rule "
                "without the date, and keep review dates in an HTML comment, which is stripped "
                "before Claude sees the file"
            )
            findings.append(Finding("info", "time-sensitive", str(f.path), msg, lineno))
        elif EXACT_VERSION_RE.search(line):
            msg = (
                "exact version number; the manifest or lockfile is the source of truth and a copy "
                "drifts. Keep a version only when it changes what Claude writes "
                "(a pinned major with different APIs)"
            )
            findings.append(Finding("info", "exact-version", str(f.path), msg, lineno))


TABLE_PADDING_MIN_CHARS = 120
TABLE_ROW_MIN_PIPES = 2
SCOPE_HEADING_MIN_BULLETS = 3
SCOPE_MIN_PATH_MENTIONS = 3
SCOPE_DOMINANT_SHARE = 0.7
PROCEDURE_MIN_ITEMS = 5
MIN_TOKEN_CHARS = 3  # shorter words, and stems, carry too little meaning to compare
LABEL_MAX_CHARS = 40  # a short line ending in ':' introduces a list; it is not an instruction
TREE_MIN_LINES = 3
SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")


def table_padding(line: str) -> int:
    """Alignment padding in one table row: beyond one space per side and three dashes."""
    waste = 0
    for cell in line.strip().strip("|").split("|"):
        core = cell.strip()
        if SEPARATOR_CELL_RE.match(core):
            waste += max(0, core.count("-") - 3) + max(0, len(cell) - len(core) - 2)
            continue
        waste += max(0, len(cell) - len(cell.lstrip()) - 1) + max(
            0, len(cell) - len(cell.rstrip()) - 1
        )
    return waste


def check_table_padding(f: InstructionFile, findings: list[Finding]) -> None:
    """Flag tables padded for visual alignment: the padding is context with no information."""
    waste = 0
    first: int | None = None
    raw = strip_html_comments(f.text).splitlines()
    for lineno, _ in prose_lines(strip_html_comments(f.text)):
        s = raw[lineno - 1].strip()  # the raw row: inline code must keep its width here
        if s.startswith("|") and s.count("|") >= TABLE_ROW_MIN_PIPES:
            row = table_padding(s)
            if row and first is None:
                first = lineno
            waste += row
    if waste >= TABLE_PADDING_MIN_CHARS:
        msg = (
            f"{waste} characters of column-alignment padding in tables; write compact rows "
            "(`| a | b |`, `| :-- |`). Markdown formatters such as Prettier re-pad tables, "
            "so exclude instruction files from them"
        )
        findings.append(Finding("info", "table-padding", str(f.path), msg, first))


def check_negative_only(f: InstructionFile, findings: list[Finding]) -> None:
    """Flag prohibitions that do not say what to do instead."""
    for lineno, line in instruction_lines(f):
        if NEGATIVE_START_RE.search(line) and not ALTERNATIVE_RE.search(line):
            msg = (
                "prohibition without an alternative; say what to do instead ('Use X, not Y'), "
                "or keep a bare 'never' only for a hard boundary "
                "(and enforce it if it must not bend)"
            )
            findings.append(Finding("info", "negative-only", str(f.path), msg, lineno))


def formatter_configs(project: Path) -> list[str]:
    """Formatter or editor configs at the project root that already enforce code style."""
    found = [name for name in FORMATTER_CONFIGS if (project / name).is_file()]
    pyproject = project / "pyproject.toml"
    if pyproject.is_file() and PYPROJECT_FORMATTER_RE.search(
        pyproject.read_text(encoding="utf-8", errors="replace")
    ):
        found.append("pyproject.toml")
    package = project / "package.json"
    if package.is_file() and '"prettier"' in package.read_text(encoding="utf-8", errors="replace"):
        found.append("package.json (prettier)")
    return found


def check_formatter_enforced(
    f: InstructionFile, configs: list[str], findings: list[Finding]
) -> None:
    """Flag code-style lines that a formatter config at the project root already enforces."""
    if not configs:
        return
    for lineno, line in instruction_lines(f):
        if STYLE_LINE_RE.search(line):
            msg = (
                f"code-style line while {', '.join(configs)} exists; if the formatter enforces it, "
                "the prose copy changes nothing and can drift from the config"
            )
            findings.append(Finding("info", "formatter-enforced", str(f.path), msg, lineno))


def content_tokens(line: str) -> set[str]:
    """Lowercased content words with light stemming, for near-duplicate comparison."""
    text = re.sub(r"https?://\S+", " ", line.lower())
    words = [m.group(0) for m in re.finditer(r"[a-z][a-z0-9_.-]+", text)]
    out: set[str] = set()
    for w in words:
        if w in STOPWORDS or len(w) < MIN_TOKEN_CHARS:
            continue
        stem = w
        for suffix in ("ing", "es", "ed", "s"):
            if w.endswith(suffix) and len(w) - len(suffix) >= MIN_TOKEN_CHARS:
                stem = w[: -len(suffix)]
                break
        out.add(stem)
    return out


def instruction_lines(f: InstructionFile) -> list[tuple[int, str]]:
    """Prose lines that look like instructions (bullets or sentences), outside code."""
    out: list[tuple[int, str]] = []
    for lineno, line in prose_lines(strip_html_comments(f.text)):
        s = line.strip()
        if (
            not s
            or s.startswith(("#", "---", "|"))
            or (s.endswith(":") and len(s) < LABEL_MAX_CHARS)
        ):
            continue
        out.append((lineno, s))
    return out


def check_near_duplicates(files: list[InstructionFile], findings: list[Finding]) -> None:
    """Flag pairs of lines with mostly the same content words (possible semantic duplicates)."""
    entries: list[tuple[InstructionFile, int, str, set[str]]] = []
    for f in files:
        for lineno, line in instruction_lines(f):
            toks = content_tokens(line)
            if len(toks) >= MIN_CONTENT_TOKENS:
                entries.append((f, lineno, line, toks))
    for i, (fa, la, ta, sa) in enumerate(entries):
        for fb, lb, tb, sb in entries[i + 1 :]:
            if normalize(ta) == normalize(tb):
                continue  # identical lines are reported as duplicate-line
            score = len(sa & sb) / len(sa | sb)
            if score >= NEAR_DUPLICATE_THRESHOLD:
                msg = (
                    f"line {la} and {fb.path}:{lb} say nearly the same thing "
                    f"(word overlap {score:.0%}); read both: if they mean the same, "
                    "keep one canonical line"
                )
                findings.append(Finding("info", "near-duplicate", str(fa.path), msg, la))


def positive_choices(line: str) -> list[tuple[str, str]]:
    """(group, member) pairs the line prescribes, skipping negated mentions."""
    if not PRESCRIPTIVE_RE.search(line):
        return []
    found: list[tuple[str, str]] = []
    lower = line.lower()
    for group, members in CHOICE_GROUPS.items():
        for member in members:
            for m in re.finditer(r"(?<![\w-])" + re.escape(member) + r"(?![\w-])", lower):
                if not NEGATION_BEFORE_RE.search(lower[: m.start()]):
                    found.append((group, member))
                    break
    return found


def check_conflicting_choices(files: list[InstructionFile], findings: list[Finding]) -> None:
    """Flag subjects where different lines prescribe different tools or styles."""
    seen: dict[str, dict[str, list[str]]] = {}
    for f in files:
        for lineno, line in instruction_lines(f):
            choices = positive_choices(line)
            groups_in_line = [g for g, _ in choices]
            for group, member in choices:
                if groups_in_line.count(group) > 1:
                    continue  # one line naming several options presents alternatives, not a choice
                seen.setdefault(group, {}).setdefault(member, []).append(f"{f.path}:{lineno}")
    for group, members in seen.items():
        if len(members) > 1:
            where = "; ".join(f"{m}: {', '.join(locs)}" for m, locs in members.items())
            first = next(iter(members.values()))[0]
            msg = (
                f"different {group} choices are prescribed ({where}); "
                "confirm which one holds and keep one"
            )
            findings.append(Finding("warning", "conflicting-choice", first.rsplit(":", 1)[0], msg))


def numbered_runs(lines: list[str]) -> list[tuple[int, int]]:
    """(first line, length) of each run of consecutive numbered-list lines."""
    runs: list[tuple[int, int]] = []
    run_start = 0
    run_len = 0
    for i, line in enumerate([*lines, ""], 1):
        if re.match(r"^\d+[.)]\s", line.strip()):
            if run_len == 0:
                run_start = i
            run_len += 1
        else:
            if run_len:
                runs.append((run_start, run_len))
            run_len = 0
    return runs


def procedure_sections(lines: list[str]) -> list[tuple[str, int, int]]:
    """(title, heading line, list items) of each section whose heading names a procedure."""
    sections: list[tuple[str, int, int]] = []
    heading = ""
    heading_line = 0
    items = 0
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#"):
            if heading:
                sections.append((heading, heading_line, items))
            heading = s.lstrip("#").strip() if PROCEDURE_HEADING_RE.match(s) else ""
            heading_line = i
            items = 0
        elif heading and re.match(r"^([-*+]|\d+[.)])\s", s):
            items += 1
    if heading:
        sections.append((heading, heading_line, items))
    return sections


def check_procedures(f: InstructionFile, findings: list[Finding]) -> None:
    """Flag ordered procedures and checklist sections: candidates for a skill."""
    lines = f.text.splitlines()
    found: list[Finding] = []
    for start, length in numbered_runs(lines):
        if length >= PROCEDURE_MIN_ITEMS:
            msg = (
                f"{length} numbered steps starting here; "
                "procedures cost context every session: consider a skill"
            )
            found.append(Finding("info", "procedure-candidate", str(f.path), msg, start))
    for title, lineno, items in procedure_sections(lines):
        if items >= PROCEDURE_MIN_ITEMS:
            msg = f"section '{title}' reads like a procedure ({items} items); consider a skill"
            found.append(Finding("info", "procedure-candidate", str(f.path), msg, lineno))
    findings.extend(sorted(found, key=lambda x: x.line or 0))


@dataclass
class Section:
    """A heading and what its body holds."""

    title: str
    line: int
    mentions: list[str] = field(default_factory=list[str])
    bullets: int = 0


def split_sections(text: str) -> list[Section]:
    """Split a file at its headings; the text before the first heading is '(top)'."""
    sections = [Section("(top)", 1)]
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            sections.append(Section(line.lstrip("#").strip(), lineno))
            continue
        sections[-1].mentions.extend(m.group(1) for m in PATH_TOKEN_RE.finditer(line))
        if line.lstrip().startswith(("- ", "* ")):
            sections[-1].bullets += 1
    return sections


def scope_by_heading(sec: Section, project: Path) -> str | None:
    """A directory the section's heading names, when the section holds enough conventions."""
    named = [m.group(1).strip("./") for m in PATH_TOKEN_RE.finditer(sec.title)]
    named = [n for n in named if n and (project / n).is_dir()]
    if named and sec.bullets >= SCOPE_HEADING_MIN_BULLETS:
        return named[0]
    return None


def scope_by_mentions(sec: Section, project: Path) -> tuple[str, int, int] | None:
    """(directory, its mentions, all mentions) when most path mentions point into one place."""
    prefixes = [
        "/".join(p.strip("./").split("/")[:2])
        for p in sec.mentions
        if not p.startswith(("http", "~"))
    ]
    prefixes = [p for p in prefixes if p and (project / p).is_dir()]
    if len(prefixes) < SCOPE_MIN_PATH_MENTIONS:
        return None
    top = max(set(prefixes), key=prefixes.count)
    if prefixes.count(top) / len(prefixes) >= SCOPE_DOMINANT_SHARE:
        return top, prefixes.count(top), len(prefixes)
    return None


def check_scope_candidates(f: InstructionFile, ctx: Context) -> None:
    """In always-on files, flag sections whose path mentions all point into one directory."""
    if f.loads != "launch" or f.kind in ("user-claude-md", "agents-md"):
        return
    for sec in split_sections(f.text):
        named = scope_by_heading(sec, ctx.project)
        if named is not None:
            msg = (
                f"section '{sec.title}' names {named}/ and holds {sec.bullets} conventions that "
                f"load in every session; area conventions belong in a rule with paths: "
                f'"{named}/**", even when short, plus a pointer line for anything needed before '
                "those files are touched"
            )
            ctx.findings.append(Finding("info", "scope-candidate", str(f.path), msg, sec.line))
            continue
        dominant = scope_by_mentions(sec, ctx.project)
        if dominant is not None:
            top, count, total = dominant
            msg = (
                f"section '{sec.title}' is about {top}/ ({count} of {total} path mentions) but "
                f'loads in every session; candidate for a rule with paths: "{top}/**" unless it '
                "is needed before those files are touched"
            )
            ctx.findings.append(Finding("info", "scope-candidate", str(f.path), msg, sec.line))


def check_discoverable(f: InstructionFile, findings: list[Finding]) -> None:
    """Flag directory trees and generic lines: usually things Claude does or finds anyway."""
    tree_lines = [i for i, line in enumerate(f.text.splitlines(), 1) if re.search(r"[├└]──", line)]
    if len(tree_lines) >= TREE_MIN_LINES:
        msg = (
            f"directory tree ({len(tree_lines)} lines); Claude reads the layout itself, "
            "so this rarely changes behavior"
        )
        findings.append(Finding("info", "discoverable-layout", str(f.path), msg, tree_lines[0]))
    for lineno, line in instruction_lines(f):
        if GENERIC_LINE_RE.search(line):
            msg = (
                "generic instruction; would Claude act differently without it? "
                "If not, it only costs context"
            )
            findings.append(Finding("info", "no-op-candidate", str(f.path), msg, lineno))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def rule_scope(f: InstructionFile, ctx: Context) -> RuleScope:
    """The listed files as the rule's patterns see them: relative to the rule's base."""
    if f.kind == "user-rule":
        return RuleScope(ctx.project, ctx.all_rel)
    base = rules_base(f.path)
    if f.kind == "ancestor-rule":  # project files sit below the ancestor base
        below = ctx.project.relative_to(base).as_posix()
        return RuleScope(base, [f"{below}/{r}" for r in ctx.all_rel], ancestor=True)
    if base == ctx.project:
        return RuleScope(base, ctx.all_rel)
    prefix = base.relative_to(ctx.project).as_posix() + "/"
    return RuleScope(base, [r[len(prefix) :] for r in ctx.all_rel if r.startswith(prefix)])


def check_claude_md_size(f: InstructionFile, findings: list[Finding]) -> None:
    """A CLAUDE.md that loads at launch should stay under the documented line target."""
    is_claude_md = f.path.name in ("CLAUDE.md", "CLAUDE.local.md")
    if is_claude_md and f.loads == "launch" and f.lines > CLAUDE_MD_LINE_TARGET:
        msg = (
            f"{f.lines} lines; the documented target is under 200 per CLAUDE.md "
            "(guidance, not truncation). Move part-of-codebase content to path-scoped rules "
            "and procedures to skills"
        )
        findings.append(Finding("warning", "claude-md-long", str(f.path), msg))


def check_rule_file(f: InstructionFile, ctx: Context) -> None:
    """Check a rule's frontmatter and globs, mark it conditional, and flag stray backups."""
    check_rule(f, rule_scope(f, ctx), ctx.findings)
    if f.paths:
        f.loads = "conditional"
    in_backup_dir = any(part.lower() in BACKUP_DIR_NAMES for part in f.path.parts)
    if in_backup_dir or BACKUP_NAME_RE.search(f.path.name):
        msg = (
            "looks like a backup or archive, but every .md under a rules directory loads; "
            "move it out"
        )
        ctx.findings.append(Finding("warning", "rule-backup-loaded", str(f.path), msg))


def check_on_demand_size(f: InstructionFile, findings: list[Finding]) -> None:
    """Files that load on demand are cut at a per-file character limit."""
    if f.loads in ("on-demand", "conditional") and f.chars > ON_DEMAND_CHAR_LIMIT_200K:
        msg = (
            f"{f.chars} characters; on-demand files are cut at 40,000 characters on a 200K "
            "context window (150,000 on current 1M-window models) and Claude sees only the start"
        )
        findings.append(Finding("warning", "on-demand-over-limit", str(f.path), msg))


def classify_agents_md(f: InstructionFile, ctx: Context, files: list[InstructionFile]) -> None:
    """An AGENTS.md loads directly only when no CLAUDE.md is on the project path."""
    where = str(f.path)
    if any(x.kind in ("project-root", "project-local", "ancestor") for x in files):
        f.loads = "not-by-default"
        if not any("@AGENTS.md" in x.text for x in files):
            msg = (
                "a CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md is on the project path, "
                "so by default Claude Code reads that instead of AGENTS.md; import it with "
                "@AGENTS.md or set Project instructions to claude-md-and-agents-md"
            )
            ctx.findings.append(Finding("info", "agents-md-shadowed", where, msg))
    else:
        f.loads = "launch"
        msg = (
            "read directly as project instructions "
            "(Claude Code v2.1.277+, default Project instructions setting)"
        )
        ctx.findings.append(Finding("info", "agents-md-direct", where, msg))


def classify(f: InstructionFile, ctx: Context, files: list[InstructionFile]) -> None:
    """Run the per-file checks that depend on the file's kind."""
    check_claude_md_size(f, ctx.findings)
    if f.kind.endswith("rule"):
        check_rule_file(f, ctx)
    check_on_demand_size(f, ctx.findings)
    if f.kind == "agents-md":
        classify_agents_md(f, ctx, files)
    if f.kind == "project-local":
        check_local_ignored(f, ctx.project, ctx.findings)


def match_rules(
    targets: list[str], files: list[InstructionFile], project: Path
) -> dict[str, list[str]]:
    """For each project-relative file, list the path-scoped rules that would load."""
    report: dict[str, list[str]] = {}
    for target in targets:
        rel = target.replace(os.sep, "/").removeprefix("./")
        loaded: list[str] = []
        for f in files:
            if f.loads != "conditional" or not f.paths:
                continue
            rel_to_base = rel
            if f.kind == "ancestor-rule":
                rel_to_base = f"{project.relative_to(rules_base(f.path)).as_posix()}/{rel}"
            elif f.kind == "nested-rule":
                prefix = rules_base(f.path).relative_to(project).as_posix() + "/"
                if not rel.startswith(prefix):
                    continue
                rel_to_base = rel[len(prefix) :]
            if any(c.matches(rel_to_base) for c in compile_paths(f.paths)):
                loaded.append(str(f.path))
        report[target] = loaded
    return report


SEVERITIES = ("error", "warning", "info")
REFERENCES_NOTE = "each reference holds the fix and what to ask the user"
LIMITS = [
    (
        "Discovery is not a loading trace: confirm with /context, `claude --debug` "
        "or an InstructionsLoaded hook."
    ),
    (
        "Glob matching approximates Claude Code's matcher; "
        "frontmatter is checked by a strict subset parser."
    ),
    "Managed policy, auto memory, plugins, skills and claudeMdExcludes are not evaluated.",
    (
        "Contradictions in meaning need a reader; the checker detects identical lines, "
        "word-overlap near-duplicates and conflicting tool choices only."
    ),
]


@dataclass
class Report:
    """Everything the text and JSON outputs show."""

    ctx: Context
    files: list[InstructionFile]
    launch_files: int
    launch_lines: int
    match_report: dict[str, list[str]]


def emit(text: str = "") -> None:
    """Write one line of the report to stdout."""
    _ = sys.stdout.write(text + "\n")


def severity_counts(findings: list[Finding]) -> dict[str, int]:
    """Number of findings per severity."""
    return {s: sum(1 for x in findings if x.severity == s) for s in SEVERITIES}


def print_text(report: Report) -> None:
    """Human-readable report."""
    ctx = report.ctx
    emit(f"Project: {ctx.project}")
    emit(f"User dir: {ctx.user_dir or '(skipped)'}")
    emit(f"Checked against: {CHECKED_AGAINST}\n")
    emit("Files:")
    for f in report.files:
        extra = f" paths={f.paths}" if f.paths is not None else ""
        emit(f"  [{f.loads}] {f.kind}: {f.path} ({f.lines} lines, {f.chars} chars){extra}")
    launch = f"{report.launch_files} files, {report.launch_lines} lines including imports"
    emit(f"\nLoaded at launch: {launch}\n")
    if report.match_report:
        emit("Path-scoped rules that would load for:")
        for target, rules in report.match_report.items():
            emit(f"  {target}: {', '.join(rules) if rules else '(none)'}")
        emit()
    emit("Findings:" if ctx.findings else "Findings: none")
    for x in ctx.findings:
        loc = f"{x.path}:{x.line}" if x.line else x.path
        emit(f"  {x.severity.upper():7} {x.code}: {loc}\n          {x.message}")
    counts = severity_counts(ctx.findings)
    emit(f"\n{counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info")
    refs = references_for(ctx.findings)
    if refs:
        emit(f"\nRead before reporting these findings ({REFERENCES_NOTE}):")
        for ref, codes in refs:
            emit(f"  {ref}  ({', '.join(codes)})")
    emit("Limits: " + " ".join(LIMITS))


def print_json(report: Report) -> None:
    """Machine-readable report."""
    ctx = report.ctx
    result: dict[str, object] = {
        "project": str(ctx.project),
        "user_dir": str(ctx.user_dir) if ctx.user_dir else None,
        "checked_against": CHECKED_AGAINST,
        "files": [f.as_dict() for f in report.files],
        "launch_set": {
            "files": report.launch_files,
            "lines_including_imports": report.launch_lines,
        },
        "findings": [x.as_dict() for x in ctx.findings],
        "summary": severity_counts(ctx.findings),
        "match": report.match_report,
        "read_before_reporting": [
            {"reference": r, "codes": c} for r, c in references_for(ctx.findings)
        ],
        "limits": LIMITS,
    }
    emit(json.dumps(result, indent=2, ensure_ascii=False))


def parse_args(argv: list[str] | None) -> tuple[argparse.ArgumentParser, Args]:
    """Parse the command line."""
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    _ = ap.add_argument(
        "--project", type=Path, default=Path.cwd(), help="session working directory (default: .)"
    )
    _ = ap.add_argument(
        "--user-dir", type=Path, default=None, help="default: $CLAUDE_CONFIG_DIR or ~/.claude"
    )
    _ = ap.add_argument("--no-user", action="store_true", help="skip user-scope files")
    _ = ap.add_argument(
        "--match", nargs="+", metavar="FILE", help="list the scoped rules that load for these files"
    )
    _ = ap.add_argument("--json", action="store_true", help="print JSON")
    return ap, ap.parse_args(argv, namespace=Args())


def read_files(files: list[InstructionFile], findings: list[Finding]) -> None:
    """Read each discovered file and record its size, hash and imports."""
    for f in files:
        launch_md = f.loads == "launch" and f.path.name in ("CLAUDE.md", "CLAUDE.local.md")
        text = read_text(f.path, findings, launch_claude_md=launch_md)
        if text is None:
            continue
        f.text = text
        f.lines = len(text.splitlines())
        f.chars = len(text)
        f.sha256 = hashlib.sha256(text.encode()).hexdigest()
        f.imports = [target for _, target in find_imports(text)]


def check_files(ctx: Context, files: list[InstructionFile]) -> None:
    """Loader checks per file, then the cross-file and heuristic checks."""
    script_cache: dict[Path, set[str] | None] = {}
    loaded = [f for f in files if f.text]
    for f in loaded:
        classify(f, ctx, files)
        check_scripts(f, ctx, script_cache)
        check_wording(f, ctx.findings)
    configs = formatter_configs(ctx.project)
    check_duplicates(loaded, ctx.findings)
    check_near_duplicates(loaded, ctx.findings)
    check_conflicting_choices(loaded, ctx.findings)
    for f in loaded:
        check_procedures(f, ctx.findings)
        check_scope_candidates(f, ctx)
        check_discoverable(f, ctx.findings)
        check_formatter_enforced(f, configs, ctx.findings)
        check_negative_only(f, ctx.findings)
        check_time_sensitive(f, ctx.findings)
        check_table_padding(f, ctx.findings)


def imported_line_counts(ctx: Context, files: list[InstructionFile]) -> dict[Path, int]:
    """Check every file's imports; return the lines each file pulls in through them."""
    counts: dict[Path, int] = {}
    for f in files:
        if f.imports:
            walk = ImportWalk(root=f, seen={f.path.resolve()})
            check_imports(ctx, walk, f.path, f.text)
            counts[f.path] = walk.total_lines
    return counts


def relativize(findings: list[Finding], project: Path) -> None:
    """Sort findings and show project files relative to the project, as people refer to them."""
    rank = {s: i for i, s in enumerate(SEVERITIES)}
    findings.sort(key=lambda x: (rank[x.severity], x.path, x.line or 0))
    prefix = str(project) + os.sep
    for x in findings:
        x.path = x.path.removeprefix(prefix)
        x.message = x.message.replace(prefix, "").replace(f"under {project} ", "under the project ")


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    ap, args = parse_args(argv)
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        ap.error(f"--project {project} is not a directory")
    config_dir = args.user_dir or Path(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
    config_dir = config_dir.expanduser().absolute()
    findings: list[Finding] = []
    all_files = walk_files(project, findings)
    ctx = Context(
        project=project,
        user_dir=None if args.no_user or not config_dir.is_dir() else config_dir,
        config_dir=config_dir,
        all_rel=sorted(p.relative_to(project).as_posix() for p in all_files),
        findings=findings,
    )
    files = discover(ctx, all_files)
    read_files(files, findings)
    check_files(ctx, files)
    imported = imported_line_counts(ctx, files)
    launch = [f for f in files if f.loads == "launch" and f.text]
    report = Report(
        ctx=ctx,
        files=files,
        launch_files=len(launch),
        launch_lines=sum(f.lines + imported.get(f.path, 0) for f in launch),
        match_report=match_rules(args.match or [], files, project),
    )
    relativize(findings, project)
    (print_json if args.json else print_text)(report)
    return 1 if any(x.severity == "error" for x in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
