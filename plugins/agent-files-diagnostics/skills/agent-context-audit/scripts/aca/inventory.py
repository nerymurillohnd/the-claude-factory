"""Build the source manifest: every file Claude Code and Codex load, accounted for.

Markdown instruction and memory files are audited. Configuration files (settings, MCP, hooks,
Codex config and rules) are discovered too, because they decide what loads, but they are kept
as evidence only: consulted, hashed, never reviewed and never reported on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca import claude_config, claude_sources, codex_sources, units, walk
from aca.claude_sources import CLAUDE, Context, Found, Place
from aca.sources import (
    ALWAYS,
    CONFIG,
    DOMAIN_B,
    DOMAIN_EVIDENCE,
    DOMAIN_ORDER,
    EVIDENCE,
    EXCLUDED,
    IN_SCOPE,
    KIND_DOMAINS,
    UNREADABLE,
    Source,
    classify,
    load_text,
)

if TYPE_CHECKING:
    from pathlib import Path

    from aca.claude_sources import ClaudeFacts, ImportEdge
    from aca.codex_sources import CodexFacts
    from aca.markdown import Unit
    from aca.paths import Env

SKIPPED = "skipped"
MAX_AUDITED_CHARS = 600_000
MANAGED_FILES = (
    ("CLAUDE.md", "managed-claude-md", ALWAYS),
    ("managed-settings.json", "managed-settings", CONFIG),
)
CONFIG_REASON = "configuration: consulted to learn what loads, never audited"


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
    text_ids: dict[str, list[str]] = field(default_factory=dict)

    def by_sid(self, sid: str) -> Source | None:
        """Find a source by its manifest ID."""
        return next((source for source in self.sources if source.sid == sid), None)

    @property
    def audited(self) -> list[Source]:
        """Sources the auditors read: user-owned Markdown, readable and not skipped."""
        return [source for source in self.sources if source.status == IN_SCOPE]


# Installed third-party code: its instruction files load, but the user can't change them.
VENDORED_DIRS = frozenset(
    {"node_modules", "bower_components", "vendor", ".venv", "venv", "site-packages", "Pods"},
)


def _managed(context: Context) -> None:
    folder = context.env.managed_dir
    if folder is None:
        return
    for name, kind, mode in MANAGED_FILES:
        path = folder / name
        if not path.is_file():
            continue
        source = claude_sources.add(
            context, path, Place(kind, "managed", DOMAIN_EVIDENCE), (mode, "managed policy")
        )
        source.owner = "managed"


def _vendored(source: Source, repo: Path) -> str:
    """The third-party folder (node_modules, vendor...) a project file sits in, or ''."""
    try:
        parts = source.path.relative_to(repo).parts
    except ValueError:
        return ""
    return next((part for part in parts[:-1] if part in VENDORED_DIRS), "")


def _status(source: Source, repo: Path) -> None:
    folder = _vendored(source, repo)
    if folder:
        source.owner = "third-party"
    if source.owner == "managed":
        source.status = EVIDENCE
        source.reason = "managed policy: cited as evidence, never reported or changed"
    elif not source.is_markdown:
        source.status = EVIDENCE if source.status != UNREADABLE else UNREADABLE
        source.reason = CONFIG_REASON if source.status == EVIDENCE else source.reason
    elif folder:
        source.status = EVIDENCE
        source.reason = f"inside {folder}/, installed third-party code: cited as evidence only"
    elif source.status == UNREADABLE:
        source.reason = f"could not be read: {source.error}"
    elif source.loaders and all(loader.mode == EXCLUDED for loader in source.loaders):
        source.status = SKIPPED
        source.reason = "excluded by claudeMdExcludes and loaded by no other tool"
    elif len(source.text) > MAX_AUDITED_CHARS:
        source.status = SKIPPED
        source.reason = f"{source.size} bytes: too large for a full semantic read in one pass"


def _domain(source: Source, by_display: dict[str, Source]) -> str:
    """The reviewer domain, fixed by file type; an import takes its first importer's domain."""
    if source.status != IN_SCOPE:
        return DOMAIN_EVIDENCE
    if source.kind in KIND_DOMAINS:
        return KIND_DOMAINS[source.kind]
    for importer in source.imported_by:
        parent = by_display.get(importer)
        if parent is not None and parent.kind in KIND_DOMAINS:
            return KIND_DOMAINS[parent.kind]
    return DOMAIN_B


def _finalize(sources: list[Source], repo: Path) -> list[Source]:
    by_display = {source.display: source for source in sources}
    for source in sources:
        if not source.sha256 and source.status != UNREADABLE:
            load_text(source)
        _status(source, repo)
    for source in sources:
        source.domain = _domain(source, by_display)
        classify(source)
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
        sources=_finalize(list(context.found.by_real.values()), repo),
        out_of_scope=context.found.out_of_scope,
        imports=context.found.imports,
        claude=claude,
        codex=codex,
        files=tree.files,
        files_truncated=tree.truncated,
    )
    index_units(inventory)
    return inventory


def index_units(inventory: Inventory) -> None:
    """Split every loaded source into units and give each unit its two identities."""
    for source in inventory.sources:
        found = units.units_for(source) if source.lines else []
        inventory.units[source.sid] = found
        inventory.unit_ids[source.sid] = units.unit_ids(source.display, found)
        inventory.text_ids[source.sid] = units.text_ids(found)


def loaded_by(source: Source, tool: str = CLAUDE) -> bool:
    """True when the tool loads the source in some situation."""
    return any(loader.tool == tool for loader in source.loaders) and source.is_live
