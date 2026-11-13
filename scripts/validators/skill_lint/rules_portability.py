#!/usr/bin/env python3
"""Portability rules (PO) for a skill: what works only on some Claudesurfaces."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from validators.skill_lint.model import Finding, Severity

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validators.skill_lint.discover import Skill
    from validators.skill_lint.markdown_model import MarkdownDoc

SKILLS_DOC = "https://code.claude.com/docs/en/skills"
OVERVIEW_DOC = "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview"
SPEC_DOC = "https://agentskills.io/specification"
SOURCES: dict[str, str] = {
    "PO-01": SKILLS_DOC,
    "PO-02": "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices",
    "PO-03": SKILLS_DOC,
    "PO-04": SKILLS_DOC,
    "PO-06": SPEC_DOC,
    "PO-07": OVERVIEW_DOC,
}

SPEC_FIELDS = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)
PLUGIN_VARIABLE = re.compile(r"\$\{?CLAUDE_PLUGIN_(?:ROOT|DATA)\b\}?")
BACKSLASH_PATH = re.compile(r"(?:scripts|references|assets)\\[\w.\\-]+")
RESERVED_WORDS = ("anthropic", "claude")
SKILL_MD = "SKILL.md"


def _finding(rule: str, severity: Severity, path: str, line: int | None, message: str) -> Finding:
    """Build one finding with the rule's source URL."""
    return Finding(rule, severity, path, line, message, SOURCES[rule])


def _po01(skill: Skill) -> list[Finding]:
    """PO-01: plugin variables in a skill that is not in a plugin."""
    if skill.kind == "plugin":
        return []
    findings: list[Finding] = []
    for rel, text in sorted(skill.text.items()):
        for number, line in enumerate(text.splitlines(), start=1):
            match = PLUGIN_VARIABLE.search(line)
            if match is not None:
                message = (
                    f"`{match.group(0)}` exists only in plugin skills; this is a {skill.kind} skill"
                )
                findings.append(_finding("PO-01", Severity.ERROR, rel, number, message))
                break
    return findings


def _po02(docs: Mapping[str, MarkdownDoc]) -> list[Finding]:
    """PO-02: a backslash in a link target or a script path."""
    findings: list[Finding] = []
    for rel, doc in sorted(docs.items()):
        for link in doc.links:
            if "\\" in link.target:
                message = f"link `{link.target}` uses a backslash; use forward slashes"
                findings.append(_finding("PO-02", Severity.ERROR, rel, link.line, message))
        for snippet in doc.code:
            match = BACKSLASH_PATH.search(snippet.text)
            if match is not None:
                message = f"path `{match.group(0)}` uses a backslash; use forward slashes"
                findings.append(_finding("PO-02", Severity.ERROR, rel, snippet.line, message))
    return findings


def _po03_po06_po07(skill: Skill) -> list[Finding]:
    """PO-03, PO-06 and PO-07: frontmatter fields, allowed-tools shape and reserved words."""
    data = skill.frontmatter.data
    if data is None:
        return []
    lines = skill.frontmatter.key_lines
    findings: list[Finding] = []
    extra = [key for key in data if key not in SPEC_FIELDS]
    if extra:
        names = ", ".join(f"`{key}`" for key in extra)
        message = f"fields outside the Agent Skills spec work only in Claude Code: {names}"
        findings.append(_finding("PO-03", Severity.WARNING, SKILL_MD, lines.get(extra[0]), message))
    if isinstance(data.get("allowed-tools"), list):
        message = "`allowed-tools` is a YAML list; the spec defines a space-separated string"
        line = lines.get("allowed-tools")
        findings.append(_finding("PO-06", Severity.WARNING, SKILL_MD, line, message))
    name = data.get("name")
    if isinstance(name, str):
        words = [word for word in RESERVED_WORDS if word in name.lower()]
        if words:
            message = f"the name contains the reserved word `{words[0]}`; the Claude API rejects it"
            findings.append(
                _finding("PO-07", Severity.WARNING, SKILL_MD, lines.get("name"), message)
            )
    return findings


def _po04(docs: Mapping[str, MarkdownDoc]) -> list[Finding]:
    """PO-04: injected commands, which run only in Claude Code."""
    findings: list[Finding] = []
    for rel, doc in sorted(docs.items()):
        for command in doc.bang_commands:
            form = "a ```! block" if command.block else "a !`command`"
            message = f"{form} does not run in claude.ai chat or Cowork"
            findings.append(_finding("PO-04", Severity.WARNING, rel, command.line, message))
    return findings


def check(skill: Skill) -> list[Finding]:
    """Run the portability rules on one skill."""
    docs = skill.markdown
    return _po01(skill) + _po02(docs) + _po03_po06_po07(skill) + _po04(docs)
