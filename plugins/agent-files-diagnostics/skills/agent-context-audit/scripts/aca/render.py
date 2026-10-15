"""The report: Markdown for people, JSON for tools, status.json for the coordinator.

Every string a model produced is redacted again before it is written, and the Markdown is built
only from validated data, so a missing or invalid stage shows up as a gap, never as a silent pass.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import re
from typing import TYPE_CHECKING, cast

from aca import VERSION
from aca.findings import CATEGORIES, DISMISSED, OPEN, SEVERITIES
from aca.jsonutil import get_int, get_str, str_list
from aca.redact import redact_text, redact_value
from aca.sources import DOMAINS, EVIDENCE, IN_SCOPE

if TYPE_CHECKING:
    from aca.findings import ExternalClaim, Finding
    from aca.jsonutil import JsonObj
    from aca.sources import Source
    from aca.state import RunState

TOP_ITEMS = 8
HEADING_LINES = 2
BACKTICKS = re.compile(r"`+")
MOVES = frozenset({"remove", "merge", "move"})
PLAN_ORDER = (
    "dead",
    "wrong",
    "false",
    "contradictory",
    "obsolete",
    "misplaced",
    "duplicated",
    "overlapping",
    "redundant-with-defaults",
    "ambiguous",
    "non-conformant",
)
AGENTS = (
    "domain-auditor",
    "cross-domain-reviewer",
    "finding-verifier",
    "claim-researcher",
)


def reported(state: RunState) -> list[Finding]:
    """Findings that stay in the report: final and open (dismissed ones are listed apart)."""
    kept = [item for item in state.findings if item.status in {"final", OPEN}]
    return sorted(kept, key=lambda item: item.rank)


def fence(text: str) -> str:
    """A code fence longer than any backtick run inside the redacted text."""
    runs = cast("list[str]", BACKTICKS.findall(text))
    longest = max((len(run) for run in runs), default=0)
    marker = "`" * max(3, longest + 1)
    return f"{marker}text\n{redact_text(text)}\n{marker}"


def where(state: RunState, sid: str, start: int, end: int) -> str:
    """`file` lines a-b."""
    source = state.inventory.by_sid(sid) if state.inventory else None
    shown = source.display if source else sid
    return f"`{shown}` lines {start}-{end}"


def table(header: list[str], rows: list[list[str]]) -> list[str]:
    """A Markdown table."""
    lines = ["| " + " | ".join(header) + " |", "|" + " :-- |" * len(header)]
    lines += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    return lines


def source_status(state: RunState, source: Source) -> str:
    """How far the audit got with one source."""
    if state.integrity and source.sid in state.integrity.changed:
        return "changed during audit"
    if source.status == EVIDENCE:
        return "evidence only"
    if source.status != IN_SCOPE:
        return f"{source.status}: {source.reason}"
    for run in state.domains:
        if source.sid in run.gaps:
            return f"partial (lines never received: {run.gaps[source.sid]})"
        if source.sid in run.package.sids:
            return "read completely" if run.status == "complete" else f"not analyzed ({run.status})"
    return "not assigned"


def _knowledge_line(state: RunState) -> str:
    knowledge = state.knowledge
    if knowledge is None:
        return "not loaded"
    live = "not checked (offline)" if state.options.offline else "live docs unreachable"
    if knowledge.online:
        changed = sum(len(items) for items in knowledge.drift.values())
        live = f"live docs checked, {changed} section(s) changed since it was written"
    covers = ", ".join(f"{tool} {version}" for tool, version in knowledge.covers.items())
    return f"version {knowledge.version}, docs {knowledge.docs_checked}, covers {covers}; {live}"


def _metadata(state: RunState) -> list[str]:
    codex = state.inventory.codex if state.inventory else None
    git = state.git_before
    revision = f"{git.head[:12]} ({'dirty' if git.status else 'clean'})"
    rows = [
        ["Repository", f"`{state.repo}`"],
        ["Revision", revision if git.available else "not a git repository"],
        ["User-level files", f"`{state.env.claude_dir}` and `{state.env.codex_home}`"],
        ["Run", f"{state.run_id}, {state.started} to {state.finished}"],
        ["Status", f"**{state.status}** (exit code {state.exit_code})"],
        ["Claude Code", state.claude_version or "unknown"],
        ["Codex CLI", (codex.version or "installed") if codex and codex.cli else "not installed"],
        ["Plugin", f"agent-files-diagnostics {VERSION}"],
        ["Knowledge", _knowledge_line(state)],
        ["Agents", ", ".join(AGENTS) + " (models and tools fixed in their definitions)"],
        ["Reconciliation", state.reconciliation],
        ["Independent verification", state.independent],
        ["Coordinator inspection", state.coordinator],
        ["External claims", state.verification],
    ]
    if state.knowledge and state.knowledge.newer_versions:
        rows.append(["Newer Claude Code releases", ", ".join(state.knowledge.newer_versions)])
    return ["## Metadata", "", *table(["Field", "Value"], rows)]


def _domains(state: RunState) -> list[str]:
    rows = [
        [
            run.package.name,
            f"{run.package.domain}: {DOMAINS.get(run.package.domain, '')}",
            ", ".join(run.package.sids),
            run.status,
            str(run.attempts),
            redact_text(run.error) or "-",
        ]
        for run in state.domains
    ]
    header = ["Package", "Domain", "Files", "Status", "Attempts", "Problem"]
    lines = ["## Domain assignments", ""]
    if not rows:
        return [*lines, "No package was assigned: nothing was in scope."]
    return [*lines, *table(header, rows)]


def _source_rows(state: RunState) -> list[list[str]]:
    rows: list[list[str]] = []
    for source in state.inventory.sources if state.inventory else []:
        loaders = "; ".join(f"{item.tool}: {item.mode}" for item in source.loaders) or "-"
        shown = f"`{source.display}`" + (f" ({source.subset})" if source.subset else "")
        rows.append(
            [
                source.sid,
                shown,
                source.kind,
                source.domain,
                loaders,
                source.loading,
                source.consumption,
                source.availability,
                source.applicability,
                str(source.line_count),
                source_status(state, source),
            ]
        )
    return rows


def _validators(state: RunState) -> list[str]:
    integrity = state.integrity
    all_complete = bool(state.domains) and all(run.status == "complete" for run in state.domains)
    checks = [
        ("Every analyzed file has a complete 1..N coverage ledger", all_complete),
        ("Every domain auditor returned validated output", all_complete),
        ("Reconciliation used every completed domain output", state.reconciliation == "complete"),
        (
            "Audited files unchanged (hashes before and after)",
            bool(integrity and not integrity.changed),
        ),
        ("Git state unchanged", bool(integrity and not integrity.git_changed)),
    ]
    rows = [f"- {'PASS' if ok else 'FAIL'}: {label}" for label, ok in checks]
    rows.append(f"- Items rejected by validation: {len(state.rejected)} (listed under Limitations)")
    return ["Validators:", "", *rows]


def _coverage(state: RunState) -> list[str]:
    header = [
        "ID",
        "File",
        "Kind",
        "Domain",
        "Loaded by",
        "Loading",
        "Consumption",
        "Availability",
        "Applicability",
        "Lines",
        "Status",
    ]
    lines = ["## Coverage", "", *table(header, _source_rows(state)), ""]
    note = "Consumption is what the documentation says happens; this run observed no session, so"
    lines += [f"{note} no source is marked `verified`.", ""]
    lines += _validators(state)
    out = state.inventory.out_of_scope if state.inventory else []
    if out:
        lines += ["", "Loaded but out of scope (counted, never reviewed):", ""]
        lines += [
            f"- `{item['path']}`: {item['what']} ({item['count']}): {item['reason']}"
            for item in out
        ]
    return lines


def _summary(state: RunState) -> list[str]:
    items = reported(state)
    severities = Counter(item.severity for item in items)
    counts = ", ".join(f"{severities.get(level, 0)} {level}" for level in SEVERITIES)
    lines = ["## Executive summary", "", f"{len(items)} findings ({counts})."]
    risks = [item for item in items if item.severity == "high"][:TOP_ITEMS]
    if risks:
        lines += ["", "Top risks:", ""]
        lines += [f"- {item.fid}: {where(state, item.sid, item.start, item.end)}" for item in risks]
    moves = [item for item in items if item.disposition in MOVES][:TOP_ITEMS]
    if moves:
        lines += ["", "Highest-value removals, merges and moves:", ""]
        lines += [
            f"- {item.fid} ({item.disposition}): {where(state, item.sid, item.start, item.end)}"
            for item in moves
        ]
    open_count = sum(1 for item in items if item.status == OPEN)
    unverified = sum(1 for claim in state.claims if claim.verdict in {"unverified", "inconclusive"})
    low = sum(1 for item in items if item.confidence == "low")
    unresolved = (
        f"Unresolved: {open_count} open decisions, {unverified} external claims to verify,"
        f" {low} low-confidence findings."
    )
    lines += ["", unresolved]
    return lines


def _conflict_text(item: Finding) -> str:
    parts = [
        f"{entry.kind} `{entry.ref}`" + (f" ({entry.detail})" if entry.detail else "")
        for entry in item.conflicts_with
    ]
    return redact_text("; ".join(parts)) or "-"


def _finding_block(state: RunState, item: Finding) -> list[str]:
    related = (
        ", ".join(where(state, entry.sid, entry.start, entry.end) for entry in item.related) or "-"
    )
    target = f", target: {item.target}" if item.target else ""
    lines = [
        f"### {item.fid}: {item.category}, {item.severity} severity, {item.confidence} confidence",
        "",
        f"- **Where:** {where(state, item.sid, item.start, item.end)} ({item.sid})",
        "- **Excerpt:**",
        "",
        fence(item.excerpt),
        "",
        f"- **Conflicts with:** {_conflict_text(item)}",
        f"- **Evidence:** {redact_text('; '.join(item.evidence)) or '-'}",
        f"- **Related:** {related}",
        f"- **Impact:** {', '.join(item.impact) or '-'}",
        f"- **Disposition:** {item.disposition}{target}",
    ]
    if item.replacement:
        lines += [
            "- **Suggested replacement** (shown only, never applied):",
            "",
            fence(item.replacement),
            "",
        ]
    lines.append(f"- **Rationale and trade-offs:** {redact_text(item.rationale)}")
    lines.append(
        f"- **Origin:** {item.origin}; evidence ladder {item.ladder}; status {item.status}"
    )
    verifier = item.verified or "unverified"
    coordinator = item.coordinator_check or "not inspected"
    lines.append(f"- **Verification:** independent verifier {verifier}; coordinator {coordinator}")
    if item.status == OPEN:
        lines += [f"  - {redact_text(text)}" for text in state.outcome.positions.get(item.fid, [])]
    lines += [f"- {redact_text(note)}" for note in item.trail]
    return [*lines, ""]


def _findings(state: RunState) -> list[str]:
    items = reported(state)
    lines = ["## Findings", ""]
    if not items:
        return [*lines, "No findings."]
    for item in items:
        lines += _finding_block(state, item)
    return lines


def _cross(state: RunState) -> list[str]:
    lines = ["## Cross-domain conflicts and open decisions", ""]
    outcome = state.outcome
    pairs = sorted(
        (pid, verdict)
        for pid, verdict in outcome.pair_verdicts.items()
        if verdict[0] != "unrelated"
    )
    opened = [item for item in reported(state) if item.status == OPEN]
    if not outcome.groups and not pairs and not opened:
        return [*lines, "None found."]
    for group in outcome.groups:
        fids = ", ".join(str_list(group.get("fids")))
        topic = redact_text(get_str(group, "topic"))
        lines.append(f"- **{topic}** ({fids}): {redact_text(get_str(group, 'precedence'))}")
    if pairs:
        lines += ["", "Similar instructions in different files, as the reviewer judged them:", ""]
        lines += [f"- {pid}: {verdict}: {redact_text(reason)}" for pid, (verdict, reason) in pairs]
    if opened:
        lines += ["", "Open decisions (both positions are recorded under each finding):", ""]
        lines += [
            f"- {item.fid}: {where(state, item.sid, item.start, item.end)}" for item in opened
        ]
    return lines


def _plan(state: RunState) -> list[str]:
    order = {name: index for index, name in enumerate(PLAN_ORDER)}
    items = sorted(
        (item for item in reported(state) if item.disposition != "keep"),
        key=lambda item: (order.get(item.category, len(order)), item.rank),
    )
    lines = ["## Remediation plan", ""]
    if not items:
        return [*lines, "Nothing to change."]
    lines += ["Recommendations only: nothing was changed. Work from the top.", ""]
    touched: dict[tuple[str, int], str] = {}
    for number, item in enumerate(items, start=1):
        span = range(item.start, item.end + 1)
        blockers = sorted(
            {touched[(item.sid, line)] for line in span if (item.sid, line) in touched}
        )
        after = f" (after {', '.join(blockers)})" if blockers else ""
        place = where(state, item.sid, item.start, item.end)
        lines.append(f"{number}. {item.disposition}: {place}, {item.fid}{after}")
        for line in span:
            _ = touched.setdefault((item.sid, line), item.fid)
    return lines


def _evidence_text(entry: dict[str, str]) -> str:
    """URL (version or date): "quote"."""
    when = entry.get("version", "") or entry.get("checked", "")
    quote = entry.get("quote", "")
    return f'{entry.get("url", "")} ({when}): "{quote}"'


def _claim_row(state: RunState, claim: ExternalClaim) -> list[str]:
    evidence = "; ".join(_evidence_text(entry) for entry in claim.verdict_evidence)
    checked = redact_text(evidence) or ", ".join(claim.sources) or "-"
    return [
        claim.cid,
        where(state, claim.sid, claim.start, claim.end),
        redact_text(claim.claim),
        redact_text(claim.subject),
        claim.verdict,
        checked,
    ]


def _claims(state: RunState) -> list[str]:
    lines = ["## External claims", ""]
    if not state.claims:
        return [*lines, "No external claims."]
    header = [
        "ID",
        "Where",
        "Claim",
        "Subject",
        "Verdict",
        "Evidence (URL, version or date, quote)",
    ]
    rows = [_claim_row(state, claim) for claim in state.claims]
    return [*lines, f"Verification: {state.verification}.", "", *table(header, rows)]


def _limitations(state: RunState) -> list[str]:
    lines = ["## Limitations and open questions", ""]
    lines += [f"- Partial: {redact_text(text)}" for text in state.problems]
    lines += [f"- Failure: {redact_text(text)}" for text in state.failures]
    lines += [f"- Note: {redact_text(text)}" for text in state.warnings]
    for item in state.findings:
        if item.status == DISMISSED:
            reason = item.trail[-1] if item.trail else ""
            lines.append(f"- Dismissed: {item.fid}: {redact_text(reason)}")
    for rejected in state.rejected:
        summary = redact_text(rejected.summary)
        lines.append(f"- Rejected by validation ({rejected.origin}): {summary}: {rejected.reason}")
    lines += [f"- Write: {redact_text(text)}" for text in state.writes]
    return lines if len(lines) > HEADING_LINES else [*lines, "None."]


def _change(state: RunState) -> list[str]:
    change = state.change
    lines = ["## Change since last run", ""]
    if not change.previous:
        return [*lines, "First run for this repository."]
    recategorized = ", ".join(f"{old} to {new}" for old, new in change.recategorized) or "-"
    lines += [
        f"Compared with run {change.previous}:",
        "",
        f"- New: {', '.join(change.new) or '-'}",
        f"- Resolved: {', '.join(change.resolved) or '-'}",
        f"- Persisting: {len(change.persisting)}",
        f"- Regressed (back after being resolved): {', '.join(change.regressed) or '-'}",
        f"- Re-categorized: {recategorized}",
    ]
    if change.unconfirmed:
        unseen = ", ".join(change.unconfirmed)
        lines.append(f"- Not seen in this partial run (not proof of a fix): {unseen}")
    return lines


def _usage(state: RunState) -> list[str]:
    header = ["Agent", "Requests", "Input tokens", "Cache read", "Cache write", "Output tokens"]
    rows = [
        [
            get_str(entry, "label"),
            str(get_int(entry, "requests")),
            str(get_int(entry, "input_tokens")),
            str(get_int(entry, "cache_read_input_tokens")),
            str(get_int(entry, "cache_creation_input_tokens")),
            str(get_int(entry, "output_tokens")),
        ]
        for entry in state.usage
    ]
    lines = ["## Usage", ""]
    if not rows:
        return [*lines, "No agent transcript was read, so no usage is known."]
    note = "Token counts come from each agent's transcript. Cost in money is not available to the"
    lines += [f"{note} audit; the run counts toward the plan's usage limits.", ""]
    return [*lines, *table(header, rows)]


def markdown(state: RunState) -> str:
    """The full Markdown report."""
    sections = [
        [f"# Agent Context Audit: {state.repo.name}"],
        _metadata(state),
        _summary(state),
        _domains(state),
        _coverage(state),
        _findings(state),
        _cross(state),
        _plan(state),
        _claims(state),
        _limitations(state),
        _change(state),
        _usage(state),
    ]
    return "\n\n".join("\n".join(section).rstrip() for section in sections) + "\n"


def _source_json(state: RunState, source: Source) -> JsonObj:
    return {
        "sid": source.sid,
        "path": source.display,
        "aliases": source.aliases,
        "kind": source.kind,
        "scope": source.scope,
        "domain": source.domain,
        "owner": source.owner,
        "status": source_status(state, source),
        "loading": source.loading,
        "consumption": source.consumption,
        "availability": source.availability,
        "applicability": source.applicability,
        "lines": source.line_count,
        "bytes": source.size,
        "sha256": source.sha256,
        "subset": source.subset,
        "loaders": [asdict(loader) for loader in source.loaders],
    }


def _domain_json(state: RunState) -> list[JsonObj]:
    return [
        {
            "package": run.package.name,
            "domain": run.package.domain,
            "files": run.package.sids,
            "status": run.status,
            "attempts": run.attempts,
            "gaps": run.gaps,
            "error": run.error,
        }
        for run in state.domains
    ]


def report_json(state: RunState) -> JsonObj:
    """Everything in machine-readable form (strings redacted)."""
    sources = state.inventory.sources if state.inventory else []
    data: JsonObj = {
        "schema": "agent-files-diagnostics/report/1",
        "run_id": state.run_id,
        "repo": str(state.repo),
        "started": state.started,
        "finished": state.finished,
        "status": state.status,
        "exit_code": state.exit_code,
        "versions": {"plugin": VERSION, "claude": state.claude_version},
        "sources": [_source_json(state, source) for source in sources],
        "findings": [item.to_json() for item in reported(state)],
        "dismissed": [item.to_json() for item in state.findings if item.status == DISMISSED],
        "external_claims": [claim.to_json() for claim in state.claims],
        "rejected": [asdict(item) for item in state.rejected],
        "domains": _domain_json(state),
        "reconciliation": state.reconciliation,
        "independent": state.independent,
        "coordinator": state.coordinator,
        "verification": state.verification,
        "change": asdict(state.change),
        "problems": state.problems,
        "failures": state.failures,
        "warnings": state.warnings,
        "writes": state.writes,
        "usage": state.usage,
        "categories": list(CATEGORIES),
    }
    return {key: redact_value(value) for key, value in data.items()}


def status_json(state: RunState, report_path: str) -> JsonObj:
    """The machine-readable status sidecar."""
    items = reported(state)
    return {
        "schema": "agent-files-diagnostics/status/1",
        "status": state.status,
        "exit_code": state.exit_code,
        "run_id": state.run_id,
        "repo": str(state.repo),
        "report": report_path,
        "started": state.started,
        "finished": state.finished,
        "findings": len(items),
        "by_severity": dict(Counter(item.severity for item in items)),
        "open_decisions": sum(1 for item in items if item.status == OPEN),
        "external_claims": len(state.claims),
        "problems": [redact_text(text) for text in state.problems],
        "failures": [redact_text(text) for text in state.failures],
    }
