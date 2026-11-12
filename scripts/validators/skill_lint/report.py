"""Rendering of skill-lint results: summary, table, details, manifest and JSON."""

from __future__ import annotations

from dataclasses import asdict
import json
from typing import TYPE_CHECKING, Literal

from validators.skill_lint.model import Family, Finding, Severity

if TYPE_CHECKING:
    from collections.abc import Sequence

    from validators.skill_lint.discover import Skill
    from validators.skill_lint.rules_capabilities import Inventory

type Status = Literal["pass", "warn", "fail"]
type Result = tuple[Skill, list[Finding]]

CELLS: dict[Status, str] = {"pass": "✓", "warn": "⚠", "fail": "✗"}
COLORS: dict[Status, str] = {"pass": "\x1b[32m", "warn": "\x1b[33m", "fail": "\x1b[31m"}
RESET = "\x1b[0m"
FAMILIES = tuple(Family)


def family_status(findings: Sequence[Finding], family: Family, *, strict: bool) -> Status:
    """Return a family's status: fail on an error (or a warning with strict), warn, or pass."""
    severities = {f.severity for f in findings if f.family is family}
    if Severity.ERROR in severities or (strict and Severity.WARNING in severities):
        return "fail"
    return "warn" if Severity.WARNING in severities else "pass"


def _cell(status: Status, *, color: bool) -> str:
    """Return a status symbol, colored when asked."""
    return f"{COLORS[status]}{CELLS[status]}{RESET}" if color else CELLS[status]


def _summary(results: Sequence[Result]) -> str:
    """Return the one-line summary."""
    findings = [f for _, found in results for f in found]
    errors = sum(1 for f in findings if f.severity is Severity.ERROR)
    warnings = len(findings) - errors
    return f"{len(results)} skills · {errors} errors · {warnings} warnings"


def _table(results: Sequence[Result], *, color: bool, strict: bool) -> list[str]:
    """Return the table: one row per skill, one status cell per family."""
    width = max([len("SKILL"), *(len(skill.command) for skill, _ in results)])
    rows = ["  ".join([f"{'SKILL':<{width}}", *(family.value for family in FAMILIES)])]
    for skill, found in results:
        cells = [
            f"{_cell(family_status(found, family, strict=strict), color=color)} "
            for family in FAMILIES
        ]
        rows.append("  ".join([f"{skill.command:<{width}}", *cells]).rstrip())
    return rows


def _details(results: Sequence[Result]) -> list[str]:
    """Return the DETAILS section: every finding of every skill that has one."""
    lines: list[str] = []
    for skill, found in results:
        if not found:
            continue
        lines.append(f"{skill.command} ({skill.root})")
        for f in sorted(found, key=lambda f: (f.rule, f.path, f.line or 0)):
            where = f"{f.path}:{f.line}" if f.line is not None else f.path
            lines.append(f"  {f.rule} {where} {f.message}")
    return lines


def render_text(results: Sequence[Result], *, color: bool, strict: bool) -> str:
    """Render the summary line, the table and the details."""
    parts = [_summary(results), "", *_table(results, color=color, strict=strict)]
    details = _details(results)
    if details:
        parts += ["", "DETAILS", *details]
    return "\n".join(parts) + "\n"


def _manifest_entry(found: Inventory) -> dict[str, object]:
    """Return one skill's inventory as JSON-ready data."""
    return {
        "bang": [
            {"file": rel, "line": b.line, "block": b.block, "command": b.command}
            for rel, b in found.bang
        ],
        "hooks": [asdict(hook) for hook in found.hooks],
        "allowed_tools": list(found.allowed_tools),
    }


def render_manifest(results: Sequence[tuple[Skill, Inventory]]) -> str:
    """Render each skill's injected commands, hooks and allowed-tools entries."""
    lines: list[str] = []
    for skill, found in results:
        lines.append(skill.command)
        lines += [f"  ! {rel}:{b.line} {b.command}" for rel, b in found.bang]
        for hook in found.hooks:
            once = " once" if hook.once else ""
            lines.append(
                f"  hook {hook.event} [{hook.matcher or '*'}] {hook.type}: {hook.run}{once}"
            )
        lines += [f"  allowed-tools {entry}" for entry in found.allowed_tools]
        if lines[-1] == skill.command:
            lines.append("  (no injected commands, hooks or allowed-tools)")
    return "\n".join(lines) + "\n"


def render_json(
    results: Sequence[Result],
    inventories: Sequence[tuple[Skill, Inventory]] | None,
    *,
    strict: bool,
) -> str:
    """Render the results, and the manifest when given, as JSON."""
    payload = {
        "skills": [
            {
                "command": skill.command,
                "path": str(skill.root),
                "families": {
                    family.value: family_status(found, family, strict=strict) for family in FAMILIES
                },
            }
            for skill, found in results
        ],
        "findings": [
            {**asdict(f), "severity": f.severity.value, "skill": skill.command}
            for skill, found in results
            for f in found
        ],
        "manifest": (
            None
            if inventories is None
            else {skill.command: _manifest_entry(found) for skill, found in inventories}
        ),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
