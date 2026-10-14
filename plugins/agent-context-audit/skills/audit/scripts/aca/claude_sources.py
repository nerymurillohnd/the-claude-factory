"""Claude Code memory sources: CLAUDE.md chains, rules, AGENTS.md, auto memory and imports.

Loading rules follow the Claude Code memory docs; the knowledge folder records the docs date and
section hashes they were taken from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from aca import globmatch, markdown, paths, settings
from aca.jsonutil import str_list
from aca.sources import (
    ALWAYS,
    CONDITIONAL,
    DEAD,
    EXCLUDED,
    NOT_LOADED,
    ON_DEMAND,
    TRUNCATED,
    Source,
    load_text,
)

if TYPE_CHECKING:
    from aca.paths import Env
    from aca.settings import Layer
    from aca.walk import Tree

CLAUDE = "claude"
MEMORY_FILE_NAMES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")
AGENTS_FILE_NAMES = ("AGENTS.md", ".claude/AGENTS.md")
NESTED_NAMES = frozenset({"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md"})
MEMORY_INDEX = "MEMORY.md"
MEMORY_INDEX_LINES = 200
MEMORY_INDEX_BYTES = 25 * 1024
MAX_IMPORT_HOPS = 4
AND_MODE = "claude-md-and-agents-md"
OR_MODE = "claude-md-or-agents-md"


@dataclass
class ClaudeFacts:
    """Effective values that decide what loads, with where each came from."""

    instruction_files: str = settings.DEFAULT_INSTRUCTION_FILES
    instruction_files_from: str = "default"
    claude_md_present: bool = False
    output_style: str = ""
    agent: str = ""
    excludes: list[str] = field(default_factory=list)
    auto_memory_dir: str = ""
    auto_memory_enabled: bool = True
    enabled_plugins: dict[str, bool] = field(default_factory=dict)
    layers: list[Layer] = field(default_factory=list)


@dataclass(frozen=True)
class ImportEdge:
    """One @-reference and what became of it."""

    importer: str
    line: int
    raw: str
    target: str
    status: str
    resolved: str = ""


@dataclass
class Found:
    """Sources collected so far, keyed by real path so aliases merge into one entry."""

    by_real: dict[Path, Source] = field(default_factory=dict)
    out_of_scope: list[dict[str, object]] = field(default_factory=list)
    imports: list[ImportEdge] = field(default_factory=list)

    def add(self, source: Source) -> Source:
        """Add a source, or merge it into the entry already holding the same real file."""
        real = paths.resolve(source.path)
        existing = self.by_real.get(real)
        if existing is None:
            self.by_real[real] = source
            return source
        if source.display != existing.display and source.display not in existing.aliases:
            existing.aliases.append(source.display)
        for loader in source.loaders:
            existing.add_loader(loader.tool, loader.mode, loader.reason)
        return existing

    def note_out_of_scope(self, display: str, what: str, count: int, reason: str) -> None:
        """Record something that loads but is never audited (skills, commands, plugins...)."""
        self.out_of_scope.append({"path": display, "what": what, "count": count, "reason": reason})


@dataclass
class Context:
    """Everything discovery needs to know about the machine and the project."""

    env: Env
    repo: Path
    tree: Tree
    found: Found
    facts: ClaudeFacts

    def show(self, path: Path) -> str:
        """Display form of a path."""
        return paths.display(path, self.repo, self.env.home)


@dataclass(frozen=True)
class Place:
    """How a discovered file is classified."""

    kind: str
    scope: str
    domain: str = "D1"


def ancestors(repo: Path) -> list[Path]:
    """Directories from the filesystem root down to the repository root."""
    return [*reversed(repo.parents), repo]


def markdown_files(directory: Path) -> list[Path]:
    """Every .md file under directory, recursively, in a stable order."""
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.rglob("*.md") if path.is_file())


def collect_facts(env: Env, repo: Path) -> ClaudeFacts:
    """Read the settings layers and derive the values that change what loads."""
    layers = settings.load_layers(env, repo)
    facts = ClaudeFacts(layers=layers)
    facts.instruction_files, facts.instruction_files_from = settings.instruction_files(layers)
    style, _ = settings.effective(layers, "outputStyle")
    facts.output_style = style if isinstance(style, str) else ""
    agent, _ = settings.effective(layers, "agent")
    facts.agent = agent if isinstance(agent, str) else ""
    facts.excludes = settings.merged_strings(layers, "claudeMdExcludes")
    enabled, _ = settings.effective(layers, "autoMemoryEnabled")
    facts.auto_memory_enabled = enabled is not False
    directory, _ = settings.effective(layers, "autoMemoryDirectory")
    if isinstance(directory, str) and directory:
        facts.auto_memory_dir = str(Path(directory).expanduser())
    else:
        key = paths.project_key(paths.memory_root(repo))
        facts.auto_memory_dir = str(env.claude_dir / "projects" / key / "memory")
    decided = settings.enabled_plugins(layers)
    facts.enabled_plugins = {plugin: value for plugin, (value, _scope) in decided.items()}
    return facts


def _excluded(context: Context, path: Path) -> bool:
    text = paths.resolve(path).as_posix()
    return any(globmatch.matches(pattern, text) for pattern in context.facts.excludes)


def add(context: Context, path: Path, place: Place, how: tuple[str, str]) -> Source:
    """Add a file with one Claude loader; claudeMdExcludes turns a memory file off."""
    source = Source(
        path=path,
        display=context.show(path),
        kind=place.kind,
        scope=place.scope,
        domain=place.domain,
    )
    mode, reason = how
    if place.domain == "D1" and _excluded(context, path):
        mode, reason = EXCLUDED, "matched by claudeMdExcludes"
    source.add_loader(CLAUDE, mode, reason)
    return context.found.add(source)


def memory_chain(context: Context) -> None:
    """User CLAUDE.md, then CLAUDE.md, .claude/CLAUDE.md and CLAUDE.local.md from / down."""
    user_md = context.env.claude_dir / "CLAUDE.md"
    if user_md.is_file():
        _ = add(context, user_md, Place("claude-md", "user"), (ALWAYS, "user instructions"))
    reason = "loads at launch: in the working directory or a directory above it"
    for directory in ancestors(context.repo):
        for name in MEMORY_FILE_NAMES:
            path = directory / name
            if not path.is_file() or paths.resolve(path) == paths.resolve(user_md):
                continue
            context.facts.claude_md_present = True
            local = name.endswith("local.md")
            here = directory == context.repo
            scope = ("local" if local else "project") if here else "ancestor"
            kind = "claude-local-md" if local else "claude-md"
            _ = add(context, path, Place(kind, scope), (ALWAYS, reason))


def _agents_mode(context: Context) -> tuple[str, str]:
    value = context.facts.instruction_files
    if value == AND_MODE:
        return ALWAYS, f"Project instructions is {AND_MODE}"
    if value == OR_MODE and not context.facts.claude_md_present:
        return ALWAYS, "no CLAUDE.md or CLAUDE.local.md in the working directory or above"
    if value == OR_MODE:
        return NOT_LOADED, "a CLAUDE.md or CLAUDE.local.md exists, so Claude Code reads that"
    return NOT_LOADED, f"Project instructions is {value}"


def agents_md(context: Context) -> None:
    """AGENTS.md as Claude Code reads it, under the Project instructions setting."""
    how = _agents_mode(context)
    for directory in ancestors(context.repo):
        for name in AGENTS_FILE_NAMES:
            path = directory / name
            if path.is_file():
                scope = "project" if directory == context.repo else "ancestor"
                _ = add(context, path, Place("agents-md", scope, "D3"), how)


def _rule_patterns(source: Source) -> tuple[list[str], str]:
    front = markdown.find_frontmatter(source.lines)
    if front is None:
        return [], ""
    if front.error:
        return [], front.error
    value = front.data.get("paths")
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()], ""
    return str_list(value), ""


def rule_mode(source: Source, files: list[str]) -> tuple[str, str]:
    """How a rule loads: at launch, when matching files are touched, or never."""
    patterns, error = _rule_patterns(source)
    if error:
        return ALWAYS, f"its frontmatter does not parse ({error}), so it loads without paths"
    if not patterns:
        return ALWAYS, "no paths frontmatter: loads at launch"
    hits = globmatch.count_matches(patterns, files)
    if hits == 0:
        return DEAD, f"paths {patterns} match no file in the project"
    return CONDITIONAL, f"loads when Claude reads or edits a file matching {patterns}"


def rules(context: Context) -> None:
    """User and project rules, with their paths frontmatter checked against the project."""
    for scope, directory in (
        ("user", context.env.claude_dir / "rules"),
        ("project", context.repo / ".claude" / "rules"),
    ):
        for path in markdown_files(directory):
            probe = Source(path=path, display="", kind="rule", scope=scope, domain="D1")
            load_text(probe)
            how = rule_mode(probe, context.tree.files)
            _ = add(context, path, Place("rule", scope), how)


def nested(context: Context) -> None:
    """CLAUDE.md, CLAUDE.local.md, rules and AGENTS.md in subdirectories (loaded on demand)."""
    for name in sorted(NESTED_NAMES):
        for path in context.tree.named(name):
            folder = path.parent
            if folder == context.repo or folder == context.repo / ".claude":
                continue
            where = folder.relative_to(context.repo).as_posix()
            how = (ON_DEMAND, f"loads when Claude reads or edits a file in {where}/")
            if name == "AGENTS.md":
                _nested_agents(context, path, how)
                continue
            kind = "claude-local-md" if name == "CLAUDE.local.md" else "claude-md"
            _ = add(context, path, Place(kind, "nested"), how)
    for rules_dir in context.tree.dirs_ending(".claude/rules"):
        if rules_dir == context.repo / ".claude" / "rules":
            continue
        where = rules_dir.parent.parent.relative_to(context.repo).as_posix()
        for path in markdown_files(rules_dir):
            how = (ON_DEMAND, f"nested rule: loads when Claude works in {where}/")
            _ = add(context, path, Place("rule", "nested"), how)


def _nested_agents(context: Context, path: Path, how: tuple[str, str]) -> None:
    has_claude = any((path.parent / name).is_file() for name in MEMORY_FILE_NAMES)
    mode, _ = _agents_mode(context)
    if has_claude and context.facts.instruction_files != AND_MODE:
        how = (NOT_LOADED, "its folder has a CLAUDE.md, which Claude Code reads instead")
    elif mode == NOT_LOADED:
        how = (NOT_LOADED, _agents_mode(context)[1])
    _ = add(context, path, Place("agents-md", "nested", "D3"), how)


def _index_mode(path: Path) -> tuple[str, str]:
    try:
        data = path.read_bytes()
    except OSError:
        return ALWAYS, "auto memory index: first 200 lines or 25 KB load at launch"
    lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
    if lines > MEMORY_INDEX_LINES or len(data) > MEMORY_INDEX_BYTES:
        return TRUNCATED, "only the first 200 lines or 25 KB load; the rest never reaches Claude"
    return ALWAYS, "auto memory index: loads at launch"


def auto_memory(context: Context) -> None:
    """The project's auto memory: MEMORY.md at launch, topic files on demand."""
    directory = Path(context.facts.auto_memory_dir)
    if not directory.is_dir():
        return
    for path in markdown_files(directory):
        if path.parent != directory:
            continue
        if not context.facts.auto_memory_enabled:
            how = (NOT_LOADED, "auto memory is turned off (autoMemoryEnabled: false)")
        elif path.name == MEMORY_INDEX:
            how = _index_mode(path)
        else:
            how = (ON_DEMAND, "auto memory topic file: Claude reads it when it needs it")
        kind = "auto-memory-index" if path.name == MEMORY_INDEX else "auto-memory-topic"
        _ = add(context, path, Place(kind, "auto-memory"), how)


def _resolve_import(base: Path, target: str, home: Path) -> Path:
    if target.startswith("~/"):
        return home / target[2:]
    candidate = Path(target)
    return candidate if candidate.is_absolute() else base / candidate


def _import_status(context: Context, source: Source, ref: markdown.ImportRef) -> tuple[str, Path]:
    resolved = _resolve_import(source.path.parent, ref.target, context.env.home)
    if ref.quoted:
        return "quoted", resolved
    if not resolved.is_file():
        return ("missing" if ref.path_like else "not-a-path"), resolved
    external = not paths.in_directory(paths.resolve(resolved), context.repo)
    if external and source.scope in {"project", "local", "nested"}:
        return "external", resolved
    return "ok", resolved


def _live_claude_markdown(source: Source) -> bool:
    return any(
        loader.tool == CLAUDE and loader.mode in {ALWAYS, CONDITIONAL, ON_DEMAND, TRUNCATED}
        for loader in source.loaders
    ) and source.kind in {"claude-md", "claude-local-md", "rule", "agents-md", "import"}


def imports(context: Context) -> None:
    """Follow @imports from every loaded memory file, up to the four-hop limit."""
    queue = [
        (source, 0) for source in context.found.by_real.values() if _live_claude_markdown(source)
    ]
    seen: set[Path] = set()
    while queue:
        source, hop = queue.pop(0)
        if source.path in seen:
            continue
        seen.add(source.path)
        if not source.lines:
            load_text(source)
        for ref in markdown.imports(source.lines):
            status, resolved = _import_status(context, source, ref)
            if status == "ok" and hop >= MAX_IMPORT_HOPS:
                status = "too-deep"
            edge = ImportEdge(
                source.display, ref.line, ref.raw, ref.target, status, context.show(resolved)
            )
            context.found.imports.append(edge)
            if status not in {"ok", "external"}:
                continue
            how = (
                (CONDITIONAL, "external import: loads only after you approve external imports")
                if status == "external"
                else (ALWAYS, f"imported by {source.display} (hop {hop + 1})")
            )
            child = add(context, resolved, Place("import", source.scope, source.domain), how)
            if source.display not in child.imported_by:
                child.imported_by.append(source.display)
            queue.append((child, hop + 1))
