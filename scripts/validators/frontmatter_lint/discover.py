#!/usr/bin/env python3
"""The files frontmatter-lint checks: every skill, agent and command of the repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

GLOBS = (
    "plugins/*/skills/*/SKILL.md",
    "plugins/*/agents/**/*.md",
    "plugins/*/commands/**/*.md",
    ".claude/skills/*/SKILL.md",
    ".claude/agents/**/*.md",
    ".claude/commands/**/*.md",
)
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
