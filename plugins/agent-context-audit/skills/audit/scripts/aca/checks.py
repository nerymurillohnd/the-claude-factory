"""Deterministic findings (mechanical facts) and candidates the auditors must confirm or reject.

A finding here is never a judgment: a missing import target, a rule whose paths match nothing, a
file cut by a size limit, an exact duplicate. Anything that needs meaning (a path in prose, a
script name in a sentence, two similar sentences) becomes a candidate instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from typing import TYPE_CHECKING

from aca import markdown, topics
from aca.findings import Conflict, Finding, Location
from aca.inventory import loaded_by
from aca.jsonutil import as_list, as_obj, get_list, get_obj, str_list
from aca.sources import (
    DEAD,
    IN_SCOPE,
    LIVE_MODES,
    MARKDOWN_KINDS,
    NOT_LOADED,
    SHADOWED,
    TRUNCATED,
)

if TYPE_CHECKING:
    from aca.inventory import Inventory
    from aca.jsonutil import JsonObj
    from aca.snapshot import Snapshot
    from aca.sources import Loader, Source

MEMORY_DOCS = "https://code.claude.com/docs/en/memory"
CODEX_DOCS = "https://developers.openai.com/codex/guides/agents-md"
CLAUDE_MD_TARGET_LINES = 200
CLAUDE_MD_LIMIT_BYTES = 4 * 1024 * 1024
MEMORY_INDEX_LINES = 200
MEMORY_INDEX_BYTES = 25 * 1024
MIN_DUPLICATE_CHARS = 24
MIN_GROUP = 2
EXCERPT_LINES = 6
PROSE_KINDS = frozenset({"item", "paragraph", "table-row", "quote"})
TOOL_NAMES = {"claude": "Claude Code", "codex": "Codex"}
OWN_CONTEXT_KINDS = frozenset({"subagent", "codex-agent-config"})
HIERARCHY_KINDS = frozenset({"claude-md", "claude-local-md", "managed-claude-md", "import"})
CLAUDE_MD_KINDS = frozenset({"claude-md", "claude-local-md"})
KEEP_RANK = {"managed": 0, "project": 1, "ancestor": 1, "nested": 2, "user": 3, "local": 4}
CODE_PATH = re.compile(r"`([^`\s]+)`")
PATHISH = re.compile(
    r"^(?:\./)?[A-Za-z0-9_.@-]+(?:/[A-Za-z0-9_.@*-]+)+/?$|^[A-Za-z0-9_-]+\.[A-Za-z]{1,6}$",
)
SCRIPT_RUN = re.compile(r"\b(npm|pnpm|yarn|bun)\s+(?:run\s+)?([A-Za-z0-9:_-]+)")
MAKE_RUN = re.compile(r"\b(make|just)\s+([A-Za-z0-9_.-]+)")
DIRECTIVE = re.compile(r"\b(always|never|must|do not|don't|use|run|prefer|avoid)\b", re.IGNORECASE)
RULE_KEYS = frozenset({"paths"})
PACKAGE_BUILTINS = frozenset(
    {
        "add",
        "ci",
        "create",
        "dlx",
        "exec",
        "i",
        "init",
        "install",
        "publish",
        "remove",
        "update",
        "x",
    },
)
PATH_SCOPES = frozenset({"project", "local", "nested", "ancestor"})


@dataclass
class Candidate:
    """Something the script noticed that only a reader can confirm."""

    sid: str
    start: int
    end: int
    kind: str
    note: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class Checks:
    """Everything the deterministic layer produced."""

    findings: list[Finding] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    pairs: list[topics.Pair] = field(default_factory=list)


@dataclass
class Context:
    """Inputs every check reads."""

    inventory: Inventory
    snapshot: Snapshot
    evidence: JsonObj
    out: Checks = field(default_factory=Checks)

    def excerpt(self, sid: str, start: int, end: int) -> str:
        """The redacted text of a line range, capped for display."""
        lines = self.snapshot.lines.get(sid, [])
        last = min(end, start + EXCERPT_LINES - 1)
        return "\n".join(lines[start - 1 : last])

    def unit(self, sid: str, line: int) -> str:
        """The ID of the unit covering line, or a hash of that line when no unit does."""
        found = self.inventory.units.get(sid, [])
        ids = self.inventory.unit_ids.get(sid, [])
        for index, unit in enumerate(found):
            if unit.start <= line <= unit.end and index < len(ids):
                return ids[index]
        source = self.inventory.by_sid(sid)
        text = self.excerpt(sid, line, line)
        display = source.display if source else sid
        return hashlib.sha256(f"{display}\0{text}".encode()).hexdigest()[:10]

    def add(self, finding: Finding) -> None:
        """Record a finding, filling its excerpt and unit."""
        if not finding.excerpt:
            finding.excerpt = self.excerpt(finding.sid, finding.start, finding.end)
        finding.unit = finding.unit or self.unit(finding.sid, finding.start)
        self.out.findings.append(finding)

    def candidate(self, where: tuple[str, int, int], kind: str, note: str) -> Candidate:
        """Record a candidate and return it, so callers can attach evidence."""
        sid, start, end = where
        item = Candidate(sid, start, end, kind, note)
        self.out.candidates.append(item)
        return item


def fact(
    category: str, severity: str, where: tuple[str, int, int], text: tuple[str, str]
) -> Finding:
    """A deterministic finding: high confidence, mechanical evidence."""
    sid, start, end = where
    rationale, disposition = text
    return Finding(
        category=category,
        severity=severity,
        confidence="high",
        sid=sid,
        start=start,
        end=end,
        excerpt="",
        disposition=disposition,
        rationale=rationale,
        origin="deterministic",
    )


def check_imports(ctx: Context) -> None:
    """Imports that never load: missing targets, quoted paths, too many hops."""
    by_display = {source.display: source for source in ctx.inventory.sources}
    messages = {
        "missing": ("the import target does not exist, so nothing is loaded", "revise"),
        "quoted": ("Claude Code does not import a path written in quotes", "revise"),
        "too-deep": ("the import is beyond the four-hop limit, so it never loads", "move"),
    }
    for edge in ctx.inventory.imports:
        source = by_display.get(edge.importer)
        if source is None or edge.status not in messages or source.status != IN_SCOPE:
            continue
        finding = fact("dead", "medium", (source.sid, edge.line, edge.line), messages[edge.status])
        finding.evidence = [f"{edge.raw} resolves to {edge.resolved} ({edge.status})"]
        finding.conflicts_with = [Conflict("doc", f"{MEMORY_DOCS}#import-additional-files")]
        finding.impact = ["correctness"]
        ctx.add(finding)


def _frontmatter_span(source: Source) -> tuple[int, int]:
    front = markdown.find_frontmatter(source.lines)
    return (front.start, front.end) if front else (1, 1)


def _truncation_line(source: Source, tool: str) -> int:
    """First line past the load limit (the auto memory index limits, or Codex's byte budget)."""
    limit_lines, limit_bytes = MEMORY_INDEX_LINES, MEMORY_INDEX_BYTES
    if tool == "codex":
        limit_lines, limit_bytes = source.line_count, CLAUDE_MD_LIMIT_BYTES
    total = 0
    for number, line in enumerate(source.lines, start=1):
        total += len(line.encode("utf-8")) + 1
        if number > limit_lines or total > limit_bytes:
            return number
    return max(source.line_count, 1)


def _loader_finding(source: Source, loader: Loader) -> Finding | None:
    sid, count = source.sid, max(source.line_count, 1)
    if loader.mode == DEAD:
        start, end = _frontmatter_span(source)
        return fact("dead", "medium", (sid, start, end), (loader.reason, "revise"))
    if loader.mode == SHADOWED:
        why = f"never loads: {loader.reason}"
        return fact("dead", "low", (sid, 1, count), (why, "investigate"))
    if loader.mode == TRUNCATED:
        start = _truncation_line(source, loader.tool)
        return fact("dead", "high", (sid, start, count), (loader.reason, "move"))
    if loader.mode == NOT_LOADED and source.kind == "agents-md" and not source.is_live:
        why = f"no tool here reads it: {loader.reason}"
        return fact("dead", "medium", (sid, 1, count), (why, "investigate"))
    return None


def check_loaders(ctx: Context) -> None:
    """Files that are dead, shadowed or cut short according to the loading rules."""
    for source in ctx.inventory.audited:
        for loader in source.loaders:
            finding = _loader_finding(source, loader)
            if finding is None:
                continue
            docs = MEMORY_DOCS if loader.tool == "claude" else CODEX_DOCS
            finding.evidence = [f"{loader.tool}: {loader.mode} — {loader.reason}"]
            finding.conflicts_with = [Conflict("doc", docs)]
            finding.impact = ["correctness", "context-cost"]
            ctx.add(finding)


def check_rule_frontmatter(ctx: Context) -> None:
    """Rule frontmatter that fails to parse, or keys Claude Code ignores."""
    for source in ctx.inventory.audited:
        front = markdown.find_frontmatter(source.lines) if source.kind == "rule" else None
        if front is None:
            continue
        where = (source.sid, front.start, front.end)
        unknown = sorted(set(front.data) - RULE_KEYS)
        if front.error:
            why = f"the frontmatter does not parse ({front.error}): the rule loads without paths"
            finding = fact("wrong", "high", where, (why, "revise"))
        elif unknown:
            why = f"Claude Code reads only `paths` from rule frontmatter; {unknown} are ignored"
            finding = fact("non-conformant", "low", where, (why, "revise"))
        else:
            continue
        finding.conflicts_with = [Conflict("doc", f"{MEMORY_DOCS}#rules-frontmatter-reference")]
        finding.ladder = "b"
        finding.impact = ["correctness"]
        ctx.add(finding)


def check_sizes(ctx: Context) -> None:
    """CLAUDE.md files over the documented size limit or the recommended length."""
    for source in ctx.inventory.audited:
        if source.kind not in {"claude-md", "claude-local-md"}:
            continue
        count = max(source.line_count, 1)
        if source.size > CLAUDE_MD_LIMIT_BYTES:
            why = "over 4 MiB: Claude Code skips the whole file"
            finding = fact("dead", "high", (source.sid, 1, count), (why, "move"))
        elif source.line_count > CLAUDE_MD_TARGET_LINES and loaded_by(source):
            why = f"{source.line_count} lines; the docs target under 200 lines per CLAUDE.md"
            finding = fact("non-conformant", "low", (source.sid, 1, count), (why, "revise"))
            finding.ladder = "b"
        else:
            continue
        finding.conflicts_with = [Conflict("doc", f"{MEMORY_DOCS}#write-effective-instructions")]
        finding.impact = ["context-cost"]
        ctx.add(finding)


def prose_units(ctx: Context) -> list[tuple[str, int, int, str]]:
    """Every prose unit (item, paragraph, table row, quote) of a loaded Markdown source."""
    items: list[tuple[str, int, int, str]] = []
    for source in ctx.inventory.audited:
        if source.kind not in MARKDOWN_KINDS or not source.is_live:
            continue
        lines = ctx.snapshot.lines.get(source.sid, [])
        for unit in ctx.inventory.units.get(source.sid, []):
            if unit.kind in PROSE_KINDS:
                text = "\n".join(lines[unit.start - 1 : unit.end])
                items.append((source.sid, unit.start, unit.end, text))
    return items


def _session_tools(source: Source) -> set[str]:
    """Tools that load the source into their main session (a subagent has its own context)."""
    if source.kind in OWN_CONTEXT_KINDS:
        return set()
    return {loader.tool for loader in source.loaders if loader.mode in LIVE_MODES}


def _reads_hierarchy(agent: Source) -> bool:
    """True when a subagent starts with the CLAUDE.md hierarchy (omitClaudeMd not set)."""
    front = markdown.find_frontmatter(agent.lines)
    return not (front is not None and front.data.get("omitClaudeMd") is True)


def shared_context(first: Source, other: Source) -> str:
    """The tool that loads both sources into one context, or '' when they load separately."""
    shared = sorted(_session_tools(first) & _session_tools(other))
    if shared:
        return shared[0]
    for agent, base in ((first, other), (other, first)):
        if agent.kind != "subagent" or base.kind not in HIERARCHY_KINDS:
            continue
        if "claude" in _session_tools(base) and _reads_hierarchy(agent):
            return "claude"
    return ""


def _agents_pair(first: Source, other: Source) -> bool:
    """True for an AGENTS.md and a CLAUDE.md, the pair an @AGENTS.md import joins."""
    kinds = (first.kind, other.kind)
    return "agents-md" in kinds and any(kind in CLAUDE_MD_KINDS for kind in kinds)


def _keep_order(ctx: Context, place: tuple[str, int, int]) -> tuple[int, str, int]:
    """Shared files first, personal ones last: the copy to keep sorts first."""
    source = ctx.inventory.by_sid(place[0])
    rank = KEEP_RANK.get(source.scope, len(KEEP_RANK)) if source else len(KEEP_RANK)
    return (rank, place[0], place[1])


Place = tuple[str, int, int]


def _duplicate(ctx: Context, keep: Source, other: Source, where: Place) -> Finding:
    tool = shared_context(keep, other)
    if tool:
        why = f"the same instruction is loaded twice into one {TOOL_NAMES[tool]} context"
        finding = fact("duplicated", "medium", where, (why, "remove"))
        finding.impact = ["context-cost", "maintenance"]
        return finding
    if _agents_pair(keep, other):
        why = (
            f"the same instruction is kept in {other.display} and {keep.display}; Codex reads"
            " only AGENTS.md, so keep that copy and import it into CLAUDE.md with @AGENTS.md"
        )
        finding = fact("duplicated", "low", where, (why, "revise"))
        finding.replacement = "@AGENTS.md (once in this file, in place of the copied lines)"
    else:
        why = (
            f"the same instruction is kept in {other.display} and {keep.display}, which load"
            " separately, so the two copies can drift apart"
        )
        finding = fact("duplicated", "low", where, (why, "merge"))
        finding.target = keep.display
        finding.replacement = ctx.excerpt(*where)
    finding.impact = ["maintenance"]
    return finding


def _pairs(ctx: Context, places: list[Place]) -> list[tuple[Place, Place]]:
    """(copy to keep, copy to change) for each repeat; AGENTS.md is kept over a CLAUDE.md."""
    first, *rest = sorted(places, key=lambda place: _keep_order(ctx, place))
    found: list[tuple[Place, Place]] = []
    for where in rest:
        keep, change = first, where
        kept, changed = ctx.inventory.by_sid(keep[0]), ctx.inventory.by_sid(change[0])
        if kept and changed and _agents_pair(kept, changed) and changed.kind == "agents-md":
            keep, change = change, keep
        found.append((keep, change))
    return found


def check_duplicates(ctx: Context, items: list[tuple[str, int, int, str]]) -> None:
    """Exact duplicates (same words after whitespace and list markers) in loaded files."""
    groups: dict[str, list[Place]] = {}
    for sid, start, end, text in items:
        key = markdown.normalize(text).lower()
        if len(key) >= MIN_DUPLICATE_CHARS:
            groups.setdefault(key, []).append((sid, start, end))
    for places in groups.values():
        if len(places) < MIN_GROUP:
            continue
        for keep, change in _pairs(ctx, places):
            kept, other = ctx.inventory.by_sid(keep[0]), ctx.inventory.by_sid(change[0])
            if kept is None or other is None:
                continue
            finding = _duplicate(ctx, kept, other, change)
            finding.related = [Location(*keep)]
            conflicts = [Conflict("file-line", f"{keep[0]}:{keep[1]}-{keep[2]}")]
            if _agents_pair(kept, other):
                conflicts.append(Conflict("doc", f"{MEMORY_DOCS}#agents-md"))
            finding.conflicts_with = conflicts
            ctx.add(finding)


def _code_paths(ctx: Context, source: Source) -> None:
    for number, line in enumerate(ctx.snapshot.lines.get(source.sid, []), start=1):
        for match in CODE_PATH.finditer(line):
            token = match.group(1).rstrip("/")
            if not PATHISH.match(token) or any(char in token for char in "*?{<$"):
                continue
            if (ctx.inventory.repo / token).exists() or (source.path.parent / token).exists():
                continue
            note = f"`{token}` reads like a project path but no such file or folder exists"
            _ = ctx.candidate((source.sid, number, number), "missing-path", note)


def script_names(evidence: JsonObj) -> set[str]:
    """Every package script name in the repository."""
    names: set[str] = set()
    for package in get_list(evidence, "packages"):
        names.update(get_obj(as_obj(package), "scripts"))
    return names


def target_names(evidence: JsonObj) -> set[str]:
    """Every make and just target in the repository."""
    found: set[str] = set()
    for names in get_obj(evidence, "make_and_just_targets").values():
        found.update(str_list(as_list(names)))
    return found


def _commands(ctx: Context, source: Source, scripts: set[str], targets: set[str]) -> None:
    for number, line in enumerate(ctx.snapshot.lines.get(source.sid, []), start=1):
        where = (source.sid, number, number)
        for match in SCRIPT_RUN.finditer(line):
            name = match.group(2)
            if scripts and name not in scripts and name not in PACKAGE_BUILTINS:
                note = f"`{match.group(0)}`: no package script named {name}"
                item = ctx.candidate(where, "missing-script", note)
                item.evidence = [f"package scripts: {sorted(scripts)}"]
        for match in MAKE_RUN.finditer(line):
            tool, name = match.group(1), match.group(2)
            if targets and name not in targets:
                note = f"`{tool} {name}`: no {tool} target named {name}"
                _ = ctx.candidate(where, "missing-target", note)


def check_candidates(ctx: Context) -> None:
    """Paths, scripts and targets named in prose, and instructions hidden in comments."""
    scripts, targets = script_names(ctx.evidence), target_names(ctx.evidence)
    note = "an instruction inside a block comment, which Claude Code strips before loading"
    for source in ctx.inventory.audited:
        if source.kind not in MARKDOWN_KINDS:
            continue
        if source.scope in PATH_SCOPES:
            _code_paths(ctx, source)
        _commands(ctx, source, scripts, targets)
        for unit in markdown.block_comments(ctx.snapshot.lines.get(source.sid, [])):
            if DIRECTIVE.search(unit.text) and loaded_by(source):
                _ = ctx.candidate((source.sid, unit.start, unit.end), "stripped-comment", note)


def run(
    inventory: Inventory,
    snapshot: Snapshot,
    evidence: JsonObj,
    taxonomy: dict[str, list[str]],
) -> Checks:
    """Run every deterministic check and collect candidate pairs for semantic comparison."""
    ctx = Context(inventory=inventory, snapshot=snapshot, evidence=evidence)
    check_imports(ctx)
    check_loaders(ctx)
    check_rule_frontmatter(ctx)
    check_sizes(ctx)
    items = prose_units(ctx)
    check_duplicates(ctx, items)
    check_candidates(ctx)
    ctx.out.pairs = topics.candidate_pairs(items, taxonomy)
    return ctx.out
