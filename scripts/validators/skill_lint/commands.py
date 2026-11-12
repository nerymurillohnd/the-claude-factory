"""Command extraction: what a skill's Markdown runs and what its scripts call."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import re
from typing import TYPE_CHECKING
import warnings

from validators.skill_lint.script_refs import is_shell

if TYPE_CHECKING:
    from collections.abc import Iterator

    from validators.skill_lint.markdown import MarkdownDoc

RUN_LANGS = frozenset({"bash", "sh", "shell", "console", "zsh"})
INTERPRETER_WORDS = frozenset({"python3", "python", "uv", "bash", "sh", "node"})
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|&\n]|\$\(|`|\bthen\b|\bdo\b|\belse\b")
ASSIGNMENT = re.compile(r"^[A-Za-z_]\w*=")
COMMAND_WORD = re.compile(r"^[A-Za-z][\w.+-]*$")
FUNCTION_DEF = re.compile(r"^\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\s*\)")
PREFIX_WORDS = frozenset({"if", "elif", "while", "until", "!", "time", "exec", "sudo", "{", "("})
SUBPROCESS_CALLS = frozenset({"run", "call", "check_call", "check_output", "Popen"})
TOKEN = re.compile(r"\S+")
BUILTINS = frozenset(
    TOKEN.findall(
        """
    alias break case cd command continue declare do done elif else esac eval exec exit
    export fi for function getopts hash if in kill let local printf pwd read readonly
    return select set shift source then trap type ulimit umask unalias unset until wait
    while . : [ [[ ]]
"""
    )
)
"""Shell builtins and keywords, never reported as external commands."""
BASELINE = frozenset(
    TOKEN.findall(
        """
    cat cp mv rm mkdir ls ln chmod find grep sed awk head tail sort uniq wc tr cut xargs
    dirname basename date env mktemp tee printf echo test true false sleep
"""
    )
)
"""POSIX and coreutils commands every target system has."""


@dataclass(frozen=True)
class Command:
    """One simple command: its words and the 1-based line it is on."""

    words: tuple[str, ...]
    line: int


def _strip_comment(line: str) -> str:
    """Drop a shell comment that starts a line or follows whitespace."""
    if line.lstrip().startswith("#"):
        return ""
    return re.split(r"\s#", line, maxsplit=1)[0]


def _segments(text: str, first_line: int) -> Iterator[tuple[str, int]]:
    """Yield each simple-command segment of shell text with its line."""
    for offset, raw in enumerate(text.split("\n")):
        line = _strip_comment(raw.removeprefix("$ ").removeprefix("> "))
        for segment in SEGMENT_SPLIT.split(line):
            if segment.strip():
                yield segment, first_line + offset


def _words(segment: str) -> tuple[str, ...]:
    """Split a segment into words, unquoting them and dropping leading assignments."""
    words = [word.strip("\"'") for word in segment.split()]
    while words and (ASSIGNMENT.match(words[0]) or words[0] in PREFIX_WORDS):
        _ = words.pop(0)
    return tuple(word for word in words if word)


def shell_commands(text: str, first_line: int = 1) -> list[Command]:
    """Return the simple commands of shell text, each with its words."""
    found: list[Command] = []
    for segment, line in _segments(text, first_line):
        words = _words(segment)
        if words:
            found.append(Command(words, line))
    return found


def run_contexts(doc: MarkdownDoc) -> list[Command]:
    """Return the commands a Markdown file runs.

    Run contexts are injected commands, fences tagged bash, sh, shell, console or zsh, and
    inline code whose first word is an interpreter.
    """
    found: list[Command] = []
    for bang in doc.bang_commands:
        found += shell_commands(bang.command, bang.line)
    for snippet in doc.code:
        if snippet.inline:
            first = snippet.text.split(maxsplit=1)[:1]
            if first and first[0] in INTERPRETER_WORDS:
                found += shell_commands(snippet.text, snippet.line)
        elif (snippet.lang or "").lower() in RUN_LANGS:
            found += shell_commands(snippet.text, snippet.line + 1)
    return found


def shell_functions(text: str) -> set[str]:
    """Return the names of the functions a shell script defines."""
    return {m.group(1) for line in text.split("\n") if (m := FUNCTION_DEF.match(line))}


def _literal_command(node: ast.expr) -> str | None:
    """Return the program a subprocess argument names, when it is a literal."""
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        first = node.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        words = node.value.split()
        return words[0] if words else None
    return None


def _called_name(node: ast.Call) -> tuple[str, str] | None:
    """Return (module, function) for a call such as subprocess.run(...)."""
    func = node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id, func.attr
    return None


def python_commands(text: str) -> list[Command]:
    """Return the programs a Python script runs or looks up, from literal arguments."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            tree = ast.parse(text)
        except SyntaxError, ValueError:
            return []
    found: list[Command] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        called = _called_name(node)
        wanted = called is not None and (
            (called[0] == "subprocess" and called[1] in SUBPROCESS_CALLS)
            or called == ("shutil", "which")
        )
        program = _literal_command(node.args[0]) if wanted else None
        if program is not None:
            found.append(Command((program,), node.lineno))
    return found


def script_commands(rel: str, text: str) -> list[Command]:
    """Return the commands one script file calls (shell or Python)."""
    if rel.endswith(".py"):
        return python_commands(text)
    if is_shell(rel, text):
        defined = shell_functions(text)
        return [c for c in shell_commands(text) if c.words[0] not in defined]
    return []


def is_command_word(word: str) -> bool:
    """Tell whether a word can name a program on PATH."""
    return COMMAND_WORD.match(word) is not None
