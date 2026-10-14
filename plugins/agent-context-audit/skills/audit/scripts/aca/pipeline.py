"""One audit of one repository, from preflight to the exit code.

Stages: inventory, snapshot and repository evidence, knowledge (with live drift), deterministic
checks, domain auditors (parallel, isolated, retried), validation and coverage, reconciliation
with the bounded challenge round, optional online verification, integrity, history, report.
Whatever fails, the run still ends with a report and a status that says what is missing.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
from typing import TYPE_CHECKING

from aca import (
    checks,
    config_checks,
    coverage,
    evidence,
    history,
    integrity,
    inventory,
    knowledge,
    notice,
    paths,
    plan,
    reconcile,
    render,
    schema,
    snapshot,
    topics,
    validate,
    workers,
)
from aca.findings import (
    CONTESTED,
    OPEN,
    assign_claim_ids,
    assign_ids,
    finding_id,
)
from aca.jsonutil import JsonObj, as_obj, dumps, get_list, get_str, write_atomic
from aca.state import DomainRun, RunState

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aca.findings import ExternalClaim, Finding
    from aca.state import Options

ROLES = knowledge.DATA / "roles"
READ_TOOLS = "Read,Grep,Glob"
WEB_TOOLS = "WebFetch"
ALLOWED_TOOL_CALLS = frozenset({"Read", "Grep", "Glob", "StructuredOutput"})
RECONCILER_TURNS = 80
SMALL_TURNS = 40
VERIFY_BATCH = 15
VERIFIER_EFFORT = "medium"
VERSION_TIMEOUT = 30
STRONG_ROLES = frozenset({"reconciler", "decide"})
UNEXPECTED = (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, RuntimeError)


@dataclass
class Audit:
    """What the model-driven stages need, all present (built by the deterministic stages)."""

    state: RunState
    inventory: inventory.Inventory
    snapshot: snapshot.Snapshot
    knowledge: knowledge.Knowledge
    deterministic: checks.Checks
    work: Path
    claude: str
    environ: Mapping[str, str]

    def context(self) -> checks.Context:
        """A checks context over this audit's inventory and snapshot."""
        out = checks.Context(self.inventory, self.snapshot, self.state.evidence)
        out.out = self.deterministic
        return out

    def checker(self, allowed: frozenset[str]) -> validate.Checker:
        """A validation context limited to the given sources."""
        return validate.Checker(self.inventory, self.snapshot, self.knowledge.defaults, allowed)


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


def claude_version(claude: str) -> str:
    """`claude --version` without the product name, or '' when it fails."""
    try:
        done = subprocess.run(
            [claude, "--version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT,
            check=False,
            stdin=subprocess.DEVNULL,
            env=workers.worker_env(os.environ),
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return done.stdout.strip().split(" ")[0] if done.returncode == 0 else ""


def new_state(repo_arg: str, options: Options, environ: Mapping[str, str]) -> RunState:
    """A fresh state for one repository."""
    repo = paths.repo_root(paths.resolve(Path(repo_arg).expanduser()))
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


# --- deterministic stages -----------------------------------------------------------------


def prepare(state: RunState, claude: str, environ: Mapping[str, str]) -> Audit:
    """Inventory, snapshot, evidence, knowledge and deterministic checks."""
    state.git_before = integrity.git_state(state.repo)
    found = inventory.build(state.repo, state.env, state.report_root)
    state.inventory = found
    for source in found.sources:
        if source.status in {inventory.SKIPPED, "unreadable"}:
            state.problems.append(f"{source.display} was not audited: {source.reason}")
    work = snapshot.make_workdir()
    state.work = work
    snap = snapshot.write(found, work)
    state.snapshot = snap
    state.evidence = evidence.collect(state.repo, found.files)
    _ = (work / "repo-evidence.json").write_text(dumps(state.evidence), encoding="utf-8")
    _ = (work / "sources.json").write_text(plan.manifest_json(found, snap), encoding="utf-8")
    known = _knowledge(state, work)
    taxonomy = topics.load_topics(knowledge.KNOWLEDGE / "topics.json")
    result = checks.run(found, snap, state.evidence, taxonomy)
    state.checks = result
    audit = Audit(state, found, snap, known, result, work, claude, environ)
    context = audit.context()
    config_checks.check_settings(context, known)
    config_checks.check_codex_config(context)
    state.findings.extend(result.findings)
    return audit


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


# --- domain auditors ----------------------------------------------------------------------


def _auditor_spec(audit: Audit, shard: plan.Shard, settings: Path) -> workers.Spec:
    options = audit.state.options
    return workers.Spec(
        name=f"auditor-{shard.name}",
        role="auditor",
        prompt=plan.auditor_prompt(shard, audit.inventory, audit.snapshot, audit.deterministic),
        schema=schema.load("auditor"),
        role_file=ROLES / "auditor.md",
        settings_file=settings,
        model=options.auditor_model,
        effort=options.auditor_effort,
        tools=READ_TOOLS,
        max_turns=plan.max_turns(shard, audit.snapshot),
        timeout=options.worker_timeout,
        budget=options.budget,
        cwd=audit.state.repo,
    )


def _status_of(run: DomainRun, result: workers.Result) -> tuple[str, str]:
    stray = sorted(set(result.tools_used) - ALLOWED_TOOL_CALLS)
    errors = schema.validate(result.output, schema.load("auditor")) if result.ok else []
    if not result.ok:
        return "failed", result.error
    if stray:
        return "failed", f"the worker used tools outside its allowlist: {stray}"
    if errors:
        return "failed", f"invalid output: {'; '.join(errors[:3])}"
    if run.gaps:
        return "partial", "some lines were never received"
    return "complete", ""


def evaluate(audit: Audit, run: DomainRun, result: workers.Result) -> None:
    """Judge one auditor attempt: schema, tools used, and the coverage ledger."""
    run.result = result
    run.attempts += 1
    run.ledgers = coverage.build(result.reads, audit.snapshot, run.shard.sids)
    run.gaps = {sid: item.describe() for sid, item in run.ledgers.items() if not item.complete}
    run.status, run.error = _status_of(run, result)


def _accept(audit: Audit, run: DomainRun) -> None:
    """Validate a usable auditor output and keep what survives."""
    if run.result is None or run.status == "failed":
        return
    origin = f"auditor:{run.shard.name}"
    result = validate.auditor_output(audit.checker(run.shard.allowed), run.result.output, origin)
    state = audit.state
    state.findings.extend(result.findings)
    state.claims.extend(result.claims)
    state.rejected.extend(result.rejected)
    state.verdicts.update(result.verdicts)


def run_auditors(audit: Audit) -> None:
    """Run every shard's auditor in parallel, retrying failures, then validate their outputs."""
    state = audit.state
    rules = plan.auditor_settings(audit.inventory, state.report_root)
    settings = workers.write_settings(audit.work / "worker-settings.json", rules)
    shards = plan.make_shards(audit.inventory, audit.snapshot, audit.deterministic)
    state.domains = [DomainRun(shard=shard) for shard in shards]
    pending = list(state.domains)
    for _attempt in range(state.options.retries + 1):
        if not pending:
            break
        specs = [_auditor_spec(audit, run.shard, settings) for run in pending]
        concurrency = state.options.concurrency
        results = workers.run_many(audit.claude, specs, audit.work, audit.environ, concurrency)
        state.results.extend(results)
        for index, run in enumerate(pending):
            evaluate(audit, run, results[index])
        pending = [run for run in pending if run.status != "complete"]
    for run in state.domains:
        _accept(audit, run)
        if run.status != "complete":
            state.problems.append(f"shard {run.shard.name} is {run.status}: {run.error}")
    expected = {cid for run in state.domains for cid in run.shard.candidates}
    missing = sorted(expected - set(state.verdicts))
    if missing:
        state.warnings.append(f"candidates the auditors left unjudged: {', '.join(missing)}")


def assign(audit: Audit) -> None:
    """Attach unit IDs and stable finding IDs; reject auditor repeats of deterministic facts."""
    state = audit.state
    context = audit.context()
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


# --- reconciliation and the challenge round -----------------------------------------------


def _spec(audit: Audit, role: str, prompt: str) -> workers.Spec:
    options = audit.state.options
    strong = role in STRONG_ROLES
    return workers.Spec(
        name=f"{role}-{secrets.token_hex(2)}",
        role=role,
        prompt=prompt,
        schema=schema.load(role),
        role_file=ROLES / f"{role}.md",
        settings_file=audit.work / "worker-settings.json",
        model=options.reconciler_model if strong else options.auditor_model,
        effort=options.reconciler_effort if strong else options.auditor_effort,
        tools=READ_TOOLS,
        max_turns=RECONCILER_TURNS if role == "reconciler" else SMALL_TURNS,
        timeout=options.worker_timeout,
        budget=options.budget,
        cwd=audit.state.repo,
    )


def run_single(audit: Audit, role: str, prompt: str) -> JsonObj | None:
    """Run one worker with retries; its validated output, or None when every attempt failed."""
    spec = _spec(audit, role, prompt)
    for _attempt in range(audit.state.options.retries + 1):
        result = workers.run_one(audit.claude, spec, audit.work, audit.environ)
        audit.state.results.append(result)
        if result.ok and not schema.validate(result.output, spec.schema):
            return result.output
    return None


def free_id(base: str, taken: set[str]) -> str:
    """base, or base-2, base-3... when base is taken."""
    candidate, number = base, 2
    while candidate in taken:
        candidate = f"{base}-{number}"
        number += 1
    return candidate


def _cross_findings(audit: Audit, output: JsonObj) -> None:
    state = audit.state
    checker = audit.checker(frozenset(source.sid for source in audit.inventory.audited))
    context = audit.context()
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


def reconcile_all(audit: Audit) -> None:
    """Cross-domain reconciliation over every completed domain output."""
    state = audit.state
    pairs = audit.deterministic.pairs
    if not state.findings and not pairs:
        state.reconciliation = "complete"
        state.warnings.append("nothing to reconcile: no findings and no candidate pairs")
        return
    if state.domains and not any(run.status != "failed" for run in state.domains):
        state.reconciliation = "skipped: no domain output to reconcile"
        state.problems.append(state.reconciliation)
        return
    lines = audit.snapshot.lines
    prompt = reconcile.reconciler_prompt(state.findings, pairs, audit.inventory, lines)
    output = run_single(audit, "reconciler", prompt)
    if output is None:
        state.reconciliation = "failed: the reconciler returned no valid output"
        state.problems.append(state.reconciliation)
        return
    reconcile.apply_decisions(state.findings, output, state.outcome)
    _cross_findings(audit, output)
    missing = state.outcome.missing
    state.reconciliation = "complete" if not missing else f"incomplete: {len(missing)} undecided"
    if missing:
        state.problems.append(f"the reconciler left findings undecided: {', '.join(missing)}")
    challenge(audit)


def _rebuttals(audit: Audit, contested: list[Finding]) -> dict[str, JsonObj]:
    state = audit.state
    pending: dict[str, JsonObj] = {}
    for owner in sorted({item.origin for item in contested}):
        items = [item for item in contested if item.origin == owner]
        prompt = reconcile.rebuttal_prompt(items, state.outcome, audit.inventory)
        output = run_single(audit, "rebuttal", prompt) or {}
        pending.update(reconcile.record_rebuttals(items, output, state.outcome))
    return pending


def challenge(audit: Audit) -> None:
    """The bounded challenge round: owners answer, the reconciler decides; two rounds at most."""
    state = audit.state
    contested = [item for item in state.findings if item.status == CONTESTED]
    rounds = max(1, min(2, state.options.challenge_rounds))
    for number in range(1, rounds + 1):
        if not contested:
            return
        last = number == rounds
        pending = _rebuttals(audit, contested)
        undecided = [item for item in contested if item.fid in pending]
        if not undecided:
            return
        prompt = reconcile.decide_prompt(undecided, state.outcome, pending, last=last)
        output = run_single(audit, "decide", prompt) or {}
        contested = reconcile.record_decisions(undecided, output, state.outcome, last=last)
    for item in contested:
        item.status = OPEN


# --- optional online verification ---------------------------------------------------------


def _verifier_spec(audit: Audit, batch: list[ExternalClaim], number: int) -> workers.Spec:
    options = audit.state.options
    settings = workers.write_settings(
        audit.work / "verifier-settings.json",
        plan.verifier_settings(options.online_domains),
    )
    rows = [{"cid": claim.cid, "subject": claim.subject, "claim": claim.claim} for claim in batch]
    body = json.dumps(rows, indent=1, ensure_ascii=False)
    return workers.Spec(
        name=f"verifier-{number}",
        role="verifier",
        prompt=f"# Claims to verify\n\n```json\n{body}\n```\n",
        schema=schema.load("verifier"),
        role_file=ROLES / "verifier.md",
        settings_file=settings,
        model=options.auditor_model,
        effort=VERIFIER_EFFORT,
        tools=WEB_TOOLS,
        max_turns=SMALL_TURNS,
        timeout=options.worker_timeout,
        budget=options.budget,
        cwd=audit.work,
    )


def apply_verdicts(claims: list[ExternalClaim], output: JsonObj) -> int:
    """Record the verifier's verdict and sources on each claim; returns how many it answered."""
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


def verify(audit: Audit) -> None:
    """Opt-in: verify external claims against live public sources with web-only workers."""
    state = audit.state
    if not state.claims:
        state.verification = "no external claims"
        return
    if not state.options.verify_online:
        state.verification = "not requested (run with --verify-online, or verify them in a session)"
        return
    size = VERIFY_BATCH
    batches = [state.claims[start : start + size] for start in range(0, len(state.claims), size)]
    specs = [_verifier_spec(audit, batch, number) for number, batch in enumerate(batches, start=1)]
    concurrency = state.options.concurrency
    results = workers.run_many(audit.claude, specs, audit.work, audit.environ, concurrency)
    state.results.extend(results)
    applied = sum(apply_verdicts(state.claims, result.output) for result in results if result.ok)
    state.verification = f"{applied} of {len(state.claims)} claims checked live"
    failed = sum(1 for result in results if not result.ok)
    if failed:
        state.warnings.append(f"{failed} verifier worker(s) failed; their claims stay unverified")


# --- integrity, report, entry point -------------------------------------------------------


def check_integrity(state: RunState) -> None:
    """Hashes and git state after the run."""
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


def write_report(state: RunState, started: float) -> None:
    """Settle the status, compare with history, write the report files and the latest pointer."""
    state.finished = utc_now()
    state.seconds = round(time.monotonic() - started, 1)
    kept = render.reported(state)
    runs = history.read_index(state.report_root)
    state.change = history.compare(kept, runs, partial=bool(state.problems or state.failures))
    state.settle()
    state.run_dir.mkdir(parents=True, exist_ok=True)
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
    write_atomic(
        state.report_root / notice.NOTICE, dumps(render.notice_json(state, str(report_md)))
    )
    if state.options.mode == "interactive":
        notice.mark_shown(state.report_root, state.run_id)


def run(repo_arg: str, options: Options, environ: Mapping[str, str], claude: str) -> RunState:
    """Audit one repository; always returns a settled state (a written report, or a failure)."""
    started = time.monotonic()
    state = new_state(repo_arg, options, environ)
    state.claude = claude
    state.claude_version = claude_version(claude)
    try:
        prepare_root(state.report_root)
        audit = prepare(state, claude, environ)
        run_auditors(audit)
        assign(audit)
        reconcile_all(audit)
        verify(audit)
    except UNEXPECTED as error:
        state.failures.append(f"internal error: {type(error).__name__}: {error}")
    check_integrity(state)
    try:
        write_report(state, started)
    except OSError as error:
        state.failures.append(f"the report could not be written: {error}")
        state.settle()
    finally:
        if state.work is not None and not options.keep_work:
            snapshot.remove(state.work)
    return state
