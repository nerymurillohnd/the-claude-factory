"""Content rules (CO) for a skill's SKILL.md."""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import TYPE_CHECKING, cast

from validators.skill_lint.model import Finding, Severity

if TYPE_CHECKING:
    from validators.skill_lint.discover import Skill

SKILLS_DOC = "https://code.claude.com/docs/en/skills"
SPEC_DOC = "https://agentskills.io/specification"
BEST_PRACTICES_DOC = (
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
)
SOURCES: dict[str, str] = {
    "CO-01": SKILLS_DOC,
    "CO-02": SPEC_DOC,
    "CO-03": SPEC_DOC,
    "CO-04": SKILLS_DOC,
    "CO-05": SPEC_DOC,
    "CO-06": BEST_PRACTICES_DOC,
}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
XML_RE = re.compile(r"<[A-Za-z/!?][^>]*>")
NAME_RULE_TEXT = (
    "it must use only a-z, 0-9 and single hyphens, with no leading or trailing hyphen, "
    "no `<>`, and no control or zero-width characters"
)
NAME_MAX = 64
DESCRIPTION_MAX = 1024
LISTING_MAX = 1536
COMPATIBILITY_MAX = 500
BODY_LINES_LIMIT = 500


def _finding(skill: Skill, rule: str, key: str | None, message: str) -> Finding:
    """Build an ERROR on SKILL.md at the key's line, or line 1 when the key is absent."""
    line = skill.frontmatter.key_lines.get(key, 1) if key is not None else 1
    return Finding(rule, Severity.ERROR, "SKILL.md", line, message, SOURCES[rule])


def _co02(skill: Skill, data: Mapping[str, object]) -> list[Finding]:
    """CO-02: name is 1-64 characters of a-z0-9-, well formed, and equals the folder."""
    if "name" not in data:
        return [_finding(skill, "CO-02", "name", "`name` is missing")]
    name = data["name"]
    if not isinstance(name, str):
        return [_finding(skill, "CO-02", "name", "`name` must be a string")]
    problems: list[str] = []
    if not 1 <= len(name) <= NAME_MAX:
        problems.append(f"it has {len(name)} characters, not 1 to {NAME_MAX}")
    if not NAME_RE.fullmatch(name):
        problems.append(NAME_RULE_TEXT)
    if problems:
        return [
            _finding(skill, "CO-02", "name", f"`name` {name!r} is invalid: " + "; ".join(problems))
        ]
    if name != skill.root.name:
        message = f"`name` {name!r} must equal the folder name {skill.root.name!r}"
        return [_finding(skill, "CO-02", "name", message)]
    return []


def _co03(skill: Skill, data: Mapping[str, object]) -> list[Finding]:
    """CO-03: description is a non-empty string of at most 1,024 characters, no XML tags."""
    if "description" not in data:
        return [_finding(skill, "CO-03", "description", "`description` is missing")]
    description = data["description"]
    if not isinstance(description, str) or not description.strip():
        message = "`description` must be a non-empty string"
        return [_finding(skill, "CO-03", "description", message)]
    findings: list[Finding] = []
    if len(description) > DESCRIPTION_MAX:
        message = f"`description` has {len(description)} characters, over {DESCRIPTION_MAX}"
        findings.append(_finding(skill, "CO-03", "description", message))
    if XML_RE.search(description):
        message = "`description` must not contain XML tags"
        findings.append(_finding(skill, "CO-03", "description", message))
    return findings


def _co04(skill: Skill, data: Mapping[str, object]) -> list[Finding]:
    """CO-04: description plus when_to_use fit in 1,536 characters, or Claude Code truncates."""
    total = 0
    for key in ("description", "when_to_use"):
        value = data.get(key)
        if isinstance(value, str):
            total += len(value)
    if total <= LISTING_MAX:
        return []
    message = (
        f"`description` and `when_to_use` total {total} characters; Claude Code truncates "
        f"the skill listing beyond {LISTING_MAX}, so the end is truncated"
    )
    return [_finding(skill, "CO-04", "description", message)]


def _all_strings(mapping: Mapping[object, object]) -> bool:
    """Return True when every key and value is a string."""
    return all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items())


def _co05(skill: Skill, data: Mapping[str, object]) -> list[Finding]:
    """CO-05: compatibility is at most 500 characters; metadata maps strings to strings."""
    findings: list[Finding] = []
    compatibility = data.get("compatibility")
    if "compatibility" in data:
        if not isinstance(compatibility, str):
            message = "`compatibility` must be a string"
            findings.append(_finding(skill, "CO-05", "compatibility", message))
        elif not 1 <= len(compatibility) <= COMPATIBILITY_MAX:
            message = (
                f"`compatibility` has {len(compatibility)} characters, not 1 to {COMPATIBILITY_MAX}"
            )
            findings.append(_finding(skill, "CO-05", "compatibility", message))
    if "metadata" in data:
        metadata = data["metadata"]
        if not isinstance(metadata, Mapping) or not _all_strings(
            cast("Mapping[object, object]", metadata)
        ):
            message = "`metadata` must be a map of strings to strings"
            findings.append(_finding(skill, "CO-05", "metadata", message))
    return findings


def _co06(skill: Skill) -> list[Finding]:
    """CO-06: the SKILL.md body has fewer than 500 lines."""
    lines = skill.text.get("SKILL.md", "").split("\n")
    if lines and lines[-1] == "":
        _ = lines.pop()
    count = len(lines) - skill.frontmatter.body_start + 1
    if count < BODY_LINES_LIMIT:
        return []
    message = f"the SKILL.md body has {count} lines; it must have fewer than {BODY_LINES_LIMIT}"
    return [_finding(skill, "CO-06", None, message)]


def check(skill: Skill) -> list[Finding]:
    """Run the content rules on one skill."""
    findings: list[Finding] = []
    error = skill.frontmatter.error
    if error is not None:
        line, message = error
        findings.append(
            Finding("CO-01", Severity.ERROR, "SKILL.md", line, message, SOURCES["CO-01"])
        )
    data = skill.frontmatter.data
    if data is not None:
        findings += _co02(skill, data) + _co03(skill, data) + _co04(skill, data)
        findings += _co05(skill, data) + _co06(skill)
    return findings
