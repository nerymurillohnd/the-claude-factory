"""One pass over the project tree, collecting every file and folder the loaders care about."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from aca import paths

SKIP_DIRS = frozenset({".git"})
MAX_LISTED_FILES = 200_000


@dataclass
class Tree:
    """What one walk of the project found."""

    root: Path
    by_name: dict[str, list[Path]] = field(default_factory=dict)
    dirs: list[Path] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    truncated: bool = False

    def named(self, name: str) -> list[Path]:
        """Every file with this exact name, in walk order."""
        return self.by_name.get(name, [])

    def dirs_ending(self, relative: str) -> list[Path]:
        """Every folder whose path ends with relative, such as .claude/rules."""
        parts = tuple(relative.split("/"))
        return [path for path in self.dirs if path.parts[-len(parts) :] == parts]


def walk_project(root: Path, names: set[str], skip: list[Path]) -> Tree:
    """Walk root once (never into .git or the skip folders), without following symlinks."""
    tree = Tree(root=root)
    for current, subdirs, files in os.walk(root):
        directory = Path(current)
        subdirs[:] = sorted(
            name
            for name in subdirs
            if name not in SKIP_DIRS
            and not any(paths.in_directory(directory / name, folder) for folder in skip)
        )
        tree.dirs.append(directory)
        for name in sorted(files):
            if name in names:
                tree.by_name.setdefault(name, []).append(directory / name)
            if len(tree.files) < MAX_LISTED_FILES:
                tree.files.append((directory / name).relative_to(root).as_posix())
            else:
                tree.truncated = True
    return tree
