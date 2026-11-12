"""Resolving the paths a skill's files mention, and the graph of which file references which."""

from __future__ import annotations

import ast
from collections import deque
import os
from pathlib import Path
import posixpath
import re
from typing import TYPE_CHECKING

from validators.skill_lint.markdown import parse_markdown

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from validators.skill_lint.discover import Skill
    from validators.skill_lint.markdown import MarkdownDoc

PATH_TOKEN = re.compile(r"[\w${}./-]+\.\w+")
PREFIX_TOKEN = re.compile(r"(?:\$\{?CLAUDE_(?:SKILL_DIR|PLUGIN_ROOT)\}?|\.\.?)/[\w${}./-]*")
"""Tokens that start with a known prefix, even without a file extension."""
VARIABLE = re.compile(
    r"^\$(?:\{(CLAUDE_SKILL_DIR|CLAUDE_PLUGIN_ROOT)\}|(CLAUDE_SKILL_DIR|CLAUDE_PLUGIN_ROOT)\b)/?"
)
SOURCE = re.compile(r"(?:^|[\s;&|(])(?:source|\.)[ \t]+([^\n;&|]+)")
SOURCE_PATH = re.compile(r"[\w.-]+(?:/[\w.-]+)*\.\w+")
MARKDOWN = (".md", ".markdown")
SHELL = (".sh", ".bash", ".zsh")
SKILL_MD = "SKILL.md"


def _path_part(token: str) -> str:
    """Drop a #fragment and a ?query from a token."""
    return token.split("#", 1)[0].split("?", 1)[0]


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


def _candidates(skill: Skill, path: str, from_file: str) -> list[Path]:
    """List the places a path may point to, in the order they are tried."""
    variable = _variable_base(skill, path)
    if variable is not None:
        base, rest = variable
        return [] if base is None else [base / rest]
    if _is_absolute(path):
        return []
    return [skill.root / posixpath.dirname(from_file) / path, skill.root / path]


def resolve(skill: Skill, token: str, from_file: str) -> str | None:
    """Return the relative POSIX path of the skill file a token names, or None."""
    path = _path_part(token)
    if not path:
        return None
    root = Path(os.path.normpath(skill.root))
    real_root = skill.root.resolve()
    for candidate in _candidates(skill, path, from_file):
        target = Path(os.path.normpath(candidate))
        if not target.is_relative_to(root):
            continue
        rel = target.relative_to(root).as_posix()
        if rel in skill.files and target.is_file() and target.resolve().is_relative_to(real_root):
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
    """Collect the path-looking tokens of some texts."""
    found: set[str] = set()
    for text in texts:
        found.update(PATH_TOKEN.findall(text))
        found.update(PREFIX_TOKEN.findall(text))
    return found


def _markdown_texts(skill: Skill, rel: str, doc: MarkdownDoc) -> list[str]:
    """Return the code and prose of a Markdown file, plus SKILL.md's frontmatter lines."""
    texts = [snippet.text for snippet in doc.code] + [text for _, text in doc.prose]
    if rel == SKILL_MD:
        lines = skill.text.get(SKILL_MD, "").replace("\r\n", "\n").split("\n")
        texts.extend(lines[: max(skill.frontmatter.body_start, 1) - 1])
    return texts


def _imported_modules(tree: ast.AST) -> list[str]:
    """List the module names a Python tree imports, absolutely or from its own package."""
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level <= 1:
            if node.module is not None:
                modules.append(node.module)
            elif node.level == 1:
                modules.extend(alias.name for alias in node.names)
    return modules


def _python_refs(skill: Skill, rel: str, text: str) -> set[str]:
    """Return the sibling modules a Python file imports; none when it does not parse."""
    try:
        tree = ast.parse(text)
    except SyntaxError, ValueError:
        return set()
    folder = posixpath.dirname(rel)
    found: set[str] = set()
    for module in _imported_modules(tree):
        stem = posixpath.join(folder, module.replace(".", "/"))
        found.update(c for c in (f"{stem}.py", f"{stem}/__init__.py") if c in skill.files)
    return found


def _is_shell(rel: str, text: str) -> bool:
    """Tell whether a file is a shell script, by extension or shebang."""
    first = text.split("\n", 1)[0]
    return rel.endswith(SHELL) or (first.startswith("#!") and "sh" in first.rsplit("/", 1)[-1])


def _shell_refs(skill: Skill, rel: str, text: str) -> set[str]:
    """Return the skill files a shell script sources with source or ."""
    if not _is_shell(rel, text):
        return set()
    found: set[str] = set()
    for line in text.split("\n"):
        if line.lstrip().startswith("#"):
            continue
        for match in SOURCE.finditer(line):
            paths: list[str] = SOURCE_PATH.findall(match.group(1))
            target = resolve(skill, paths[-1], rel) if paths else None
            if target is not None:
                found.add(target)
    return found


def _script_refs(skill: Skill, rel: str) -> set[str]:
    """Return the files a script imports or sources."""
    text = skill.text.get(rel)
    if text is None:
        return set()
    refs = _shell_refs(skill, rel, text)
    if rel.endswith(".py"):
        refs |= _python_refs(skill, rel, text)
    return refs


def _file_refs(skill: Skill, rel: str) -> set[str]:
    """Return the files one skill file references."""
    text = skill.text.get(rel)
    if text is None:
        return set()
    found = _script_refs(skill, rel)
    if rel.endswith(MARKDOWN):
        doc = skill.body if rel == SKILL_MD else parse_markdown(text)
        targets = [link.target for link in doc.links]
        targets.extend(_tokens(_markdown_texts(skill, rel, doc)))
    else:
        targets = sorted(_tokens([text]))
    for token in targets:
        target = resolve(skill, token, rel)
        if target is not None:
            found.add(target)
    found.discard(rel)
    return found


def reference_graph(skill: Skill) -> dict[str, set[str]]:
    """Map every file of the skill, binary ones included, to the files it references."""
    return {rel: _file_refs(skill, rel) for rel in skill.files}


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
    found: set[str] = set()
    for rel in skill.files:
        found |= _script_refs(skill, rel) - {rel}
    return found
