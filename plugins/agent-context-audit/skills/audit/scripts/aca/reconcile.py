"""Cross-domain reconciliation and the bounded challenge round.

The reconciler decides every validated finding and judges every candidate pair. When it disputes
an auditor's finding, the owning auditor answers (concede or rebut) and the reconciler decides;
one round by default, two at most. Deterministic findings are facts: only their disposition can
change. Anything still disputed is reported as an open decision with both positions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import TYPE_CHECKING

from aca.findings import CONTESTED, DETERMINISTIC, DISMISSED, FINAL, OPEN
from aca.jsonutil import JsonObj, as_obj, get_list, get_str, str_list

if TYPE_CHECKING:
    from aca.findings import Finding
    from aca.inventory import Inventory
    from aca.topics import Pair

ACCEPT = "accept"
REVISE = "revise"
DISMISS = "dismiss"


@dataclass
class Proposal:
    """What the reconciler wants to change about one finding, and why."""

    verdict: str
    disposition: str
    severity: str
    reason: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class Outcome:
    """The reconciliation state carried into the report."""

    proposals: dict[str, Proposal] = field(default_factory=dict)
    pair_verdicts: dict[str, tuple[str, str]] = field(default_factory=dict)
    groups: list[JsonObj] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    positions: dict[str, list[str]] = field(default_factory=dict)


def _finding_row(item: Finding, inventory: Inventory) -> JsonObj:
    source = inventory.by_sid(item.sid)
    return {
        "fid": item.fid,
        "origin": item.origin,
        "category": item.category,
        "severity": item.severity,
        "confidence": item.confidence,
        "sid": item.sid,
        "file": source.display if source else item.sid,
        "lines": f"{item.start}-{item.end}",
        "excerpt": item.excerpt,
        "disposition": item.disposition,
        "rationale": item.rationale,
        "evidence": item.evidence,
        "conflicts_with": [f"{c.kind}: {c.ref}" for c in item.conflicts_with],
        "ladder": item.ladder,
    }


def _pair_rows(pairs: list[Pair], lines: dict[str, list[str]]) -> list[JsonObj]:
    def side(location: tuple[str, int, int]) -> JsonObj:
        sid, start, end = location
        text = "\n".join(lines.get(sid, [])[start - 1 : end])
        return {"sid": sid, "lines": f"{start}-{end}", "text": text}

    return [
        {
            "id": f"P{number:03d}",
            "left": side(pair.left),
            "right": side(pair.right),
            "score": round(pair.score, 2),
            "topics": list(pair.shared_topics),
        }
        for number, pair in enumerate(pairs, start=1)
    ]


def reconciler_prompt(
    findings: list[Finding],
    pairs: list[Pair],
    inventory: Inventory,
    lines: dict[str, list[str]],
) -> str:
    """The reconciler's task: every finding, every pair, and the loader map."""
    sources = [
        {
            "sid": source.sid,
            "file": source.display,
            "kind": source.kind,
            "scope": source.scope,
            "domain": source.domain,
            "status": source.status,
            "loaders": [f"{loader.tool}: {loader.mode}" for loader in source.loaders],
        }
        for source in inventory.sources
    ]
    payload = {
        "findings": [_finding_row(item, inventory) for item in findings],
        "pairs": _pair_rows(pairs, lines),
        "sources": sources,
    }
    intro = (
        "# Reconciliation task\n\nDecide every finding and judge every pair below. The snapshot"
        " copies, knowledge files and repo-evidence.json are in the work folder; sources.json maps"
        " each ID to its snapshot copy.\n\n"
    )
    body = json.dumps(payload, indent=1, ensure_ascii=False)
    return f"{intro}```json\n{body}\n```\n\nReturn only the structured result.\n"


def apply_decisions(findings: list[Finding], output: JsonObj, outcome: Outcome) -> None:
    """Apply the reconciler's decisions; disputed auditor findings become contested."""
    by_id = {item.fid: item for item in findings}
    seen: set[str] = set()
    for raw in get_list(output, "decisions"):
        entry = as_obj(raw)
        fid = get_str(entry, "fid")
        item = by_id.get(fid)
        if item is None:
            continue
        seen.add(fid)
        proposal = Proposal(
            verdict=get_str(entry, "verdict"),
            disposition=get_str(entry, "disposition", item.disposition),
            severity=get_str(entry, "severity", item.severity),
            reason=get_str(entry, "reason"),
            evidence=str_list(entry.get("evidence")),
        )
        _apply_one(item, proposal, outcome)
    outcome.missing = sorted(fid for fid in by_id if fid not in seen)
    for raw in get_list(output, "pairs"):
        entry = as_obj(raw)
        outcome.pair_verdicts[get_str(entry, "id")] = (
            get_str(entry, "verdict"),
            get_str(entry, "reason"),
        )
    outcome.groups = [as_obj(raw) for raw in get_list(output, "conflict_groups")]


def _apply_one(item: Finding, proposal: Proposal, outcome: Outcome) -> None:
    if proposal.verdict == ACCEPT:
        item.status = FINAL
        return
    if item.origin == DETERMINISTIC:
        if proposal.verdict == REVISE:
            item.disposition = proposal.disposition
            item.trail.append(f"reconciler revised the disposition: {proposal.reason}")
        else:
            item.trail.append(f"reconciler disputed a mechanical fact (kept): {proposal.reason}")
        item.status = FINAL
        return
    item.status = CONTESTED
    outcome.proposals[item.fid] = proposal
    outcome.positions[item.fid] = [f"reconciler ({proposal.verdict}): {proposal.reason}"]


def apply_proposal(item: Finding, proposal: Proposal) -> None:
    """Make the reconciler's change final."""
    if proposal.verdict == DISMISS:
        item.status = DISMISSED
    else:
        item.disposition = proposal.disposition
        item.severity = proposal.severity
        item.status = FINAL
    item.trail.append(f"reconciler: {proposal.verdict} — {proposal.reason}")


def rebuttal_prompt(items: list[Finding], outcome: Outcome, inventory: Inventory) -> str:
    """The owner's task: answer each disputed finding."""
    rows: list[JsonObj] = []
    for item in items:
        proposal = outcome.proposals[item.fid]
        row = _finding_row(item, inventory)
        row["reconciler"] = {
            "verdict": proposal.verdict,
            "proposed_disposition": proposal.disposition,
            "proposed_severity": proposal.severity,
            "reason": proposal.reason,
            "evidence": proposal.evidence,
        }
        rows.append(row)
    body = json.dumps(rows, indent=1, ensure_ascii=False)
    intro = "# Rebuttal task\n\nThe reconciler disputed these findings of yours. Answer each one."
    return f"{intro}\n\n```json\n{body}\n```\n"


def decide_prompt(
    items: list[Finding], outcome: Outcome, rebuttals: dict[str, JsonObj], *, last: bool
) -> str:
    """The reconciler's decision task for rebutted items."""
    rows = [
        {
            "fid": item.fid,
            "finding": item.rationale,
            "positions": outcome.positions.get(item.fid, []),
            "owner": rebuttals.get(item.fid, {}),
        }
        for item in items
    ]
    rounds = (
        "No further round remains: never answer another-round."
        if last
        else "One more round remains: another-round is allowed."
    )
    body = json.dumps(rows, indent=1, ensure_ascii=False)
    return f"# Decision task\n\n{rounds}\n\n```json\n{body}\n```\n"


def record_rebuttals(items: list[Finding], output: JsonObj, outcome: Outcome) -> dict[str, JsonObj]:
    """Apply concessions; return the rebuttals that still need a decision."""
    answers = {get_str(as_obj(raw), "fid"): as_obj(raw) for raw in get_list(output, "responses")}
    pending: dict[str, JsonObj] = {}
    for item in items:
        answer = answers.get(item.fid)
        if answer is None:
            item.status = OPEN
            outcome.positions[item.fid].append("owner: no answer was returned")
            continue
        reason = get_str(answer, "reason")
        outcome.positions[item.fid].append(f"owner ({get_str(answer, 'position')}): {reason}")
        if get_str(answer, "position") == "concede":
            apply_proposal(item, outcome.proposals[item.fid])
        else:
            pending[item.fid] = answer
    return pending


def record_decisions(
    items: list[Finding], output: JsonObj, outcome: Outcome, *, last: bool
) -> list[Finding]:
    """Apply the reconciler's decisions; return items sent to another round."""
    answers = {get_str(as_obj(raw), "fid"): as_obj(raw) for raw in get_list(output, "decisions")}
    again: list[Finding] = []
    for item in items:
        answer = answers.get(item.fid, {})
        result = get_str(answer, "outcome", "open")
        outcome.positions[item.fid].append(f"decision ({result}): {get_str(answer, 'reason')}")
        if result == "owner":
            item.status = FINAL
            item.trail.append("challenge round: the owner's evidence stood")
        elif result == "reconciler":
            apply_proposal(item, outcome.proposals[item.fid])
        elif result == "another-round" and not last:
            outcome.proposals[item.fid].reason = get_str(answer, "reason")
            again.append(item)
        else:
            item.status = OPEN
    return again
