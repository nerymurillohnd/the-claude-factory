"""Content rules (CO) for a skill's SKILL.md."""

from __future__ import annotations

from typing import TYPE_CHECKING

from validators.skill_lint.model import Finding, Severity

if TYPE_CHECKING:
    from validators.skill_lint.discover import Skill

SKILLS_DOC = "https://code.claude.com/docs/en/skills"
SOURCES: dict[str, str] = {"CO-01": SKILLS_DOC}


def check(skill: Skill) -> list[Finding]:
    """Run the content rules on one skill."""
    findings: list[Finding] = []
    error = skill.frontmatter.error
    if error is not None:
        line, message = error
        findings.append(
            Finding("CO-01", Severity.ERROR, "SKILL.md", line, message, SOURCES["CO-01"])
        )
    return findings
