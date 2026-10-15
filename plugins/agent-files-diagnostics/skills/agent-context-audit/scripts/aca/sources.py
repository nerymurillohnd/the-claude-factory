"""The source manifest: every file an agent may load, why, and what the audit does with it."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import TYPE_CHECKING

from aca.markdown import split_lines

if TYPE_CHECKING:
    from pathlib import Path

# Load modes recorded per loader (always / conditional / on-demand / config / dead, plus the
# precise reasons a file does not load).
ALWAYS = "always"
CONDITIONAL = "conditional"
ON_DEMAND = "on-demand"
CONFIG = "config"
SHADOWED = "shadowed"
TRUNCATED = "truncated"
DEAD = "dead"
NOT_LOADED = "not-loaded"
EXCLUDED = "excluded"
LIVE_MODES = (ALWAYS, CONDITIONAL, ON_DEMAND, CONFIG, TRUNCATED)

# What the audit does with a source.
IN_SCOPE = "in-scope"
EVIDENCE = "evidence"
ABSENT = "absent"
UNREADABLE = "unreadable"

# The four classification fields every source carries, each with its closed set of values.
LOADING_AUTOMATIC = "automatic"
LOADING_CONDITIONAL = "conditional"
LOADING_ON_DEMAND = "on-demand"
LOADING_UNKNOWN = "unknown"
CONSUMPTION_VERIFIED = "verified"
CONSUMPTION_DOCUMENTED = "documented-not-observed"
CONSUMPTION_UNVERIFIED = "unverified"
AVAILABILITY_COMPLETE = "complete"
AVAILABILITY_TRUNCATED = "truncated"
AVAILABILITY_INACCESSIBLE = "inaccessible"
AVAILABILITY_OPAQUE = "opaque"
APPLICABLE = "applicable"
APPLICABILITY_EXCLUDED = "excluded"
APPLICABILITY_SUPERSEDED = "superseded"
APPLICABILITY_UNRESOLVED = "unresolved"

# Reviewer domains, fixed by file type: A Codex files and every AGENTS.md, B the CLAUDE.md
# family, C rules, D memory, E instruction-bearing extensions.
DOMAIN_A = "A"
DOMAIN_B = "B"
DOMAIN_C = "C"
DOMAIN_D = "D"
DOMAIN_E = "E"
DOMAIN_EVIDENCE = "evidence"
DOMAINS = {
    DOMAIN_A: "Codex instruction files and every AGENTS.md, whichever tool reads it",
    DOMAIN_B: "The CLAUDE.md family: user, ancestor, project, local and nested CLAUDE.md files",
    DOMAIN_C: "Rules: user, project and nested rule files with their paths frontmatter",
    DOMAIN_D: "Memory: auto memory, subagent memory and Codex memory",
    DOMAIN_E: "Instruction-bearing extensions: subagent definitions, output styles, loop.md",
}
DOMAIN_ORDER = {DOMAIN_A: 0, DOMAIN_B: 1, DOMAIN_C: 2, DOMAIN_D: 3, DOMAIN_E: 4, DOMAIN_EVIDENCE: 5}

MARKDOWN_KINDS = frozenset(
    {
        "claude-md",
        "claude-local-md",
        "rule",
        "import",
        "auto-memory-index",
        "auto-memory-topic",
        "agents-md",
        "codex-agents-md",
        "codex-override",
        "codex-fallback",
        "codex-memory",
        "subagent",
        "output-style",
        "agent-memory",
        "loop-md",
        "managed-claude-md",
    },
)
JSON_KINDS = frozenset(
    {"settings", "mcp-json", "claude-json-mcp", "managed-settings", "codex-hooks-json"},
)
TOML_KINDS = frozenset({"codex-config", "codex-agent-config"})
STARLARK_KINDS = frozenset({"codex-rules"})
KIND_DOMAINS = {
    "agents-md": DOMAIN_A,
    "codex-agents-md": DOMAIN_A,
    "codex-override": DOMAIN_A,
    "codex-fallback": DOMAIN_A,
    "claude-md": DOMAIN_B,
    "claude-local-md": DOMAIN_B,
    "rule": DOMAIN_C,
    "auto-memory-index": DOMAIN_D,
    "auto-memory-topic": DOMAIN_D,
    "agent-memory": DOMAIN_D,
    "codex-memory": DOMAIN_D,
    "subagent": DOMAIN_E,
    "output-style": DOMAIN_E,
    "loop-md": DOMAIN_E,
}


@dataclass
class Loader:
    """One tool that loads (or would load) the file, how, and why."""

    tool: str
    mode: str
    reason: str


@dataclass
class Source:
    """One file in the manifest. Text is kept in memory only; reports carry hashes and lines."""

    path: Path
    display: str
    kind: str
    scope: str
    domain: str
    owner: str = "user"
    status: str = IN_SCOPE
    reason: str = ""
    loaders: list[Loader] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    imported_by: list[str] = field(default_factory=list)
    subset: str = ""
    sid: str = ""
    sha256: str = ""
    size: int = 0
    text: str = ""
    lines: list[str] = field(default_factory=list)
    symlink: str = ""
    error: str = ""
    loading: str = LOADING_UNKNOWN
    consumption: str = CONSUMPTION_UNVERIFIED
    availability: str = AVAILABILITY_COMPLETE
    applicability: str = APPLICABILITY_UNRESOLVED

    @property
    def line_count(self) -> int:
        """Number of lines a line-numbered reader shows."""
        return len(self.lines)

    def add_loader(self, tool: str, mode: str, reason: str) -> None:
        """Record a loader once."""
        if not any(item.tool == tool and item.mode == mode for item in self.loaders):
            self.loaders.append(Loader(tool, mode, reason))

    @property
    def is_live(self) -> bool:
        """True when some tool loads the file in some situation."""
        return any(loader.mode in LIVE_MODES for loader in self.loaders)

    @property
    def is_markdown(self) -> bool:
        """True for the instruction and memory Markdown the audit reviews."""
        return self.kind in MARKDOWN_KINDS


def _loading(modes: set[str], status: str) -> str:
    if ALWAYS in modes or (CONFIG in modes and status == EVIDENCE):
        return LOADING_AUTOMATIC
    if CONDITIONAL in modes or TRUNCATED in modes:
        return LOADING_CONDITIONAL
    if ON_DEMAND in modes:
        return LOADING_ON_DEMAND
    return LOADING_UNKNOWN


def _availability(source: Source, modes: set[str]) -> str:
    if source.status == UNREADABLE:
        return AVAILABILITY_INACCESSIBLE
    if source.subset:
        return AVAILABILITY_OPAQUE
    if TRUNCATED in modes:
        return AVAILABILITY_TRUNCATED
    return AVAILABILITY_COMPLETE


def _applicability(source: Source, modes: set[str]) -> str:
    if modes and modes <= {EXCLUDED}:
        return APPLICABILITY_EXCLUDED
    if modes and modes <= {SHADOWED, NOT_LOADED, DEAD}:
        return APPLICABILITY_SUPERSEDED
    if source.is_live:
        return APPLICABLE
    return APPLICABILITY_UNRESOLVED


def classify(source: Source) -> None:
    """Fill the four classification fields from the loaders and the read status.

    Loading comes from the strongest loader mode. Consumption is what the documentation says
    happens, never an observation: the audit reads no session transcript, so nothing here is
    `verified`; a source with no recognized loader stays `unverified`. Availability records how
    much of the text the audit could read. Applicability says whether the file governs anything
    today, as far as the loading rules show.
    """
    modes = {loader.mode for loader in source.loaders}
    source.loading = _loading(modes, source.status)
    source.consumption = (
        CONSUMPTION_DOCUMENTED if source.loading != LOADING_UNKNOWN else CONSUMPTION_UNVERIFIED
    )
    source.availability = _availability(source, modes)
    source.applicability = _applicability(source, modes)


def digest_bytes(data: bytes) -> str:
    """Return the sha256 hex digest."""
    return hashlib.sha256(data).hexdigest()


def load_text(source: Source, text: str | None = None) -> None:
    """Fill hash, size, text and lines from disk (or from synthesized text for a subset)."""
    if text is not None:
        data = text.encode("utf-8")
    else:
        try:
            data = source.path.read_bytes()
        except OSError as error:
            source.status = UNREADABLE
            source.error = error.strerror or str(error)
            return
    source.sha256 = digest_bytes(data)
    source.size = len(data)
    source.text = data.decode("utf-8", errors="replace")
    source.lines = split_lines(source.text)
    if source.path.is_symlink():
        try:
            source.symlink = str(source.path.readlink())
        except (OSError, AttributeError):
            source.symlink = "(unresolved)"


def current_digest(source: Source) -> str:
    """Hash the file as it is now ('' when it can no longer be read)."""
    try:
        return digest_bytes(source.path.read_bytes())
    except OSError:
        return ""
