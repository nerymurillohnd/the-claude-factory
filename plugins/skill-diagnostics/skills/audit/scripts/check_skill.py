#!/usr/bin/env python3
"""Check the structure of one skill directory, read-only.

Usage: check_skill.py [--format json|text] [--listing-cap N] SKILL_DIR
       check_skill.py --list [--format json|text] SKILL_DIR

--list prints the skill's full file inventory instead of checking it: every
file at any depth, hidden files included, symlinked folders inside the skill
followed, nothing excluded, names and sizes only (no file is opened). Links
whose target lies outside the skill are listed under "outside" (with whether the
target exists), not followed.

Checks what `claude plugin validate` does not: frontmatter syntax and quoting,
known fields and values, name and description limits per surface,
argument placeholders, body size, render-time syntax, links, references and
scripts. It never writes files and never runs the skill.

Every report covers all four surfaces, each with its own findings and summary:
  code    Claude Code skills (personal, project, plugin).
  cowork  Plugin skills used in Cowork.
  upload  claude.ai skill upload (also covers account skills synced to Cowork).
  api     Skills API.

Exit codes: 0 report printed (errors are counted in summary.error), 2 bad input.
A report never exits 1: Claude Code treats exit 1 as a failed command and cuts
its output at about 10,000 characters.
Requires Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
from dataclasses import asdict, dataclass, field
import difflib
from functools import cached_property
import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, TypedDict
from urllib.parse import unquote

if TYPE_CHECKING:
    from collections.abc import Iterator

# --- Facts, each with its source -------------------------------------------------
# Skill frontmatter fields Claude Code reads.
# https://code.claude.com/docs/en/skills#frontmatter-reference
CODE_FIELDS = frozenset(
    {
        "name",
        "description",
        "when_to_use",
        "argument-hint",
        "arguments",
        "disable-model-invocation",
        "user-invocable",
        "allowed-tools",
        "disallowed-tools",
        "model",
        "effort",
        "context",
        "agent",
        "background",
        "hooks",
        "paths",
        "shell",
        "metadata",
        "license",
        "compatibility",
    }
)
# Fields claude.ai uploads and the Skills API accept; any other key is a hard error.
# https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code
UPLOAD_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)
BOOLEAN_FIELDS = ("disable-model-invocation", "user-invocable", "background")
BOOLEAN_VALUES = frozenset({"true", "false", "yes", "no", "on", "off", "1", "0"})
ENUM_FIELDS = {
    "effort": frozenset({"low", "medium", "high", "xhigh", "max"}),
    "context": frozenset({"fork"}),
    "shell": frozenset({"bash", "powershell"}),
}
# Agent Skills specification: name 1-64 chars, lowercase letters, digits and
# single hyphens, no leading or trailing hyphen, equal to the directory name;
# description 1-1024 chars; compatibility up to 500 chars.
# https://agentskills.io/specification
NAME_MAX = 64
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED_WORDS = ("anthropic", "claude")
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
# Claude Code cuts description + when_to_use at this many characters in the
# skill listing by default (setting skillListingMaxDescChars).
# https://code.claude.com/docs/en/settings-reference#skilllistingmaxdescchars
LISTING_CAP_DEFAULT = 1536
# Recommended SKILL.md body budget: under 500 lines, about 5,000 tokens.
# https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
BODY_LINES_MAX = 500
BODY_TOKENS_MAX = 5000
CHARS_PER_TOKEN = 4  # rough English average, enough for a budget warning
# Reference files over this many lines should open with a contents list.
CONTENTS_THRESHOLD = 100

TARGETS = ("code", "cowork", "upload", "api")
UPLOAD_TARGETS = frozenset({"upload", "api"})

# --- Patterns ---------------------------------------------------------------------
KEY_LINE = re.compile(r"^([A-Za-z0-9_-]+):(?:\s+(.*)|\s*)$")
BLOCK_SCALAR = re.compile(r"^[|>][+-]?[0-9]?\s*(#.*)?$")
YAML_INDICATORS = tuple("[]{}&*!|>%@`'\",#?-:")
LINK = re.compile(r"\[[^\]]*\]\(\s*(?:<([^>\n]+)>|([^)\s]+))(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"`[^`]*`")
TAG = re.compile(r"</?[A-Za-z][^>]*>")
PERSON = re.compile(r"^\s*(I|I'm|I'll|I can|We|We'll|You|You can|You'll|Let me)\b", re.IGNORECASE)
TRIGGER = re.compile(
    r"\b(use|invoke|apply)\b[^.]*?\b(when|whenever|for|if|before|after|to)\b|\bwhen the user\b",
    re.IGNORECASE,
)
CLAUDE_VAR = re.compile(r"\$\{CLAUDE_[A-Z_]+\}")
SKILL_DIR_PATH = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9_./-]+)")
MONEY = re.compile(r"(?<![\\\w])\$\d+(?:[.,]\d+)")
INDEXED = re.compile(r"(?<![\\\w])\$(?:ARGUMENTS(?:\[\d+\])?|\d+)(?![\w.,])")
DYNAMIC_INLINE = re.compile(r"(?:^|\s)!`")
RELATIVE_SCRIPT = re.compile(
    r"`(?:(?:python3?|bash|sh|node)\s+(?:\./)?scripts/[^`\s]+|\./scripts/[^`\s]+|scripts/[^`\s]+\s+[^`]*)`"
)  # a command, not a bare file mention
SCRIPT_SUFFIXES = frozenset(
    {".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl"}
)
EXTERNAL = ("http://", "https://", "mailto:", "#")


@dataclass
class Finding:
    """One problem found in the skill; `file` is relative to the skill directory."""

    rule: str
    severity: str  # error | warning | info
    file: str
    line: int
    message: str
    hint: str = ""


@dataclass
class Field:
    """One top-level frontmatter key and its value."""

    key: str
    line: int
    raw: str  # text after "key:" on its own line
    style: str  # plain | single | double | block | flow | nested | empty
    value: str  # best-effort text value
    lines: int = 1  # physical lines the value spans


@dataclass
class Frontmatter:
    """The top-level frontmatter keys and where the frontmatter ends."""

    fields: dict[str, Field] = field(default_factory=dict)
    end_line: int = 0  # line number of the closing marker


# --- Frontmatter parsing (top-level keys only, no dependencies) -------------------
def parse_scalar(raw: str) -> tuple[str, str]:
    """Return (style, value) for a single-line scalar."""
    if not raw:
        return "empty", ""
    if raw[0] == '"' and len(raw) > 1 and raw.endswith('"'):
        return "double", raw[1:-1].replace('\\"', '"')
    if raw[0] == "'" and len(raw) > 1 and raw.endswith("'"):
        return "single", raw[1:-1].replace("''", "'")
    if raw[0] in "[{":
        return "flow", raw
    if BLOCK_SCALAR.match(raw):
        return "block", ""
    # A plain scalar ends where " #" starts a comment.
    cut = raw.find(" #")
    return "plain", (raw[:cut] if cut >= 0 else raw).rstrip()


def parse_frontmatter(lines: list[str]) -> tuple[Frontmatter | None, list[tuple[str, int, str]]]:
    """Parse top-level keys. Returns the frontmatter (None when absent) and syntax problems."""
    problems: list[tuple[str, int, str]] = []
    if not lines or lines[0].strip() != "---":
        problems.append(
            (
                "frontmatter-start",
                1,
                "line 1 is not '---': Claude Code reads no frontmatter and the description is lost",
            )
        )
        return None, problems
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        problems.append(("frontmatter-end", 1, "the frontmatter has no closing '---'"))
        return None, problems
    fm = Frontmatter(end_line=end + 1)
    current: Field | None = None
    for index in range(1, end):
        text = lines[index]
        number = index + 1
        if not text.strip() or text.lstrip().startswith("#"):
            continue
        if text[0] in " \t" or text.startswith("- "):
            if current is not None:
                continue_field(current, text)
            continue
        match = KEY_LINE.match(text)
        if match is None:
            problems.append(
                ("frontmatter-syntax", number, f"not a 'key: value' line: {text.strip()}")
            )
            current = None
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        style, value = parse_scalar(raw)
        current = Field(key=key, line=number, raw=raw, style=style, value=value)
        fm.fields[key] = current
    return fm, problems


def continue_field(current: Field, text: str) -> None:
    """Add an indented or list line to the value of the field above it."""
    current.lines += 1
    if current.style in {"block", "plain"}:
        current.value = (current.value + " " + text.strip()).strip()
    elif current.style == "empty":
        current.style = "nested"


def needs_quotes(value: str) -> str:
    """Why a plain scalar must be quoted, or '' when it is safe unquoted."""
    if not value:
        return ""
    if ": " in value or value.endswith(":"):
        return "contains ': '"
    if " #" in value:
        return "contains ' #', which starts a YAML comment and cuts the text"
    if value[0] in YAML_INDICATORS:
        return f"starts with '{value[0]}', a YAML indicator"
    if value.lower() in {"true", "false", "yes", "no", "on", "off", "null", "~"}:
        return "reads as a boolean or null"
    return ""


# --- Checker -------------------------------------------------------------------------
def fenced(lines: list[str]) -> Iterator[tuple[str, str, str]]:
    """Yield (line, kind, info) per line; kind is "fence", "code" or "text" (CommonMark fences).

    A fence closes only with the same character, at least as long, and no info string,
    so a ``` line inside a ~~~ block (or a longer fence) stays code.
    """
    opener: tuple[str, int] | None = None
    for line in lines:
        match = FENCE.match(line)
        if opener is None:
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                opener = (match.group(1)[0], len(match.group(1)))
                yield line, "fence", match.group(2).strip()
            else:
                yield line, "text", ""
        elif (
            match
            and match.group(1)[0] == opener[0]
            and len(match.group(1)) >= opener[1]
            and not match.group(2).strip()
        ):
            opener = None
            yield line, "fence", ""
        else:
            yield line, "code", ""


class Checker:
    """Collects the findings of one skill directory for one target surface."""

    def __init__(self, skill_dir: Path, target: str, listing_cap: int) -> None:
        """Prepare a check of `skill_dir` for `target` with the given listing cap."""
        self.dir = skill_dir
        self.dir_real = skill_dir.resolve()
        self.skill_md = skill_dir / "SKILL.md"
        self.target = target
        self.listing_cap = listing_cap
        self.findings: list[Finding] = []
        self.texts: dict[Path, str | None] = {}

    # helpers
    def rel(self, path: Path) -> str:
        """Return `path` relative to the skill directory, with forward slashes."""
        return path.relative_to(self.dir).as_posix()

    def add(self, rule: str, severity: str, line: int, message: str, hint: str = "") -> None:
        """Record a finding in SKILL.md; findings in other files append a Finding directly."""
        self.findings.append(Finding(rule, severity, self.rel(self.skill_md), line, message, hint))

    def read(self, path: Path) -> str | None:
        """Return the file's UTF-8 text, cached; None (and a finding) when it cannot be read."""
        if path not in self.texts:
            try:
                self.texts[path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                self.findings.append(
                    Finding(
                        "read",
                        "error",
                        self.rel(path),
                        1,
                        f"cannot read as UTF-8 text: {type(exc).__name__}",
                    )
                )
                self.texts[path] = None
        return self.texts[path]

    @property
    def upload(self) -> bool:
        """True when the target is a claude.ai upload or the Skills API."""
        return self.target in UPLOAD_TARGETS

    # entry point
    def run(self) -> list[Finding]:
        """Run every check and return the findings in the order they were found."""
        text = self.read(self.skill_md)
        if text is None:
            return self.findings
        lines = text.splitlines()
        fm, problems = parse_frontmatter(lines)
        for rule, line, message in problems:
            self.add(rule, "error", line, message)
        body_start = 1
        if fm is not None:
            self.check_fields(fm)
            self.check_name(fm)
            self.check_local_reserved(fm)
            self.check_description(fm)
            body_start = fm.end_line + 1
        body = lines[body_start - 1 :]
        self.check_body(body, body_start, fm)
        self.check_links()
        self.check_references()
        self.check_scripts(body, body_start)
        return self.findings

    # fields
    def check_fields(self, fm: Frontmatter) -> None:
        """Check field names, values and YAML quoting."""
        self.check_unknown_fields(fm)
        self.check_field_values(fm)
        self.check_field_quoting(fm)

    def check_unknown_fields(self, fm: Frontmatter) -> None:
        """Report fields the target does not know."""
        allowed = UPLOAD_FIELDS if self.upload else CODE_FIELDS
        for key, fld in fm.fields.items():
            if key in allowed:
                continue
            guess = difflib.get_close_matches(key, sorted(CODE_FIELDS), n=1)
            if self.upload and key in CODE_FIELDS:
                self.add(
                    "field-unknown",
                    "error",
                    fld.line,
                    f"'{key}' is a Claude Code-only field; {self.target} rejects the skill",
                    "Remove it, or keep two versions of the skill.",
                )
            else:
                hint = (
                    f"Did you mean '{guess[0]}'?" if guess else "Remove it or check the field list."
                )
                self.add(
                    "field-unknown",
                    "error" if self.upload else "warning",
                    fld.line,
                    f"unknown field '{key}': Claude Code ignores it silently"
                    + (f" (did you mean '{guess[0]}'?)" if guess else ""),
                    hint,
                )

    def check_field_values(self, fm: Frontmatter) -> None:
        """Check boolean and enum values, the compatibility length and the metadata shape."""
        for key in BOOLEAN_FIELDS:
            fld = fm.fields.get(key)
            if fld and fld.value.lower() not in BOOLEAN_VALUES:
                self.add(
                    "field-value",
                    "error",
                    fld.line,
                    f"'{key}' must be true or false, got '{fld.value}'",
                )
        for key, values in ENUM_FIELDS.items():
            fld = fm.fields.get(key)
            if fld and fld.value and fld.value.lower() not in values:
                self.add(
                    "field-value",
                    "error",
                    fld.line,
                    f"'{key}' must be one of {', '.join(sorted(values))}, got '{fld.value}'",
                )
        compat = fm.fields.get("compatibility")
        if compat and len(compat.value) > COMPATIBILITY_MAX:
            self.add(
                "field-value",
                "error",
                compat.line,
                f"'compatibility' is {len(compat.value)} characters;"
                f" the limit is {COMPATIBILITY_MAX}",
            )
        meta = fm.fields.get("metadata")
        if meta and meta.style not in {"nested", "flow"}:
            self.add(
                "field-value",
                "warning",
                meta.line,
                "'metadata' must be a map; Claude Code drops any other value",
            )

    def check_field_quoting(self, fm: Frontmatter) -> None:
        """Report text fields that YAML reads differently unless they are quoted."""
        for key in ("argument-hint", "when_to_use", "model", "agent"):
            fld = fm.fields.get(key)
            if fld and fld.style == "plain":
                reason = needs_quotes(fld.value)
                if reason:
                    self.add(
                        "yaml-quoting",
                        "error",
                        fld.line,
                        f"'{key}' {reason}: strict YAML parsers and uploads read it differently",
                        "Quote the value.",
                    )
            elif fld and fld.style == "flow" and key == "argument-hint":
                self.add(
                    "yaml-quoting",
                    "error",
                    fld.line,
                    "'argument-hint' starts with '[', so YAML reads a list, not text",
                    'Quote it: argument-hint: "[tag]".',
                )

    # name
    def check_name(self, fm: Frontmatter) -> None:
        """Check the name's presence, length, format, reserved words and directory match."""
        fld = fm.fields.get("name")
        if fld is None or not fld.value:
            self.add(
                "name-missing",
                "error" if self.upload else "info",
                1,
                "no 'name': Claude Code uses the directory name; uploads and the spec require it",
            )
            return
        name, line = fld.value, fld.line
        if len(name) > NAME_MAX:
            self.add(
                "name-length",
                "error",
                line,
                f"'name' is {len(name)} characters; the limit is {NAME_MAX}",
            )
        if not NAME_PATTERN.match(name):
            self.add(
                "name-format",
                "error",
                line,
                "'name' must use lowercase letters, digits and single hyphens,"
                " with no hyphen at either end",
            )
        for word in RESERVED_WORDS:
            if word in name:
                self.add(
                    "name-reserved",
                    "error" if self.upload else "info",
                    line,
                    f"'name' contains the reserved word '{word}':"
                    " claude.ai uploads and the Skills API reject it"
                    + ("" if self.upload else "; it matters only if you upload the skill"),
                )
        if name != self.dir.name:
            self.add(
                "name-directory",
                "error" if self.upload else "warning",
                line,
                f"'name' is '{name}' but the directory is '{self.dir.name}';"
                " the spec requires them to match",
            )

    def check_local_reserved(self, fm: Frontmatter) -> None:
        """Names Claude Code refuses to load, whatever the frontmatter says."""
        if self.upload:
            return
        fld = fm.fields.get("name")
        line = fld.line if fld else 1
        if self.dir.name.lower() == "synced":
            self.add(
                "name-reserved-local",
                "error",
                line,
                "the directory is named 'synced',"
                " which Claude Code reserves for skills synced from claude.ai;"
                " it skips this skill",
                "Rename the directory.",
            )
        for value in (self.dir.name, fld.value if fld else ""):
            if value == "anthropic-skills" or value.startswith("anthropic-skills:"):
                self.add(
                    "name-reserved-local",
                    "error",
                    line,
                    f"'{value}' uses 'anthropic-skills',"
                    " which Claude Code reserves for synced skills; it does not load",
                    "Rename the directory and the 'name'.",
                )
                break

    # description
    def check_description(self, fm: Frontmatter) -> None:
        """Check the description's presence, form, wording and length."""
        fld = fm.fields.get("description")
        if fld is None or not fld.value:
            self.add(
                "description-missing",
                "error",
                fld.line if fld else 1,
                "no 'description': Claude has nothing to decide when to use the skill",
            )
            return
        self.check_description_form(fld)
        self.check_description_wording(fld)
        self.check_description_length(fm, fld)

    def check_description_form(self, fld: Field) -> None:
        """Report a multi-line description and quoting it needs or does not need."""
        text, line = fld.value, fld.line
        if fld.style == "block" or fld.lines > 1:
            self.add(
                "description-one-line",
                "warning",
                line,
                "'description' spans several lines; keep it on one line",
                "Write it as one plain line.",
            )
        if fld.style == "plain":
            reason = needs_quotes(text if " #" not in fld.raw else fld.raw)
            if reason:
                self.add(
                    "yaml-quoting",
                    "error",
                    line,
                    f"'description' {reason}: strict YAML parsers and uploads reject or cut it",
                    "Reword it so it needs no quotes"
                    " (for example 'Use when …' instead of 'Use when: …'), or quote it.",
                )
        elif fld.style in {"double", "single"} and not needs_quotes(text) and "\\" not in fld.raw:
            self.add(
                "yaml-quoting",
                "info",
                line,
                "'description' is quoted but needs no quotes",
                "Recommended: write it as one plain, unquoted line.",
            )

    def check_description_wording(self, fld: Field) -> None:
        """Report tags, a first- or second-person start and a missing 'when to use' clause."""
        text, line = fld.value, fld.line
        if TAG.search(text):
            self.add(
                "description-tags",
                "error" if self.upload else "info",
                line,
                "'description' contains an angle-bracket tag;"
                " uploads reject it and Claude Code escapes it",
            )
        if PERSON.match(text):
            self.add(
                "description-person",
                "warning",
                line,
                "'description' is not in the third person; it is read as part of the system prompt",
                "Start with what the skill does: 'Formats …'.",
            )
        if not TRIGGER.search(text):
            self.add(
                "description-trigger",
                "warning",
                line,
                "'description' says what the skill does but not when to use it",
                "Add a 'Use when …' clause with the words users type.",
            )

    def check_description_length(self, fm: Frontmatter, fld: Field) -> None:
        """Check the upload length limit, or the Claude Code listing cap."""
        text, line = fld.value, fld.line
        if self.upload:
            if len(text) > DESCRIPTION_MAX:
                self.add(
                    "description-length",
                    "error",
                    line,
                    f"'description' is {len(text)} characters;"
                    f" {self.target} rejects more than {DESCRIPTION_MAX}",
                )
            return
        when = fm.fields.get("when_to_use")
        total = len(text) + (len(when.value) if when else 0)
        if total > self.listing_cap:
            self.add(
                "description-listing-cap",
                "warning",
                line,
                f"'description' + 'when_to_use' is {total} characters;"
                f" Claude Code cuts the listing at {self.listing_cap}"
                f" for users with that setting (default {LISTING_CAP_DEFAULT})",
                "Put the key use case first and shorten it;"
                " the cap is the user's skillListingMaxDescChars setting.",
            )

    # body
    def check_body(self, body: list[str], start: int, fm: Frontmatter | None) -> None:
        """Check body size, argument placeholders and render-time syntax."""
        self.check_body_size(body, start)
        declared = self.declared_arguments(fm)
        used: set[str] = set()
        for offset, (line, kind, info) in enumerate(fenced(body)):
            number = start + offset
            if kind == "fence":
                if info.startswith("!"):
                    self.dynamic(number)
                continue
            used.update(
                name
                for name in declared
                if re.search(rf"(?<![\\\w])\${re.escape(name)}(?!\w)", line)
            )
            self.check_body_line(line, number, kind)
        for name in sorted(set(declared) - used):
            self.add(
                "arguments-unused",
                "warning",
                start,
                f"argument '{name}' is declared in 'arguments'"
                f" but '${name}' never appears in the body",
            )

    def check_body_size(self, body: list[str], start: int) -> None:
        """Warn when the body passes the line or token budget."""
        if len(body) >= BODY_LINES_MAX:
            self.add(
                "body-lines",
                "warning",
                start,
                f"the body is {len(body)} lines;"
                f" keep SKILL.md under {BODY_LINES_MAX} and move detail to references",
            )
        tokens = sum(len(line) + 1 for line in body) // CHARS_PER_TOKEN
        if tokens > BODY_TOKENS_MAX:
            self.add(
                "body-tokens",
                "warning",
                start,
                f"the body is about {tokens} tokens; aim under {BODY_TOKENS_MAX}",
            )

    def check_body_line(self, line: str, number: int, kind: str) -> None:
        """Check one body line that is not a fence marker; `kind` is "code" or "text"."""
        in_fence = kind == "code"
        for match in MONEY.finditer(line):
            self.add(
                "arguments-escape",
                "warning",
                number,
                f"'{match.group(0)}' expands as an argument placeholder when the skill loads",
                f"Escape it: \\{match.group(0)}.",
            )
        if in_fence and INDEXED.search(line):
            self.add(
                "arguments-escape",
                "warning",
                number,
                "an argument placeholder inside a code block still expands when the skill loads",
                "Escape the '$' if the example must stay literal.",
            )
        if in_fence:
            return
        if DYNAMIC_INLINE.search(line):
            self.dynamic(number)
        if CLAUDE_VAR.search(INLINE_CODE.sub("", line)):
            self.add(
                "render-variable",
                "warning",
                number,
                "a ${CLAUDE_*} variable in prose expands to a path when the skill loads",
                "Name it without braces in prose; keep the braced form in commands.",
            )

    def dynamic(self, number: int) -> None:
        """Report a dynamic-context command with the severity of the target."""
        if self.upload:
            self.add(
                "dynamic-context",
                "error",
                number,
                f"dynamic-context commands do not run on {self.target}",
            )
        elif self.target == "cowork":
            self.add(
                "dynamic-context",
                "warning",
                number,
                "in Cowork this command is replaced by a placeholder and does not run",
            )
        else:
            self.add(
                "dynamic-context",
                "info",
                number,
                "runs when the skill loads; a non-zero exit aborts the whole skill",
            )

    @staticmethod
    def declared_arguments(fm: Frontmatter | None) -> list[str]:
        """Return the argument names declared in the 'arguments' field."""
        if fm is None or "arguments" not in fm.fields:
            return []
        fld = fm.fields["arguments"]
        raw = fld.raw.strip("[]") if fld.style == "flow" else fld.value
        return [
            part.strip().strip("'\"")
            for part in re.split(r"[,\s]+", raw)
            if part.strip().strip("'\"")
        ]

    # files
    @cached_property
    def markdown_files(self) -> list[Path]:
        """Every Markdown file in the skill, outside .git, sorted."""
        return sorted(
            p for p in self.dir.rglob("*.md") if ".git" not in p.relative_to(self.dir).parts
        )

    def is_reference(self, path: Path) -> bool:
        """True for a Markdown file inside the skill that is not SKILL.md or an asset."""
        try:
            rel = path.resolve().relative_to(self.dir_real)
        except ValueError:
            return False
        return path.suffix == ".md" and path.name != "SKILL.md" and "assets" not in rel.parts

    def links(self, text: str) -> Iterator[tuple[int, str]]:
        """Yield (line, target) for each local link outside code."""
        for number, (line, kind, _) in enumerate(fenced(text.splitlines()), 1):
            if kind != "text":
                continue
            for match in LINK.finditer(INLINE_CODE.sub("", line)):
                target = unquote(match.group(1) or match.group(2))
                if not target.startswith(EXTERNAL) and "${" not in target:
                    yield number, target

    def check_links(self) -> None:
        """Report backslashes in link paths and links to missing files."""
        for path in self.markdown_files:
            text = self.read(path)
            if text is None:
                continue
            for number, target in self.links(text):
                if "\\" in target:
                    self.findings.append(
                        Finding(
                            "link-backslash",
                            "error",
                            self.rel(path),
                            number,
                            f"backslash in a path: {target}",
                            "Use forward slashes.",
                        )
                    )
                elif not (path.parent / target.split("#", 1)[0]).exists():
                    self.findings.append(
                        Finding(
                            "link-broken", "error", self.rel(path), number, f"broken link: {target}"
                        )
                    )

    def check_references(self) -> None:
        """Report long references without contents and references that link to others."""
        for path in self.markdown_files:
            if not self.is_reference(path):
                continue
            text = self.read(path)
            if text is None:
                continue
            lines = text.splitlines()
            first_h2 = next((line.strip() for line in lines if line.startswith("## ")), "")
            if len(lines) > CONTENTS_THRESHOLD and first_h2 != "## Contents":
                self.findings.append(
                    Finding(
                        "reference-contents",
                        "warning",
                        self.rel(path),
                        1,
                        f"{len(lines)} lines and no '## Contents' as the first section;"
                        " partial reads miss its scope",
                    )
                )
            for number, target in self.links(text):
                if self.is_reference(path.parent / target.split("#", 1)[0]):
                    self.findings.append(
                        Finding(
                            "reference-nested",
                            "warning",
                            self.rel(path),
                            number,
                            f"links to another reference ({target});"
                            " link every reference from SKILL.md",
                        )
                    )

    def check_scripts(self, body: list[str], start: int) -> None:
        """Check script paths in the body, then the shebang and mode of each mentioned script."""
        for offset, line in enumerate(body):
            self.check_script_line(line, start + offset)
        scripts = self.dir / "scripts"
        if not scripts.is_dir():
            return
        mentioned = " ".join(text for md in self.markdown_files if (text := self.read(md)))
        for path in sorted(p for p in scripts.rglob("*") if p.is_file()):
            if (
                path.name.startswith(".")
                or "__pycache__" in path.parts
                or path.name == "__init__.py"
            ):
                continue
            if path.name not in mentioned:
                continue  # a helper module imported by another script, never run by its path
            self.check_script_file(path)

    def check_script_line(self, line: str, number: int) -> None:
        """Check the ${CLAUDE_SKILL_DIR} paths and relative script calls on one body line."""
        matches = list(SKILL_DIR_PATH.finditer(line))
        if self.upload:
            if matches:
                scripts_used = any(m.group(1).startswith("scripts/") for m in matches)
                self.add(
                    "script-path",
                    "warning",
                    number,
                    f"${{CLAUDE_SKILL_DIR}} is documented only where Claude Code runs the skill; "
                    f"{self.target} docs use paths relative to the skill",
                    "Call it through its interpreter, relative to the skill: python3 scripts/x.py"
                    if scripts_used
                    else "Use a path relative to the skill: references/x.md",
                )
            return
        for match in matches:
            if not (self.dir / match.group(1).rstrip(".")).exists():
                self.add(
                    "script-missing",
                    "error",
                    number,
                    f"missing file: {match.group(1)}",
                )
        if RELATIVE_SCRIPT.search(line) and "CLAUDE_SKILL_DIR" not in line:
            self.add(
                "script-path",
                "warning",
                number,
                "a relative script path fails:"
                " commands run in the session's directory, not the skill's",
                "Use ${CLAUDE_SKILL_DIR}/scripts/… in the command.",
            )

    def check_script_file(self, path: Path) -> None:
        """Check that a script the skill mentions has an env shebang and is executable."""
        try:
            with path.open("rb") as handle:
                first = handle.readline()
        except OSError as exc:
            self.findings.append(
                Finding("read", "error", self.rel(path), 1, f"cannot read: {type(exc).__name__}")
            )
            return
        if path.suffix not in SCRIPT_SUFFIXES and not first.startswith(b"#!"):
            return
        if not first.startswith(b"#!/usr/bin/env "):
            self.findings.append(
                Finding(
                    "script-shebang",
                    "warning",
                    self.rel(path),
                    1,
                    "no '#!/usr/bin/env <interpreter>' shebang; the script cannot run by its path",
                )
            )
        if os.name != "nt" and not path.stat().st_mode & 0o111:
            self.findings.append(
                Finding(
                    "script-executable",
                    "warning",
                    self.rel(path),
                    1,
                    "not executable",
                    "chmod +x, and commit it as 100755 (git update-index --chmod=+x).",
                )
            )


# --- Output --------------------------------------------------------------------------
def summary(findings: list[Finding]) -> dict[str, int]:
    """Count the findings per severity."""
    return {
        sev: sum(1 for f in findings if f.severity == sev) for sev in ("error", "warning", "info")
    }


def render(skill: Path, results: dict[str, list[Finding]], fmt: str) -> str:
    """Format the report of every surface as JSON or text, most severe findings first."""
    order = {"error": 0, "warning": 1, "info": 2}
    ranked = {
        surface: sorted(found, key=lambda f: (order[f.severity], f.file, f.line))
        for surface, found in results.items()
    }
    if fmt == "text":
        rows = [f"Skill: {skill.as_posix()}"]
        for surface, found in ranked.items():
            counts = summary(found)
            rows.append(f"== {surface}")
            for f in found:
                rows.append(f"{f.severity:7} {f.rule:24} {f.file}:{f.line}  {f.message}")
                if f.hint:
                    rows.append(f"{'':33}hint: {f.hint}")
            rows.append(
                f"Summary: {counts['error']} error, {counts['warning']} warning,"
                f" {counts['info']} info."
            )
        return "\n".join(rows)
    surfaces = {
        surface: {"findings": [asdict(f) for f in found], "summary": summary(found)}
        for surface, found in ranked.items()
    }
    return json.dumps(
        {"skill": skill.as_posix(), "surfaces": surfaces}, indent=2, ensure_ascii=False
    )


def under(path: str, root: str) -> bool:
    """True when `path` is `root` or lies inside it (both already resolved)."""
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


class Inventory(TypedDict):
    """The --list output: every file of the skill and what could not be listed."""

    skill: str
    count: int
    files: list[dict[str, object]]
    not_listed: list[dict[str, str]]
    outside: list[dict[str, object]]
    loops: list[dict[str, str]]


def exists(path: str) -> bool:
    """Like os.path.exists: False when the path is missing or cannot be checked."""
    try:
        Path(path).stat()
    except (OSError, ValueError):
        return False
    return True


class Walk:
    """State of one inventory walk; see `inventory`."""

    def __init__(self, skill: Path) -> None:
        """Start an empty walk of `skill`."""
        self.skill = skill
        self.root_real = os.path.realpath(skill)
        self.files: list[dict[str, object]] = []
        self.not_listed: list[dict[str, str]] = []
        self.outside: list[dict[str, object]] = []
        self.loops: list[dict[str, str]] = []
        self.seen: set[str] = set()

    def rel(self, path: Path) -> str:
        """Return `path` relative to the skill, with forward slashes ("." for the skill)."""
        return path.relative_to(self.skill).as_posix() if path != self.skill else "."

    def failed(self, error: OSError) -> None:
        """Record a folder os.walk could not read."""
        where = self.rel(Path(error.filename)) if error.filename else "?"
        self.not_listed.append({"path": where, "reason": error.strerror or str(error)})

    def folders(self, base: Path, real: str, dirs: list[str]) -> list[str]:
        """Return the subfolders to descend into; record links that leave or loop."""
        keep: list[str] = []
        kept: set[str] = set()
        for name in sorted(
            dirs, key=lambda d: (base / d).is_symlink()
        ):  # real folders before aliases
            target = os.path.realpath(base / name)
            if not under(target, self.root_real):
                self.outside.append(
                    {"path": self.rel(base / name), "target": target, "exists": exists(target)}
                )
            elif target in self.seen or target in kept:
                if under(real, target):
                    self.loops.append(
                        {"path": self.rel(base / name), "target": target}
                    )  # its files are already listed
                # otherwise a duplicate path to a folder already listed: nothing is missing
            else:
                keep.append(name)
                kept.add(target)
        return keep

    def file(self, path: Path) -> None:
        """List one file, or record it as outside the skill or not listable."""
        target = os.path.realpath(path)
        if not under(target, self.root_real):
            self.outside.append(
                {"path": self.rel(path), "target": target, "exists": exists(target)}
            )
            return
        try:
            size = path.stat().st_size
        except OSError as error:
            self.not_listed.append({"path": self.rel(path), "reason": error.strerror or str(error)})
            return
        self.files.append({"path": self.rel(path), "bytes": size})


def inventory(skill: Path) -> Inventory:
    """Every file under the skill, hidden ones included; nothing is opened or excluded.

    Symlinked folders inside the skill are followed (like `find -L`). A folder reached a
    second time is skipped: silently when it is a duplicate path, and under `loops` when
    it links back to an ancestor; either way its files are already listed, so neither
    is a gap. not_listed holds only what could not be read (permissions, errors).
    A link whose target lies outside the skill is not followed: it goes to `outside`,
    with whether its target exists, so the audit never reads files that do not belong
    to the skill and still sees a broken link.
    """
    walk = Walk(skill)
    for root, dirs, names in os.walk(skill, onerror=walk.failed, followlinks=True):
        base = Path(root)
        real = os.path.realpath(base)
        walk.seen.add(real)
        dirs[:] = walk.folders(base, real, dirs)
        for name in names:
            walk.file(base / name)
    walk.files.sort(key=lambda f: str(f["path"]))
    walk.not_listed.sort(key=lambda f: f["path"])
    walk.outside.sort(key=lambda f: str(f["path"]))
    walk.loops.sort(key=lambda f: f["path"])
    return {
        "skill": skill.as_posix(),
        "count": len(walk.files),
        "files": walk.files,
        "not_listed": walk.not_listed,
        "outside": walk.outside,
        "loops": walk.loops,
    }


def render_inventory(data: Inventory, fmt: str) -> str:
    """Format the inventory as JSON or text."""
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    rows = [f"Skill: {data['skill']}  ({data['count']} files)"]
    rows += [f"{f['bytes']:>9}  {f['path']}" for f in data["files"]]
    rows += [f"not listed  {f['path']}  ({f['reason']})" for f in data["not_listed"]]
    rows += [
        f"outside     {f['path']} -> {f['target']}{'' if f['exists'] else '  (missing)'}"
        for f in data["outside"]
    ]
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments, print the report or the inventory, and return the exit code."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)  # absent on some wrapped streams
        if reconfigure is not None:
            with contextlib.suppress(ValueError):
                reconfigure(encoding="utf-8")  # Windows consoles default to another code page
    parser = argparse.ArgumentParser(
        description="Check the structure of one skill directory. Read-only.",
        epilog="Exit codes: 0 report printed (see summary.error), 2 bad input.",
    )
    parser.add_argument(
        "skill_dir", help="directory that holds SKILL.md (a SKILL.md path is accepted)"
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument(
        "--list", action="store_true", help="print the full file inventory instead of checking"
    )
    parser.add_argument(
        "--listing-cap",
        type=int,
        default=LISTING_CAP_DEFAULT,
        help=f"listing cap for description + when_to_use (default {LISTING_CAP_DEFAULT})",
    )
    args = parser.parse_args(argv)
    path = Path(args.skill_dir).expanduser().resolve()
    if path.is_file() and path.name == "SKILL.md":
        path = path.parent
    if not (path / "SKILL.md").is_file():
        sys.stderr.write(f"Error: no SKILL.md in {path}. Pass the skill directory.\n")
        return 2
    if args.list:
        sys.stdout.write(render_inventory(inventory(path), args.format) + "\n")
        return 0
    if args.listing_cap < 1:
        sys.stderr.write("Error: --listing-cap must be a positive number.\n")
        return 2
    results = {surface: Checker(path, surface, args.listing_cap).run() for surface in TARGETS}
    sys.stdout.write(render(path, results, args.format) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
