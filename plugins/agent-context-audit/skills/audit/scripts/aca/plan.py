"""Shards, read plans, task messages and per-run worker settings.

Sources are grouped by domain and packed into shards under a character budget; a file is never
split across shards. Each file gets explicit Read chunks (offset, limit) small enough for one
Read call, so full coverage never depends on how the model pages through a long file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca.jsonutil import JsonObj, dumps

if TYPE_CHECKING:
    from pathlib import Path

    from aca.checks import Candidate, Checks
    from aca.findings import Finding
    from aca.inventory import Inventory
    from aca.snapshot import Snapshot
    from aca.sources import Source

SHARD_CHARS = 120_000
CHUNK_CHARS = 50_000
CHUNK_LINES = 1_500
TURN_SLACK = 40
DOMAINS = {
    "D1": "Claude Code memory and rules (always-loaded and path-scoped instructions)",
    "D2": "Claude Code on-demand components (subagents, output styles, subagent memory, loop.md)",
    "D3": "Codex instructions (AGENTS.md chain, overrides, fallbacks, custom agents)",
    "D4": "Behavior-shaping configuration (settings, hooks, permissions, MCP, Codex config)",
}
SECRET_DENY = (
    "Read(**/.env)",
    "Read(**/.env.*)",
    "Read(**/*.pem)",
    "Read(**/*.key)",
    "Read(**/*.p12)",
    "Read(**/*.pfx)",
    "Read(**/*.kdbx)",
    "Read(**/*.tfstate)",
    "Read(**/terraform.tfvars)",
    "Read(**/id_rsa*)",
    "Read(**/id_dsa*)",
    "Read(**/id_ecdsa*)",
    "Read(**/id_ed25519*)",
    "Read(**/.npmrc)",
    "Read(**/.pypirc)",
    "Read(**/.netrc)",
    "Read(**/.git-credentials)",
    "Read(**/credentials)",
    "Read(**/credentials.*)",
)
VERIFIER_DOMAINS = (
    "github.com",
    "raw.githubusercontent.com",
    "api.github.com",
    "registry.npmjs.org",
    "www.npmjs.com",
    "pypi.org",
    "crates.io",
    "docs.rs",
    "pkg.go.dev",
    "rubygems.org",
    "packagist.org",
    "www.nuget.org",
    "code.claude.com",
    "platform.claude.com",
    "docs.anthropic.com",
    "developers.openai.com",
    "learn.chatgpt.com",
)


@dataclass
class Shard:
    """One auditor's assignment."""

    name: str
    domain: str
    sids: list[str] = field(default_factory=list)
    chars: int = 0
    candidates: dict[str, Candidate] = field(default_factory=dict)

    @property
    def allowed(self) -> frozenset[str]:
        """The sources this shard may report on."""
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


def make_shards(inventory: Inventory, snapshot: Snapshot, checks: Checks) -> list[Shard]:
    """Pack audited sources into shards per domain, never splitting a file."""
    shards: list[Shard] = []
    for domain in DOMAINS:
        current: Shard | None = None
        for source in inventory.audited:
            if source.domain != domain:
                continue
            size = sum(len(line) + 1 for line in snapshot.lines.get(source.sid, []))
            if current is None or (current.sids and current.chars + size > SHARD_CHARS):
                current = Shard(
                    name=f"{domain}-{sum(s.domain == domain for s in shards) + 1}", domain=domain
                )
                shards.append(current)
            current.sids.append(source.sid)
            current.chars += size
    for number, candidate in enumerate(checks.candidates, start=1):
        for shard in shards:
            if candidate.sid in shard.sids:
                shard.candidates[f"C{number:03d}"] = candidate
    return shards


def _loaders(source: Source) -> str:
    return "; ".join(f"{loader.tool}: {loader.mode} ({loader.reason})" for loader in source.loaders)


def _file_rows(shard: Shard, inventory: Inventory, snapshot: Snapshot) -> list[str]:
    rows = ["| ID | Original | Snapshot copy | Lines | Read chunks (offset, limit) | Loaded by |"]
    rows.append("| :-- | :-- | :-- | --: | :-- | :-- |")
    for sid in shard.sids:
        source = inventory.by_sid(sid)
        if source is None:
            continue
        plan = ", ".join(
            f"({offset}, {limit})" for offset, limit in chunks(snapshot.lines.get(sid, []))
        )
        subset = f" — subset: {source.subset}" if source.subset else ""
        cells = [
            sid,
            source.display + subset,
            str(snapshot.paths[sid]),
            str(source.line_count),
            plan,
            _loaders(source),
        ]
        rows.append("| " + " | ".join(cells) + " |")
    return rows


def _recorded(findings: list[Finding], shard: Shard) -> list[str]:
    lines = [
        f"- {item.sid}:{item.start}-{item.end} {item.category}: {item.rationale}"
        for item in findings
        if item.sid in shard.sids
    ]
    return lines or ["- (none)"]


def _candidate_rows(shard: Shard) -> list[str]:
    rows = [
        f"- {cid} {item.sid}:{item.start}-{item.end} [{item.kind}] {item.note}"
        + (f" (evidence: {'; '.join(item.evidence)})" if item.evidence else "")
        for cid, item in sorted(shard.candidates.items())
    ]
    return rows or ["- (none)"]


def auditor_prompt(shard: Shard, inventory: Inventory, snapshot: Snapshot, checks: Checks) -> str:
    """The task message for one domain auditor."""
    work = snapshot.work
    parts = [
        f"# Audit task {shard.name}: domain {shard.domain}",
        "",
        f"Domain: {DOMAINS[shard.domain]}.",
        f"Project root (your working directory): {inventory.repo}",
        f"Work folder: {work}",
        "",
        "## Files to audit: read every line, using exactly these chunks",
        "",
        *_file_rows(shard, inventory, snapshot),
        "",
        "## Deterministic findings already recorded (do not repeat them)",
        "",
        *_recorded(checks.findings, shard),
        "",
        "## Candidates to judge (confirm and report, or reject with a reason)",
        "",
        *_candidate_rows(shard),
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


def max_turns(shard: Shard, snapshot: Snapshot) -> int:
    """Turn cap: every planned read plus room for verification reads."""
    reads = sum(len(chunks(snapshot.lines.get(sid, []))) for sid in shard.sids)
    return reads * 2 + TURN_SLACK


def auditor_settings(inventory: Inventory, report_root: Path) -> JsonObj:
    """The --settings layer for every read-only worker."""
    deny = [*SECRET_DENY, f"Read(/{report_root.as_posix()}/**)"]
    deny.extend(
        f"Read(/{source.path.as_posix()})"
        for source in inventory.sources
        if source.path.is_absolute()
    )
    return {
        "permissions": {"deny": deny},
        "autoMemoryEnabled": False,
        "crossSessionInbound": "refuse",
        "disableAllHooks": True,
        "includeGitInstructions": False,
    }


def verifier_settings(extra_domains: list[str]) -> JsonObj:
    """The --settings layer for online verifiers: WebFetch only to the allowed domains."""
    domains = [*VERIFIER_DOMAINS, *extra_domains]
    return {
        "permissions": {"allow": [f"WebFetch(domain:{domain})" for domain in domains]},
        "autoMemoryEnabled": False,
        "crossSessionInbound": "refuse",
        "disableAllHooks": True,
        "includeGitInstructions": False,
    }


def manifest_json(inventory: Inventory, snapshot: Snapshot) -> str:
    """sources.json for the workers: every source, its loaders and its snapshot copy."""
    rows: list[JsonObj] = [
        {
            "sid": source.sid,
            "display": source.display,
            "kind": source.kind,
            "scope": source.scope,
            "domain": source.domain,
            "status": source.status,
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
