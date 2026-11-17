"""Findings and results of the frontmatter checks, printed as one line of compact JSON.

The output contract: keys in a fixed order, findings sorted by position, `found` cut at
FOUND_LIMIT characters with its full length kept in `found_length`, and no severity: each
reviewer grades a finding from its `basis`, `surfaces` and `condition`.
"""

from dataclasses import dataclass
import json
import sys
from typing import Literal

type Surface = Literal["claude-code", "open-spec", "upload"]
type Basis = Literal["official", "convention", "inference"]
type Status = Literal["ran", "not_run"]

FOUND_LIMIT = 120
ELLIPSIS = "\N{HORIZONTAL ELLIPSIS}"
SURFACE_ORDER: tuple[Surface, ...] = ("claude-code", "open-spec", "upload")


@dataclass(frozen=True, slots=True)
class Finding:
    """One rule a check found broken, at a 1-based file position when it has one."""

    check: str
    rule: str
    line: int | None
    column: int | None
    field: str | None
    found: str | None
    expected: str
    basis: Basis
    surfaces: tuple[Surface, ...]
    condition: str | None = None
    file: str = "SKILL.md"

    @property
    def found_length(self) -> int | None:
        """The length of the untruncated found value, in characters."""
        return None if self.found is None else len(self.found)


@dataclass(frozen=True, slots=True)
class CheckResult:
    """What one check prints: whether it ran, why not, its findings and its own data."""

    check: str
    status: Status
    reason: str | None
    skill: str
    findings: list[Finding]
    data: dict[str, object]


def _excerpt(found: str | None) -> str | None:
    """The found value, cut to FOUND_LIMIT characters plus an ellipsis when longer."""
    if found is None or len(found) <= FOUND_LIMIT:
        return found
    return found[:FOUND_LIMIT] + ELLIPSIS


def _sort_key(f: Finding) -> tuple[bool, int, bool, int, str, str, str]:
    """Sort by line, then column, then rule, with unpositioned findings after positioned ones."""
    return (
        f.line is None,
        f.line or 0,
        f.column is None,
        f.column or 0,
        f.rule,
        f.field or "",
        f.found or "",
    )


def _finding_dict(f: Finding) -> dict[str, object]:
    """A finding's JSON object, keys in the contract's order."""
    return {
        "check": f.check,
        "rule": f.rule,
        "file": f.file,
        "line": f.line,
        "column": f.column,
        "field": f.field,
        "found": _excerpt(f.found),
        "found_length": f.found_length,
        "expected": f.expected,
        "basis": f.basis,
        "surfaces": [s for s in SURFACE_ORDER if s in f.surfaces],
        "condition": f.condition,
    }


def to_json(result: CheckResult) -> str:
    """The result as one line of compact JSON, in the contract's key order."""
    document: dict[str, object] = {
        "check": result.check,
        "status": result.status,
        "reason": result.reason,
        "skill": result.skill,
        "findings": [_finding_dict(f) for f in sorted(result.findings, key=_sort_key)],
        "data": result.data,
    }
    return json.dumps(document, ensure_ascii=False, separators=(",", ":"))


def emit(result: CheckResult) -> None:
    """Write the result and a newline to stdout."""
    _ = sys.stdout.write(to_json(result) + "\n")
