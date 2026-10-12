#!/usr/bin/env python3
"""Check the structure of one skill directory, read-only.

Usage: check_skill.py [--format json|text] [--target code|cowork|upload|api]
                      [--listing-cap N] SKILL_DIR
       check_skill.py --list [--format json|text] SKILL_DIR

--list prints the skill's full file inventory instead of checking it: every
file at any depth, hidden files included, symlinked folders followed, nothing
excluded, names and sizes only (no file is opened).

Checks what `claude plugin validate` does not: frontmatter syntax and quoting,
known fields and values, name and description limits per target surface,
argument placeholders, body size, render-time syntax, links, references and
scripts. It never writes files and never runs the skill.

Targets:
  code    Claude Code skills (personal, project, plugin). Default.
  cowork  Plugin skills used in Cowork.
  upload  claude.ai skill upload (also covers account skills synced to Cowork).
  api     Skills API.

Exit codes: 0 no errors, 1 at least one error, 2 bad input.
Requires Python 3.9+, standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import json
import os
import re
import sys
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import unquote

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
UPLOAD_FIELDS = frozenset({"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
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
PERSON = re.compile(r"^\s*(I|I'm|I'll|I can|We|We'll|You|You can|You'll|Let me)\b", re.I)
TRIGGER = re.compile(r"\b(use|invoke|apply)\b[^.]*?\b(when|whenever|for|if|before|after|to)\b|\bwhen the user\b", re.I)
CLAUDE_VAR = re.compile(r"\$\{CLAUDE_[A-Z_]+\}")
SKILL_DIR_PATH = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9_./-]+)")
MONEY = re.compile(r"(?<![\\\w])\$\d+(?:[.,]\d+)")
INDEXED = re.compile(r"(?<![\\\w])\$(?:ARGUMENTS(?:\[\d+\])?|\d+)(?![\w.,])")
DYNAMIC_INLINE = re.compile(r"(?:^|\s)!`")
RELATIVE_SCRIPT = re.compile(
    r"`(?:(?:python3?|bash|sh|node)\s+(?:\./)?scripts/[^`\s]+|\./scripts/[^`\s]+|scripts/[^`\s]+\s+[^`]*)`"
)  # a command, not a bare file mention
SCRIPT_SUFFIXES = frozenset({".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl"})
EXTERNAL = ("http://", "https://", "mailto:", "#")


@dataclass
class Finding:
    rule: str
    severity: str  # error | warning | info
    file: str
    line: int
    message: str
    hint: str = ""


@dataclass
class Field:
    key: str
    line: int
    raw: str  # text after "key:" on its own line
    style: str  # plain | single | double | block | flow | nested | empty
    value: str  # best-effort text value
    lines: int = 1  # physical lines the value spans


@dataclass
class Frontmatter:
    fields: dict[str, Field] = field(default_factory=dict)
    end_line: int = 0  # line number of the closing marker


# --- Frontmatter parsing (top-level keys only, no dependencies) -------------------
def parse_scalar(raw: str) -> tuple[str, str]:
    """Return (style, value) for a single-line scalar."""
    if not raw:
        return "empty", ""
    if raw[0] == '"' and len(raw) >= 2 and raw.endswith('"'):
        return "double", raw[1:-1].replace('\\"', '"')
    if raw[0] == "'" and len(raw) >= 2 and raw.endswith("'"):
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
                current.lines += 1
                if current.style == "block" or current.style == "plain":
                    current.value = (current.value + " " + text.strip()).strip()
                elif current.style == "empty":
                    current.style = "nested"
            continue
        match = KEY_LINE.match(text)
        if match is None:
            problems.append(("frontmatter-syntax", number, f"not a 'key: value' line: {text.strip()}"))
            current = None
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        style, value = parse_scalar(raw)
        current = Field(key=key, line=number, raw=raw, style=style, value=value)
        fm.fields[key] = current
    return fm, problems


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
            match and match.group(1)[0] == opener[0] and len(match.group(1)) >= opener[1] and not match.group(2).strip()
        ):
            opener = None
            yield line, "fence", ""
        else:
            yield line, "code", ""


class Checker:
    def __init__(self, skill_dir: Path, target: str, listing_cap: int) -> None:
        self.dir = skill_dir
        self.skill_md = skill_dir / "SKILL.md"
        self.target = target
        self.listing_cap = listing_cap
        self.findings: list[Finding] = []
        self.texts: dict[Path, str | None] = {}

    # helpers
    def add(self, rule: str, severity: str, path: Path, line: int, message: str, hint: str = "") -> None:
        rel = path.relative_to(self.dir).as_posix()
        self.findings.append(Finding(rule, severity, rel, line, message, hint))

    def read(self, path: Path) -> str | None:
        if path not in self.texts:
            try:
                self.texts[path] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                self.add("read", "error", path, 1, f"cannot read as UTF-8 text: {type(exc).__name__}")
                self.texts[path] = None
        return self.texts[path]

    @property
    def upload(self) -> bool:
        return self.target in UPLOAD_TARGETS

    # entry point
    def run(self) -> list[Finding]:
        text = self.read(self.skill_md)
        if text is None:
            return self.findings
        lines = text.splitlines()
        fm, problems = parse_frontmatter(lines)
        for rule, line, message in problems:
            self.add(rule, "error", self.skill_md, line, message)
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
        allowed = UPLOAD_FIELDS if self.upload else CODE_FIELDS
        fld: Field | None
        for key, fld in fm.fields.items():
            if key not in allowed:
                guess = difflib.get_close_matches(key, sorted(CODE_FIELDS), n=1)
                if self.upload and key in CODE_FIELDS:
                    self.add(
                        "field-unknown",
                        "error",
                        self.skill_md,
                        fld.line,
                        f"'{key}' is a Claude Code-only field; {self.target} rejects the skill",
                        "Remove it, or keep two versions of the skill.",
                    )
                else:
                    hint = f"Did you mean '{guess[0]}'?" if guess else "Remove it or check the field list."
                    self.add(
                        "field-unknown",
                        "error" if self.upload else "warning",
                        self.skill_md,
                        fld.line,
                        f"unknown field '{key}': Claude Code ignores it silently"
                        + (f" (did you mean '{guess[0]}'?)" if guess else ""),
                        hint,
                    )
        for key in BOOLEAN_FIELDS:
            fld = fm.fields.get(key)
            if fld and fld.value.lower() not in BOOLEAN_VALUES:
                self.add(
                    "field-value", "error", self.skill_md, fld.line, f"'{key}' must be true or false, got '{fld.value}'"
                )
        for key, values in ENUM_FIELDS.items():
            fld = fm.fields.get(key)
            if fld and fld.value and fld.value.lower() not in values:
                self.add(
                    "field-value",
                    "error",
                    self.skill_md,
                    fld.line,
                    f"'{key}' must be one of {', '.join(sorted(values))}, got '{fld.value}'",
                )
        compat = fm.fields.get("compatibility")
        if compat and len(compat.value) > COMPATIBILITY_MAX:
            self.add(
                "field-value",
                "error",
                self.skill_md,
                compat.line,
                f"'compatibility' is {len(compat.value)} characters; the limit is {COMPATIBILITY_MAX}",
            )
        meta = fm.fields.get("metadata")
        if meta and meta.style not in {"nested", "flow"}:
            self.add(
                "field-value",
                "warning",
                self.skill_md,
                meta.line,
                "'metadata' must be a map; Claude Code drops any other value",
            )
        for key in ("argument-hint", "when_to_use", "model", "agent"):
            fld = fm.fields.get(key)
            if fld and fld.style == "plain":
                reason = needs_quotes(fld.value)
                if reason:
                    self.add(
                        "yaml-quoting",
                        "error",
                        self.skill_md,
                        fld.line,
                        f"'{key}' {reason}: strict YAML parsers and uploads read it differently",
                        "Quote the value.",
                    )
            elif fld and fld.style == "flow" and key == "argument-hint":
                self.add(
                    "yaml-quoting",
                    "error",
                    self.skill_md,
                    fld.line,
                    "'argument-hint' starts with '[', so YAML reads a list, not text",
                    'Quote it: argument-hint: "[tag]".',
                )

    # name
    def check_name(self, fm: Frontmatter) -> None:
        fld = fm.fields.get("name")
        if fld is None or not fld.value:
            self.add(
                "name-missing",
                "error" if self.upload else "warning",
                self.skill_md,
                1,
                "no 'name': Claude Code uses the directory name; uploads and the spec require it",
            )
            return
        name, line = fld.value, fld.line
        if len(name) > NAME_MAX:
            self.add(
                "name-length",
                "error",
                self.skill_md,
                line,
                f"'name' is {len(name)} characters; the limit is {NAME_MAX}",
            )
        if not NAME_PATTERN.match(name):
            self.add(
                "name-format",
                "error",
                self.skill_md,
                line,
                "'name' must use lowercase letters, digits and single hyphens, with no hyphen at either end",
            )
        for word in RESERVED_WORDS:
            if word in name:
                self.add(
                    "name-reserved",
                    "error" if self.upload else "info",
                    self.skill_md,
                    line,
                    f"'name' contains the reserved word '{word}': claude.ai uploads and the Skills API reject it"
                    + ("" if self.upload else "; it matters only if you upload the skill"),
                )
        if name != self.dir.name:
            self.add(
                "name-directory",
                "error" if self.upload else "warning",
                self.skill_md,
                line,
                f"'name' is '{name}' but the directory is '{self.dir.name}'; the spec requires them to match",
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
                self.skill_md,
                line,
                "the directory is named 'synced', which Claude Code reserves for skills synced from claude.ai;"
                " it skips this skill",
                "Rename the directory.",
            )
        for value in (self.dir.name, fld.value if fld else ""):
            if value == "anthropic-skills" or value.startswith("anthropic-skills:"):
                self.add(
                    "name-reserved-local",
                    "error",
                    self.skill_md,
                    line,
                    f"'{value}' uses 'anthropic-skills', which Claude Code reserves for synced skills;"
                    " it does not load",
                    "Rename the directory and the 'name'.",
                )
                break

    # description
    def check_description(self, fm: Frontmatter) -> None:
        fld = fm.fields.get("description")
        if fld is None or not fld.value:
            self.add(
                "description-missing",
                "error",
                self.skill_md,
                fld.line if fld else 1,
                "no 'description': Claude has nothing to decide when to use the skill",
            )
            return
        text, line = fld.value, fld.line
        if fld.style == "block" or fld.lines > 1:
            self.add(
                "description-one-line",
                "warning",
                self.skill_md,
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
                    self.skill_md,
                    line,
                    f"'description' {reason}: strict YAML parsers and uploads reject or cut it",
                    "Reword it so it needs no quotes (for example 'Use when …' instead of 'Use when: …'), or quote it.",
                )
        elif fld.style in {"double", "single"} and not needs_quotes(text) and "\\" not in fld.raw:
            self.add(
                "yaml-quoting",
                "info",
                self.skill_md,
                line,
                "'description' is quoted but needs no quotes",
                "Recommended: write it as one plain, unquoted line.",
            )
        if TAG.search(text):
            self.add(
                "description-tags",
                "error" if self.upload else "info",
                self.skill_md,
                line,
                "'description' contains an angle-bracket tag; uploads reject it and Claude Code escapes it",
            )
        if PERSON.match(text):
            self.add(
                "description-person",
                "warning",
                self.skill_md,
                line,
                "'description' is not in the third person; it is read as part of the system prompt",
                "Start with what the skill does: 'Formats …'.",
            )
        if not TRIGGER.search(text):
            self.add(
                "description-trigger",
                "warning",
                self.skill_md,
                line,
                "'description' says what the skill does but not when to use it",
                "Add a 'Use when …' clause with the words users type.",
            )
        if self.upload:
            if len(text) > DESCRIPTION_MAX:
                self.add(
                    "description-length",
                    "error",
                    self.skill_md,
                    line,
                    f"'description' is {len(text)} characters; {self.target} rejects more than {DESCRIPTION_MAX}",
                )
        else:
            when = fm.fields.get("when_to_use")
            total = len(text) + (len(when.value) if when else 0)
            if total > self.listing_cap:
                self.add(
                    "description-listing-cap",
                    "warning",
                    self.skill_md,
                    line,
                    f"'description' + 'when_to_use' is {total} characters; Claude Code cuts the listing at "
                    f"{self.listing_cap} for users with that setting (default {LISTING_CAP_DEFAULT})",
                    "Put the key use case first, shorten it, or pass --listing-cap for a known audience.",
                )

    # body
    def check_body(self, body: list[str], start: int, fm: Frontmatter | None) -> None:
        if len(body) >= BODY_LINES_MAX:
            self.add(
                "body-lines",
                "warning",
                self.skill_md,
                start,
                f"the body is {len(body)} lines; keep SKILL.md under {BODY_LINES_MAX} and move detail to references",
            )
        tokens = sum(len(line) + 1 for line in body) // CHARS_PER_TOKEN
        if tokens > BODY_TOKENS_MAX:
            self.add(
                "body-tokens",
                "warning",
                self.skill_md,
                start,
                f"the body is about {tokens} tokens; aim under {BODY_TOKENS_MAX}",
            )
        declared = self.declared_arguments(fm)
        used: set[str] = set()
        for offset, (line, kind, info) in enumerate(fenced(body)):
            number = start + offset
            if kind == "fence":
                if info.startswith("!"):
                    self.dynamic(number)
                continue
            in_fence = kind == "code"
            for name in declared:
                if re.search(rf"(?<![\\\w])\${re.escape(name)}(?!\w)", line):
                    used.add(name)
            for match in MONEY.finditer(line):
                self.add(
                    "arguments-escape",
                    "warning",
                    self.skill_md,
                    number,
                    f"'{match.group(0)}' expands as an argument placeholder when the skill loads",
                    f"Escape it: \\{match.group(0)}.",
                )
            if in_fence and INDEXED.search(line):
                self.add(
                    "arguments-escape",
                    "warning",
                    self.skill_md,
                    number,
                    "an argument placeholder inside a code block still expands when the skill loads",
                    "Escape the '$' if the example must stay literal.",
                )
            if in_fence:
                continue
            if DYNAMIC_INLINE.search(line):
                self.dynamic(number)
            if CLAUDE_VAR.search(INLINE_CODE.sub("", line)):
                self.add(
                    "render-variable",
                    "warning",
                    self.skill_md,
                    number,
                    "a ${CLAUDE_*} variable in prose expands to a path when the skill loads",
                    "Name it without braces in prose; keep the braced form in commands.",
                )
        for name in sorted(set(declared) - used):
            self.add(
                "arguments-unused",
                "warning",
                self.skill_md,
                start,
                f"argument '{name}' is declared in 'arguments' but '${name}' never appears in the body",
            )

    def dynamic(self, number: int) -> None:
        if self.upload:
            self.add(
                "dynamic-context",
                "error",
                self.skill_md,
                number,
                f"dynamic-context commands do not run on {self.target}",
            )
        elif self.target == "cowork":
            self.add(
                "dynamic-context",
                "warning",
                self.skill_md,
                number,
                "in Cowork this command is replaced by a placeholder and does not run",
            )
        else:
            self.add(
                "dynamic-context",
                "info",
                self.skill_md,
                number,
                "runs when the skill loads; a non-zero exit aborts the whole skill",
            )

    @staticmethod
    def declared_arguments(fm: Frontmatter | None) -> list[str]:
        if fm is None or "arguments" not in fm.fields:
            return []
        fld = fm.fields["arguments"]
        raw = fld.raw.strip("[]") if fld.style == "flow" else fld.value
        return [part.strip().strip("'\"") for part in re.split(r"[,\s]+", raw) if part.strip().strip("'\"")]

    # files
    def markdown_files(self) -> list[Path]:
        return sorted(p for p in self.dir.rglob("*.md") if ".git" not in p.relative_to(self.dir).parts)

    def is_reference(self, path: Path) -> bool:
        try:
            rel = path.resolve().relative_to(self.dir.resolve())
        except ValueError:
            return False
        return path.suffix == ".md" and path.name != "SKILL.md" and "assets" not in rel.parts

    def links(self, text: str) -> Iterator[tuple[int, str]]:
        for number, (line, kind, _) in enumerate(fenced(text.splitlines()), 1):
            if kind != "text":
                continue
            for match in LINK.finditer(INLINE_CODE.sub("", line)):
                target = unquote(match.group(1) or match.group(2))
                if not target.startswith(EXTERNAL) and "${" not in target:
                    yield number, target

    def check_links(self) -> None:
        for path in self.markdown_files():
            text = self.read(path)
            if text is None:
                continue
            for number, target in self.links(text):
                if "\\" in target:
                    self.add(
                        "link-backslash",
                        "error",
                        path,
                        number,
                        f"backslash in a path: {target}",
                        "Use forward slashes.",
                    )
                elif not (path.parent / target.split("#", 1)[0]).exists():
                    self.add("link-broken", "error", path, number, f"broken link: {target}")

    def check_references(self) -> None:
        for path in self.markdown_files():
            if not self.is_reference(path):
                continue
            text = self.read(path)
            if text is None:
                continue
            lines = text.splitlines()
            first_h2 = next((line.strip() for line in lines if line.startswith("## ")), "")
            if len(lines) > CONTENTS_THRESHOLD and first_h2 != "## Contents":
                self.add(
                    "reference-contents",
                    "warning",
                    path,
                    1,
                    f"{len(lines)} lines and no '## Contents' as the first section; partial reads miss its scope",
                )
            for number, target in self.links(text):
                if self.is_reference(path.parent / target.split("#", 1)[0]):
                    self.add(
                        "reference-nested",
                        "warning",
                        path,
                        number,
                        f"links to another reference ({target}); link every reference from SKILL.md",
                    )

    def check_scripts(self, body: list[str], start: int) -> None:
        for offset, line in enumerate(body):
            number = start + offset
            matches = list(SKILL_DIR_PATH.finditer(line))
            if self.upload and matches:
                scripts_used = any(m.group(1).startswith("scripts/") for m in matches)
                self.add(
                    "script-path",
                    "error",
                    self.skill_md,
                    number,
                    f"${{CLAUDE_SKILL_DIR}} does not exist on {self.target}",
                    "Call it through its interpreter, relative to the skill: python3 scripts/x.py"
                    if scripts_used
                    else "Use a path relative to the skill: references/x.md",
                )
            for match in matches:
                if self.upload:
                    continue
                if not (self.dir / match.group(1).rstrip(".")).exists():
                    self.add("script-missing", "error", self.skill_md, number, f"missing file: {match.group(1)}")
            if not self.upload and RELATIVE_SCRIPT.search(line) and "CLAUDE_SKILL_DIR" not in line:
                self.add(
                    "script-path",
                    "warning",
                    self.skill_md,
                    number,
                    "a relative script path fails: commands run in the session's directory, not the skill's",
                    "Use ${CLAUDE_SKILL_DIR}/scripts/… in the command.",
                )
        scripts = self.dir / "scripts"
        if not scripts.is_dir():
            return
        mentioned = " ".join(text for md in self.markdown_files() if (text := self.read(md)))
        for path in sorted(p for p in scripts.rglob("*") if p.is_file()):
            if path.name.startswith(".") or "__pycache__" in path.parts or path.name == "__init__.py":
                continue
            if path.name not in mentioned:
                continue  # a helper module imported by another script, never run by its path
            try:
                with path.open("rb") as handle:
                    first = handle.readline()
            except OSError as exc:
                self.add("read", "error", path, 1, f"cannot read: {type(exc).__name__}")
                continue
            if path.suffix not in SCRIPT_SUFFIXES and not first.startswith(b"#!"):
                continue
            if not first.startswith(b"#!/usr/bin/env "):
                self.add(
                    "script-shebang",
                    "warning",
                    path,
                    1,
                    "no '#!/usr/bin/env <interpreter>' shebang; the script cannot run by its path",
                )
            if os.name != "nt" and not path.stat().st_mode & 0o111:
                self.add(
                    "script-executable",
                    "warning",
                    path,
                    1,
                    "not executable",
                    "chmod +x, and commit it as 100755 (git update-index --chmod=+x).",
                )


# --- Output --------------------------------------------------------------------------
def summary(findings: list[Finding]) -> dict[str, int]:
    return {sev: sum(1 for f in findings if f.severity == sev) for sev in ("error", "warning", "info")}


def render(skill: Path, target: str, findings: list[Finding], fmt: str) -> str:
    order = {"error": 0, "warning": 1, "info": 2}
    findings = sorted(findings, key=lambda f: (order[f.severity], f.file, f.line))
    counts = summary(findings)
    if fmt == "text":
        rows = [f"Skill: {skill.as_posix()}  (target: {target})"]
        for f in findings:
            rows.append(f"{f.severity:7} {f.rule:24} {f.file}:{f.line}  {f.message}")
            if f.hint:
                rows.append(f"{'':33}hint: {f.hint}")
        rows.append(f"Summary: {counts['error']} error, {counts['warning']} warning, {counts['info']} info.")
        return "\n".join(rows)
    return json.dumps(
        {"skill": skill.as_posix(), "target": target, "findings": [asdict(f) for f in findings], "summary": counts},
        indent=2,
        ensure_ascii=False,
    )


def inventory(skill: Path) -> dict[str, object]:
    """Every file under the skill, hidden ones included; nothing is opened or excluded.

    Symlinked folders are followed (like `find -L`); a folder already visited through
    another path (a symlink loop) is reported in not_listed instead of being entered again.
    """
    files: list[dict[str, object]] = []
    not_listed: list[dict[str, str]] = []
    seen: set[str] = set()

    def rel(path: Path) -> str:
        return path.relative_to(skill).as_posix() if path != skill else "."

    def failed(error: OSError) -> None:
        where = rel(Path(error.filename)) if error.filename else "?"
        not_listed.append({"path": where, "reason": error.strerror or str(error)})

    for root, dirs, names in os.walk(skill, onerror=failed, followlinks=True):
        base = Path(root)
        real = os.path.realpath(base)
        if real in seen:
            dirs[:] = []
            not_listed.append({"path": rel(base), "reason": "symlink loop"})
            continue
        seen.add(real)
        for name in names:
            path = base / name
            try:
                size = path.stat().st_size
            except OSError as error:
                not_listed.append({"path": rel(path), "reason": error.strerror or str(error)})
                continue
            files.append({"path": rel(path), "bytes": size})
    files.sort(key=lambda f: str(f["path"]))
    not_listed.sort(key=lambda f: f["path"])
    return {"skill": skill.as_posix(), "count": len(files), "files": files, "not_listed": not_listed}


def render_inventory(data: dict[str, object], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    files = data["files"]
    not_listed = data["not_listed"]
    assert isinstance(files, list) and isinstance(not_listed, list)
    rows = [f"Skill: {data['skill']}  ({data['count']} files)"]
    rows += [f"{f['bytes']:>9}  {f['path']}" for f in files]
    rows += [f"not listed  {f['path']}  ({f['reason']})" for f in not_listed]
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)  # absent on some wrapped streams
        if reconfigure is not None:
            with contextlib.suppress(ValueError):
                reconfigure(encoding="utf-8")  # Windows consoles default to another code page
    parser = argparse.ArgumentParser(
        description="Check the structure of one skill directory. Read-only.",
        epilog="Exit codes: 0 no errors, 1 errors found, 2 bad input.",
    )
    parser.add_argument("skill_dir", help="directory that holds SKILL.md (a SKILL.md path is accepted)")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--list", action="store_true", help="print the full file inventory instead of checking")
    parser.add_argument(
        "--target", choices=TARGETS, default="code", help="surface the skill must work on (default code)"
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
    findings = Checker(path, args.target, args.listing_cap).run()
    sys.stdout.write(render(path, args.target, findings, args.format) + "\n")
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
