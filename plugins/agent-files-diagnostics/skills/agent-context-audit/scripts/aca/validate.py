"""Deterministic validation of everything a worker returns, before it can reach the report.

A finding survives only if it points at a real line range of an audited user-owned source, its
excerpt is really there, and every conflict it names resolves (a real file and line, an existing
repository path, an official docs URL, or an entry of the documented-defaults catalog). Rejected
items are kept with their reason and shown in the report; nothing is dropped silently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import TYPE_CHECKING, cast
from urllib.parse import urlsplit

from aca import paths
from aca.findings import (
    CATEGORIES,
    Conflict,
    ExternalClaim,
    Finding,
    Location,
)
from aca.jsonutil import JsonObj, as_obj, get_int, get_list, get_str, str_list
from aca.sources import IN_SCOPE

if TYPE_CHECKING:
    from collections.abc import Callable

    from aca.inventory import Inventory
    from aca.snapshot import Snapshot

WHITESPACE = re.compile(r"\s+")
FILE_LINE = re.compile(r"^(S\d{3})(?::(\d+)(?:-(\d+))?)?$")
PATH_TOKEN = re.compile(r"[A-Za-z0-9_.@~/-]+")
DOC_HOSTS = frozenset(
    {
        "code.claude.com",
        "docs.anthropic.com",
        "docs.claude.com",
        "platform.claude.com",
        "support.claude.com",
        "claude.com",
        "developers.openai.com",
        "learn.chatgpt.com",
        "agents.md",
        "agentskills.io",
    },
)
DEFAULT_ID = re.compile(r"^DEF-[A-Z0-9-]+$")
NEEDS_REPLACEMENT = frozenset({"revise", "merge"})


@dataclass
class Rejected:
    """A worker item that failed validation, and why."""

    origin: str
    reason: str
    summary: str


@dataclass
class Validated:
    """What survived validation from one worker output."""

    findings: list[Finding] = field(default_factory=list)
    claims: list[ExternalClaim] = field(default_factory=list)
    rejected: list[Rejected] = field(default_factory=list)
    verdicts: dict[str, tuple[str, str]] = field(default_factory=dict)


@dataclass
class Checker:
    """Validation context: what exists, what each worker may report on."""

    inventory: Inventory
    snapshot: Snapshot
    defaults: frozenset[str]
    allowed: frozenset[str]

    def lines(self, sid: str) -> list[str]:
        """The redacted lines of a source."""
        return self.snapshot.lines.get(sid, [])

    def range_ok(self, sid: str, start: int, end: int) -> bool:
        """True when start..end is a real line range of the source."""
        return 1 <= start <= end <= len(self.lines(sid))

    def excerpt_ok(self, sid: str, start: int, end: int, excerpt: str) -> bool:
        """True when the excerpt appears in those lines (whitespace collapsed)."""
        wanted = WHITESPACE.sub(" ", excerpt).strip().rstrip(".…")
        text = WHITESPACE.sub(" ", "\n".join(self.lines(sid)[start - 1 : end]))
        return bool(wanted) and wanted in text

    def resolve_sid(self, ref: str) -> str:
        """Turn S001, a display path or an alias into a manifest ID ('' when unknown)."""
        if FILE_LINE.match(ref):
            return ref.split(":", maxsplit=1)[0]
        for source in self.inventory.sources:
            if ref in {source.display, *source.aliases}:
                return source.sid
        return ""


def _file_line_error(checker: Checker, ref: str) -> str:
    match = FILE_LINE.match(ref)
    path, _, numbers = ref.rpartition(":")
    sid = match.group(1) if match else checker.resolve_sid(path or ref)
    if not sid:
        return f"file-line {ref!r} names no audited source"
    start = int(match.group(2)) if match and match.group(2) else _first_int(numbers)
    end = int(match.group(3)) if match and match.group(3) else start
    if start and not checker.range_ok(sid, start, end or start):
        return f"file-line {ref!r} points past the end of {sid}"
    return ""


def _repo_fact_error(checker: Checker, ref: str) -> str:
    repo = checker.inventory.repo
    for token in cast("list[str]", PATH_TOKEN.findall(ref)):
        candidate = Path(token)
        if candidate.is_absolute():
            if paths.in_directory(paths.resolve(candidate), repo) and candidate.exists():
                return ""
            continue
        relative = token.strip("/").removeprefix("./")
        if relative and (repo / relative).exists():
            return ""
    return f"repo fact {ref!r} names no existing path in the project"


def _doc_error(_checker: Checker, ref: str) -> str:
    parts = urlsplit(ref)
    host = parts.hostname or ""
    if parts.scheme == "https" and (host in DOC_HOSTS or host.endswith(".claude.com")):
        return ""
    return f"doc {ref!r} is not an official Claude Code or Codex docs URL"


def _default_error(checker: Checker, ref: str) -> str:
    return "" if ref in checker.defaults else f"default {ref!r} is not in the defaults catalog"


CONFLICT_CHECKS: dict[str, Callable[[Checker, str], str]] = {
    "file-line": _file_line_error,
    "repo-fact": _repo_fact_error,
    "doc": _doc_error,
    "default": _default_error,
}


def _conflict_error(checker: Checker, conflict: Conflict) -> str:
    """'' when the conflict resolves, else why not."""
    check = CONFLICT_CHECKS.get(conflict.kind)
    if check is None:
        return "every finding must name what it conflicts with"
    return check(checker, conflict.ref.strip())


def _first_int(text: str) -> int:
    match = re.match(r"\d+", text)
    return int(match.group(0)) if match else 0


def _conflicts(item: JsonObj) -> list[Conflict]:
    found: list[Conflict] = []
    for raw in get_list(item, "conflicts_with"):
        entry = as_obj(raw)
        ref = get_str(entry, "ref").strip().strip("<>")
        found.append(Conflict(get_str(entry, "kind"), ref, get_str(entry, "detail")))
    return found


def _related(item: JsonObj) -> list[Location]:
    found: list[Location] = []
    for raw in get_list(item, "related"):
        entry = as_obj(raw)
        start, end = get_int(entry, "line_start"), get_int(entry, "line_end")
        found.append(Location(get_str(entry, "sid"), start, end))
    return found


def _build(item: JsonObj, origin: str) -> Finding:
    return Finding(
        category=get_str(item, "category"),
        severity=get_str(item, "severity"),
        confidence=get_str(item, "confidence"),
        sid=get_str(item, "sid"),
        start=get_int(item, "line_start"),
        end=get_int(item, "line_end"),
        excerpt=get_str(item, "excerpt"),
        disposition=get_str(item, "disposition"),
        rationale=get_str(item, "rationale"),
        origin=origin,
        evidence=str_list(item.get("evidence")),
        conflicts_with=_conflicts(item),
        related=_related(item),
        ladder=get_str(item, "ladder", "n/a"),
        impact=str_list(item.get("impact")),
        target=get_str(item, "target"),
        replacement=get_str(item, "replacement"),
        topics=str_list(item.get("topics")),
    )


def _location_error(checker: Checker, finding: Finding) -> str:
    source = checker.inventory.by_sid(finding.sid)
    if source is None or source.status != IN_SCOPE:
        return f"{finding.sid} is not an audited user-owned source"
    if finding.sid not in checker.allowed:
        return f"{finding.sid} was not assigned to this worker"
    if not checker.range_ok(finding.sid, finding.start, finding.end):
        return f"lines {finding.start}-{finding.end} do not exist in {finding.sid}"
    if not checker.excerpt_ok(finding.sid, finding.start, finding.end, finding.excerpt):
        return "the excerpt does not appear in those lines"
    return ""


def _normalize(finding: Finding) -> None:
    """Apply the evidence-ladder and replacement rules, recording each change in the trail."""
    if finding.ladder == "c" and (finding.confidence != "low" or finding.disposition == "remove"):
        finding.confidence = "low"
        if finding.disposition == "remove":
            finding.disposition = "investigate"
        finding.trail.append("validator: ladder (c) is judgment only: low confidence, no removal")
    if finding.disposition in NEEDS_REPLACEMENT and not finding.replacement.strip():
        note = f"validator: {finding.disposition} had no replacement text, so investigate"
        finding.trail.append(note)
        finding.disposition = "investigate"


def check_finding(checker: Checker, item: JsonObj, origin: str) -> tuple[Finding | None, str]:
    """Validate one finding object; returns (finding, '') or (None, reason)."""
    finding = _build(item, origin)
    if finding.category not in CATEGORIES:
        return None, f"unknown category {finding.category!r}"
    error = _location_error(checker, finding)
    if not error and finding.category == "redundant-with-defaults" and finding.ladder == "n/a":
        error = "a redundant-with-defaults finding needs an evidence ladder level"
    if not error:
        live = [conflict for conflict in finding.conflicts_with if conflict.kind != "none"]
        errors = [_conflict_error(checker, conflict) for conflict in live] or ["no conflict named"]
        error = next((text for text in errors if text), "")
    if error:
        return None, error
    _normalize(finding)
    return finding, ""


def check_claim(checker: Checker, item: JsonObj) -> tuple[ExternalClaim | None, str]:
    """Validate one external claim."""
    claim = ExternalClaim(
        sid=get_str(item, "sid"),
        start=get_int(item, "line_start"),
        end=get_int(item, "line_end"),
        excerpt=get_str(item, "excerpt"),
        claim=get_str(item, "claim"),
        subject=get_str(item, "subject"),
        why=get_str(item, "why"),
        sources=str_list(item.get("sources")),
        impact_if_false=get_str(item, "impact_if_false"),
    )
    probe = Finding(
        "ambiguous",
        "low",
        "low",
        claim.sid,
        claim.start,
        claim.end,
        claim.excerpt,
        "investigate",
        "",
        "",
    )
    error = _location_error(checker, probe)
    return (None, error) if error else (claim, "")


def summarize(item: JsonObj) -> str:
    """A short label of a rejected item for the report."""
    where = f"{get_str(item, 'sid')}:{get_int(item, 'line_start')}"
    text = get_str(item, "rationale") or get_str(item, "claim") or get_str(item, "excerpt")
    return f"{where} {get_str(item, 'category')} — {text[:160]}".strip()


def auditor_output(checker: Checker, output: JsonObj, origin: str) -> Validated:
    """Validate an auditor's findings, external claims and candidate verdicts."""
    result = Validated()
    for raw in get_list(output, "findings"):
        item = as_obj(raw)
        finding, reason = check_finding(checker, item, origin)
        if finding is None:
            result.rejected.append(Rejected(origin, reason, summarize(item)))
        else:
            result.findings.append(finding)
    for raw in get_list(output, "external_claims"):
        item = as_obj(raw)
        claim, reason = check_claim(checker, item)
        if claim is None:
            result.rejected.append(Rejected(origin, reason, summarize(item)))
        else:
            result.claims.append(claim)
    for raw in get_list(output, "candidates"):
        item = as_obj(raw)
        result.verdicts[get_str(item, "id")] = (get_str(item, "verdict"), get_str(item, "reason"))
    return result


def claimed_files(output: JsonObj) -> dict[str, str]:
    """Sid -> status the worker claims for each assigned file."""
    claimed: dict[str, str] = {}
    for raw in get_list(output, "files"):
        entry = as_obj(raw)
        claimed[get_str(entry, "sid")] = get_str(entry, "status")
    return claimed
