#!/usr/bin/env python3
"""Check how a skill's SKILL.md behaves at run time: substitutions, commands, tools and hooks.

Usage: python3 check-runtime.py <skill-dir> [--previous <check-structure json file>] [--output FILE]

Prints one JSON object on stdout:
  {"script": "check-runtime", "skill": <abs path>, "ran": true,
   "checks": [{"check", "item", "kind", "status", "location", "detail"}], "truncated": <int>}
Diagnostics go to stderr. Exit codes: 0 the script ran (findings included); 2 usage error (no
such folder, no SKILL.md, bad arguments, a --previous file that isn't check-structure's JSON;
a --previous file that doesn't exist is reported on stderr and the folder is walked instead);
1 could not run (an unexpected error, on stderr). With --previous, the files scanned for
network and credential signals are the inventory of that result; without it, the script walks
the skill folder itself.

Check ids and the checklist item each one serves (references/checklist.md):
  R-1  CF-1 proved  no literal $ that substitution would replace: a doubled backslash before
                    $<digit>, $ARGUMENTS or a declared $name, or a money amount such as $1.00
  R-2  CF-1 lead    $<digit>, or $ARGUMENTS or a declared $name inside code, or $<digit> in
                    prose: substituted at invocation; confirm it is meant as a placeholder
  R-3  CF-1 proved  every name declared in arguments is used as $name
  R-4  CF-4 proved  no argument placeholder inside a ! command (a !`...` line or a ```! block)
  R-5  CF-2 lead    a bare Bash (or Bash(*)) in allowed-tools
  R-6  SE-4 lead    the same bare Bash, as an over-broad pre-approval
  R-7  SC-7 proved  every bundled script the body runs is reached through CLAUDE_SKILL_DIR
  R-8  SC-8 proved  every bundled script the body runs has its interpreter as a prefix (a
                    direct call fails; the reviewer judges whether the body says so)
  R-9  BS-4 proved  every path after the CLAUDE_SKILL_DIR variable stays inside the skill
  R-10 CF-3 proved  every Bash(...) pattern in allowed-tools matches a command the body runs
  R-11 CF-3 proved  every script command the body runs matches a Bash(...) pattern, when
                    allowed-tools is set
  R-12 CF-6 proved  frontmatter hook commands reach files through the plugin root, the project
                    folder or the plugin data folder, never CLAUDE_SKILL_DIR or a relative path
  R-13 CF-6 proved  shell-form hook commands double-quote every placeholder
  R-14 CF-6 proved  no onFailure on Stop, SubagentStop, TaskCompleted or TeammateIdle hooks
  R-15 SE-1 lead    network signals in a file (curl, wget, fetch(), requests, urllib, WebFetch,
                    http.client, sockets; URLs too in files other than Markdown)
  R-16 SE-3 lead    reads of credentials or history (~/.ssh, keys, .env, .aws/credentials,
                    .netrc, *_history, keychains, browser profiles)
  R-17 SE-4 lead    an argument placeholder inside a ! command, as shell injection

How commands are found: inline code spans, lines of fenced blocks marked bash, sh, shell, zsh,
console, terminal or unmarked, and ! commands; each is split at &&, ||, ;, | and $(. A script
command is an interpreter (python, python3, bash, sh, zsh, node, deno, bun, ruby, perl, uv run)
followed by a path under scripts/, or such a path run directly (with the variable prefix, ./,
or arguments after it). A Bash(...) pattern matches the whole command: * matches anything, and
a trailing " *" (or the legacy ":*") also matches the command with no arguments. A ! line is
read wherever it is, fenced examples included, because the script can't tell an example from a
command. Signals are grouped per file and kind: one lead per file, at the first line.
--output FILE also writes the same JSON object to FILE (UTF-8, overwritten, parent folders
created), so the next script can read it with --previous without a shell redirect, which
Claude Code checks against its edit rules. stdout is unchanged. If FILE can't be written, the
script prints nothing on stdout, names FILE on stderr and exits 1.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import posixpath
import re
import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

MAX_CHECKS = 200  # the orchestrator reads the whole result inline; 200 short entries stay small
MAX_DETAIL = 300  # characters per detail, so one finding can't flood the output
MAX_FILES = 5000  # chat's plugin upload limit; a larger folder is not a skill to walk whole
MAX_READ = 2 * 1024 * 1024  # bytes of one file scanned for signals; a skill's text files are far
# smaller, and the bound keeps a stray large file from slowing the scan
INDICATORS = "[]{}&*!|>'\"%@`,#"
NAME_RE = re.compile(r"[a-z0-9-]+")
XML_TAG_RE = re.compile(r"<[A-Za-z/!?][^<>]*>")
BLOCK_HEADER_RE = re.compile(r"([|>])([+-]?)([1-9]?)([+-]?)(\s+#.*)?\s*")
KEY_LIKE_RE = re.compile(r"[A-Za-z0-9_][\w.-]*:(\s|$)")
DOUBLE_ESCAPES = {
    "0": "\0",
    "a": "\a",
    "b": "\b",
    "t": "\t",
    "\t": "\t",
    "n": "\n",
    "v": "\v",
    "f": "\f",
    "r": "\r",
    "e": "\x1b",
    " ": " ",
    '"': '"',
    "/": "/",
    "\\": "\\",
    "N": "\x85",
    "_": "\xa0",
    "L": chr(0x2028),
    "P": chr(0x2029),
}
HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def clip(text: str) -> str:
    """Cut a detail to MAX_DETAIL characters."""
    return text if len(text) <= MAX_DETAIL else text[: MAX_DETAIL - 1] + "…"


@dataclass
class Report:
    """Collects check results; passes are added for proved checks that ran without failing."""

    table: dict[str, tuple[str, str]]
    found: list[dict[str, object]] = field(default_factory=list[dict[str, object]])
    applied: dict[str, str] = field(default_factory=dict[str, str])
    failed: set[str] = field(default_factory=set[str])

    def _entry(self, cid: str, status: str, location: str | None, detail: str) -> dict[str, object]:
        item, kind = self.table[cid]
        return {
            "check": cid,
            "item": item,
            "kind": kind,
            "status": status,
            "location": location,
            "detail": clip(detail),
        }

    def fail(self, cid: str, location: str | None, detail: str) -> None:
        """Record a failure of a proved check."""
        if self.table[cid][1] != "proved":
            msg = f"{cid} is a lead check"
            raise ValueError(msg)
        self.failed.add(cid)
        self.found.append(self._entry(cid, "fail", location, detail))

    def lead(self, cid: str, location: str | None, detail: str) -> None:
        """Record a lead for a reviewer."""
        if self.table[cid][1] != "lead":
            msg = f"{cid} is a proved check"
            raise ValueError(msg)
        self.found.append(self._entry(cid, "lead", location, detail))

    def ran(self, cid: str, detail: str) -> None:
        """Mark a proved check as run; it passes with this detail unless it fails."""
        _ = self.applied.setdefault(cid, detail)

    def results(self) -> tuple[list[dict[str, object]], int]:
        """Failures first, then leads, then passes, cut to MAX_CHECKS."""
        fails = [r for r in self.found if r["status"] == "fail"]
        leads = [r for r in self.found if r["status"] == "lead"]
        passes = [
            self._entry(cid, "pass", None, self.applied[cid])
            for cid in self.table
            if cid in self.applied and cid not in self.failed
        ]
        everything = fails + leads + passes
        return everything[:MAX_CHECKS], max(0, len(everything) - MAX_CHECKS)


def at(line: int) -> str:
    """A location in SKILL.md."""
    return f"SKILL.md:{line}"


# ---------------------------------------------------------------------------
# Strict YAML subset
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Scalar:
    """A scalar value: its text, its style and the SKILL.md line it starts on."""

    text: str
    style: str  # plain, single, double, literal, folded, empty
    line: int


type Value = Scalar | list[Value] | dict[str, Value]


class YamlError(Exception):
    """The frontmatter is outside the strict YAML subset."""

    def __init__(self, line: int, message: str) -> None:
        """Keep the line and the message."""
        super().__init__(message)
        self.line: int = line
        self.message: str = message


def indent_of(line: str) -> int:
    """Number of leading spaces."""
    return len(line) - len(line.lstrip(" "))


def skippable(line: str) -> bool:
    """A blank line or a full-line comment."""
    stripped = line.strip()
    return not stripped or stripped.startswith("#")


def is_item(text: str) -> bool:
    """A block list item marker."""
    return text == "-" or text.startswith("- ")


def decode_double(raw: str, line: int) -> tuple[str, str] | None:
    """Decode a double-quoted scalar at the start of raw: (value, rest after the quote)."""
    out: list[str] = []
    i = 1
    while i < len(raw):
        c = raw[i]
        if c == '"':
            return "".join(out), raw[i + 1 :]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        esc = raw[i + 1 : i + 2]
        if esc in DOUBLE_ESCAPES:
            out.append(DOUBLE_ESCAPES[esc])
            i += 2
        elif esc in HEX_ESCAPES:
            width = HEX_ESCAPES[esc]
            digits = raw[i + 2 : i + 2 + width]
            if len(digits) != width or not all(d in "0123456789abcdefABCDEF" for d in digits):
                raise YamlError(line, f"bad \\{esc} escape in a double-quoted value")
            out.append(chr(int(digits, 16)))
            i += 2 + width
        else:
            raise YamlError(line, f"unknown escape \\{esc} in a double-quoted value")
    return None


def decode_single(raw: str) -> tuple[str, str] | None:
    """Decode a single-quoted scalar at the start of raw: (value, rest after the quote)."""
    out: list[str] = []
    i = 1
    while i < len(raw):
        c = raw[i]
        if c == "'" and raw[i + 1 : i + 2] == "'":
            out.append("'")
            i += 2
        elif c == "'":
            return "".join(out), raw[i + 1 :]
        else:
            out.append(c)
            i += 1
    return None


def decode_quoted(raw: str, line: int) -> tuple[str, str] | None:
    """Decode a quoted scalar of either style at the start of raw."""
    return decode_double(raw, line) if raw.startswith('"') else decode_single(raw)


def clean_rest(rest: str) -> bool:
    """Nothing but whitespace or a comment follows a value."""
    stripped = rest.strip()
    return not stripped or (stripped.startswith("#") and rest[:1] in (" ", "\t"))


def split_key(text: str, line: int) -> tuple[str, str] | None:
    """Split 'key: rest' into the key and the rest, or None when text is no key line."""
    if text[:1] in ('"', "'"):
        decoded = decode_quoted(text, line)
        if decoded is None:
            return None
        key, rem = decoded
        if rem.startswith(":") and rem[1:2] in ("", " ", "\t"):
            return key, rem[1:]
        return None
    if not text or text[0] in INDICATORS or is_item(text) or text.startswith("? "):
        return None
    match = re.search(r":(\s|$)", text)
    key = text[: match.start()].rstrip() if match else ""
    if not match or not key or " #" in key:
        return None
    return key, text[match.start() + 1 :]


class Flow:
    """A flow list or map on one line: [a, b] or {k: v}."""

    def __init__(self, text: str, line: int) -> None:
        """Parse text from its first character."""
        self.text: str = text
        self.line: int = line
        self.i: int = 0

    def peek(self) -> str:
        """The next character, or '' at the end."""
        return self.text[self.i : self.i + 1]

    def spaces(self) -> None:
        """Skip spaces."""
        while self.peek() in (" ", "\t") and self.peek():
            self.i += 1

    def parse(self) -> Value | None:
        """The parsed collection, or None when it isn't a complete flow collection."""
        try:
            value = self.node(in_map=False)
        except YamlError:
            return None
        return value if clean_rest(self.text[self.i :]) else None

    def node(self, *, in_map: bool) -> Value:
        """One flow node."""
        self.spaces()
        c = self.peek()
        if c == "[":
            return self.sequence()
        if c == "{":
            return self.mapping()
        if c in ('"', "'"):
            decoded = decode_quoted(self.text[self.i :], self.line)
            if decoded is None:
                raise YamlError(self.line, "unclosed quote")
            self.i = len(self.text) - len(decoded[1])
            return Scalar(decoded[0], "double" if c == '"' else "single", self.line)
        return self.plain(in_map=in_map)

    def plain(self, *, in_map: bool) -> Scalar:
        """A plain scalar inside a flow collection."""
        start = self.i
        while self.peek() and self.peek() not in ",[]{}":
            if in_map and self.peek() == ":" and self.text[self.i + 1 : self.i + 2] in " ,]}":
                break
            self.i += 1
        text = self.text[start : self.i].strip()
        if not text:
            raise YamlError(self.line, "empty flow entry")
        return Scalar(text, "plain", self.line)

    def sequence(self) -> list[Value]:
        """A flow list."""
        self.i += 1
        items: list[Value] = []
        while True:
            self.spaces()
            if self.peek() == "]":
                self.i += 1
                return items
            items.append(self.node(in_map=False))
            self.separator("]")

    def mapping(self) -> dict[str, Value]:
        """A flow map."""
        self.i += 1
        result: dict[str, Value] = {}
        while True:
            self.spaces()
            if self.peek() == "}":
                self.i += 1
                return result
            key = self.node(in_map=True)
            self.spaces()
            if not isinstance(key, Scalar) or self.peek() != ":":
                raise YamlError(self.line, "flow map entry without key: value")
            self.i += 1
            self.spaces()
            if self.peek() in (",", "}"):
                result[key.text] = Scalar("", "empty", self.line)
            else:
                result[key.text] = self.node(in_map=True)
            self.separator("}")

    def separator(self, close: str) -> None:
        """A comma, or the closing bracket left for the caller."""
        self.spaces()
        if self.peek() == ",":
            self.i += 1
        elif self.peek() != close:
            raise YamlError(self.line, "expected ',' or a closing bracket")


def fold(segments: list[tuple[int, str]]) -> str:
    """Fold block lines: (blank lines before, text) pairs joined by spaces or newlines."""
    out = ""
    for index, (blanks, text) in enumerate(segments):
        if index == 0:
            out = "\n" * blanks + text
        elif blanks:
            out += "\n" * blanks + text
        elif text.startswith((" ", "\t")) or segments[index - 1][1].startswith((" ", "\t")):
            out += "\n" + text
        else:
            out += " " + text
    return out


class Parser:
    """Recursive parser for the strict YAML subset, over the frontmatter lines."""

    def __init__(self, lines: list[str], first_line: int) -> None:
        """Lines are the frontmatter without its --- lines; first_line is lines[0]'s number."""
        self.lines: list[str] = list(lines)
        self.first: int = first_line
        self.pos: int = 0

    def number(self, index: int) -> int:
        """The SKILL.md line number of a frontmatter line index."""
        return self.first + index

    def skip(self) -> None:
        """Move past blank and comment lines."""
        while self.pos < len(self.lines) and skippable(self.lines[self.pos]):
            self.pos += 1

    def current(self) -> tuple[int, str]:
        """The indentation and the text of the current line; tabs in indentation don't parse."""
        line = self.lines[self.pos]
        lead = line[: len(line) - len(line.lstrip(" \t"))]
        if "\t" in lead:
            raise YamlError(self.number(self.pos), "tab used for indentation")
        width = indent_of(line)
        return width, line[width:]

    def document(self) -> dict[str, Value]:
        """The whole frontmatter: a mapping at column 1."""
        self.skip()
        if self.pos >= len(self.lines):
            return {}
        width, _ = self.current()
        if width:
            raise YamlError(self.number(self.pos), "the first key must start at column 1")
        result = self.mapping(0)
        self.skip()
        if self.pos < len(self.lines):
            raise YamlError(self.number(self.pos), "unexpected indentation or line")
        return result

    def mapping(self, width: int) -> dict[str, Value]:
        """A block mapping whose keys start at column width."""
        result: dict[str, Value] = {}
        while True:
            self.skip()
            if self.pos >= len(self.lines):
                return result
            here, text = self.current()
            if here < width or (here == width and is_item(text)):
                return result
            line = self.number(self.pos)
            if here > width:
                raise YamlError(line, "unexpected indentation")
            split = split_key(text, line)
            if split is None:
                raise YamlError(line, "expected 'key: value'")
            key, rest = split
            if key in result:
                raise YamlError(line, f"duplicate key {key!r}")
            start = self.pos
            self.pos += 1
            result[key] = self.value(rest, width, start)

    def sequence(self, width: int) -> list[Value]:
        """A block list whose dashes start at column width."""
        items: list[Value] = []
        while True:
            self.skip()
            if self.pos >= len(self.lines):
                return items
            here, text = self.current()
            if here < width or not is_item(text):
                if here > width:
                    raise YamlError(self.number(self.pos), "unexpected indentation")
                return items
            if here > width:
                raise YamlError(self.number(self.pos), "unexpected indentation")
            items.append(self.item(width, text))

    def item(self, width: int, text: str) -> Value:
        """One list item: a nested block, a map starting on the dash line, or a value."""
        content = text[1:].lstrip(" ")
        start = self.pos
        line = self.number(start)
        if skippable(content):
            self.pos += 1
            return self.nested(width, start, same_width_list=False)
        if split_key(content, line) is not None:
            column = width + len(text) - len(content)
            self.lines[self.pos] = " " * column + content
            return self.mapping(column)
        self.pos += 1
        return self.value(content, width, start)

    def nested(self, width: int, start: int, *, same_width_list: bool) -> Value:
        """The block under a key or a dash with nothing after it, or an empty value."""
        self.skip()
        if self.pos < len(self.lines):
            here, text = self.current()
            if is_item(text) and (here > width or (same_width_list and here == width)):
                return self.sequence(here)
            if here > width:
                return self.mapping(here)
        return Scalar("", "empty", self.number(start))

    def value(self, rest: str, width: int, start: int) -> Value:
        """The value after 'key:' (or after a dash), starting at line index start."""
        text = rest.strip()
        line = self.number(start)
        if skippable(text):
            return self.nested(width, start, same_width_list=True)
        if text[0] in "|>" and BLOCK_HEADER_RE.fullmatch(text):
            return self.block(text, width, line)
        if text[0] in ('"', "'"):
            quoted = self.quoted(text, width, start)
            if quoted is not None:
                return quoted
        if text[0] in "[{":
            flow = Flow(text, line).parse()
            if flow is not None:
                return flow
        return self.plain(text, width, line)

    def quoted(self, text: str, width: int, start: int) -> Scalar | None:
        """A quoted scalar, possibly over several lines; None when text follows the quote."""
        line = self.number(start)
        raw = text
        while True:
            decoded = decode_quoted(raw, line)
            if decoded is not None:
                value, rest = decoded
                if not clean_rest(rest):
                    return None
                return Scalar(value, "double" if text[0] == '"' else "single", line)
            if self.pos >= len(self.lines):
                raise YamlError(line, "unclosed quote")
            following = self.lines[self.pos]
            if following.strip() and indent_of(following) <= width:
                raise YamlError(line, "unclosed quote")
            raw += (" " + following.strip()) if following.strip() else "\n"
            self.pos += 1

    def plain(self, text: str, width: int, line: int) -> Scalar:
        """A plain scalar, continued on more-indented lines."""
        value = text
        newlines = 0
        while self.pos < len(self.lines):
            following = self.lines[self.pos]
            stripped = following.strip()
            if not stripped:
                newlines += 1
                self.pos += 1
                continue
            if stripped.startswith("#") or indent_of(following) <= width:
                break
            if KEY_LIKE_RE.match(stripped):
                raise YamlError(self.number(self.pos), "a key indented under a scalar value")
            value += ("\n" * newlines if newlines else " ") + stripped
            newlines = 0
            self.pos += 1
        return Scalar(value, "plain", line)

    def block(self, header: str, width: int, line: int) -> Scalar:
        """A literal or folded block scalar."""
        match = BLOCK_HEADER_RE.fullmatch(header)
        style, chomp_a, digit, chomp_b = match.groups()[:4] if match else ("|", "", "", "")
        chomp = chomp_a or chomp_b
        block_width = width + int(digit) if digit else 0
        collected: list[str] = []
        while self.pos < len(self.lines):
            following = self.lines[self.pos]
            if following.strip():
                if not block_width:
                    block_width = indent_of(following)
                if indent_of(following) < block_width or block_width <= width:
                    break
                collected.append(following[block_width:])
            else:
                collected.append("")
            self.pos += 1
        trailing = len(collected) - len("\n".join(collected).rstrip("\n").split("\n"))
        body = collected[: len(collected) - trailing] if any(collected) else []
        trailing = len(collected) - len(body)
        text = "\n".join(body) if style == "|" else fold(segments(body))
        if chomp == "-" or not text:
            final = text
        elif chomp == "+":
            final = text + "\n" + "\n" * trailing
        else:
            final = text + "\n"
        return Scalar(final, "literal" if style == "|" else "folded", line)


def segments(body: list[str]) -> list[tuple[int, str]]:
    """Pair each non-blank block line with the number of blank lines before it."""
    out: list[tuple[int, str]] = []
    blanks = 0
    for text in body:
        if text.strip():
            out.append((blanks, text))
            blanks = 0
        else:
            blanks += 1
    return out


# ---------------------------------------------------------------------------
# Runtime constants
# ---------------------------------------------------------------------------

CHECKS: dict[str, tuple[str, str]] = {
    "R-1": ("CF-1", "proved"),
    "R-2": ("CF-1", "lead"),
    "R-3": ("CF-1", "proved"),
    "R-4": ("CF-4", "proved"),
    "R-5": ("CF-2", "lead"),
    "R-6": ("SE-4", "lead"),
    "R-7": ("SC-7", "proved"),
    "R-8": ("SC-8", "proved"),
    "R-9": ("BS-4", "proved"),
    "R-10": ("CF-3", "proved"),
    "R-11": ("CF-3", "proved"),
    "R-12": ("CF-6", "proved"),
    "R-13": ("CF-6", "proved"),
    "R-14": ("CF-6", "proved"),
    "R-15": ("SE-1", "lead"),
    "R-16": ("SE-3", "lead"),
    "R-17": ("SE-4", "lead"),
}
SKILL_DIR = "${CLAUDE_SKILL_DIR}"
INTERPRETERS = frozenset(
    {"python", "python3", "bash", "sh", "zsh", "node", "deno", "bun", "ruby", "perl"}
)
SHELL_FENCES = frozenset({"", "bash", "sh", "shell", "zsh", "console", "terminal", "!"})
STOP_EVENTS = frozenset({"Stop", "SubagentStop", "TaskCompleted", "TeammateIdle"})
HOOK_ROOTS = ("CLAUDE_PLUGIN_ROOT", "CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_DATA")
SCRIPT_SUFFIXES = (".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl")

FENCE_RE = re.compile(r" {0,3}(`{3,}|~{3,})\s*([^`\s]*)")
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
BANG_LINE_RE = re.compile(r"\s*!`([^`]+)`")
SPLIT_RE = re.compile(r"&&|\|\||;|\||\$\(")
SKILL_DIR_PATH_RE = re.compile(r"\$\{CLAUDE_SKILL_DIR\}((?:/[^\s`'\"()<>\[\]]*)?)")
PLACEHOLDER_IN_HOOK_RE = re.compile(r"\$\{?CLAUDE_\w+\}?")
MONEY_RE = re.compile(r"[.,]\d")
NETWORK_PATTERN = (
    r"\b(curl|wget|WebFetch|urllib|http\.client|Invoke-WebRequest)\b"
    r"|\brequests\.(?:get|post|put|patch|delete|head|Session)\b|\bfetch\(|\bsocket\.socket\b"
)
NETWORK_RE = re.compile(NETWORK_PATTERN)
URL_RE = re.compile(r"\bhttps?://")
CREDENTIAL_PATTERN = (
    r"~/\.ssh|\.ssh/|\bid_(?:rsa|ed25519|ecdsa|dsa)\b|(?<![\w.])\.env(?![\w-])"
    r"|\.aws/credentials|\.netrc\b|\w_history\b|\bkeychain\b|find-(?:generic|internet)-password"
    r"|Google/Chrome|BraveSoftware|\.mozilla/firefox|\.config/(?:google-chrome|chromium)"
    r"|Login Data|\.npmrc\b|\.pypirc\b|\.docker/config\.json|\.kube/config"
)
CREDENTIAL_RE = re.compile(CREDENTIAL_PATTERN, re.IGNORECASE)


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


# ---------------------------------------------------------------------------
# SKILL.md
# ---------------------------------------------------------------------------


@dataclass
class Body:
    """SKILL.md split into frontmatter fields and body lines with code marked."""

    fields: dict[str, Value]
    key_lines: dict[str, int]
    lines: list[tuple[int, str]]
    in_code: dict[int, list[tuple[int, int]]] = field(
        default_factory=dict[int, list[tuple[int, int]]]
    )
    fenced: set[int] = field(default_factory=set[int])
    fence_lang: dict[int, str] = field(default_factory=dict[int, str])

    def is_code(self, number: int, column: int) -> bool:
        """Whether a column of a body line is inside a fence or an inline code span."""
        if number in self.fenced:
            return True
        return any(a <= column < b for a, b in self.in_code.get(number, []))


def split_frontmatter(text: str) -> tuple[list[str], int, list[str], int]:
    """Frontmatter lines and their first line number; body lines and theirs."""
    lines = text.splitlines()
    if lines and lines[0].rstrip() == "---":
        for index in range(1, len(lines)):
            if lines[index].rstrip() == "---":
                return lines[1:index], 2, lines[index + 1 :], index + 2
    return [], 1, lines, 1


def top_key_lines(lines: list[str], first: int) -> dict[str, int]:
    """The SKILL.md line of each top-level key."""
    found: dict[str, int] = {}
    for index, line in enumerate(lines):
        if line[:1] not in ("", " ", "#", "-"):
            split = split_key(line, first + index)
            if split is not None:
                _ = found.setdefault(split[0], first + index)
    return found


def mark_code(body: Body) -> None:
    """Record fenced lines, their fence's language, and inline code spans."""
    fence = ""
    lang = ""
    for number, line in body.lines:
        opener = FENCE_RE.match(line)
        if fence:
            if opener and opener.group(1)[0] == fence[0] and len(opener.group(1)) >= len(fence):
                fence = ""
            else:
                body.fenced.add(number)
                body.fence_lang[number] = lang
        elif opener:
            fence, lang = opener.group(1), opener.group(2).lower()
        else:
            body.in_code[number] = [(m.start(), m.end()) for m in CODE_SPAN_RE.finditer(line)]


def parse_skill(text: str) -> Body:
    """Parse SKILL.md; a frontmatter outside the strict subset gives no fields."""
    fm, fm_first, body_lines, body_first = split_frontmatter(text)
    try:
        fields = Parser(fm, fm_first).document()
    except YamlError as error:
        _ = sys.stderr.write(f"check-runtime: frontmatter not parsed ({error.message})\n")
        fields = {}
    numbered = [(body_first + i, line) for i, line in enumerate(body_lines)]
    body = Body(fields, top_key_lines(fm, fm_first), numbered)
    mark_code(body)
    return body


def words(value: Value | None) -> list[tuple[str, int]]:
    """A list field or a space- or comma-separated string, with each entry's line."""
    if isinstance(value, list):
        return [(v.text.strip(), v.line) for v in value if isinstance(v, Scalar) and v.text.strip()]
    if not isinstance(value, Scalar):
        return []
    return [(w, value.line) for w in tool_tokens(value.text)]


def tool_tokens(text: str) -> list[str]:
    """Split on spaces and commas outside parentheses."""
    tokens: list[str] = []
    depth = 0
    current = ""
    for char in text:
        depth += (char == "(") - (char == ")")
        if depth <= 0 and char in " ,\t\n":
            if current:
                tokens.append(current)
            current = ""
        else:
            current += char
    return [*tokens, current] if current else tokens


def argument_names(body: Body) -> list[str]:
    """The names declared in arguments."""
    return [w for w, _ in words(body.fields.get("arguments")) if re.fullmatch(r"[\w-]+", w)]


def backslashes_before(text: str, index: int) -> int:
    """How many backslashes directly precede index."""
    count = 0
    while index - count - 1 >= 0 and text[index - count - 1] == "\\":
        count += 1
    return count


def placeholder_re(names: list[str]) -> re.Pattern[str]:
    """$<digit>, $ARGUMENTS (with an optional [N]) or a declared $name."""
    named = "".join(f"|{re.escape(n)}\\b" for n in sorted(names, key=len, reverse=True))
    return re.compile(r"\$(?:ARGUMENTS\b(?:\[\d+\])?|\d+" + named + ")")


# ---------------------------------------------------------------------------
# Substitutions and ! commands
# ---------------------------------------------------------------------------


def bang_commands(body: Body) -> Iterator[tuple[int, str]]:
    """Every ! command: a !`...` line or a line of a ```! block."""
    for number, line in body.lines:
        match = BANG_LINE_RE.match(line)
        if match:
            yield number, match.group(1)
        elif number in body.fenced and body.fence_lang.get(number) == "!":
            yield number, line


def check_dollars(report: Report, body: Body, pattern: re.Pattern[str]) -> None:
    """R-1 and R-2: $ that substitution would replace."""
    report.ran("R-1", "no literal $ that substitution would replace")
    bang = {number for number, _ in bang_commands(body)}
    for number, line in body.lines:
        for match in pattern.finditer(line):
            slashes = backslashes_before(line, match.start())
            token = match.group(0)
            where = at(number)
            if slashes == 1:
                continue
            if slashes > 1:
                report.fail("R-1", where, f"a doubled backslash doesn't escape {token}; use one")
            elif token[1:].isdigit() and MONEY_RE.match(line, match.end()):
                report.fail("R-1", where, f"{token} looks like an amount; write \\{token}")
            elif number not in bang and (
                body.is_code(number, match.start()) or token[1:].isdigit()
            ):
                report.lead("R-2", where, f"{token} is substituted at invocation; escape a literal")


def check_argument_use(report: Report, body: Body, names: list[str]) -> None:
    """R-3: every declared name is used as $name."""
    if not names:
        return
    report.ran("R-3", "every declared argument is used")
    text = "\n".join(line for _, line in body.lines)
    for name in names:
        uses = [
            m
            for m in re.finditer(r"\$" + re.escape(name) + r"\b", text)
            if backslashes_before(text, m.start()) != 1
        ]
        if not uses:
            line = body.key_lines.get("arguments", 1)
            report.fail(
                "R-3", at(line), f"arguments declares {name!r} but the body never uses ${name}"
            )


def check_bang(report: Report, body: Body, pattern: re.Pattern[str]) -> None:
    """R-4 and R-17: no argument placeholder inside a ! command."""
    report.ran("R-4", "no argument placeholder inside a ! command")
    for number, command in bang_commands(body):
        found = [
            m.group(0)
            for m in pattern.finditer(command)
            if backslashes_before(command, m.start()) != 1
        ]
        if found:
            detail = f"{found[0]} inside a ! command runs user text in the shell; pass it in prose"
            report.fail("R-4", at(number), detail)
            report.lead("R-17", at(number), detail)


# ---------------------------------------------------------------------------
# Commands, scripts and allowed-tools
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Call:
    """A bundled script the body runs."""

    line: int
    command: str
    interpreter: str
    path: str
    via_skill_dir: bool


def candidates(body: Body) -> list[tuple[int, str]]:
    """Command texts: inline code, shell fence lines and ! commands, split at operators."""
    texts: list[tuple[int, str]] = []
    for number, line in body.lines:
        if number in body.fenced:
            if body.fence_lang.get(number, "") in SHELL_FENCES:
                texts.append((number, line))
        else:
            texts += [(number, line[a:b].strip("`")) for a, b in body.in_code.get(number, [])]
    texts += [(n, c) for n, c in bang_commands(body) if (n, c) not in texts]
    pieces: list[tuple[int, str]] = []
    for number, text in texts:
        for piece in SPLIT_RE.split(text):
            cleaned = piece.strip().removeprefix("$ ").strip()
            if cleaned:
                pieces.append((number, cleaned))
    return pieces


def script_path(token: str) -> tuple[str, bool] | None:
    """The skill-relative path of a script token and whether it uses the variable."""
    path = token.strip("'\"")
    via = path.startswith(SKILL_DIR + "/")
    rel = path[len(SKILL_DIR) + 1 :] if via else path.removeprefix("./")
    return (rel, via) if rel.startswith("scripts/") and len(rel) > len("scripts/") else None


def script_call(number: int, command: str) -> Call | None:
    """The script call in one command, if any."""
    tokens = command.split()
    index = 0
    interpreter = ""
    if tokens and (tokens[0] in INTERPRETERS or tokens[:2] == ["uv", "run"]):
        interpreter = tokens[0]
        index = 2 if tokens[0] == "uv" else 1
        while index < len(tokens) and tokens[index].startswith("-"):
            index += 1
    if index >= len(tokens):
        return None
    found = script_path(tokens[index])
    if found is None:
        return None
    rel, via = found
    direct_ok = via or tokens[index].startswith("./") or len(tokens) > index + 1
    if not interpreter and not direct_ok:
        return None
    return Call(number, command, interpreter, rel, via)


def check_calls(report: Report, calls: list[Call]) -> None:
    """R-7 and R-8: how scripts are called."""
    report.ran("R-7", "every script call goes through CLAUDE_SKILL_DIR")
    report.ran("R-8", "every script call has its interpreter as a prefix")
    for call in calls:
        if not call.via_skill_dir:
            detail = f"{call.path} isn't reached through {SKILL_DIR}; commands run elsewhere"
            report.fail("R-7", at(call.line), detail)
        if not call.interpreter:
            detail = (
                f"{call.path} runs directly; call it with its interpreter, "
                "or say so and pre-approve that exact form"
            )
            report.fail("R-8", at(call.line), detail)


def check_skill_dir_paths(report: Report, text: str) -> None:
    """R-9: every path after the variable stays inside the skill."""
    report.ran("R-9", "every CLAUDE_SKILL_DIR path stays inside the skill")
    for index, line in enumerate(text.splitlines()):
        for match in SKILL_DIR_PATH_RE.finditer(line):
            rest = match.group(1).lstrip("/")
            if rest and posixpath.normpath(rest).startswith(".."):
                report.fail("R-9", at(index + 1), f"{match.group(0)[:80]} leaves the skill folder")


def pattern_regex(pattern: str) -> re.Pattern[str]:
    """A Bash(...) rule as a regex over the whole command line."""
    core = pattern
    tail = ""
    if core.endswith(":*"):
        core = core[:-2] + " *"
    if core.endswith(" *"):
        core = core[:-2]
        tail = r"(?: .*)?"
    return re.compile(".*".join(re.escape(part) for part in core.split("*")) + tail, re.DOTALL)


def check_patterns(
    report: Report, body: Body, pieces: list[tuple[int, str]], calls: list[Call]
) -> None:
    """R-10 and R-11: Bash(...) patterns against the commands the body runs."""
    tools = words(body.fields.get("allowed-tools"))
    if not tools:
        return
    bare = [(t, line) for t, line in tools if t in ("Bash", "Bash(*)")]
    for token, line in bare:
        report.lead(
            "R-5", at(line), f"{token} pre-approves every shell command; name exact commands"
        )
        report.lead("R-6", at(line), f"{token} is an over-broad pre-approval")
    rules = [
        (t[5:-1].strip(), line)
        for t, line in tools
        if t.startswith("Bash(") and t.endswith(")") and t != "Bash(*)"
    ]
    compiled = [(rule, line, pattern_regex(rule)) for rule, line in rules]
    report.ran("R-10", "every Bash() pattern matches a command the body runs")
    for rule, line, regex in compiled:
        if not any(regex.fullmatch(text) for _, text in pieces):
            report.fail("R-10", at(line), f"Bash({rule[:120]}) matches no command the body runs")
    report.ran("R-11", "every script command matches a Bash() pattern")
    for call in calls if not bare else []:
        if not any(regex.fullmatch(call.command) for _, _, regex in compiled):
            report.fail(
                "R-11",
                at(call.line),
                f"{call.command[:120]} matches no Bash() pattern in allowed-tools; it will prompt",
            )


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hook:
    """One hook entry of the frontmatter."""

    event: str
    fields: dict[str, Value]


def hooks_of(body: Body) -> list[Hook]:
    """Every hook entry: hooks -> event -> groups -> hooks."""
    found: list[Hook] = []
    events = body.fields.get("hooks")
    if not isinstance(events, dict):
        return found
    for event, groups in events.items():
        for group in groups if isinstance(groups, list) else []:
            entries = group.get("hooks") if isinstance(group, dict) else None
            listed = entries if isinstance(entries, list) else []
            found.extend(Hook(event, entry) for entry in listed if isinstance(entry, dict))
    return found


def unquoted_placeholders(command: str) -> list[str]:
    """Placeholders outside double quotes in a shell command."""
    found: list[str] = []
    quote = ""
    index = 0
    while index < len(command):
        char = command[index]
        if char == "\\" and quote != "'":
            index += 2
            continue
        if char in "\"'" and (not quote or quote == char):
            quote = "" if quote else char
        match = PLACEHOLDER_IN_HOOK_RE.match(command, index) if char == "$" else None
        if match and quote != '"':
            found.append(match.group(0))
        index += 1
    return found


def bad_path(token: str) -> bool:
    """A path token that doesn't start from a hook root variable."""
    clean = token.strip("'\"\\")
    if not clean or "://" in clean or clean.startswith("$"):
        return False
    relative = clean.startswith(("./", "../", "~")) or bool(
        re.fullmatch(r"[\w.-]+/[\w./-]+", clean)
    )
    personal = clean.startswith(("/home/", "/Users/"))
    return relative or personal or clean.endswith(SCRIPT_SUFFIXES)


def hook_texts(hook: Hook) -> tuple[Scalar | None, list[str]]:
    """The command scalar and every command or argument text."""
    command = hook.fields.get("command")
    scalar = command if isinstance(command, Scalar) else None
    args = hook.fields.get("args")
    texts = [scalar.text] if scalar else []
    texts += [a.text for a in args if isinstance(a, Scalar)] if isinstance(args, list) else []
    return scalar, texts


def check_hook(report: Report, hook: Hook) -> None:
    """R-12 to R-14 for one hook."""
    scalar, texts = hook_texts(hook)
    where = at(scalar.line) if scalar else at(1)
    if any("CLAUDE_SKILL_DIR" in t for t in texts):
        report.fail(
            "R-12", where, "hook commands don't get CLAUDE_SKILL_DIR; use CLAUDE_PLUGIN_ROOT"
        )
    else:
        for token in (tok for t in texts for tok in t.split()):
            if bad_path(token):
                detail = (
                    f"{token[:80]} isn't reached through "
                    "CLAUDE_PLUGIN_ROOT, CLAUDE_PROJECT_DIR or CLAUDE_PLUGIN_DATA"
                )
                report.fail("R-12", where, detail)
                break
    if scalar and "args" not in hook.fields:
        loose = unquoted_placeholders(scalar.text)
        if loose:
            detail = (
                f"{loose[0]} is unquoted in shell form; wrap it in double "
                "quotes or use exec form (args)"
            )
            report.fail("R-13", where, detail)
    failure = hook.fields.get("onFailure")
    if failure is not None and hook.event in STOP_EVENTS:
        line = failure.line if isinstance(failure, Scalar) else 1
        report.fail("R-14", at(line), f"onFailure has no effect on {hook.event} hooks")


def check_hooks(report: Report, body: Body) -> None:
    """R-12 to R-14."""
    hooks = hooks_of(body)
    if not hooks:
        return
    report.ran("R-12", "hook commands use the plugin or project root")
    report.ran("R-13", "shell-form hook commands quote every placeholder")
    report.ran("R-14", "no onFailure on Stop-type events")
    for hook in hooks:
        check_hook(report, hook)


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str | None:
    """The first MAX_READ bytes of a text file, or None for a binary or unreadable file."""
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_READ)
    except OSError as error:
        _ = sys.stderr.write(f"check-runtime: could not read {path.name}: {error}\n")
        return None
    if len(data) == MAX_READ:
        _ = sys.stderr.write(
            f"check-runtime: {path.name}: only the first {MAX_READ} bytes scanned\n"
        )
    return None if b"\0" in data else data.decode("utf-8", errors="replace")


def signal_lead(report: Report, cid: str, rel: str, hits: list[tuple[int, str]]) -> None:
    """One lead per file and kind, at the first line, naming what was found."""
    if not hits:
        return
    counts: dict[str, int] = {}
    for _, name in hits:
        counts[name] = counts.get(name, 0) + 1
    names = ", ".join(f"{n} x{c}" for n, c in sorted(counts.items()))
    kind = "network" if cid == "R-15" else "credential or history"
    report.lead(
        cid, f"{rel}:{hits[0][0]}", f"{kind} signals: {names}; check against the description"
    )


def check_signals(report: Report, root: Path, files: list[str]) -> None:
    """R-15 and R-16 over every file."""
    for rel in files:
        text = read_text(root / rel)
        if text is None:
            continue
        network: list[tuple[int, str]] = []
        credentials: list[tuple[int, str]] = []
        markdown = rel.lower().endswith(".md")
        for index, line in enumerate(text.splitlines()):
            network += [(index + 1, m.group(0)) for m in NETWORK_RE.finditer(line)]
            if not markdown:
                network += [(index + 1, m.group(0)) for m in URL_RE.finditer(line)]
            credentials += [(index + 1, m.group(0)) for m in CREDENTIAL_RE.finditer(line)]
        signal_lead(report, "R-15", rel, network)
        signal_lead(report, "R-16", rel, credentials)


# ---------------------------------------------------------------------------
# Files and main
# ---------------------------------------------------------------------------


class UsageError(Exception):
    """A bad argument: exit 2."""


def walk(root: Path) -> list[str]:
    """Every file under the skill, hidden ones included, sorted, up to MAX_FILES."""
    found: list[str] = []
    for folder, dirs, names in os.walk(root):
        dirs.sort()
        found += [(Path(folder) / n).relative_to(root).as_posix() for n in names]
    found.sort()
    if len(found) > MAX_FILES:
        _ = sys.stderr.write(
            f"check-runtime: {len(found) - MAX_FILES} files past {MAX_FILES} not scanned\n"
        )
    return found[:MAX_FILES]


def inventory_paths(previous: Path) -> list[str]:
    """The inventory paths of a check-structure result."""
    try:
        data = _decode(previous.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        msg = f"--previous {previous}: not readable JSON ({error})"
        raise UsageError(msg) from error
    inventory = data.get("inventory") if isinstance(data, JsonObject) else None
    if not isinstance(inventory, list):
        msg = f"--previous {previous}: no inventory list; pass check-structure's output"
        raise UsageError(msg)
    paths: list[str] = []
    for entry in cast("list[object]", inventory):
        path = entry.get("path") if isinstance(entry, JsonObject) else None
        if isinstance(path, str) and not posixpath.isabs(path) and not path.startswith(".."):
            paths.append(path)
    return paths


def run_checks(report: Report, root: Path, text: str, files: list[str]) -> None:
    """Every check, in id order."""
    body = parse_skill(text)
    names = argument_names(body)
    pattern = placeholder_re(names)
    check_dollars(report, body, pattern)
    check_argument_use(report, body, names)
    check_bang(report, body, pattern)
    pieces = candidates(body)
    calls = [c for c in (script_call(n, t) for n, t in pieces) if c is not None]
    check_calls(report, calls)
    check_skill_dir_paths(report, text)
    check_patterns(report, body, pieces, calls)
    check_hooks(report, body)
    check_signals(report, root, files)


def emit(text: str, output: Path | None) -> int:
    """Write the result to --output FILE when given, then to stdout; 1 if FILE can't be written."""
    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _ = output.write_text(text, encoding="utf-8", newline="")
        except OSError as error:
            _ = sys.stderr.write(
                f"check-runtime: --output {output}: could not write the result: {error}\n"
            )
            return 1
    _ = sys.stdout.write(text)
    return 0


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    skill_dir: Path = Path()
    previous: Path | None = None
    output: Path | None = None


def parse_args(argv: list[str] | None) -> Args:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        prog="check-runtime.py",
        description="Check a skill's substitutions, commands, tools and hooks; print JSON.",
        epilog=(
            "Example: python3 check-runtime.py path/to/my-skill --previous structure.json\n"
            "Exit codes: 0 ran (findings are in the JSON), 2 usage error, 1 could not run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("skill_dir", type=Path, help="the skill folder (holds SKILL.md)")
    _ = parser.add_argument(
        "--previous",
        type=Path,
        help="check-structure's JSON result; its inventory is the file list",
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="also write the JSON result to FILE (parent folders created, overwritten)",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str] | None = None) -> int:
    """Run the checks and print the JSON result."""
    args = parse_args(argv)
    root = args.skill_dir.expanduser()
    if not root.is_dir():
        _ = sys.stderr.write(f"check-runtime: no such folder: {root}\n")
        return 2
    root = root.resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        _ = sys.stderr.write(f"check-runtime: {root} has no SKILL.md; pass the skill folder\n")
        return 2
    try:
        if args.previous and not args.previous.exists():
            missing = f"check-runtime: --previous {args.previous} doesn't exist"
            _ = sys.stderr.write(f"{missing}; walking the skill folder instead\n")
            args.previous = None
        files = inventory_paths(args.previous) if args.previous else walk(root)
        text = skill_md.read_bytes().decode("utf-8", errors="replace")
    except UsageError as error:
        _ = sys.stderr.write(f"check-runtime: {error}\n")
        return 2
    except OSError as error:
        _ = sys.stderr.write(f"check-runtime: could not read the skill: {error}\n")
        return 1
    report = Report(CHECKS)
    run_checks(report, root, text, files)
    checks, truncated = report.results()
    result: dict[str, object] = {
        "script": "check-runtime",
        "skill": str(root),
        "ran": True,
        "checks": checks,
        "truncated": truncated,
    }
    return emit(json.dumps(result, indent=1) + "\n", args.output)


if __name__ == "__main__":
    raise SystemExit(main())
