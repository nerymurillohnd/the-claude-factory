"""The source manifest: every file an agent may load, why, and what the audit does with it."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import TYPE_CHECKING

from aca.markdown import split_lines

if TYPE_CHECKING:
    from pathlib import Path

# Load modes recorded per loader (the brief's always / conditional / on-demand / config / dead,
# plus the precise reasons a file does not load).
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
