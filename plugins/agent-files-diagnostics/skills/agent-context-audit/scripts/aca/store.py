"""Persistence of one run's state between stages: `state.json` in the run folder.

The stages run as separate processes, so everything a later stage needs is written here and
read back. Sources carry their redacted lines through the snapshot copies, never the originals.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from aca import inventory as inventory_module, knowledge as knowledge_module
from aca.checks import Candidate, Checks
from aca.claude_sources import ImportEdge
from aca.findings import Conflict, ExternalClaim, Finding, Location
from aca.integrity import GitState, Integrity
from aca.jsonutil import (
    JsonObj,
    as_list,
    as_obj,
    dumps,
    get_bool,
    get_float,
    get_int,
    get_list,
    get_obj,
    get_str,
    read_json,
    str_list,
    write_atomic,
)
from aca.plan import Package
from aca.reconcile import Outcome, Proposal
from aca.snapshot import Snapshot
from aca.sources import Loader, Source
from aca.state import DomainRun, Options, RunState
from aca.topics import Pair
from aca.validate import Rejected

if TYPE_CHECKING:
    from collections.abc import Mapping

    from aca.paths import Env

STATE_FILE = "state.json"


def _source_json(source: Source, snapshot: Snapshot | None) -> JsonObj:
    data: JsonObj = {
        "path": str(source.path),
        "display": source.display,
        "kind": source.kind,
        "scope": source.scope,
        "domain": source.domain,
        "owner": source.owner,
        "status": source.status,
        "reason": source.reason,
        "loaders": [asdict(loader) for loader in source.loaders],
        "aliases": source.aliases,
        "imported_by": source.imported_by,
        "subset": source.subset,
        "sid": source.sid,
        "sha256": source.sha256,
        "size": source.size,
        "lines": source.line_count,
        "symlink": source.symlink,
        "error": source.error,
        "loading": source.loading,
        "consumption": source.consumption,
        "availability": source.availability,
        "applicability": source.applicability,
    }
    if snapshot is not None and source.sid in snapshot.paths:
        data["snapshot"] = str(snapshot.paths[source.sid])
    return data


def _pair_json(pair: Pair) -> JsonObj:
    return {
        "left": list(pair.left),
        "right": list(pair.right),
        "score": pair.score,
        "topics": list(pair.shared_topics),
    }


def _checks_json(checks: Checks | None) -> JsonObj:
    if checks is None:
        return {}
    return {
        "candidates": [asdict(item) for item in checks.candidates],
        "pairs": [_pair_json(pair) for pair in checks.pairs],
    }


def _domain_json(run: DomainRun) -> JsonObj:
    return {
        "package": {
            "name": run.package.name,
            "domain": run.package.domain,
            "sids": run.package.sids,
            "chars": run.package.chars,
            "candidates": {cid: asdict(item) for cid, item in run.package.candidates.items()},
        },
        "status": run.status,
        "attempts": run.attempts,
        "error": run.error,
        "agent_id": run.agent_id,
        "gaps": run.gaps,
    }


def _knowledge_json(knowledge: knowledge_module.Knowledge | None) -> JsonObj:
    if knowledge is None:
        return {}
    return {
        "version": knowledge.version,
        "docs_checked": knowledge.docs_checked,
        "covers": knowledge.covers,
        "online": knowledge.online,
        "drift": knowledge.drift,
        "unreachable": knowledge.unreachable,
        "newer_versions": knowledge.newer_versions,
        "defaults": sorted(knowledge.defaults),
        "settings_keys_from": knowledge.settings_keys_from,
    }


def _outcome_json(outcome: Outcome) -> JsonObj:
    return {
        "proposals": {fid: asdict(item) for fid, item in outcome.proposals.items()},
        "pair_verdicts": {pid: list(verdict) for pid, verdict in outcome.pair_verdicts.items()},
        "groups": outcome.groups,
        "missing": outcome.missing,
        "positions": outcome.positions,
    }


def to_json(state: RunState) -> JsonObj:
    """Everything a later stage needs, as plain JSON."""
    found = state.inventory
    return {
        "schema": "agent-files-diagnostics/state/1",
        "options": asdict(state.options),
        "repo": str(state.repo),
        "report_root": str(state.report_root),
        "run_id": state.run_id,
        "run_dir": str(state.run_dir),
        "started": state.started,
        "stage": state.stage,
        "claude_version": state.claude_version,
        "work": str(state.work) if state.work else "",
        "git_before": asdict(state.git_before),
        "evidence": state.evidence,
        "knowledge": _knowledge_json(state.knowledge),
        "sources": [_source_json(source, state.snapshot) for source in found.sources]
        if found
        else [],
        "imports": [asdict(edge) for edge in found.imports] if found else [],
        "out_of_scope": found.out_of_scope if found else [],
        "files_truncated": found.files_truncated if found else False,
        "checks": _checks_json(state.checks),
        "domains": [_domain_json(run) for run in state.domains],
        "findings": [item.to_json() for item in state.findings],
        "claims": [claim.to_json() for claim in state.claims],
        "rejected": [asdict(item) for item in state.rejected],
        "verdicts": {cid: list(verdict) for cid, verdict in state.verdicts.items()},
        "outcome": _outcome_json(state.outcome),
        "reconciliation": state.reconciliation,
        "verification": state.verification,
        "independent": state.independent,
        "coordinator": state.coordinator,
        "usage": state.usage,
        "problems": state.problems,
        "failures": state.failures,
        "warnings": state.warnings,
        "writes": state.writes,
    }


def save(state: RunState) -> Path:
    """Write state.json into the run folder."""
    target = state.run_dir / STATE_FILE
    state.run_dir.mkdir(parents=True, exist_ok=True)
    write_atomic(target, dumps(to_json(state)))
    return target


# --- reading back ---------------------------------------------------------------------------


def _source_from(item: JsonObj) -> Source:
    source = Source(
        path=Path(get_str(item, "path")),
        display=get_str(item, "display"),
        kind=get_str(item, "kind"),
        scope=get_str(item, "scope"),
        domain=get_str(item, "domain"),
        owner=get_str(item, "owner"),
        status=get_str(item, "status"),
        reason=get_str(item, "reason"),
        aliases=str_list(item.get("aliases")),
        imported_by=str_list(item.get("imported_by")),
        subset=get_str(item, "subset"),
        sid=get_str(item, "sid"),
        sha256=get_str(item, "sha256"),
        size=get_int(item, "size"),
        symlink=get_str(item, "symlink"),
        error=get_str(item, "error"),
        loading=get_str(item, "loading"),
        consumption=get_str(item, "consumption"),
        availability=get_str(item, "availability"),
        applicability=get_str(item, "applicability"),
    )
    for raw in get_list(item, "loaders"):
        loader = as_obj(raw)
        source.loaders.append(
            Loader(get_str(loader, "tool"), get_str(loader, "mode"), get_str(loader, "reason"))
        )
    return source


def _snapshot_from(work: Path, sources: list[JsonObj]) -> Snapshot:
    snap = Snapshot(work=work)
    for item in sources:
        copy = get_str(item, "snapshot")
        if not copy:
            continue
        path = Path(copy)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        snap.paths[get_str(item, "sid")] = path
        snap.lines[get_str(item, "sid")] = (
            text.split("\n")[:-1] if text.endswith("\n") else (text.split("\n") if text else [])
        )
    return snap


def _candidate_from(item: JsonObj) -> Candidate:
    return Candidate(
        sid=get_str(item, "sid"),
        start=get_int(item, "line_start") or get_int(item, "start"),
        end=get_int(item, "line_end") or get_int(item, "end"),
        kind=get_str(item, "kind"),
        note=get_str(item, "note"),
        evidence=str_list(item.get("evidence")),
    )


def _pair_from(item: JsonObj) -> Pair:
    def place(value: object) -> tuple[str, int, int]:
        parts = as_list(value)
        return (str(parts[0]), int(str(parts[1])), int(str(parts[2])))

    return Pair(
        left=place(item.get("left")),
        right=place(item.get("right")),
        score=get_float(item, "score"),
        shared_topics=tuple(str_list(item.get("topics"))),
    )


def _checks_from(item: JsonObj) -> Checks:
    checks = Checks()
    checks.candidates = [_candidate_from(as_obj(raw)) for raw in get_list(item, "candidates")]
    checks.pairs = [_pair_from(as_obj(raw)) for raw in get_list(item, "pairs")]
    return checks


def _package_from(item: JsonObj) -> Package:
    package = Package(
        name=get_str(item, "name"),
        domain=get_str(item, "domain"),
        sids=str_list(item.get("sids")),
        chars=get_int(item, "chars"),
    )
    for cid, raw in get_obj(item, "candidates").items():
        package.candidates[cid] = _candidate_from(as_obj(raw))
    return package


def _domain_from(item: JsonObj) -> DomainRun:
    run = DomainRun(package=_package_from(get_obj(item, "package")))
    run.status = get_str(item, "status", "pending")
    run.attempts = get_int(item, "attempts")
    run.error = get_str(item, "error")
    run.agent_id = get_str(item, "agent_id")
    run.gaps = {sid: str(text) for sid, text in get_obj(item, "gaps").items()}
    return run


def finding_from(item: JsonObj) -> Finding:
    """A Finding from its to_json form."""
    finding = Finding(
        category=get_str(item, "category"),
        severity=get_str(item, "severity"),
        confidence=get_str(item, "confidence"),
        sid=get_str(item, "sid"),
        start=get_int(item, "start"),
        end=get_int(item, "end"),
        excerpt=get_str(item, "excerpt"),
        disposition=get_str(item, "disposition"),
        rationale=get_str(item, "rationale"),
        origin=get_str(item, "origin"),
        evidence=str_list(item.get("evidence")),
        ladder=get_str(item, "ladder", "n/a"),
        impact=str_list(item.get("impact")),
        target=get_str(item, "target"),
        replacement=get_str(item, "replacement"),
        topics=str_list(item.get("topics")),
        unit=get_str(item, "unit"),
        fid=get_str(item, "fid"),
        status=get_str(item, "status", "final"),
        trail=str_list(item.get("trail")),
        drift=get_bool(item, "drift"),
        verified=get_str(item, "verified"),
        coordinator_check=get_str(item, "coordinator_check"),
    )
    for raw in get_list(item, "conflicts_with"):
        entry = as_obj(raw)
        finding.conflicts_with.append(
            Conflict(get_str(entry, "kind"), get_str(entry, "ref"), get_str(entry, "detail"))
        )
    for raw in get_list(item, "related"):
        entry = as_obj(raw)
        finding.related.append(
            Location(get_str(entry, "sid"), get_int(entry, "start"), get_int(entry, "end"))
        )
    return finding


def claim_from(item: JsonObj) -> ExternalClaim:
    """An ExternalClaim from its to_json form."""
    claim = ExternalClaim(
        sid=get_str(item, "sid"),
        start=get_int(item, "start"),
        end=get_int(item, "end"),
        excerpt=get_str(item, "excerpt"),
        claim=get_str(item, "claim"),
        subject=get_str(item, "subject"),
        why=get_str(item, "why"),
        sources=str_list(item.get("sources")),
        impact_if_false=get_str(item, "impact_if_false"),
        unit=get_str(item, "unit"),
        cid=get_str(item, "cid"),
        verdict=get_str(item, "verdict", "unverified"),
    )
    claim.verdict_evidence = [
        {key: str(value) for key, value in as_obj(entry).items()}
        for entry in get_list(item, "verdict_evidence")
    ]
    return claim


def _outcome_from(item: JsonObj) -> Outcome:
    outcome = Outcome()
    for fid, raw in get_obj(item, "proposals").items():
        entry = as_obj(raw)
        outcome.proposals[fid] = Proposal(
            verdict=get_str(entry, "verdict"),
            disposition=get_str(entry, "disposition"),
            severity=get_str(entry, "severity"),
            reason=get_str(entry, "reason"),
            evidence=str_list(entry.get("evidence")),
        )
    for pid, raw in get_obj(item, "pair_verdicts").items():
        parts = str_list(raw)
        outcome.pair_verdicts[pid] = (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")
    outcome.groups = [as_obj(raw) for raw in get_list(item, "groups")]
    outcome.missing = str_list(item.get("missing"))
    outcome.positions = {fid: str_list(raw) for fid, raw in get_obj(item, "positions").items()}
    return outcome


def _knowledge_from(item: JsonObj) -> knowledge_module.Knowledge:
    knowledge = knowledge_module.Knowledge(
        version=get_str(item, "version"),
        docs_checked=get_str(item, "docs_checked"),
        covers={key: str(value) for key, value in get_obj(item, "covers").items()},
        online=get_bool(item, "online"),
        unreachable=str_list(item.get("unreachable")),
        newer_versions=str_list(item.get("newer_versions")),
        settings_keys_from=get_str(item, "settings_keys_from", "bundled"),
    )
    knowledge.drift = {url: str_list(raw) for url, raw in get_obj(item, "drift").items()}
    knowledge.defaults = frozenset(str_list(item.get("defaults")))
    return knowledge


def _options_from(item: JsonObj) -> Options:
    return Options(
        repo=get_str(item, "repo", "."),
        out=get_str(item, "out") or None,
        challenge_rounds=get_int(item, "challenge_rounds", 1),
        offline=get_bool(item, "offline"),
        keep_work=get_bool(item, "keep_work"),
    )


def _inventory_from(data: JsonObj, env: Env, snapshot: Snapshot) -> inventory_module.Inventory:
    found = inventory_module.Inventory(
        repo=Path(get_str(data, "repo")),
        env=env,
        report_root=Path(get_str(data, "report_root")),
        files_truncated=get_bool(data, "files_truncated"),
    )
    for raw in get_list(data, "sources"):
        source = _source_from(as_obj(raw))
        source.lines = snapshot.lines.get(source.sid, [])
        found.sources.append(source)
    found.out_of_scope = [dict(as_obj(raw)) for raw in get_list(data, "out_of_scope")]
    for raw in get_list(data, "imports"):
        edge = as_obj(raw)
        found.imports.append(
            ImportEdge(
                importer=get_str(edge, "importer"),
                line=get_int(edge, "line"),
                raw=get_str(edge, "raw"),
                target=get_str(edge, "target"),
                status=get_str(edge, "status"),
                resolved=get_str(edge, "resolved"),
            )
        )
    inventory_module.index_units(found)
    return found


def load(run_dir: Path, env: Env, environ: Mapping[str, str]) -> RunState:
    """Read a run back from its state.json."""
    data = as_obj(read_json(run_dir / STATE_FILE))
    work = Path(get_str(data, "work")) if get_str(data, "work") else None
    sources = [as_obj(raw) for raw in get_list(data, "sources")]
    snapshot = _snapshot_from(work, sources) if work else Snapshot(work=run_dir)
    git = get_obj(data, "git_before")
    state = RunState(
        options=_options_from(get_obj(data, "options")),
        env=env,
        repo=Path(get_str(data, "repo")),
        report_root=Path(get_str(data, "report_root")),
        run_id=get_str(data, "run_id"),
        run_dir=run_dir,
        started=get_str(data, "started"),
        stage=get_str(data, "stage"),
        claude_version=get_str(data, "claude_version"),
        work=work,
        git_before=GitState(
            available=get_bool(git, "available"),
            head=get_str(git, "head"),
            status=get_str(git, "status"),
        ),
        evidence=get_obj(data, "evidence"),
    )
    _ = environ
    state.snapshot = snapshot
    state.inventory = _inventory_from(data, env, snapshot)
    state.knowledge = _knowledge_from(get_obj(data, "knowledge"))
    state.checks = _checks_from(get_obj(data, "checks"))
    state.domains = [_domain_from(as_obj(raw)) for raw in get_list(data, "domains")]
    state.findings = [finding_from(as_obj(raw)) for raw in get_list(data, "findings")]
    state.claims = [claim_from(as_obj(raw)) for raw in get_list(data, "claims")]
    for raw in get_list(data, "rejected"):
        entry = as_obj(raw)
        state.rejected.append(
            Rejected(get_str(entry, "origin"), get_str(entry, "reason"), get_str(entry, "summary"))
        )
    for cid, raw in get_obj(data, "verdicts").items():
        parts = str_list(raw)
        state.verdicts[cid] = (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")
    state.outcome = _outcome_from(get_obj(data, "outcome"))
    state.reconciliation = get_str(data, "reconciliation", "not run")
    state.verification = get_str(data, "verification", "not run")
    state.independent = get_str(data, "independent", "not run")
    state.coordinator = get_str(data, "coordinator", "not run")
    state.usage = [as_obj(raw) for raw in get_list(data, "usage")]
    state.problems = str_list(data.get("problems"))
    state.failures = str_list(data.get("failures"))
    state.warnings = str_list(data.get("warnings"))
    state.writes = str_list(data.get("writes"))
    state.integrity = None
    _ = Integrity
    return state
