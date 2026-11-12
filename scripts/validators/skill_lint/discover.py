"""Finding skills in a repository and loading their files, text and git modes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import TYPE_CHECKING

from validators.skill_lint.frontmatter import Frontmatter, parse_frontmatter

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from validators.skill_lint.model import SkillKind

type ModeReader = Callable[[Path], Mapping[str, str]]

GLOBS = ("plugins/*/skills/*/SKILL.md", ".claude/skills/*/SKILL.md")
SKIPPED_TEXT = frozenset({"__pycache__", ".DS_Store"})
EXECUTABLE_BITS = 0o111


def git_modes(skill_dir: Path) -> dict[str, str]:
    """Map each tracked file of a folder to its git mode; empty outside git or on failure."""
    git = shutil.which("git")
    if git is None:
        return {}
    try:
        result = subprocess.run(
            [git, "-C", str(skill_dir), "ls-files", "-s", "-z", "--", "."],
            capture_output=True,
            check=False,
            text=True,
        )
    except OSError:
        return {}
    if result.returncode != 0:
        return {}
    modes: dict[str, str] = {}
    for entry in result.stdout.split("\0"):
        meta, _, path = entry.partition("\t")
        if path:
            modes[path] = meta.split(" ", 1)[0]
    return modes


@dataclass(frozen=True)
class Skill:
    """A skill folder with its files, git modes and parsed frontmatter."""

    root: Path
    kind: SkillKind
    plugin: str | None
    command: str
    plugin_root: Path | None
    files: tuple[str, ...]
    """Relative POSIX paths, sorted, symlinks included."""
    text: Mapping[str, str]
    """The files that decode as UTF-8."""
    modes: Mapping[str, str]
    frontmatter: Frontmatter

    def is_executable(self, rel: str) -> tuple[bool, bool]:
        """Return (executable, tracked), using the git mode when tracked, else stat."""
        mode = self.modes.get(rel)
        if mode is not None:
            return mode == "100755", True
        try:
            return bool((self.root / rel).stat().st_mode & EXECUTABLE_BITS), False
        except OSError:
            return False, False


def _identify(skill_md: Path) -> tuple[SkillKind, str | None, str, Path | None]:
    """Derive kind, plugin, command and plugin root from the SKILL.md path."""
    folder = skill_md.parent
    name = folder.name
    parts = folder.parts
    if len(parts) >= 4 and parts[-2] == "skills":  # noqa: PLR2004
        if parts[-4] == "plugins":
            return "plugin", parts[-3], f"{parts[-3]}:{name}", folder.parent.parent
        if parts[-3] == ".claude":
            return "project", None, f"project:{name}", None
    return "standalone", None, name, None


def _list_files(root: Path) -> tuple[str, ...]:
    """List every file and symlink under a folder as sorted relative POSIX paths."""
    found = (p for p in root.rglob("*") if p.is_symlink() or p.is_file())
    return tuple(sorted(p.relative_to(root).as_posix() for p in found))


def _read_text(root: Path, files: tuple[str, ...]) -> dict[str, str]:
    """Read the UTF-8 files, skipping caches and OS litter."""
    texts: dict[str, str] = {}
    for rel in files:
        if SKIPPED_TEXT & set(rel.split("/")):
            continue
        try:
            texts[rel] = (root / rel).read_text(encoding="utf-8")
        except UnicodeDecodeError, OSError:
            continue
    return texts


def load_skill(skill_md: Path, *, mode_reader: ModeReader = git_modes) -> Skill:
    """Load the skill whose SKILL.md is given."""
    root = skill_md.parent
    kind, plugin, command, plugin_root = _identify(skill_md)
    files = _list_files(root)
    text = _read_text(root, files)
    return Skill(
        root=root,
        kind=kind,
        plugin=plugin,
        command=command,
        plugin_root=plugin_root,
        files=files,
        text=text,
        modes=dict(mode_reader(root)),
        frontmatter=parse_frontmatter(text.get("SKILL.md", "")),
    )


def discover(repo: Path) -> list[Skill]:
    """Load every skill matched by the two skill globs, sorted by command."""
    found = [path for pattern in GLOBS for path in repo.glob(pattern)]
    return sorted((load_skill(p) for p in found), key=lambda skill: skill.command)
