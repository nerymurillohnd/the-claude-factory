"""The data model shared by the skill-lint rules: findings, severities and families."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

type SkillKind = Literal["plugin", "project", "standalone"]


class Severity(StrEnum):
    """How serious a finding is."""

    ERROR = "error"
    WARNING = "warning"


class Family(StrEnum):
    """A rule family, named by the two-letter prefix of its rule ids."""

    CONTENT = "CO"
    PORTABILITY = "PO"
    SCRIPTS = "SC"
    CAPABILITIES = "CA"


@dataclass(frozen=True, slots=True)
class Finding:
    """One rule violation found in a skill folder."""

    rule: str
    severity: Severity
    path: str
    """Path of the file, relative to the skill root."""
    line: int | None
    message: str
    source: str

    @property
    def family(self) -> Family:
        """The rule family, taken from the prefix of the rule id."""
        return Family(self.rule.split("-", 1)[0])
