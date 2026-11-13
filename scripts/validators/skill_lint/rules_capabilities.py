#!/usr/bin/env python3
"""Capability rules (CA) for a skill: its inventory of injected commands, hooks and tools."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import fnmatch
import re
from typing import TYPE_CHECKING, cast

from validators.skill_lint.model import Finding, Severity

if TYPE_CHECKING:
    from validators.skill_lint.discover import Skill
    from validators.skill_lint.markdown_model import BangCommand

SKILLS_DOC = "https://code.claude.com/docs/en/skills"
SOURCES: dict[str, str] = {
    "CA-01": SKILLS_DOC,
    "CA-02": "https://code.claude.com/docs/en/permissions",
    "CA-03": SKILLS_DOC,
    "CA-04": "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview",
}

TOOL_ENTRY = re.compile(r"[^\s,(]+(?:\([^)]*\))?")
BASH_PATTERN = re.compile(r"^Bash\((.*)\)$")
UNSCOPED_BASH = frozenset({"Bash", "Bash(*)", "Bash(:*)"})
ARGUMENT_PLACEHOLDER = re.compile(r"\$ARGUMENTS(?:\[\d+\])?|\$\d+")
CODE_EXTENSIONS = (".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts")
NETWORK_SIGNALS = (
    re.compile(r"\bcurl\b"),
    re.compile(r"\bwget\b"),
    re.compile(r"\burllib\b"),
    re.compile(r"\brequests\b"),
    re.compile(r"\bsocket\b"),
    re.compile(r"\bhttp\.client\b"),
    re.compile(r"\bfetch\("),
    re.compile(r"~/\.ssh"),
    re.compile(r"(?:^|/)\.env\b"),
    re.compile(r"\.netrc"),
)


@dataclass(frozen=True)
class Hook:
    """One frontmatter hook handler."""

    event: str
    matcher: str | None
    type: str
    run: str
    once: bool


@dataclass(frozen=True)
class Inventory:
    """What a skill can do on its own: injected commands, hooks and pre-approved tools."""

    bang: tuple[tuple[str, BangCommand], ...]
    """Each injected command with the file it is in."""
    hooks: tuple[Hook, ...]
    allowed_tools: tuple[str, ...]


def _finding(rule: str, severity: Severity, path: str, line: int | None, message: str) -> Finding:
    """Build one finding with the rule's source URL."""
    return Finding(rule, severity, path, line, message, SOURCES[rule])


def _as_mapping(value: object) -> Mapping[str, object] | None:
    """Return value as a string-keyed mapping, or None."""
    if isinstance(value, Mapping):
        return cast("Mapping[str, object]", value)
    return None


def _as_list(value: object) -> list[object]:
    """Return value as a list of objects, or an empty list."""
    return cast("list[object]", value) if isinstance(value, list) else []


def _allowed_tools(value: object) -> tuple[str, ...]:
    """Read allowed-tools as a space- or comma-separated string, or as a list."""
    if isinstance(value, str):
        return tuple(match.group(0) for match in TOOL_ENTRY.finditer(value))
    return tuple(str(item) for item in _as_list(value))


def _hooks(value: object) -> tuple[Hook, ...]:
    """Read the frontmatter hooks: {Event: [{matcher, hooks: [{type, command|prompt}]}]}."""
    events = _as_mapping(value)
    found: list[Hook] = []
    for event, groups in (events or {}).items():
        for group in _as_list(groups):
            entry = _as_mapping(group) or {}
            matcher = entry.get("matcher")
            for handler in _as_list(entry.get("hooks")):
                fields = _as_mapping(handler) or {}
                run = fields.get("command", fields.get("prompt", ""))
                found.append(
                    Hook(
                        event=event,
                        matcher=matcher if isinstance(matcher, str) else None,
                        type=str(fields.get("type", "")),
                        run=str(run),
                        once=fields.get("once") is True,
                    )
                )
    return tuple(found)


def inventory(skill: Skill) -> Inventory:
    """List the skill's injected commands, frontmatter hooks and allowed-tools entries."""
    bang: list[tuple[str, BangCommand]] = []
    for rel, doc in sorted(skill.markdown.items()):
        if rel.endswith(".md"):
            bang += [(rel, command) for command in doc.bang_commands]
    data = skill.frontmatter.data or {}
    return Inventory(
        bang=tuple(bang),
        hooks=_hooks(data.get("hooks")),
        allowed_tools=_allowed_tools(data.get("allowed-tools")),
    )


def _argument_names(skill: Skill) -> list[str]:
    """Return the names the skill declares in its arguments field."""
    data = skill.frontmatter.data or {}
    value = data.get("arguments")
    if isinstance(value, str):
        return value.split()
    return [str(item) for item in _as_list(value)]


def _ca01(skill: Skill, found: Inventory) -> list[Finding]:
    """CA-01: an argument placeholder inside an injected command."""
    names = "|".join(re.escape(name) for name in _argument_names(skill))
    pattern = ARGUMENT_PLACEHOLDER
    if names:
        pattern = re.compile(rf"{ARGUMENT_PLACEHOLDER.pattern}|\$\{{?(?:{names})\b\}}?")
    findings: list[Finding] = []
    for rel, command in found.bang:
        match = pattern.search(command.command)
        if match is not None:
            message = f"`{match.group(0)}` inside an injected command allows shell injection"
            findings.append(_finding("CA-01", Severity.ERROR, rel, command.line, message))
    return findings


def _approves(entry: str, command: str) -> bool:
    """Tell whether one allowed-tools entry approves a shell command."""
    if entry == "Bash":
        return True
    match = BASH_PATTERN.match(entry)
    if match is None:
        return False
    pattern = match.group(1).replace(":*", " *")
    candidates = [pattern, pattern.removesuffix(" *")] if pattern.endswith(" *") else [pattern]
    return any(fnmatch.fnmatchcase(command.strip(), candidate) for candidate in candidates)


def _ca02_ca03(skill: Skill, found: Inventory) -> list[Finding]:
    """CA-02 (an unscoped Bash entry) and CA-03 (a self-approved injected command)."""
    line = skill.frontmatter.key_lines.get("allowed-tools")
    findings = [
        _finding("CA-02", Severity.WARNING, "SKILL.md", line, f"`{entry}` approves every command")
        for entry in found.allowed_tools
        if entry in UNSCOPED_BASH
    ]
    for rel, command in found.bang:
        entry = next((e for e in found.allowed_tools if _approves(e, command.command)), None)
        if entry is not None:
            message = f"the skill's own `{entry}` pre-approves this injected command"
            findings.append(_finding("CA-03", Severity.WARNING, rel, command.line, message))
    return findings


def _ca04(skill: Skill) -> list[Finding]:
    """CA-04: network or credential signals in scripts (never in Markdown)."""
    findings: list[Finding] = []
    for rel, text in sorted(skill.text.items()):
        if not (rel.lower().endswith(CODE_EXTENSIONS) or text.startswith("#!")):
            continue
        for signal in NETWORK_SIGNALS:
            hit = next(
                (
                    (number, m)
                    for number, line in enumerate(text.split("\n"), start=1)
                    if (m := signal.search(line))
                ),
                None,
            )
            if hit is not None:
                number, match = hit
                message = f"network or credential signal: `{match.group(0)}`"
                findings.append(_finding("CA-04", Severity.WARNING, rel, number, message))
    return findings


def check(skill: Skill) -> list[Finding]:
    """Run the capability rules on one skill."""
    found = inventory(skill)
    return _ca01(skill, found) + _ca02_ca03(skill, found) + _ca04(skill)
