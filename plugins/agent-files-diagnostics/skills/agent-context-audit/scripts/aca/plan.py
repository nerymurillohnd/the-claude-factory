"""Packages, read plans and task messages for the domain auditors.

Sources are grouped by domain and packed into packages under a character budget; a file is never
split across packages. Each file gets explicit Read chunks (offset, limit) small enough for one
Read call, so full coverage never depends on how the model pages through a long file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca.jsonutil import JsonObj, dumps
from aca.sources import DOMAINS

if TYPE_CHECKING:
    from aca.checks import Candidate, Checks
    from aca.findings import Finding
    from aca.inventory import Inventory
    from aca.snapshot import Snapshot
    from aca.sources import Source

PACKAGE_CHARS = 120_000
CHUNK_CHARS = 50_000
CHUNK_LINES = 1_500
TURN_SLACK = 40


@dataclass
class Package:
    """One domain auditor's assignment."""

    name: str
    domain: str
    sids: list[str] = field(default_factory=list)
    chars: int = 0
    candidates: dict[str, Candidate] = field(default_factory=dict)

    @property
    def allowed(self) -> frozenset[str]:
        """The sources this package may report on."""
        return frozenset(self.sids)


def chunks(lines: list[str]) -> list[tuple[int, int]]:
    """Read chunks (offset, limit) covering lines 1..N, each within the size limits.

    A chunk closes before the line that would take it over the limit, so only a single line
    longer than the limit makes a chunk larger than it.
    """
    plan: list[tuple[int, int]] = []
    start, size = 1, 0
    for number, line in enumerate(lines, start=1):
        width = len(line) + 1
        count = number - start
        if count and (size + width > CHUNK_CHARS or count >= CHUNK_LINES):
            plan.append((start, count))
            start, size = number, 0
        size += width
    if lines:
        plan.append((start, len(lines) - start + 1))
    return plan or [(1, 1)]


def make_packages(inventory: Inventory, snapshot: Snapshot, checks: Checks) -> list[Package]:
    """Pack audited sources into packages per domain, never splitting a file."""
    packages: list[Package] = []
    for domain in DOMAINS:
        current: Package | None = None
        for source in inventory.audited:
            if source.domain != domain:
                continue
            size = sum(len(line) + 1 for line in snapshot.lines.get(source.sid, []))
            if current is None or (current.sids and current.chars + size > PACKAGE_CHARS):
                number = sum(item.domain == domain for item in packages) + 1
                current = Package(name=f"{domain}{number}", domain=domain)
                packages.append(current)
            current.sids.append(source.sid)
            current.chars += size
    for number, candidate in enumerate(checks.candidates, start=1):
        for package in packages:
            if candidate.sid in package.sids:
                package.candidates[f"C{number:03d}"] = candidate
    return packages


def _loaders(source: Source) -> str:
    return "; ".join(f"{loader.tool}: {loader.mode} ({loader.reason})" for loader in source.loaders)


def _file_rows(package: Package, inventory: Inventory, snapshot: Snapshot) -> list[str]:
    rows = ["| ID | Original | Snapshot copy | Lines | Read chunks (offset, limit) | Loaded by |"]
    rows.append("| :-- | :-- | :-- | --: | :-- | :-- |")
    for sid in package.sids:
        source = inventory.by_sid(sid)
        if source is None:
            continue
        plan = ", ".join(
            f"({offset}, {limit})" for offset, limit in chunks(snapshot.lines.get(sid, []))
        )
        cells = [
            sid,
            source.display,
            str(snapshot.paths[sid]),
            str(source.line_count),
            plan,
            _loaders(source),
        ]
        rows.append("| " + " | ".join(cells) + " |")
    return rows


def _recorded(findings: list[Finding], package: Package) -> list[str]:
    lines = [
        f"- {item.sid}:{item.start}-{item.end} {item.category}: {item.rationale}"
        for item in findings
        if item.sid in package.sids
    ]
    return lines or ["- (none)"]


def _candidate_rows(package: Package) -> list[str]:
    rows = [
        f"- {cid} {item.sid}:{item.start}-{item.end} [{item.kind}] {item.note}"
        + (f" (evidence: {'; '.join(item.evidence)})" if item.evidence else "")
        for cid, item in sorted(package.candidates.items())
    ]
    return rows or ["- (none)"]


def auditor_task(package: Package, inventory: Inventory, snapshot: Snapshot, checks: Checks) -> str:
    """The task message for one domain auditor."""
    work = snapshot.work
    parts = [
        f"# Audit task {package.name}: domain {package.domain}",
        "",
        f"Domain: {DOMAINS[package.domain]}.",
        f"Project root (your working directory): {inventory.repo}",
        f"Work folder: {work}",
        "",
        "## Files to audit: read every line, using exactly these chunks",
        "",
        *_file_rows(package, inventory, snapshot),
        "",
        "## Deterministic findings already recorded (do not repeat them)",
        "",
        *_recorded(checks.findings, package),
        "",
        "## Candidates to judge (confirm and report, or reject with a reason)",
        "",
        *_candidate_rows(package),
        "",
        "## Reference files in the work folder",
        "",
        f"- {work}/knowledge/drift.md (read first)",
        f"- {work}/knowledge/claude-code.md, codex.md, defaults.md, topics.json",
        f"- {work}/repo-evidence.json",
        f"- {work}/sources.json (every source, its loaders and its snapshot copy)",
        "",
        "Return only the structured result.",
    ]
    return "\n".join(parts) + "\n"


def max_turns(package: Package, snapshot: Snapshot) -> int:
    """Turn estimate: every planned read plus room for verification reads."""
    reads = sum(len(chunks(snapshot.lines.get(sid, []))) for sid in package.sids)
    return reads * 2 + TURN_SLACK


def manifest_json(inventory: Inventory, snapshot: Snapshot) -> str:
    """sources.json for the agents: every source, its loaders and its snapshot copy."""
    rows: list[JsonObj] = [
        {
            "sid": source.sid,
            "display": source.display,
            "kind": source.kind,
            "scope": source.scope,
            "domain": source.domain,
            "status": source.status,
            "loading": source.loading,
            "consumption": source.consumption,
            "availability": source.availability,
            "applicability": source.applicability,
            "lines": source.line_count,
            "snapshot": str(snapshot.paths.get(source.sid, "")),
            "subset": source.subset,
            "loaders": [
                {"tool": loader.tool, "mode": loader.mode, "reason": loader.reason}
                for loader in source.loaders
            ],
        }
        for source in inventory.sources
    ]
    return dumps(rows)
