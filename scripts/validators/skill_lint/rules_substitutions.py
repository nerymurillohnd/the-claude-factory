#!/usr/bin/env python3
"""Substitution rules (CA-05, CA-06): text Claude Code replaces when it loads SKILL.md.

Claude Code substitutes argument placeholders and `${CLAUDE_*}` variables in the skill's
Markdown content, which is SKILL.md's body, before Claude reads it (code.claude.com/docs/en/skills,
"Available string substitutions"). Reference files are read later with the Read tool, unchanged.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from validators.skill_lint.discover import body_lines
from validators.skill_lint.model import Finding, Severity

if TYPE_CHECKING:
    from validators.skill_lint.discover import Skill

SUBSTITUTIONS_DOC = "https://code.claude.com/docs/en/skills#available-string-substitutions"
SOURCES: dict[str, str] = {
    "CA-05": SUBSTITUTIONS_DOC,
    "CA-06": SUBSTITUTIONS_DOC,
}

ARGUMENT = re.compile(r"\$ARGUMENTS(?:\[\d+\])?|\$\d")
PATH_VARIABLE = re.compile(r"\$\{(CLAUDE_[A-Z_]+)\}")
PATH_USE = re.compile(r"[\"']?/")
INLINE_SPAN = re.compile(r"`([^`]+)`")
ALWAYS_PATHS = frozenset({"CLAUDE_SKILL_DIR", "CLAUDE_PROJECT_DIR"})
PLUGIN_PATHS = frozenset({"CLAUDE_PLUGIN_ROOT", "CLAUDE_PLUGIN_DATA"})


def _finding(rule: str, severity: Severity, line: int, message: str) -> Finding:
    """Build one SKILL.md finding with the rule's source URL."""
    return Finding(rule, severity, "SKILL.md", line, message, SOURCES[rule])


def _escaped(text: str, start: int) -> bool:
    """Tell whether exactly one backslash sits directly before position start."""
    return text[max(start - 1, 0) : start] == "\\" and text[max(start - 2, 0) : start] != "\\\\"


def _body_lines(skill: Skill) -> list[tuple[int, str]]:
    """Return SKILL.md's body lines with their numbers, without its injected commands.

    Injected commands are CA-01's: an inline one is cut from its line, and a block one drops
    the lines between its fences.
    """
    start, body = body_lines(skill.text, skill.frontmatter)
    lines = dict(enumerate(body, start=start))
    for command in skill.body.bang_commands:
        if command.block:
            for number in range(command.line + 1, command.line + 1 + command.command.count("\n")):
                lines[number] = ""
        else:
            lines[command.line] = lines.get(command.line, "").replace(f"!`{command.command}`", "")
    return sorted(lines.items())


def _declares_arguments(skill: Skill) -> bool:
    """Tell whether the skill says it takes arguments, so its placeholders are intended."""
    data = skill.frontmatter.data or {}
    return "arguments" in data or "argument-hint" in data


def _ca05(skill: Skill, lines: list[tuple[int, str]]) -> list[Finding]:
    """CA-05: an argument placeholder in a skill that declares no arguments."""
    if _declares_arguments(skill):
        return []
    findings: list[Finding] = []
    for number, text in lines:
        for match in ARGUMENT.finditer(text):
            if not _escaped(text, match.start()):
                token = match.group(0)
                message = (
                    f"`{token}` is replaced with the skill's arguments when it loads; write "
                    f"`\\{token}` to keep it literal, or declare `argument-hint` if it takes "
                    "arguments"
                )
                findings.append(_finding("CA-05", Severity.ERROR, number, message))
    return findings


def _code_block_lines(skill: Skill) -> set[int]:
    """Return the SKILL.md lines inside fenced or indented code blocks, fence lines included."""
    lines: set[int] = set()
    for snippet in skill.body.code:
        if not snippet.inline:
            lines.update(range(snippet.line, snippet.line + snippet.text.count("\n") + 1))
    return lines


def _named(text: str, match: re.Match[str]) -> bool:
    """Tell whether a variable is written as a name: in prose, or alone in an inline span.

    Inside a longer inline span, such as a command, it is used as a value.
    """
    for span in INLINE_SPAN.finditer(text):
        if span.start() < match.start() < span.end():
            return span.group(1).strip().strip("\"'") == match.group(0)
    return True


def _ca06(skill: Skill, lines: list[tuple[int, str]]) -> list[Finding]:
    """CA-06: a path variable written as a bare name, so Claude reads a path instead."""
    names = ALWAYS_PATHS | PLUGIN_PATHS if skill.kind == "plugin" else ALWAYS_PATHS
    blocks = _code_block_lines(skill)
    findings: list[Finding] = []
    for number, text in lines:
        if number in blocks:
            continue
        for match in PATH_VARIABLE.finditer(text):
            if (
                match.group(1) in names
                and PATH_USE.match(text, match.end()) is None
                and _named(text, match)
            ):
                message = (
                    f"`{match.group(0)}` is replaced with a path when the skill loads, so Claude "
                    "reads the path, not the variable name. Fine when the path is what you mean; "
                    "to name the variable, put the sentence in a reference file"
                )
                findings.append(_finding("CA-06", Severity.WARNING, number, message))
    return findings


def check(skill: Skill) -> list[Finding]:
    """Run the substitution rules on one skill's SKILL.md body."""
    lines = _body_lines(skill)
    return _ca05(skill, lines) + _ca06(skill, lines)
