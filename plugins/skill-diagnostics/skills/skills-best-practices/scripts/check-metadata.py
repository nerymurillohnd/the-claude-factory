#!/usr/bin/env python3
"""Check a skill's SKILL.md frontmatter: placement, strict YAML, name, description and fields.

Usage: python3 check-metadata.py <skill-dir> [--previous <json file>] [--output FILE]

Prints one JSON object on stdout:
  {"script": "check-metadata", "skill": <abs path>, "ran": true, "origin": ..., "surfaces": [...],
   "checks": [{"check", "item", "kind", "status", "location", "detail"}], "truncated": <int>}
Diagnostics go to stderr. Exit codes: 0 the script ran (findings included); 2 usage error (no
such folder, no SKILL.md, bad arguments); 1 could not run (an unexpected error, on stderr).
--previous is accepted so the three scripts share one command form; this script doesn't read it.

Check ids and the checklist item each one serves (references/checklist.md):
  M-1  FM-4 proved  The frontmatter opens with --- on line 1 and closes with ---
  M-2  FM-4 proved  It parses as the strict YAML subset below
  M-3  FM-1 proved  name is present (required where the skill reaches chat or uploads)
  M-4  FM-1 proved  name is 1-64 characters
  M-5  FM-1 proved  name uses only a-z, 0-9 and -
  M-6  FM-1 proved  name has no leading, trailing or double hyphen
  M-7  FM-1 proved  name matches the folder name
  M-8  FM-1 proved  name contains neither of the reserved words anthropic, claude
  M-9  FM-1 proved  neither name nor folder is synced or anthropic-skills
  M-10 FM-1 proved  name has no <, >, control or zero-width character
  M-11 FM-1 proved  description is a non-empty string
  M-12 FM-1 proved  description is at most 1,024 characters
  M-13 FM-1 proved  description has no XML tag
  M-14 FM-1 proved  description + when_to_use are at most 1,536 characters
  M-15 FM-1 proved  compatibility is at most 500 characters (an open-standard limit; checked with
                    the name and description limits because it is the same kind of limit)
  M-16 FM-2 proved  only the six standard fields, when the origin reaches chat or uploads
  M-17 FM-5 proved  metadata is a map of strings
  M-18 FM-5 proved  no strict-YAML trap in a plain value
  M-19 FM-6 proved  not disable-model-invocation: true together with user-invocable: false
  M-20 FM-6 lead    paths set while disable-model-invocation: true (paths then does nothing)

Strict YAML subset parsed here (the standard library has no YAML parser): a top-level mapping of
scalar keys; plain, single-quoted and double-quoted scalars (also over several lines); literal (|)
and folded (>) block scalars with optional chomping (+/-) and indentation indicator; flow lists
and maps; block lists; nested block maps (metadata, hooks); full-line and trailing comments. Tabs
in indentation, duplicate keys, a key indented under a scalar and an unclosed quote don't parse.

Origin (guide section 2), checked in this order:
  account   the folder is under <config>/skills/synced/
  plugin    the folder or an ancestor holds .claude-plugin/plugin.json
  personal  the folder is under <config>/skills/
  project   the folder is under a .claude/skills/ folder (a repository's)
  loose     anywhere else
where <config> is $CLAUDE_CONFIG_DIR, or ~/.claude when it is unset.

Surfaces per origin, as stable ids: claude-code, chat, cowork, cloud-sessions,
project-cloud-threads, api-upload.
  account   claude-code, chat, cowork, cloud-sessions, project-cloud-threads, api-upload
            (the section 2 row; api-upload because an account skill is a claude.ai upload)
  plugin    claude-code, chat, cowork (chat and Cowork only when the plugin is on the account;
            the script can't see that, so it lists them and the reviewers judge)
  personal  claude-code (desktop scheduled tasks run Claude Code on the same machine)
  project   claude-code, cloud-sessions (standalone cloud sessions clone the repository)
  loose     claude-code
FM-2 fails for the origins that reach chat or uploads (account, plugin). A personal skill passes
with a warning: enabling it on a claude.ai account is an upload that rejects the extra fields, and
the script can't see whether that was done.
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
import re
import sys
import unicodedata

MAX_CHECKS = 200  # the orchestrator reads the whole result inline; 200 short entries stay small
MAX_DETAIL = 300  # characters per detail, so one finding can't flood the output
NAME_MAX = 64  # [AS][PL]
DESCRIPTION_MAX = 1024  # [AS][PL]
LISTING_MAX = 1536  # [CC] description + when_to_use are cut here in the skill listing
COMPATIBILITY_MAX = 500  # [AS]

STANDARD_FIELDS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
STRING_KEYS = frozenset(
    {
        "name",
        "description",
        "when_to_use",
        "license",
        "compatibility",
        "argument-hint",
        "model",
        "effort",
        "context",
        "agent",
        "shell",
    }
)
BOOL_NULL_WORDS = frozenset({"yes", "no", "on", "off", "null", "true", "false", "~"})
UNLOADABLE_NAMES = frozenset({"synced", "anthropic-skills"})
RESERVED_WORDS = ("anthropic", "claude")
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

SURFACES = {
    "account": [
        "claude-code",
        "chat",
        "cowork",
        "cloud-sessions",
        "project-cloud-threads",
        "api-upload",
    ],
    "plugin": ["claude-code", "chat", "cowork"],
    "personal": ["claude-code"],
    "project": ["claude-code", "cloud-sessions"],
    "loose": ["claude-code"],
}
UPLOAD_ORIGINS = frozenset({"account", "plugin"})

CHECKS: dict[str, tuple[str, str]] = {
    "M-1": ("FM-4", "proved"),
    "M-2": ("FM-4", "proved"),
    "M-3": ("FM-1", "proved"),
    "M-4": ("FM-1", "proved"),
    "M-5": ("FM-1", "proved"),
    "M-6": ("FM-1", "proved"),
    "M-7": ("FM-1", "proved"),
    "M-8": ("FM-1", "proved"),
    "M-9": ("FM-1", "proved"),
    "M-10": ("FM-1", "proved"),
    "M-11": ("FM-1", "proved"),
    "M-12": ("FM-1", "proved"),
    "M-13": ("FM-1", "proved"),
    "M-14": ("FM-1", "proved"),
    "M-15": ("FM-1", "proved"),
    "M-16": ("FM-2", "proved"),
    "M-17": ("FM-5", "proved"),
    "M-18": ("FM-5", "proved"),
    "M-19": ("FM-6", "proved"),
    "M-20": ("FM-6", "lead"),
}


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
# Origin
# ---------------------------------------------------------------------------


def config_dir() -> Path:
    """$CLAUDE_CONFIG_DIR, or ~/.claude."""
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(configured).expanduser() if configured else Path.home() / ".claude"
    return base.resolve()


def under(path: Path, folder: Path) -> bool:
    """Whether path lies strictly inside folder."""
    return path != folder and path.is_relative_to(folder)


def origin_of(skill: Path) -> str:
    """The skill's origin, by the rules in the module docstring."""
    config = config_dir()
    if under(skill, config / "skills" / "synced"):
        return "account"
    for folder in (skill, *skill.parents):
        if (folder / ".claude-plugin" / "plugin.json").is_file():
            return "plugin"
    if under(skill, config / "skills"):
        return "personal"
    parts = skill.parts[:-1]
    if any(parts[i : i + 2] == (".claude", "skills") for i in range(len(parts) - 1)):
        return "project"
    return "loose"


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Context:
    """What every check needs: the parsed fields, the folder name, the origin."""

    fields: dict[str, Value]
    lines: dict[str, int]
    folder: str
    origin: str


def text_of(value: Value | None) -> str | None:
    """A scalar's text; None for a missing value, a list or a map."""
    return value.text if isinstance(value, Scalar) else None


def flag(value: Value | None) -> str:
    """A scalar's text lowercased, for true/false fields."""
    text = text_of(value)
    return text.strip().lower() if text is not None else ""


def check_name_form(report: Report, name: str, line: int) -> None:
    """M-4 to M-6, M-8 and M-10: the name's length, characters and words."""
    report.ran("M-4", f"name is {len(name)} characters")
    if not 1 <= len(name) <= NAME_MAX:
        report.fail("M-4", at(line), f"name is {len(name)} characters; the limit is 1-{NAME_MAX}")
    report.ran("M-5", "name uses only a-z, 0-9 and -")
    if not NAME_RE.fullmatch(name):
        report.fail("M-5", at(line), f"name {name!r} has characters outside a-z, 0-9 and -")
    report.ran("M-6", "no leading, trailing or double hyphen")
    if name.startswith("-") or name.endswith("-") or "--" in name:
        report.fail("M-6", at(line), f"name {name!r} has a leading, trailing or double hyphen")
    report.ran("M-8", "no reserved word")
    for word in RESERVED_WORDS:
        if word in name.lower():
            report.fail(
                "M-8", at(line), f"name contains the reserved word {word!r}; uploads refuse it"
            )
    report.ran("M-10", "no <, >, control or zero-width character")
    bad = [c for c in name if c in "<>" or unicodedata.category(c) in ("Cc", "Cf")]
    if bad:
        shown = ", ".join(f"U+{ord(c):04X}" for c in bad[:5])
        report.fail("M-10", at(line), f"name has <, >, control or zero-width characters: {shown}")


def check_name(report: Report, ctx: Context) -> None:
    """M-3 to M-10."""
    name = text_of(ctx.fields.get("name"))
    line = ctx.lines.get("name", 1)
    report.ran("M-9", f"folder {ctx.folder!r} loads")
    if ctx.folder in UNLOADABLE_NAMES:
        report.fail("M-9", at(1), f"Claude Code doesn't load a folder named {ctx.folder!r}")
    if not name:
        report.ran("M-3", "name is absent; Claude Code uses the folder name")
        if ctx.origin in UPLOAD_ORIGINS:
            report.fail("M-3", at(line), f"name is required where a {ctx.origin} skill reaches")
        return
    report.ran("M-3", "name is present")
    check_name_form(report, name, line)
    report.ran("M-7", "name matches the folder")
    if name != ctx.folder:
        report.fail("M-7", at(line), f"name {name!r} differs from the folder {ctx.folder!r}")
    if name in UNLOADABLE_NAMES:
        report.fail("M-9", at(line), f"name {name!r} is reserved by Claude Code")


def check_description(report: Report, ctx: Context) -> None:
    """M-11 to M-15."""
    value = ctx.fields.get("description")
    line = ctx.lines.get("description", 1)
    description = text_of(value)
    report.ran("M-11", "description is a non-empty string")
    if description is None or not description.strip():
        report.fail("M-11", at(line), "description is missing, empty or not a string")
        description = ""
    report.ran("M-12", f"description is {len(description)} characters")
    if len(description) > DESCRIPTION_MAX:
        report.fail(
            "M-12", at(line), f"description is {len(description)} characters; max {DESCRIPTION_MAX}"
        )
    report.ran("M-13", "no XML tag in the description")
    tag = XML_TAG_RE.search(description)
    if tag:
        report.fail("M-13", at(line), f"description holds the XML tag {tag.group(0)[:40]!r}")
    extra = text_of(ctx.fields.get("when_to_use")) or ""
    total = len(description) + len(extra)
    report.ran("M-14", f"description + when_to_use are {total} characters")
    if total > LISTING_MAX:
        report.fail("M-14", at(line), f"description + when_to_use are {total}; max {LISTING_MAX}")
    if "compatibility" in ctx.fields:
        compat = text_of(ctx.fields["compatibility"]) or ""
        report.ran("M-15", f"compatibility is {len(compat)} characters")
        if len(compat) > COMPATIBILITY_MAX:
            where = at(ctx.lines["compatibility"])
            report.fail("M-15", where, f"compatibility is {len(compat)}; max {COMPATIBILITY_MAX}")


def check_fields(report: Report, ctx: Context) -> None:
    """M-16: fields outside the six standard ones, judged by the origin."""
    extra = [k for k in ctx.fields if k not in STANDARD_FIELDS]
    if not extra:
        report.ran("M-16", "only the six standard fields")
        return
    names = ", ".join(extra)
    if ctx.origin in UPLOAD_ORIGINS:
        report.ran("M-16", "")
        for key in extra:
            report.fail(
                "M-16",
                at(ctx.lines[key]),
                (
                    f"{key} is not one of the six standard fields; a {ctx.origin} skill reaches "
                    "claude.ai or the API, where uploads reject it"
                ),
            )
        return
    note = (
        "; enabling this personal skill on a claude.ai account is an upload that rejects them"
        if ctx.origin == "personal"
        else ""
    )
    report.ran(
        "M-16",
        (
            f"Claude Code-only fields ({names}) are fine for a {ctx.origin} skill, which "
            f"reaches only {', '.join(SURFACES[ctx.origin])}{note}"
        ),
    )


def check_metadata_map(report: Report, ctx: Context) -> None:
    """M-17: metadata is a map of strings."""
    if "metadata" not in ctx.fields:
        return
    value = ctx.fields["metadata"]
    line = ctx.lines["metadata"]
    report.ran("M-17", "metadata is a map of strings")
    if not isinstance(value, dict):
        report.fail("M-17", at(line), "metadata is not a map; Claude Code drops it")
        return
    for key, entry in value.items():
        if not isinstance(entry, Scalar):
            report.fail("M-17", at(line), f"metadata.{key} is not a string")


def trap_reasons(scalar: Scalar, *, string_expected: bool) -> list[str]:
    """Why a plain scalar reads differently in a strict YAML parser."""
    text = scalar.text
    reasons: list[str] = []
    if ": " in text or text.endswith(":"):
        reasons.append("a colon followed by a space")
    if " #" in text:
        reasons.append("' #', which starts a comment")
    if text[:1] and (text[0] in INDICATORS or text.startswith(("- ", "? "))):
        reasons.append(f"it starts with the indicator {text[0]!r}")
    if string_expected and text.strip().lower() in BOOL_NULL_WORDS:
        reasons.append(f"{text.strip()!r} reads as a boolean or null")
    return reasons


def walk_traps(report: Report, value: Value, *, string_expected: bool) -> None:
    """M-18 over one value and everything nested in it."""
    if isinstance(value, Scalar):
        if value.style == "plain":
            reasons = trap_reasons(value, string_expected=string_expected)
            if reasons:
                report.fail(
                    "M-18",
                    at(value.line),
                    f"quote or reword {value.text[:60]!r}: {'; '.join(reasons)}",
                )
        return
    children = value.values() if isinstance(value, dict) else value
    for child in children:
        walk_traps(report, child, string_expected=False)


def check_traps(report: Report, ctx: Context) -> None:
    """M-18: strict-YAML traps in plain values."""
    report.ran("M-18", "no strict-YAML trap in a plain value")
    for key, value in ctx.fields.items():
        if key == "metadata" and isinstance(value, dict):
            for entry in value.values():
                walk_traps(report, entry, string_expected=True)
        else:
            walk_traps(report, value, string_expected=key in STRING_KEYS)


def check_combinations(report: Report, ctx: Context) -> None:
    """M-19 and M-20: combinations that disable the skill or a field."""
    disabled = flag(ctx.fields.get("disable-model-invocation")) == "true"
    report.ran("M-19", "someone can invoke the skill")
    if disabled and flag(ctx.fields.get("user-invocable")) == "false":
        report.fail(
            "M-19",
            at(ctx.lines["user-invocable"]),
            "disable-model-invocation: true with user-invocable: false: nobody can run the skill",
        )
    if disabled and "paths" in ctx.fields:
        report.lead(
            "M-20",
            at(ctx.lines["paths"]),
            (
                "paths limits automatic activation, which disable-model-invocation: true "
                "already turns off, so paths does nothing"
            ),
        )


# ---------------------------------------------------------------------------
# Frontmatter extraction and main
# ---------------------------------------------------------------------------


def key_lines(lines: list[str], first: int) -> dict[str, int]:
    """The SKILL.md line of each top-level key."""
    found: dict[str, int] = {}
    for index, line in enumerate(lines):
        if line[:1] not in ("", " ", "#", "-"):
            split = split_key(line, first + index)
            if split is not None:
                _ = found.setdefault(split[0], first + index)
    return found


def frontmatter(report: Report, text: str) -> tuple[list[str], int] | None:
    """M-1: the frontmatter lines and the line number of the first one, or None."""
    lines = text.splitlines()
    report.ran("M-1", "the frontmatter starts on line 1 and closes")
    if not lines or lines[0].rstrip() != "---":
        detail = "the first line isn't ---, so Claude Code reads no frontmatter"
        if text.startswith("﻿"):
            detail = "the file starts with a byte-order mark before ---"
        report.fail("M-1", at(1), detail)
        return None
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return lines[1:index], 2
    report.fail("M-1", at(1), "the frontmatter has no closing --- line")
    return None


def run_checks(report: Report, skill: Path, text: str, origin: str) -> None:
    """Every check, in order; later checks need a frontmatter that parses."""
    extracted = frontmatter(report, text)
    if extracted is None:
        return
    lines, first = extracted
    report.ran("M-2", "the frontmatter parses as strict YAML")
    try:
        fields = Parser(lines, first).document()
    except YamlError as error:
        report.fail("M-2", at(error.line), f"strict YAML: {error.message}")
        return
    ctx = Context(fields, key_lines(lines, first), skill.name, origin)
    check_name(report, ctx)
    check_description(report, ctx)
    check_fields(report, ctx)
    check_metadata_map(report, ctx)
    check_traps(report, ctx)
    check_combinations(report, ctx)


def emit(text: str, output: Path | None) -> int:
    """Write the result to --output FILE when given, then to stdout; 1 if FILE can't be written."""
    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _ = output.write_text(text, encoding="utf-8", newline="")
        except OSError as error:
            _ = sys.stderr.write(
                f"check-metadata: --output {output}: could not write the result: {error}\n"
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
        prog="check-metadata.py",
        description="Check a skill's SKILL.md frontmatter and print one JSON result.",
        epilog=(
            "Example: python3 check-metadata.py path/to/my-skill\n"
            "Exit codes: 0 ran (findings are in the JSON), 2 usage error, 1 could not run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("skill_dir", type=Path, help="the skill folder (holds SKILL.md)")
    _ = parser.add_argument(
        "--previous", type=Path, help="accepted for a uniform command form; not read"
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
    skill = args.skill_dir.expanduser()
    if not skill.is_dir():
        _ = sys.stderr.write(f"check-metadata: no such folder: {skill}\n")
        return 2
    skill = skill.resolve()
    skill_md = skill / "SKILL.md"
    if not skill_md.is_file():
        _ = sys.stderr.write(f"check-metadata: {skill} has no SKILL.md; pass the skill folder\n")
        return 2
    try:
        text = skill_md.read_bytes().decode("utf-8", errors="replace")
    except OSError as error:
        _ = sys.stderr.write(f"check-metadata: could not read {skill_md}: {error}\n")
        return 1
    origin = origin_of(skill)
    report = Report(CHECKS)
    run_checks(report, skill, text, origin)
    checks, truncated = report.results()
    result: dict[str, object] = {
        "script": "check-metadata",
        "skill": str(skill),
        "ran": True,
        "origin": origin,
        "surfaces": SURFACES[origin],
        "checks": checks,
        "truncated": truncated,
    }
    return emit(json.dumps(result, indent=1) + "\n", args.output)


if __name__ == "__main__":
    raise SystemExit(main())
