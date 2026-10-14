"""Build the source manifest: every file Claude Code and Codex load, accounted for."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca import claude_config, claude_sources, codex_sources, units, walk
from aca.claude_sources import CLAUDE, Context, Found, Place
from aca.sources import (
    ALWAYS,
    CONFIG,
    EVIDENCE,
    EXCLUDED,
    IN_SCOPE,
    UNREADABLE,
    Source,
    load_text,
)

if TYPE_CHECKING:
    from pathlib import Path

    from aca.claude_sources import ClaudeFacts, ImportEdge
    from aca.codex_sources import CodexFacts
    from aca.markdown import Unit
    from aca.paths import Env

SKIPPED = "skipped"
DOMAIN_ORDER = {"D1": 0, "D2": 1, "D3": 2, "D4": 3, "evidence": 4}
MAX_AUDITED_CHARS = 600_000
MANAGED_FILES = (
    ("CLAUDE.md", "managed-claude-md", ALWAYS),
    ("managed-settings.json", "managed-settings", CONFIG),
)


@dataclass
class Inventory:
    """The manifest and the facts that explain it."""

    repo: Path
    env: Env
    report_root: Path
    sources: list[Source] = field(default_factory=list)
    out_of_scope: list[dict[str, object]] = field(default_factory=list)
    imports: list[ImportEdge] = field(default_factory=list)
    claude: ClaudeFacts | None = None
    codex: CodexFacts | None = None
    files: list[str] = field(default_factory=list)
    files_truncated: bool = False
    units: dict[str, list[Unit]] = field(default_factory=dict)
    unit_ids: dict[str, list[str]] = field(default_factory=dict)

    def by_sid(self, sid: str) -> Source | None:
        """Find a source by its manifest ID."""
        return next((source for source in self.sources if source.sid == sid), None)

    @property
    def audited(self) -> list[Source]:
        """Sources the auditors read: user-owned, readable and not skipped."""
        return [source for source in self.sources if source.status == IN_SCOPE]


def _managed(context: Context) -> None:
    folder = context.env.managed_dir
    if folder is None:
        return
    for name, kind, mode in MANAGED_FILES:
        path = folder / name
        if not path.is_file():
            continue
        source = claude_sources.add(
            context, path, Place(kind, "managed", "evidence"), (mode, "managed policy")
        )
        source.owner = "managed"


def _status(source: Source) -> None:
    if source.owner == "managed":
        source.status = EVIDENCE
        source.reason = "managed policy: cited as evidence, never reported or changed"
    elif source.status == UNREADABLE:
        source.reason = f"could not be read: {source.error}"
    elif source.loaders and all(loader.mode == EXCLUDED for loader in source.loaders):
        source.status = SKIPPED
        source.reason = "excluded by claudeMdExcludes and loaded by no other tool"
    elif len(source.text) > MAX_AUDITED_CHARS:
        source.status = SKIPPED
        source.reason = f"{source.size} bytes: too large for a full semantic read in one pass"


def _finalize(sources: list[Source]) -> list[Source]:
    for source in sources:
        if not source.sha256 and source.status != UNREADABLE:
            load_text(source)
        _status(source)
    ordered = sorted(
        sources, key=lambda item: (DOMAIN_ORDER.get(item.domain, len(DOMAIN_ORDER)), item.display)
    )
    for index, source in enumerate(ordered, start=1):
        source.sid = f"S{index:03d}"
    return ordered


def build(repo: Path, env: Env, report_root: Path) -> Inventory:
    """Discover, load and classify every source for the project at repo."""
    claude = claude_sources.collect_facts(env, repo)
    codex = codex_sources.collect_facts(env.codex_home, repo)
    names = set(claude_sources.NESTED_NAMES) | set(codex.candidates)
    tree = walk.walk_project(repo, names, [report_root])
    context = Context(env=env, repo=repo, tree=tree, found=Found(), facts=claude)
    _managed(context)
    claude_sources.memory_chain(context)
    claude_sources.agents_md(context)
    claude_sources.rules(context)
    claude_sources.nested(context)
    claude_sources.auto_memory(context)
    claude_config.discover(context)
    codex_sources.discover(context, codex)
    claude_sources.imports(context)
    inventory = Inventory(
        repo=repo,
        env=env,
        report_root=report_root,
        sources=_finalize(list(context.found.by_real.values())),
        out_of_scope=context.found.out_of_scope,
        imports=context.found.imports,
        claude=claude,
        codex=codex,
        files=tree.files,
        files_truncated=tree.truncated,
    )
    for source in inventory.sources:
        found = units.units_for(source) if source.lines else []
        inventory.units[source.sid] = found
        inventory.unit_ids[source.sid] = units.unit_ids(source.display, found)
    return inventory


def loaded_by(source: Source, tool: str = CLAUDE) -> bool:
    """True when the tool loads the source in some situation."""
    return any(loader.tool == tool for loader in source.loaders) and source.is_live
