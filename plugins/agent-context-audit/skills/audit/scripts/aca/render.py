"""The report: Markdown for people, JSON for tools, status.json for scripts, notice for the hook.

Every string a model produced is redacted again before it is written, and the Markdown is built
only from validated data, so a missing or invalid stage shows up as a gap, never as a silent pass.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import re
from typing import TYPE_CHECKING, cast
from urllib.parse import quote

from aca import VERSION
from aca.findings import CATEGORIES, DISMISSED, OPEN, SEVERITIES
from aca.jsonutil import as_obj, get_float, get_str, str_list
from aca.redact import redact_text, redact_value
from aca.sources import EVIDENCE, IN_SCOPE

if TYPE_CHECKING:
    from aca.findings import ExternalClaim, Finding
    from aca.jsonutil import JsonObj
    from aca.sources import Source
    from aca.state import RunState

TOP_ITEMS = 8
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
SUBSCRIPTION_NOTE = (
    "Costs are the estimates Claude Code reports at API list price. On a Claude subscription"
    " they are API-equivalent figures; the run counts toward your plan's usage limits instead."
)
EXPOSURE_NOTE = (
    "Residual exposure: managed policy settings always apply to the audit's own sessions, and"
    " each worker updates ~/.claude.json like any Claude Code session (only its MCP subset is"
    " audited)."
)


def deep_link(state: RunState) -> str:
    """A claude-cli:// link that opens this repository with the latest-report prompt filled in."""
    prompt = quote("/agent-context-audit:audit latest", safe="")
    return f"claude-cli://open?cwd={quote(str(state.repo), safe='/')}&q={prompt}"


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
        if source.sid in run.shard.sids:
            return "analyzed" if run.status == "complete" else f"not analyzed ({run.status})"
    return "analyzed"


def _knowledge_line(state: RunState) -> str:
    knowledge = state.knowledge
    if knowledge is None:
        return "not loaded"
    live = "not checked (--offline)" if state.options.offline else "live docs unreachable"
    if knowledge.online:
        changed = sum(len(items) for items in knowledge.drift.values())
        live = f"live docs checked, {changed} section(s) changed since it was written"
    covers = ", ".join(f"{tool} {version}" for tool, version in knowledge.covers.items())
    return f"version {knowledge.version}, docs {knowledge.docs_checked}, covers {covers}; {live}"


def _metadata(state: RunState) -> list[str]:
    codex = state.inventory.codex if state.inventory else None
    git = state.git_before
    revision = f"{git.head[:12]} ({'dirty' if git.status else 'clean'})"
    models = f"auditors {state.options.auditor_model}, reconciler {state.options.reconciler_model}"
    rows = [
        ["Repository", f"`{state.repo}`"],
        ["Revision", revision if git.available else "not a git repository"],
        ["Run", f"{state.run_id}, {state.options.mode} mode, {state.started} to {state.finished}"],
        ["Status", f"**{state.status}** (exit code {state.exit_code})"],
        ["Claude Code", state.claude_version or "unknown"],
        ["Codex CLI", (codex.version or "installed") if codex and codex.cli else "not installed"],
        ["Plugin", f"agent-context-audit {VERSION}"],
        ["Knowledge", _knowledge_line(state)],
        ["Models", models],
        ["Open in Claude Code", f"`{deep_link(state)}`"],
    ]
    if state.knowledge and state.knowledge.newer_versions:
        rows.append(["Newer Claude Code releases", ", ".join(state.knowledge.newer_versions)])
    return ["## Metadata", "", *table(["Field", "Value"], rows)]


def _source_rows(state: RunState) -> list[list[str]]:
    rows: list[list[str]] = []
    for source in state.inventory.sources if state.inventory else []:
        loaders = "; ".join(f"{item.tool}: {item.mode}" for item in source.loaders) or "-"
        shown = f"`{source.display}`" + (f" ({source.subset})" if source.subset else "")
        status = source_status(state, source)
        rows.append(
            [source.sid, shown, source.kind, source.scope, loaders, str(source.line_count), status]
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
    header = ["ID", "File", "Kind", "Scope", "Loaded by", "Lines", "Status"]
    lines = ["## Coverage", "", *table(header, _source_rows(state)), ""]
    shards = [
        [
            run.shard.name,
            run.shard.domain,
            str(len(run.shard.sids)),
            run.status,
            str(run.attempts),
            redact_text(run.error) or "-",
        ]
        for run in state.domains
    ]
    lines += [*table(["Shard", "Domain", "Files", "Status", "Attempts", "Problem"], shards), ""]
    lines += _validators(state)
    out = state.inventory.out_of_scope if state.inventory else []
    if out:
        lines += ["", "Loaded but out of scope (never reported):", ""]
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
    lines = ["## Cross-domain conflicts", ""]
    outcome = state.outcome
    pairs = sorted(
        (pid, verdict)
        for pid, verdict in outcome.pair_verdicts.items()
        if verdict[0] != "unrelated"
    )
    if not outcome.groups and not pairs:
        return [*lines, "None found."]
    for group in outcome.groups:
        fids = ", ".join(str_list(group.get("fids")))
        topic = redact_text(get_str(group, "topic"))
        lines.append(f"- **{topic}** ({fids}): {redact_text(get_str(group, 'precedence'))}")
    if pairs:
        lines += ["", "Similar instructions in different files, as the reconciler judged them:", ""]
        lines += [f"- {pid}: {verdict}: {redact_text(reason)}" for pid, (verdict, reason) in pairs]
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


def _claim_row(state: RunState, claim: ExternalClaim) -> list[str]:
    evidence = "; ".join(
        f'{entry.get("url", "")}: "{entry.get("quote", "")}"' for entry in claim.verdict_evidence
    )
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
    lines = ["## Needs live verification", ""]
    if not state.claims:
        return [*lines, "No external claims."]
    header = ["ID", "Where", "Claim", "Subject", "Verdict", "Evidence, or sources to check"]
    rows = [_claim_row(state, claim) for claim in state.claims]
    return [*lines, f"Online verification: {state.verification}.", "", *table(header, rows)]


def _limitations(state: RunState) -> list[str]:
    lines = ["## Limitations and open questions", ""]
    lines += [f"- Partial: {redact_text(text)}" for text in state.problems]
    lines += [f"- Failure: {redact_text(text)}" for text in state.failures]
    lines += [f"- Note: {redact_text(text)}" for text in state.warnings]
    for item in state.findings:
        if item.status == DISMISSED:
            reason = item.trail[-1] if item.trail else ""
            lines.append(f"- Dismissed after reconciliation: {item.fid}: {redact_text(reason)}")
    for rejected in state.rejected:
        summary = redact_text(rejected.summary)
        lines.append(f"- Rejected by validation ({rejected.origin}): {summary}: {rejected.reason}")
    return [*lines, f"- {EXPOSURE_NOTE}"]


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


def _usage_tokens(usage: JsonObj) -> tuple[float, float]:
    tokens_in = tokens_out = 0.0
    for raw in usage.values():
        entry = as_obj(raw)
        tokens_in += get_float(entry, "inputTokens") + get_float(entry, "cacheReadInputTokens")
        tokens_in += get_float(entry, "cacheCreationInputTokens")
        tokens_out += get_float(entry, "outputTokens")
    return tokens_in, tokens_out


def cost_rows(state: RunState) -> dict[str, dict[str, float]]:
    """Workers, seconds, tokens and cost per worker role."""
    roles: dict[str, dict[str, float]] = {}
    for result in state.results:
        empty = {"workers": 0.0, "seconds": 0.0, "input": 0.0, "output": 0.0, "cost": 0.0}
        row = roles.setdefault(result.spec.role, empty)
        tokens_in, tokens_out = _usage_tokens(result.usage)
        row["workers"] += 1
        row["seconds"] += result.seconds
        row["input"] += tokens_in
        row["output"] += tokens_out
        row["cost"] += result.cost
    return roles


def _cost(state: RunState) -> list[str]:
    roles = cost_rows(state)
    header = ["Role", "Workers", "Seconds", "Input tokens", "Output tokens", "Cost (USD)"]
    rows = [
        [
            role,
            f"{row['workers']:.0f}",
            f"{row['seconds']:.0f}",
            f"{row['input']:.0f}",
            f"{row['output']:.0f}",
            f"{row['cost']:.4f}",
        ]
        for role, row in sorted(roles.items())
    ]
    total = sum(row["cost"] for row in roles.values())
    rows.append(["total", "", "", "", "", f"{total:.4f}"])
    return [
        "## Run cost",
        "",
        f"Wall time: {state.seconds:.0f} s.",
        "",
        *table(header, rows),
        "",
        SUBSCRIPTION_NOTE,
    ]


def markdown(state: RunState) -> str:
    """The full Markdown report."""
    sections = [
        [f"# Agent Context Audit: {state.repo.name}"],
        _metadata(state),
        _coverage(state),
        _summary(state),
        _findings(state),
        _cross(state),
        _plan(state),
        _claims(state),
        _limitations(state),
        _change(state),
        _cost(state),
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
        "lines": source.line_count,
        "bytes": source.size,
        "sha256": source.sha256,
        "subset": source.subset,
        "loaders": [asdict(loader) for loader in source.loaders],
    }


def _domain_json(state: RunState) -> list[JsonObj]:
    return [
        {
            "shard": run.shard.name,
            "domain": run.shard.domain,
            "files": run.shard.sids,
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
        "schema": "agent-context-audit/report/1",
        "run_id": state.run_id,
        "repo": str(state.repo),
        "mode": state.options.mode,
        "started": state.started,
        "finished": state.finished,
        "status": state.status,
        "exit_code": state.exit_code,
        "versions": {"plugin": VERSION, "claude": state.claude_version},
        "deep_link": deep_link(state),
        "sources": [_source_json(state, source) for source in sources],
        "findings": [item.to_json() for item in reported(state)],
        "dismissed": [item.to_json() for item in state.findings if item.status == DISMISSED],
        "external_claims": [claim.to_json() for claim in state.claims],
        "rejected": [asdict(item) for item in state.rejected],
        "domains": _domain_json(state),
        "reconciliation": state.reconciliation,
        "verification": state.verification,
        "change": asdict(state.change),
        "problems": state.problems,
        "failures": state.failures,
        "warnings": state.warnings,
        "cost": cost_rows(state),
        "categories": list(CATEGORIES),
    }
    return {key: redact_value(value) for key, value in data.items()}


def status_json(state: RunState, report_path: str) -> JsonObj:
    """The machine-readable status sidecar."""
    items = reported(state)
    return {
        "schema": "agent-context-audit/status/1",
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
        "cost_usd": round(sum(result.cost for result in state.results), 4),
    }


def notice_json(state: RunState, report_path: str) -> JsonObj:
    """What the SessionStart hook prints once for this report, keyed by its run."""
    items = reported(state)
    high = sum(1 for item in items if item.severity == "high")
    message = (
        f"Agent Context Audit: new report for {state.repo.name} ({state.status},"
        f" {len(items)} findings, {high} high). Review it with /agent-context-audit:audit latest"
    )
    context = (
        f"A new Agent Context Audit report exists at {report_path} ({state.status},"
        f" {len(items)} findings, {high} high). Mention it if it is relevant to the request;"
        " read it only if the user asks."
    )
    output: JsonObj = {
        "systemMessage": message,
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
    }
    return {"run_id": state.run_id, "output": output}
