#!/usr/bin/env python3
"""Finding skills in a repository and loading their files, text and git modes."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import TYPE_CHECKING

from validators.skill_lint.frontmatter import BOM, Frontmatter, parse_frontmatter
from validators.skill_lint.markdown import parse_markdown

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from validators.skill_lint.markdown_model import MarkdownDoc
    from validators.skill_lint.model import SkillKind

type ModeReader = Callable[[Path], Mapping[str, str]]

GLOBS = ("plugins/*/skills/*/SKILL.md", ".claude/skills/*/SKILL.md")
SKIPPED_TEXT = frozenset({"__pycache__", ".DS_Store"})
PRUNED_DIRS = frozenset({".git", "node_modules", ".venv"})
"""Folders never listed: git's own data and vendored dependency trees."""
EXECUTABLE_BITS = 0o111
MAX_TEXT_BYTES = 1024 * 1024
"""Files larger than this are listed but not read."""
NOT_A_REPOSITORY = "not a git repository"
MARKDOWN = (".md", ".markdown")


class GitError(Exception):
    """Git failed for a reason other than the folder not being in a repository."""


def git_modes(skill_dir: Path) -> dict[str, str]:
    """Map each tracked file of a folder to its git mode.

    Empty when git is not installed or the folder is not in a repository; any other
    failure raises GitError with git's first error line.
    """
    git = shutil.which("git")
    if git is None:
        return {}
    try:
        result = subprocess.run(
            [git, "-C", str(skill_dir), "ls-files", "-s", "-z", "--", "."],
            capture_output=True,
            check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
    except OSError as exc:
        raise GitError(str(exc)) from exc
    if result.returncode != 0:
        error = os.fsdecode(result.stderr).strip()
        if NOT_A_REPOSITORY in error:
            return {}
        lines = error.splitlines()
        raise GitError(lines[-1] if lines else f"git exited with {result.returncode}")
    modes: dict[str, str] = {}
    for entry in result.stdout.split(b"\0"):
        meta, _, path = os.fsdecode(entry).partition("\t")
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
    """Relative POSIX paths, sorted, symlinks included, PRUNED_DIRS left out."""
    text: Mapping[str, str]
    """The files that decode as UTF-8."""
    modes: Mapping[str, str]
    frontmatter: Frontmatter
    body: MarkdownDoc
    """The SKILL.md body, the lines from frontmatter.body_start on, with file line numbers."""
    markdown: Mapping[str, MarkdownDoc]
    """Every readable .md and .markdown file, parsed once; SKILL.md maps to body."""
    modes_error: str | None = None
    """Why git could not report modes, when it failed; None when it worked or was absent."""

    def is_executable(self, rel: str) -> tuple[bool, bool]:
        """Return (executable, tracked), using the git mode when tracked, else stat."""
        mode = self.modes.get(rel)
        if mode is not None:
            return mode == "100755", True
        try:
            return bool((self.root / rel).stat().st_mode & EXECUTABLE_BITS), False
        except OSError:
            return False, False


def _identify(folder: Path) -> tuple[SkillKind, str | None, str, Path | None]:
    """Derive kind, plugin, command and plugin root from the skill folder's path."""
    name = folder.name
    match folder.parts:
        case (*_, "plugins", plugin, "skills", _):
            return "plugin", plugin, f"{plugin}:{name}", folder.parent.parent
        case (*_, ".claude", "skills", _):
            return "project", None, f"project:{name}", None
        case _:
            return "standalone", None, name, None


def _list_files(root: Path) -> tuple[str, ...]:
    """List every file and symlink under a folder as sorted relative POSIX paths.

    PRUNED_DIRS are not entered; a symlinked folder is listed, not entered.
    """
    found: list[str] = []
    for current, dirnames, filenames in os.walk(root):
        folder = Path(current)
        dirnames[:] = [d for d in dirnames if d not in PRUNED_DIRS]
        links = [d for d in dirnames if (folder / d).is_symlink()]
        for name in [*filenames, *links]:
            path = folder / name
            if path.is_symlink() or path.is_file():
                found.append(path.relative_to(root).as_posix())
    return tuple(sorted(found))


def _read_text(root: Path, files: tuple[str, ...]) -> tuple[dict[str, str], dict[str, str]]:
    """Read the UTF-8 files, skipping caches and OS litter.

    Returns (texts, unread), where unread maps each other file to why it was not read.
    """
    texts: dict[str, str] = {}
    unread: dict[str, str] = {}
    real_root = root.resolve()
    for rel in files:
        if SKIPPED_TEXT & set(rel.split("/")):
            continue
        path = root / rel
        if not path.resolve().is_relative_to(real_root):
            unread[rel] = "links to a path outside the skill folder"
            continue
        try:
            if path.stat().st_size > MAX_TEXT_BYTES:
                unread[rel] = "is larger than 1 MiB and was not read"
                continue
            texts[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            unread[rel] = "is not valid UTF-8 text"
        except OSError as exc:
            unread[rel] = f"cannot be read: {exc.strerror or exc}"
    return texts, unread


def _frontmatter(text: Mapping[str, str], unread: Mapping[str, str]) -> Frontmatter:
    """Parse SKILL.md, or report why it could not be read."""
    if "SKILL.md" not in text:
        reason = unread.get("SKILL.md", "cannot be read")
        return Frontmatter(None, {}, 1, (1, f"SKILL.md {reason}"))
    return parse_frontmatter(text["SKILL.md"])


def _body(text: Mapping[str, str], frontmatter: Frontmatter) -> MarkdownDoc:
    """Parse the SKILL.md lines from body_start on, split as parse_frontmatter splits them."""
    source = text.get("SKILL.md", "").removeprefix(BOM).replace("\r\n", "\n")
    start = max(frontmatter.body_start, 1)
    body = "\n".join(source.split("\n")[start - 1 :])
    return parse_markdown(body, first_line=start)


def _modes(root: Path, mode_reader: ModeReader) -> tuple[dict[str, str], str | None]:
    """Read the git modes, or keep why git failed."""
    try:
        return dict(mode_reader(root)), None
    except GitError as exc:
        return {}, str(exc)


def load_skill(skill_md: Path, *, mode_reader: ModeReader = git_modes) -> Skill:
    """Load the skill whose SKILL.md is given; a relative path is made absolute first."""
    root = skill_md.absolute().parent
    kind, plugin, command, plugin_root = _identify(root)
    files = _list_files(root)
    text, unread = _read_text(root, files)
    frontmatter = _frontmatter(text, unread)
    modes, modes_error = _modes(root, mode_reader)
    body = _body(text, frontmatter)
    markdown = {
        rel: body if rel == "SKILL.md" else parse_markdown(content)
        for rel, content in text.items()
        if rel.endswith(MARKDOWN)
    }
    return Skill(
        root=root,
        kind=kind,
        plugin=plugin,
        command=command,
        plugin_root=plugin_root,
        files=files,
        text=text,
        modes=modes,
        frontmatter=frontmatter,
        body=body,
        markdown=markdown,
        modes_error=modes_error,
    )


def discover(repo: Path) -> list[Skill]:
    """Load every skill matched by the two skill globs, sorted by command."""
    found = [path for pattern in GLOBS for path in repo.glob(pattern)]
    return sorted((load_skill(p) for p in found), key=lambda skill: skill.command)
