"""Resolving the paths a skill's files mention, and the graph of which file references which."""

from __future__ import annotations

from collections import deque
import os
from pathlib import Path
import posixpath
import re
from typing import TYPE_CHECKING

from validators.skill_lint.script_refs import is_shell, python_imports, sourced_paths

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from validators.skill_lint.discover import Skill
    from validators.skill_lint.markdown_model import MarkdownDoc

PATH_TOKEN = re.compile(r"[\w${}./-]+\.\w+")
PREFIX_TOKEN = re.compile(r"(?:\$\{?CLAUDE_(?:SKILL_DIR|PLUGIN_ROOT)\}?|\.\.?)/[\w${}./-]*")
"""Tokens that start with a known prefix, even without a file extension."""
URL = re.compile(r"[A-Za-z][\w+.-]*://\S+")
VARIABLE_NAME = r"(CLAUDE_SKILL_DIR|CLAUDE_PLUGIN_ROOT)"
VARIABLE = re.compile(rf"^\$(?:\{{{VARIABLE_NAME}\}}|{VARIABLE_NAME})(?:/|$)")
SKILL_MD = "SKILL.md"


def _path_part(token: str) -> str:
    """Drop a #fragment and a ?query from a token, then restore an encoded # or ?."""
    path = token.split("#", 1)[0].split("?", 1)[0]
    return path.replace("%23", "#").replace("%3F", "?")


def _is_absolute(path: str) -> bool:
    """Tell whether a path is absolute or home-relative."""
    return path.startswith(("/", "~/")) or path == "~"


def _variable_base(skill: Skill, path: str) -> tuple[Path | None, str] | None:
    """Return (base folder, rest) for a path through a skill variable, else None.

    The base is None for ${CLAUDE_PLUGIN_ROOT} in a skill outside a plugin.
    """
    match = VARIABLE.match(path)
    if match is None:
        return None
    name = match.group(1) or match.group(2)
    rest = path[match.end() :]
    if name == "CLAUDE_SKILL_DIR":
        return skill.root, rest
    if skill.kind == "plugin" and skill.plugin_root is not None:
        return skill.plugin_root, rest
    return None, rest


class Resolver:
    """Resolves tokens against one skill, with its file set and root computed once.

    Build one per check and reuse it for every token. A Markdown link (link=True) is read
    only from its file's folder, as GitHub and Claude read it; any other relative token is
    read from that folder, then from the skill root.
    """

    def __init__(self, skill: Skill) -> None:
        """Index the skill's files and normalize its root."""
        self.skill: Skill = skill
        self.files: frozenset[str] = frozenset(skill.files)
        self.root: Path = Path(os.path.normpath(skill.root))
        self.real_root: Path = skill.root.resolve()

    def candidates(self, path: str, from_file: str, *, link: bool) -> list[Path]:
        """List the places a path may point to, in the order they are tried."""
        variable = _variable_base(self.skill, path)
        if variable is not None:
            base, rest = variable
            return [] if base is None else [base / rest]
        if _is_absolute(path):
            return []
        near = self.skill.root / posixpath.dirname(from_file) / path
        return [near] if link else [near, self.skill.root / path]

    def resolve(self, token: str, from_file: str, *, link: bool = False) -> str | None:
        """Return the relative POSIX path of the skill file a token names, or None."""
        path = _path_part(token)
        if not path:
            return None
        for candidate in self.candidates(path, from_file, link=link):
            target = Path(os.path.normpath(candidate))
            if not target.is_relative_to(self.root):
                continue
            rel = target.relative_to(self.root).as_posix()
            if (
                rel in self.files
                and target.is_file()
                and target.resolve().is_relative_to(self.real_root)
            ):
                return rel
        return None


def escapes(skill: Skill, token: str, from_file: str) -> bool:
    """Tell whether a token is absolute, or its real path lies outside the skill folder."""
    path = _path_part(token)
    if not path:
        return False
    if _is_absolute(path):
        return True
    variable = _variable_base(skill, path)
    if variable is None:
        target = skill.root / posixpath.dirname(from_file) / path
    else:
        base, rest = variable
        if base is None:
            return False
        target = base / rest
    return not Path(os.path.realpath(target)).is_relative_to(skill.root.resolve())


def _tokens(texts: Iterable[str]) -> set[str]:
    """Collect the path-looking tokens of some texts, ignoring URLs."""
    found: set[str] = set()
    for text in texts:
        local = URL.sub(" ", text)
        found.update(PATH_TOKEN.findall(local))
        found.update(PREFIX_TOKEN.findall(local))
    return found


def _markdown_texts(skill: Skill, rel: str, doc: MarkdownDoc) -> list[str]:
    """Return the code and prose of a Markdown file, plus SKILL.md's frontmatter lines."""
    texts = [snippet.text for snippet in doc.code] + [text for _, text in doc.prose]
    if rel == SKILL_MD:
        lines = skill.text.get(SKILL_MD, "").replace("\r\n", "\n").split("\n")
        texts.extend(lines[: max(skill.frontmatter.body_start, 1) - 1])
    return texts


def _script_refs(resolver: Resolver, rel: str) -> set[str]:
    """Return the files a script imports or sources."""
    text = resolver.skill.text.get(rel)
    if text is None:
        return set()
    refs: set[str] = set()
    if is_shell(rel, text):
        for path in sourced_paths(text):
            target = resolver.resolve(path, rel)
            if target is not None:
                refs.add(target)
    if rel.endswith(".py"):
        refs |= python_imports(rel, text, resolver.files)
    return refs - {rel}


def _file_refs(resolver: Resolver, rel: str) -> set[str]:
    """Return the files one skill file references."""
    skill = resolver.skill
    text = skill.text.get(rel)
    if text is None:
        return set()
    found = _script_refs(resolver, rel)
    tokens: Iterable[str]
    doc = skill.markdown.get(rel)
    if doc is not None:
        for link in doc.links:
            found.add(resolver.resolve(link.target, rel, link=True) or rel)
        tokens = _tokens(_markdown_texts(skill, rel, doc))
    else:
        tokens = _tokens([text])
    for token in tokens:
        found.add(resolver.resolve(token, rel) or rel)
    found.discard(rel)
    return found


def reference_graph(skill: Skill) -> dict[str, set[str]]:
    """Map every file of the skill, binary ones included, to the files it references.

    Markdown links are read from their file's folder only; path tokens in code, prose,
    frontmatter and scripts, and sourced shell paths, also from the skill root. Tokens that
    name no file are ignored.
    """
    resolver = Resolver(skill)
    return {rel: _file_refs(resolver, rel) for rel in skill.files}


def depths(graph: Mapping[str, set[str]], start: str = SKILL_MD) -> dict[str, int]:
    """Return the breadth-first distance from start of every file it reaches; start is 0."""
    found = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for target in sorted(graph.get(current, set())):
            if target not in found:
                found[target] = found[current] + 1
                queue.append(target)
    return found


def imported_or_sourced(skill: Skill) -> set[str]:
    """Return the files another file of the skill imports (Python) or sources (shell)."""
    resolver = Resolver(skill)
    found: set[str] = set()
    for rel in skill.files:
        found |= _script_refs(resolver, rel)
    return found
