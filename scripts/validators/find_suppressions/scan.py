#!/usr/bin/env python3
"""Find each suppression in one file: the comment directives and calls that silence a check.

Python is read with tokenize and ast, so only real comments and real cast() calls count; shell
and TypeScript or JavaScript lines count when the directive follows their comment marker.
"""

import ast
from dataclasses import dataclass
import io
import re
import tokenize
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

type Patterns = tuple[tuple[str, re.Pattern[str]], ...]

PYTHON_SUFFIXES = frozenset({".py", ".pyi"})
SCRIPT_SUFFIXES = frozenset({".ts", ".tsx", ".mts", ".cts", ".js", ".mjs", ".cjs"})
SHELL_SUFFIXES = frozenset({".sh", ".bash"})
SHELL_SHEBANG = re.compile(r"^#!.*\b(ba|da|k|z)?sh\b")

PYTHON_COMMENTS: Patterns = (
    ("noqa", re.compile(r"#\s*noqa\b", re.IGNORECASE)),
    ("ruff: noqa", re.compile(r"#\s*ruff\s*:\s*noqa\b", re.IGNORECASE)),
    ("type: ignore", re.compile(r"#\s*type\s*:\s*ignore\b")),
    ("pyright: ignore", re.compile(r"#\s*(based)?pyright\s*:\s*ignore\b")),
    ("fmt: off/skip", re.compile(r"#\s*fmt\s*:\s*(off|skip)\b")),
    ("isort: skip", re.compile(r"#\s*isort\s*:\s*(skip|off)\b")),
)
SHELL_COMMENTS: Patterns = (
    ("shellcheck disable", re.compile(r"(^|\s)#\s*shellcheck\s+disable\s*=")),
)
SCRIPT_COMMENTS: Patterns = (
    ("biome-ignore", re.compile(r"(//|/\*)\s*biome-ignore\b")),
    ("@ts-ignore", re.compile(r"(//|/\*)\s*@ts-(ignore|expect-error|nocheck)\b")),
    ("eslint-disable", re.compile(r"(//|/\*)\s*eslint-disable\b")),
)


@dataclass(frozen=True)
class Suppression:
    """One suppression: where it is, what kind it is, and the line that holds it."""

    path: Path
    line: int
    kind: str
    text: str


def language(path: Path) -> str | None:
    """Name the language whose suppressions this file can hold, or None to skip it unread.

    The extension decides; a file with none is read as shell only when its first line is a shell
    shebang, which is checked on raw bytes so a binary file is never decoded.
    """
    if path.suffix in PYTHON_SUFFIXES:
        return "python"
    if path.suffix in SCRIPT_SUFFIXES:
        return "script"
    if path.suffix in SHELL_SUFFIXES:
        return "shell"
    if path.suffix:
        return None
    with path.open("rb") as handle:
        first = handle.readline(200)
    if SHELL_SHEBANG.match(first.decode("utf-8", errors="replace")):
        return "shell"
    return None


def _python(path: Path, text: str) -> list[Suppression]:
    """Comment directives from tokenize, and cast() calls from the syntax tree."""
    lines = text.splitlines()
    found: list[Suppression] = []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        for kind, pattern in PYTHON_COMMENTS:
            if pattern.search(token.string):
                row = token.start[0]
                found.append(Suppression(path, row, kind, lines[row - 1].strip()))
                break
    for node in ast.walk(ast.parse(text, filename=str(path))):
        if isinstance(node, ast.Call):
            func = node.func
            named = isinstance(func, ast.Name) and func.id == "cast"
            attribute = isinstance(func, ast.Attribute) and func.attr == "cast"
            if named or attribute:
                found.append(Suppression(path, node.lineno, "cast", lines[node.lineno - 1].strip()))
    return sorted(found, key=lambda item: item.line)


def _by_line(
    path: Path, text: str, patterns: tuple[tuple[str, re.Pattern[str]], ...]
) -> list[Suppression]:
    """Each line where a directive follows the language's comment marker."""
    found: list[Suppression] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in patterns:
            if pattern.search(line):
                found.append(Suppression(path, number, kind, line.strip()))
                break
    return found


def scan_file(path: Path) -> list[Suppression]:
    """Return every suppression in the file, or none when its type holds none."""
    kind = language(path)
    if kind is None:
        return []
    text = path.read_text(encoding="utf-8")
    match kind:
        case "python":
            return _python(path, text)
        case "shell":
            return _by_line(path, text, SHELL_COMMENTS)
        case "script":
            return _by_line(path, text, SCRIPT_COMMENTS)
        case _:
            return []
