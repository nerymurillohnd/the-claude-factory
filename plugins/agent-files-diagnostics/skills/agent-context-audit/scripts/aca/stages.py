"""The stages of one audit, run as separate commands around the two workflows.

`prepare` discovers, snapshots, checks and plans. `accept_domains` reads the domain auditors'
results from the workflow journal, proves coverage from their transcripts, validates every
finding and writes the tasks of the review workflow. `accept_review` applies the reconciler,
the challenge round, the independent verification and the external verdicts. `finalize` records
the coordinator's own inspection, checks integrity and writes the report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import secrets
import time
from typing import TYPE_CHECKING

from aca import (
    checks,
    coverage,
    evidence,
    history,
    integrity,
    inventory,
    knowledge,
    paths,
    plan,
    reconcile,
    render,
    schema,
    snapshot,
    store,
    topics,
    validate,
)
from aca.findings import (
    CONTESTED,
    DISMISSED,
    FINAL,
    OPEN,
    assign_claim_ids,
    assign_ids,
    finding_id,
)
from aca.jsonutil import (
    JsonObj,
    as_obj,
    dumps,
    get_bool,
    get_list,
    get_str,
    read_json,
    write_atomic,
)
from aca.sources import IN_SCOPE
from aca.state import DomainRun, RunState

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aca.findings import ExternalClaim, Finding
    from aca.state import Options

ALLOWED_TOOL_CALLS = frozenset({"Read", "Grep", "Glob", "StructuredOutput"})
VERIFY_BATCH = 12
CLAIM_BATCH = 15
WORK_MODE = 0o700
NOT_INSPECTED = "not inspected"
NO_INVENTORY = "the run state has no inventory: run prepare first"


def utc_now() -> str:
    """The current UTC time in ISO 8601 with seconds."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def new_run_id() -> str:
    """A unique, sortable run ID: UTC timestamp plus a random suffix."""
    return f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}"


def prepare_root(root: Path) -> None:
    """Create the report folder with a .gitignore that ignores everything in it, itself too."""
    root.mkdir(parents=True, exist_ok=True)
    ignore = root / ".gitignore"
    if not ignore.exists():
        _ = ignore.write_text("*\n", encoding="utf-8")


def new_state(options: Options, environ: Mapping[str, str]) -> RunState:
    """A fresh state for one repository."""
    repo = paths.repo_root(paths.resolve(Path(options.repo).expanduser()))
    root = paths.report_root(repo, environ, options.out)
    run_id = new_run_id()
    return RunState(
        options=options,
        env=paths.detect_env(environ),
        repo=repo,
        report_root=root,
        run_id=run_id,
        run_dir=root / run_id,
        started=utc_now(),
    )


def _parts(state: RunState) -> tuple[inventory.Inventory, snapshot.Snapshot, checks.Checks]:
    """The inventory, snapshot and checks of a prepared run."""
    if state.inventory is None or state.snapshot is None or state.checks is None:
        raise RuntimeError(NO_INVENTORY)
    return state.inventory, state.snapshot, state.checks


# --- stage 1: prepare -----------------------------------------------------------------------


def _knowledge(state: RunState, work: Path) -> knowledge.Knowledge:
    known = knowledge.load()
    state.knowledge = known
    if not state.options.offline:
        knowledge.check_live(known)
        if not known.online:
            state.warnings.append("the live docs could not be reached; bundled knowledge only")
    _ = knowledge.copy_to(known, work)
    if known.drifted:
        changed = sum(len(items) for items in known.drift.values())
        state.warnings.append(f"{changed} tracked docs section(s) changed since the knowledge date")
    return known


def _write_tasks(state: RunState) -> None:
    found, snap, result = _parts(state)
    tasks = state.work_tasks()
    tasks.mkdir(mode=WORK_MODE, exist_ok=True)
    for run in state.domains:
        text = plan.auditor_task(run.package, found, snap, result)
        _ = (tasks / f"{run.package.name}.md").write_text(text, encoding="utf-8")


def prepare(options: Options, environ: Mapping[str, str], claude_version: str) -> RunState:
    """Inventory, snapshot, evidence, knowledge, deterministic checks and the audit plan."""
    state = new_state(options, environ)
    state.claude_version = claude_version
    prepare_root(state.report_root)
    state.run_dir.mkdir(parents=True, exist_ok=True)
    state.writes.append(f"{state.run_dir}: run folder (state, tasks, report)")
    state.git_before = integrity.git_state(state.repo)
    found = inventory.build(state.repo, state.env, state.report_root)
    state.inventory = found
    for source in found.sources:
        if source.status in {inventory.SKIPPED, "unreadable"}:
            state.problems.append(f"{source.display} was not audited: {source.reason}")
    work = state.run_dir / "work"
    work.mkdir(mode=WORK_MODE, exist_ok=True)
    state.work = work
    state.writes.append(f"{work}: private working copies and task files, deleted at the end")
    snap = snapshot.write(found, work)
    state.snapshot = snap
    for source in found.sources:
        if source.sid in snap.lines:
            source.lines = snap.lines[source.sid]
    inventory.index_units(found)
    state.evidence = evidence.collect(state.repo, found.files)
    _ = (work / "repo-evidence.json").write_text(dumps(state.evidence), encoding="utf-8")
    _ = (work / "sources.json").write_text(plan.manifest_json(found, snap), encoding="utf-8")
    _ = _knowledge(state, work)
    taxonomy = topics.load_topics(knowledge.KNOWLEDGE / "topics.json")
    result = checks.run(found, snap, state.evidence, taxonomy)
    state.checks = result
    state.findings.extend(result.findings)
    packages = plan.make_packages(found, snap, result)
    state.domains = [DomainRun(package=package) for package in packages]
    _write_tasks(state)
    state.stage = "prepared"
    _ = store.save(state)
    return state


def _external_sources(state: RunState) -> list[str]:
    found = state.inventory
    if found is None:
        return []
    return [
        source.display
        for source in found.sources
        if not paths.in_directory(paths.resolve(source.path), state.repo)
    ]


def prepare_summary(state: RunState) -> JsonObj:
    """What the coordinator shows the user and passes to the first workflow."""
    found = state.inventory
    sources = found.sources if found else []
    snap = state.snapshot
    tasks = state.work_tasks()
    packages = [
        {
            "name": run.package.name,
            "domain": run.package.domain,
            "files": run.package.sids,
            "chars": run.package.chars,
            "task": str(tasks / f"{run.package.name}.md"),
            "turns": plan.max_turns(run.package, snap) if snap else 0,
        }
        for run in state.domains
    ]
    by_status: dict[str, int] = {}
    for source in sources:
        by_status[source.status] = by_status.get(source.status, 0) + 1
    return {
        "schema": "agent-files-diagnostics/prepare/1",
        "run_id": state.run_id,
        "run_dir": str(state.run_dir),
        "work": str(state.work) if state.work else "",
        "repo": str(state.repo),
        "report_root": str(state.report_root),
        "sources": by_status,
        "audited": sum(1 for source in sources if source.status == IN_SCOPE),
        "external_sources": _external_sources(state),
        "out_of_scope": found.out_of_scope if found else [],
        "deterministic_findings": len(state.findings),
        "candidates": len(state.checks.candidates) if state.checks else 0,
        "pairs": len(state.checks.pairs) if state.checks else 0,
        "packages": packages,
        "knowledge_online": bool(state.knowledge and state.knowledge.online),
        "problems": state.problems,
        "warnings": state.warnings,
    }


# --- stage 2: accept the domain audits ------------------------------------------------------


@dataclass
class Journal:
    """What a workflow run left behind: results by label, and where the transcripts are."""

    run_dir: Path | None = None
    results: dict[str, JsonObj] = field(default_factory=dict)
    agents: dict[str, str] = field(default_factory=dict)
    error: str = ""

    def transcript(self, label: str) -> Path | None:
        """The transcript of the agent that carried a label, when the run folder is known."""
        agent = self.agents.get(label)
        if self.run_dir is None or not agent:
            return None
        return coverage.transcript(self.run_dir, agent)


def _results_from_journal(run_dir: Path) -> dict[str, JsonObj]:
    by_agent: dict[str, JsonObj] = {}
    labels: dict[str, str] = {}
    for entry in coverage.events(run_dir / "journal.jsonl"):
        kind = get_str(entry, "type")
        if kind == "started":
            labels[get_str(entry, "agentId")] = get_str(entry, "label")
        elif kind == "result":
            by_agent[get_str(entry, "agentId")] = as_obj(entry.get("result"))
    return {labels[agent]: result for agent, result in by_agent.items() if agent in labels}


def _journal_from_file(journal: Journal, results_file: str) -> None:
    try:
        data = as_obj(read_json(Path(results_file)))
    except (OSError, ValueError) as error:
        journal.error = f"the results file could not be read: {error}"
        return
    for raw in get_list(data, "results"):
        item = as_obj(raw)
        journal.results[get_str(item, "label")] = as_obj(item.get("result"))
    folder = get_str(data, "run_dir")
    journal.run_dir = Path(folder) if folder else None


def read_journal(state: RunState, workflow_run: str, results_file: str) -> Journal:
    """Results of a workflow run: from Claude Code's journal, or from a file the tests write."""
    journal = Journal()
    if results_file:
        _journal_from_file(journal, results_file)
    elif workflow_run:
        journal.run_dir = coverage.find_run_dir(state.env.transcripts, workflow_run)
        if journal.run_dir is None:
            journal.error = f"no workflow run folder named {workflow_run} under the session folders"
        else:
            journal.results = _results_from_journal(journal.run_dir)
    else:
        journal.error = "no workflow run id and no results file were given"
    if not journal.error and journal.run_dir is not None:
        journal.agents = coverage.agent_ids(journal.run_dir)
    return journal


def _coverage(state: RunState, run: DomainRun, journal: Journal) -> None:
    """Prove coverage from the transcript, or mark the package partial when there is none."""
    _, snap, _ = _parts(state)
    label = run.package.name
    transcript = journal.transcript(label)
    if transcript is None or not transcript.is_file():
        run.status = "partial"
        run.error = "coverage unverified: the agent's transcript was not found"
        return
    reads, tools = coverage.reads_from_transcript(transcript)
    run.agent_id = journal.agents.get(label, "")
    stray = sorted(tools - ALLOWED_TOOL_CALLS)
    if stray:
        run.status, run.error = "failed", f"the agent used tools outside its allowlist: {stray}"
        return
    run.ledgers = coverage.build(reads, snap, run.package.sids)
    run.gaps = {sid: item.describe() for sid, item in run.ledgers.items() if not item.complete}
    if run.gaps:
        run.status, run.error = "partial", "some lines were never received"
    else:
        run.status, run.error = "complete", ""


def _evaluate(state: RunState, run: DomainRun, journal: Journal) -> JsonObj | None:
    """Judge one auditor result: presence, schema, tools used and the coverage ledger."""
    run.attempts += 1
    output = journal.results.get(run.package.name)
    if output is None:
        run.status, run.error = "failed", "no result for this package in the workflow journal"
        return None
    errors = schema.validate(output, schema.load("auditor"))
    if errors:
        run.status, run.error = "failed", f"invalid output: {'; '.join(errors[:3])}"
        return None
    _coverage(state, run, journal)
    return None if run.status == "failed" else output


def _checker(state: RunState, allowed: frozenset[str]) -> validate.Checker:
    found, snap, _ = _parts(state)
    defaults: frozenset[str] = state.knowledge.defaults if state.knowledge else frozenset()
    return validate.Checker(found, snap, defaults, allowed)


def _context(state: RunState) -> checks.Context:
    found, snap, _ = _parts(state)
    return checks.Context(found, snap, state.evidence)


def _accept_output(state: RunState, run: DomainRun, output: JsonObj) -> None:
    origin = f"auditor:{run.package.name}"
    result = validate.auditor_output(_checker(state, run.package.allowed), output, origin)
    state.findings.extend(result.findings)
    state.claims.extend(result.claims)
    state.rejected.extend(result.rejected)
    state.verdicts.update(result.verdicts)


def _assign(state: RunState) -> None:
    """Attach unit IDs and stable finding IDs; reject auditor repeats of deterministic facts."""
    context = _context(state)
    for item in state.findings:
        item.unit = item.unit or context.unit(item.sid, item.start)
    for claim in state.claims:
        claim.unit = claim.unit or context.unit(claim.sid, claim.start)
    facts = {
        (item.unit, item.category) for item in state.findings if item.origin == "deterministic"
    }
    kept: list[Finding] = []
    for item in state.findings:
        if item.origin != "deterministic" and (item.unit, item.category) in facts:
            summary = f"{item.sid}:{item.start} {item.category}"
            state.rejected.append(
                validate.Rejected(item.origin, "repeats a deterministic finding", summary)
            )
            continue
        kept.append(item)
    state.findings = kept
    assign_ids(state.findings)
    assign_claim_ids(state.claims)


def _usage(state: RunState, journal: Journal, labels: list[str]) -> None:
    for label in labels:
        transcript = journal.transcript(label)
        if transcript is None or not transcript.is_file():
            continue
        tokens = coverage.usage_from_transcript(transcript)
        state.usage.append({"label": label, **tokens})


def accept_domains(state: RunState, journal: Journal) -> JsonObj:
    """Validate every domain auditor result and plan the review workflow."""
    if journal.error:
        state.failures.append(journal.error)
        return accept_summary(state, [])
    pending = [run for run in state.domains if run.status != "complete"]
    accepted: list[str] = []
    for run in pending:
        output = _evaluate(state, run, journal)
        if output is not None:
            _accept_output(state, run, output)
            accepted.append(run.package.name)
    _assign(state)
    _usage(state, journal, accepted)
    retry = [run.package.name for run in state.domains if run.status != "complete"]
    for run in state.domains:
        if run.status != "complete":
            state.problems.append(f"package {run.package.name} is {run.status}: {run.error}")
    expected = {cid for run in state.domains for cid in run.package.candidates}
    missing = sorted(expected - set(state.verdicts))
    if missing:
        state.warnings.append(f"candidates the auditors left unjudged: {', '.join(missing)}")
    state.stage = "domains-accepted"
    review = _write_review_tasks(state)
    _ = store.save(state)
    return accept_summary(state, retry, review)


def _finding_rows(state: RunState, items: list[Finding]) -> list[JsonObj]:
    found, snap, _ = _parts(state)
    rows: list[JsonObj] = []
    for item in items:
        source = found.by_sid(item.sid)
        rows.append(
            {
                "fid": item.fid,
                "origin": item.origin,
                "category": item.category,
                "severity": item.severity,
                "confidence": item.confidence,
                "sid": item.sid,
                "file": source.display if source else item.sid,
                "snapshot": str(snap.paths.get(item.sid, "")),
                "lines": f"{item.start}-{item.end}",
                "excerpt": item.excerpt,
                "conflicts_with": [f"{c.kind}: {c.ref}" for c in item.conflicts_with],
                "evidence": item.evidence,
                "disposition": item.disposition,
                "rationale": item.rationale,
            }
        )
    return rows


def _batches(items: list[Finding], size: int) -> list[list[Finding]]:
    return [items[start : start + size] for start in range(0, len(items), size)]


def _write_verify_tasks(state: RunState, tasks: Path) -> list[JsonObj]:
    verify: list[JsonObj] = []
    for number, batch in enumerate(_batches(state.findings, VERIFY_BATCH), start=1):
        path = tasks / f"verify-{number}.md"
        body = json.dumps(_finding_rows(state, batch), indent=1, ensure_ascii=False)
        text = (
            "# Independent verification task\n\nFor each finding below, read the cited lines of"
            " the snapshot copy and every cited conflict, then say whether the finding holds.\n\n"
            f"```json\n{body}\n```\n"
        )
        _ = path.write_text(text, encoding="utf-8")
        verify.append({"label": f"verify-{number}", "task": str(path)})
    return verify


def _write_claim_tasks(state: RunState, tasks: Path) -> list[JsonObj]:
    claims: list[JsonObj] = []
    batches = [
        state.claims[start : start + CLAIM_BATCH]
        for start in range(0, len(state.claims), CLAIM_BATCH)
    ]
    for number, batch in enumerate(batches, start=1):
        path = tasks / f"claims-{number}.md"
        rows = [
            {"cid": claim.cid, "subject": claim.subject, "claim": claim.claim} for claim in batch
        ]
        body = json.dumps(rows, indent=1, ensure_ascii=False)
        _ = path.write_text(f"# Claims to verify\n\n```json\n{body}\n```\n", encoding="utf-8")
        claims.append({"label": f"claims-{number}", "task": str(path)})
    return claims


def _write_review_tasks(state: RunState) -> JsonObj:
    """The task files of the review workflow: reconciliation, verification and claims."""
    found, snap, result = _parts(state)
    tasks = state.work_tasks()
    tasks.mkdir(mode=WORK_MODE, exist_ok=True)
    prompt = reconcile.reconciler_prompt(state.findings, result.pairs, found, snap.lines)
    reconcile_path = tasks / "reconcile.md"
    _ = reconcile_path.write_text(prompt, encoding="utf-8")
    findings_path = tasks / "findings.json"
    _ = findings_path.write_text(dumps(_finding_rows(state, state.findings)), encoding="utf-8")
    owners = sorted({item.origin for item in state.findings if item.origin != "deterministic"})
    owners_by_fid = {
        item.fid: item.origin for item in state.findings if item.origin != "deterministic"
    }
    return {
        "reconcile_task": str(reconcile_path),
        "findings_file": str(findings_path),
        "owners": owners,
        "owners_by_fid": owners_by_fid,
        "verify": _write_verify_tasks(state, tasks),
        "claims": _write_claim_tasks(state, tasks),
        "rounds": max(1, min(2, state.options.challenge_rounds)),
        "deterministic": [item.fid for item in state.findings if item.origin == "deterministic"],
    }


def accept_summary(state: RunState, retry: list[str], review: JsonObj | None = None) -> JsonObj:
    """What the coordinator learns after the domain audits."""
    return {
        "schema": "agent-files-diagnostics/accept-domains/1",
        "run_id": state.run_id,
        "run_dir": str(state.run_dir),
        "packages": [
            {
                "name": run.package.name,
                "status": run.status,
                "attempts": run.attempts,
                "error": run.error,
                "gaps": run.gaps,
            }
            for run in state.domains
        ],
        "retry": retry,
        "findings": len(state.findings),
        "claims": len(state.claims),
        "rejected": len(state.rejected),
        "review": review or {},
        "problems": state.problems,
        "failures": state.failures,
        "warnings": state.warnings,
    }


# --- stage 3: accept the review -------------------------------------------------------------


def free_id(base: str, taken: set[str]) -> str:
    """base, or base-2, base-3... when base is taken."""
    candidate, number = base, 2
    while candidate in taken:
        candidate = f"{base}-{number}"
        number += 1
    return candidate


def _cross_findings(state: RunState, output: JsonObj) -> None:
    found, _, _ = _parts(state)
    checker = _checker(state, frozenset(source.sid for source in found.audited))
    context = _context(state)
    taken = {item.fid for item in state.findings}
    for raw in get_list(output, "cross_findings"):
        item = as_obj(raw)
        finding, reason = validate.check_finding(checker, item, "reconciler")
        if finding is None:
            summary = validate.summarize(item)
            state.rejected.append(validate.Rejected("reconciler", reason, summary))
            continue
        finding.unit = context.unit(finding.sid, finding.start)
        finding.fid = free_id(finding_id(finding.category, finding.unit), taken)
        taken.add(finding.fid)
        state.findings.append(finding)


def _reconciliation(state: RunState, journal: Journal) -> None:
    output = journal.results.get("reconcile")
    if not state.findings and not (state.checks and state.checks.pairs):
        state.reconciliation = "complete"
        state.warnings.append("nothing to reconcile: no findings and no candidate pairs")
        return
    if output is None or schema.validate(output, schema.load("reconciler")):
        state.reconciliation = "failed: the reconciler returned no valid output"
        state.problems.append(state.reconciliation)
        return
    reconcile.apply_decisions(state.findings, output, state.outcome)
    _cross_findings(state, output)
    missing = state.outcome.missing
    state.reconciliation = "complete" if not missing else f"incomplete: {len(missing)} undecided"
    if missing:
        state.problems.append(f"the reconciler left findings undecided: {', '.join(missing)}")
    _challenge(state, journal)


def _challenge(state: RunState, journal: Journal) -> None:
    """Replay the challenge round from the journal: owners answered, the reconciler decided."""
    contested = [item for item in state.findings if item.status == CONTESTED]
    rounds = max(1, min(2, state.options.challenge_rounds))
    for number in range(1, rounds + 1):
        if not contested:
            return
        last = number == rounds
        pending: dict[str, JsonObj] = {}
        for owner in sorted({item.origin for item in contested}):
            items = [item for item in contested if item.origin == owner]
            output = journal.results.get(f"rebuttal-{number}:{owner}") or {}
            pending.update(reconcile.record_rebuttals(items, output, state.outcome))
        undecided = [item for item in contested if item.fid in pending]
        if not undecided:
            return
        output = journal.results.get(f"decide-{number}") or {}
        contested = reconcile.record_decisions(undecided, output, state.outcome, last=last)
    for item in contested:
        item.status = OPEN


def _apply_verdict(state: RunState, item: Finding, entry: JsonObj) -> None:
    reason = get_str(entry, "reason")
    if get_bool(entry, "holds"):
        item.verified = "confirmed"
        return
    if reason.lower().startswith("could not verify"):
        item.verified = "unverified"
        item.trail.append(f"independent verifier: {reason}")
        return
    item.verified = "refuted"
    item.trail.append(f"independent verifier: does not hold: {reason}")
    if item.status == FINAL:
        item.status = OPEN
        state.outcome.positions.setdefault(item.fid, []).append(f"verifier: {reason}")


def _verification(state: RunState, journal: Journal) -> None:
    """Apply the independent verifiers' verdicts on every finding."""
    by_fid = {item.fid: item for item in state.findings}
    answered = 0
    for label, output in journal.results.items():
        if not label.startswith("verify-"):
            continue
        for raw in get_list(output, "results"):
            entry = as_obj(raw)
            item = by_fid.get(get_str(entry, "fid"))
            if item is not None:
                answered += 1
                _apply_verdict(state, item, entry)
    unverified = [item for item in state.findings if not item.verified]
    for item in unverified:
        item.verified = "unverified"
    total = len(state.findings)
    state.independent = f"{answered} of {total} findings re-checked independently"
    if unverified and total:
        state.warnings.append(f"{len(unverified)} finding(s) were not independently verified")


def apply_verdicts(claims: list[ExternalClaim], output: JsonObj) -> int:
    """Record the researcher's verdict and sources on each claim; returns how many it answered."""
    by_id = {claim.cid: claim for claim in claims}
    applied = 0
    for raw in get_list(output, "results"):
        entry = as_obj(raw)
        claim = by_id.get(get_str(entry, "cid"))
        if claim is None:
            continue
        claim.verdict = get_str(entry, "verdict", "inconclusive")
        claim.verdict_evidence = [
            {key: str(value) for key, value in as_obj(source).items()}
            for source in get_list(entry, "sources")
        ]
        applied += 1
    return applied


def _claims(state: RunState, journal: Journal) -> None:
    if not state.claims:
        state.verification = "no external claims"
        return
    applied = 0
    for label, output in journal.results.items():
        if label.startswith("claims-"):
            applied += apply_verdicts(state.claims, output)
    state.verification = f"{applied} of {len(state.claims)} claims checked against live sources"
    if applied < len(state.claims):
        state.warnings.append(f"{len(state.claims) - applied} claim(s) stay unverified")


def accept_review(state: RunState, journal: Journal) -> JsonObj:
    """Apply everything the review workflow returned."""
    if journal.error:
        state.failures.append(journal.error)
        return review_summary(state)
    _reconciliation(state, journal)
    _verification(state, journal)
    _claims(state, journal)
    _usage(state, journal, sorted(journal.results))
    state.stage = "review-accepted"
    _ = store.save(state)
    return review_summary(state)


def review_summary(state: RunState) -> JsonObj:
    """What the coordinator inspects before the report: every reported finding and its evidence."""
    reported = [item for item in state.findings if item.status in {FINAL, OPEN}]
    return {
        "schema": "agent-files-diagnostics/accept-review/1",
        "run_id": state.run_id,
        "run_dir": str(state.run_dir),
        "reconciliation": state.reconciliation,
        "independent": state.independent,
        "verification": state.verification,
        "to_inspect": _finding_rows(state, reported),
        "open_decisions": sum(1 for item in reported if item.status == OPEN),
        "problems": state.problems,
        "failures": state.failures,
        "warnings": state.warnings,
    }


# --- stage 4: finalize ----------------------------------------------------------------------


def _coordinator(state: RunState, checked: Mapping[str, str]) -> None:
    """Record the coordinator's own inspection of every reported finding."""
    reported = [item for item in state.findings if item.status in {FINAL, OPEN}]
    inspected = 0
    for item in reported:
        verdict = checked.get(item.fid, "")
        if not verdict:
            item.coordinator_check = NOT_INSPECTED
            continue
        inspected += 1
        if verdict.lower().startswith("ok"):
            item.coordinator_check = "ok"
        else:
            item.coordinator_check = verdict
            item.status = DISMISSED
            item.trail.append(f"coordinator: rejected after inspecting the evidence: {verdict}")
    skipped = len(reported) - inspected
    state.coordinator = f"{inspected} of {len(reported)} findings inspected by the coordinator"
    if skipped:
        state.problems.append(f"{skipped} finding(s) were not inspected by the coordinator")


def _integrity(state: RunState) -> None:
    if state.inventory is None:
        return
    state.integrity = integrity.check(state.inventory, state.git_before)
    for sid in state.integrity.changed:
        state.problems.append(
            f"{sid} changed during the audit (the audit only reads, so another process edited it)"
        )
    for sid in state.integrity.vanished:
        state.problems.append(f"{sid} disappeared during the audit")
    if state.integrity.git_changed:
        state.problems.append("the git working tree or HEAD changed during the audit")


def _write_report(state: RunState) -> None:
    state.finished = utc_now()
    kept = render.reported(state)
    runs = history.read_index(state.report_root)
    state.change = history.compare(kept, runs, partial=bool(state.problems or state.failures))
    state.settle()
    report_md = state.run_dir / "report.md"
    write_atomic(state.run_dir / "report.json", dumps(render.report_json(state)))
    write_atomic(report_md, render.markdown(state))
    status = render.status_json(state, str(report_md))
    write_atomic(state.run_dir / "status.json", dumps(status))
    entry: JsonObj = {
        "run_id": state.run_id,
        "status": state.status,
        "finished": state.finished,
        "findings": [item.fid for item in kept],
        "units": {item.fid: item.unit for item in kept},
    }
    history.record(state.report_root, entry, {**status, "run_dir": str(state.run_dir)})
    state.writes.append(f"{report_md}: the report, with report.json and status.json beside it")


def finalize(state: RunState, checked: Mapping[str, str]) -> JsonObj:
    """Coordinator checks, integrity, history and the report."""
    _coordinator(state, checked)
    _integrity(state)
    try:
        _write_report(state)
    except OSError as error:
        state.failures.append(f"the report could not be written: {error}")
        state.settle()
    state.stage = "finalized"
    _ = store.save(state)
    if state.work is not None and not state.options.keep_work:
        snapshot.remove(state.work)
    report = state.run_dir / "report.md"
    return render.status_json(state, str(report) if report.exists() else "")
