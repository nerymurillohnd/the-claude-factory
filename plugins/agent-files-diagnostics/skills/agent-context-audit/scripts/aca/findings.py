"""Findings, external claims and their stable IDs: the shapes every stage of the audit shares."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

CATEGORIES = {
    "false": "FAL",
    "wrong": "WRG",
    "obsolete": "OBS",
    "dead": "DED",
    "ambiguous": "AMB",
    "duplicated": "DUP",
    "overlapping": "OVL",
    "misplaced": "MIS",
    "contradictory": "CON",
    "redundant-with-defaults": "RED",
    "non-conformant": "NCF",
}
SEVERITIES = ("high", "medium", "low")
CONFIDENCES = ("high", "medium", "low")
DISPOSITIONS = ("keep", "remove", "merge", "move", "revise", "investigate")
IMPACTS = ("correctness", "reliability", "context-cost", "maintenance")
LADDER = ("a", "b", "c", "n/a")
CONFLICT_KINDS = ("file-line", "repo-fact", "doc", "default", "none")
VERDICTS = ("unverified", "confirmed", "outdated", "contradicted", "inconclusive")
FINAL = "final"
CONTESTED = "contested"
OPEN = "open"
DISMISSED = "dismissed"
DETERMINISTIC = "deterministic"
SEVERITY_RANK = {name: index for index, name in enumerate(SEVERITIES)}


@dataclass
class Conflict:
    """What an instruction conflicts with: another file and line, a repo fact, a doc, a default."""

    kind: str
    ref: str
    detail: str = ""


@dataclass
class Location:
    """A line range in a source (by manifest ID)."""

    sid: str
    start: int
    end: int


@dataclass
class Finding:
    """One evidence-backed problem with an instruction, and what to do about it."""

    category: str
    severity: str
    confidence: str
    sid: str
    start: int
    end: int
    excerpt: str
    disposition: str
    rationale: str
    origin: str
    evidence: list[str] = field(default_factory=list)
    conflicts_with: list[Conflict] = field(default_factory=list)
    related: list[Location] = field(default_factory=list)
    ladder: str = "n/a"
    impact: list[str] = field(default_factory=list)
    target: str = ""
    replacement: str = ""
    topics: list[str] = field(default_factory=list)
    unit: str = ""
    fid: str = ""
    status: str = FINAL
    trail: list[str] = field(default_factory=list)
    drift: bool = False
    verified: str = ""
    coordinator_check: str = ""

    @property
    def rank(self) -> tuple[int, str, str]:
        """Sort key: severity first, then a stable ID."""
        return (SEVERITY_RANK.get(self.severity, len(SEVERITIES)), self.category, self.fid)

    def to_json(self) -> dict[str, object]:
        """Serialize for report.json."""
        return asdict(self)


@dataclass
class ExternalClaim:
    """A statement about a third-party tool or version that the offline audit cannot check."""

    sid: str
    start: int
    end: int
    excerpt: str
    claim: str
    subject: str
    why: str
    sources: list[str] = field(default_factory=list)
    impact_if_false: str = ""
    unit: str = ""
    cid: str = ""
    verdict: str = "unverified"
    verdict_evidence: list[dict[str, str]] = field(default_factory=list)

    def to_json(self) -> dict[str, object]:
        """Serialize for report.json."""
        return asdict(self)


def finding_id(category: str, unit: str) -> str:
    """ACA-<CATEGORY>-<unit>: the same issue on the same text keeps its ID across runs."""
    return f"ACA-{CATEGORIES.get(category, 'GEN')}-{unit}"


def assign_ids(found: list[Finding]) -> None:
    """Give every finding its ID; repeats of the same ID get a numeric suffix in a stable order."""
    ordered = sorted(found, key=lambda item: (item.unit, item.category, item.start, item.excerpt))
    seen: dict[str, int] = {}
    for item in ordered:
        base = finding_id(item.category, item.unit)
        seen[base] = seen.get(base, 0) + 1
        item.fid = base if seen[base] == 1 else f"{base}-{seen[base]}"


def assign_claim_ids(claims: list[ExternalClaim]) -> None:
    """ACA-EXT-<unit> for each external claim, suffixed on repeats."""
    ordered = sorted(claims, key=lambda item: (item.unit, item.start, item.claim))
    seen: dict[str, int] = {}
    for item in ordered:
        base = f"ACA-EXT-{item.unit}"
        seen[base] = seen.get(base, 0) + 1
        item.cid = base if seen[base] == 1 else f"{base}-{seen[base]}"
