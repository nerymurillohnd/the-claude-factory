"""Codex CLI sources: AGENTS.md chain, overrides, fallbacks, config.toml, rules, hooks, agents.

Loading rules follow the Codex docs (Custom instructions with AGENTS.md, Advanced
Configuration, Rules, Hooks, Subagents). The Codex domain is skipped cleanly when there is no
Codex CLI and no Codex file; files without the CLI are still audited against those rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
import subprocess
from typing import TYPE_CHECKING

from aca import tomlish
from aca.claude_sources import Place
from aca.jsonutil import str_list
from aca.markdown import split_lines
from aca.sources import (
    ALWAYS,
    CONDITIONAL,
    CONFIG,
    NOT_LOADED,
    ON_DEMAND,
    SHADOWED,
    TRUNCATED,
    Source,
)

if TYPE_CHECKING:
    from aca.claude_sources import Context

CODEX = "codex"
DEFAULT_MAX_BYTES = 32 * 1024
OVERRIDE = "AGENTS.override.md"
AGENTS = "AGENTS.md"
VERSION_TIMEOUT = 10
TRUSTED = "trusted"


@dataclass
class CodexFacts:
    """What decides Codex loading on this machine for this project."""

    cli: str = ""
    version: str = ""
    home: str = ""
    max_bytes: int = DEFAULT_MAX_BYTES
    fallbacks: list[str] = field(default_factory=list)
    trust: str = ""
    present: bool = False

    @property
    def candidates(self) -> list[str]:
        """File names Codex checks in each directory, in order."""
        return [OVERRIDE, AGENTS, *self.fallbacks]


def codex_version(cli: str) -> str:
    """Return `codex --version` output, or '' when it cannot run."""
    try:
        done = subprocess.run(
            [cli, "--version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT,
            check=False,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def _config_entries(path: Path) -> list[tomlish.Entry]:
    try:
        lines = split_lines(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return []
    return tomlish.entries(lines)[0]


def _apply(facts: CodexFacts, entries: list[tomlish.Entry], repo: Path) -> None:
    for entry in entries:
        name = entry.path
        if name == "project_doc_max_bytes" and isinstance(entry.value, int):
            facts.max_bytes = entry.value
        elif name == "project_doc_fallback_filenames":
            facts.fallbacks = str_list(entry.value)
        elif (
            entry.table[:1] == ("projects",)
            and entry.key == ("trust_level",)
            and len(entry.table) > 1
            and Path(entry.table[1]).expanduser() == repo
            and isinstance(entry.value, str)
        ):
            facts.trust = entry.value


def collect_facts(home: Path, repo: Path) -> CodexFacts:
    """Find the Codex CLI and read the config values that change instruction loading."""
    facts = CodexFacts(home=str(home))
    facts.cli = shutil.which("codex") or ""
    if facts.cli:
        facts.version = codex_version(facts.cli)
    _apply(facts, _config_entries(home / "config.toml"), repo)
    if facts.trust == TRUSTED:
        _apply(facts, _config_entries(repo / ".codex" / "config.toml"), repo)
    project_files = [repo / OVERRIDE, repo / AGENTS, repo / ".codex"]
    facts.present = bool(facts.cli) or home.is_dir() or any(path.exists() for path in project_files)
    return facts


def _add(context: Context, path: Path, place: Place, how: tuple[str, str]) -> Source:
    source = Source(
        path=path,
        display=context.show(path),
        kind=place.kind,
        scope=place.scope,
        domain=place.domain,
    )
    source.add_loader(CODEX, *how)
    return context.found.add(source)


def _size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _kind(name: str) -> str:
    if name == OVERRIDE:
        return "codex-override"
    return "codex-agents-md" if name == AGENTS else "codex-fallback"


def _directory_chain(
    context: Context, facts: CodexFacts, folder: Path, live: tuple[str, str]
) -> None:
    """One directory: the first non-empty candidate loads, the rest are shadowed."""
    chosen = ""
    scope = "project" if folder == context.repo else "nested"
    for name in facts.candidates:
        path = folder / name
        if not path.is_file():
            continue
        size = _size(path)
        if size == 0:
            how = (NOT_LOADED, "empty file: Codex skips it")
        elif chosen:
            how = (SHADOWED, f"{chosen} in the same folder loads instead")
        else:
            chosen = name
            how = live
            if size > facts.max_bytes:
                how = (
                    TRUNCATED,
                    f"over project_doc_max_bytes ({facts.max_bytes}); the rest is cut",
                )
        _ = _add(context, path, Place(_kind(name), scope, "D3"), how)


def _global(context: Context, facts: CodexFacts) -> None:
    home = Path(facts.home)
    override, base = home / OVERRIDE, home / AGENTS
    override_live = override.is_file() and _size(override) > 0
    if override.is_file():
        how = (ALWAYS, "global override") if override_live else (NOT_LOADED, "empty file")
        _ = _add(context, override, Place("codex-override", "user", "D3"), how)
    if base.is_file():
        if override_live:
            how = (SHADOWED, "AGENTS.override.md in the Codex home loads instead")
        elif _size(base) == 0:
            how = (NOT_LOADED, "empty file: Codex skips it")
        else:
            how = (ALWAYS, "global instructions in the Codex home")
        _ = _add(context, base, Place("codex-agents-md", "user", "D3"), how)


def _project_chain(context: Context, facts: CodexFacts) -> None:
    root_how = (ALWAYS, "project root: Codex starts at the root and walks to the working directory")
    _directory_chain(context, facts, context.repo, root_how)
    names = set(facts.candidates)
    folders = sorted(
        {path.parent for name in names for path in context.tree.named(name)} - {context.repo},
    )
    for folder in folders:
        where = folder.relative_to(context.repo).as_posix()
        how = (CONDITIONAL, f"loads when Codex starts in {where}/ or below")
        _directory_chain(context, facts, folder, how)


def _layer_how(facts: CodexFacts, what: str, *, project: bool) -> tuple[str, str]:
    if not project:
        return CONFIG, f"user {what}"
    if facts.trust == TRUSTED:
        return CONFIG, f"project {what} (the project is trusted)"
    return CONDITIONAL, f"project {what}: loads only once you trust the project in Codex"


def _config_layers(context: Context, facts: CodexFacts) -> None:
    for project, base in ((False, Path(facts.home)), (True, context.repo / ".codex")):
        scope = "project" if project else "user"
        config = base / "config.toml"
        if config.is_file():
            how = _layer_how(facts, "config", project=project)
            _ = _add(context, config, Place("codex-config", scope, "D4"), how)
        hooks = base / "hooks.json"
        if hooks.is_file():
            how = _layer_how(facts, "hooks", project=project)
            _ = _add(context, hooks, Place("codex-hooks-json", scope, "D4"), how)
        rules_dir = base / "rules"
        for path in sorted(rules_dir.glob("*.rules")) if rules_dir.is_dir() else []:
            how = _layer_how(facts, "command rules", project=project)
            _ = _add(context, path, Place("codex-rules", scope, "D4"), how)
        agents_dir = base / "agents"
        for path in sorted(agents_dir.glob("*.toml")) if agents_dir.is_dir() else []:
            how = (ON_DEMAND, "custom agent: loads when Codex spawns it")
            _ = _add(context, path, Place("codex-agent-config", scope, "D3"), how)


def _out_of_scope(context: Context, facts: CodexFacts) -> None:
    for base in (context.env.home / ".agents" / "skills", context.repo / ".agents" / "skills"):
        total = sum(1 for _ in base.rglob("SKILL.md")) if base.is_dir() else 0
        if total:
            reason = "Codex skills are out of scope (the brief excludes skills)"
            context.found.note_out_of_scope(context.show(base), "Codex skills", total, reason)
    prompts = Path(facts.home) / "prompts"
    total = sum(1 for _ in prompts.glob("*.md")) if prompts.is_dir() else 0
    if total:
        reason = "Codex custom prompts (deprecated in favor of skills) are out of scope"
        context.found.note_out_of_scope(context.show(prompts), "Codex prompts", total, reason)


def discover(context: Context, facts: CodexFacts) -> None:
    """Every Codex source, when Codex is present or its files exist."""
    if not facts.present:
        return
    _global(context, facts)
    _project_chain(context, facts)
    _config_layers(context, facts)
    _out_of_scope(context, facts)
