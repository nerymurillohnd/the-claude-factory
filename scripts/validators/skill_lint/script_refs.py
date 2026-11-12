"""What a skill's scripts load: Python sibling imports and shell source lines."""

from __future__ import annotations

import ast
import posixpath
import re
from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from collections.abc import Set as AbstractSet

SOURCE = re.compile(r"(?:^|[;&|({]|\b(?:then|do|else))[ \t]*(?:source|\.)[ \t]+([^;&|]+)")
"""source or . in command position: at line start, or after a separator or then/do/else."""
SHELL_NAMES = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
SHELL_FOLDER = re.compile(r"^\$(?:\{([A-Za-z_]\w*)[^}]*\}|([A-Za-z_]\w*)|\(\))/")
"""A leading $NAME/, ${NAME...}/ or $(...)/ segment of a sourced path."""
BACKTICKS = re.compile(r"`[^`]*`")
CLAUDE_VARIABLES = frozenset({"CLAUDE_SKILL_DIR", "CLAUDE_PLUGIN_ROOT"})
SHELL = (".sh", ".bash", ".zsh")


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


def python_imports(rel: str, text: str, files: AbstractSet[str]) -> set[str]:
    """Return the sibling modules (among files) a Python file imports; none if it fails to parse."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(text)
    except SyntaxError, ValueError:
        return set()
    folder = posixpath.dirname(rel)
    found: set[str] = set()
    for module in _imported_modules(tree):
        stem = posixpath.join(folder, module.replace(".", "/"))
        found.update(c for c in (f"{stem}.py", f"{stem}/__init__.py") if c in files)
    return found


def _shebang_program(first: str) -> str | None:
    """Return the program a shebang line runs, looking through env and its options."""
    if not first.startswith("#!"):
        return None
    words = first[2:].split()
    if not words:
        return None
    program = posixpath.basename(words[0])
    if program == "env":
        rest = [word for word in words[1:] if not word.startswith("-") and "=" not in word]
        return rest[0] if rest else None
    return program


def is_shell(rel: str, text: str) -> bool:
    """Tell whether a file is a shell script, by extension or shebang interpreter."""
    return rel.endswith(SHELL) or _shebang_program(text.split("\n", 1)[0]) in SHELL_NAMES


def _drop_substitutions(line: str) -> str:
    """Replace each $(...) command substitution, nested ones included, with $()."""
    out: list[str] = []
    index = 0
    while index < len(line):
        if line.startswith("$(", index):
            depth, index = 1, index + 2
            while index < len(line) and depth:
                depth += {"(": 1, ")": -1}.get(line[index], 0)
                index += 1
            out.append("$()")
            continue
        out.append(line[index])
        index += 1
    return BACKTICKS.sub("$()", "".join(out))


def _source_path(argument: str) -> str | None:
    """Return the first word of a source argument, without leading shell-variable folders."""
    words = argument.replace('"', "").replace("'", "").split()
    if not words:
        return None
    word = words[0]
    while (match := SHELL_FOLDER.match(word)) is not None:
        if (match.group(1) or match.group(2)) in CLAUDE_VARIABLES:
            break
        word = word[match.end() :]
    return word or None


def sourced_paths(text: str) -> list[str]:
    """Return the path each source or . line of a shell script loads, in order.

    Leading $NAME/, ${NAME}/ and $(...)/ folders are dropped, so the rest is read from the
    script's own folder, then from the skill root, since bash reads it from the working
    directory; ${CLAUDE_SKILL_DIR} and ${CLAUDE_PLUGIN_ROOT} are kept.
    """
    paths: list[str] = []
    for line in text.split("\n"):
        if line.lstrip().startswith("#"):
            continue
        for match in SOURCE.finditer(_drop_substitutions(line)):
            path = _source_path(match.group(1))
            if path is not None:
                paths.append(path)
    return paths
