"""The files agent-headings checks: every subagent of the plugins and of .claude/."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

GLOBS = ("plugins/*/agents/**/*.md", ".claude/agents/**/*.md")
PRUNED_DIRS = frozenset({".git", "node_modules", ".venv"})
"""Folders never searched: git's own data and vendored dependency trees."""


def discover(root: Path) -> list[Path]:
    """Return every file the globs match under root, sorted, outside the pruned folders."""
    found = {
        path
        for pattern in GLOBS
        for path in root.glob(pattern)
        if path.is_file() and not PRUNED_DIRS.intersection(path.relative_to(root).parts)
    }
    return sorted(found)
