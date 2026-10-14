"""Line-accurate reading of Codex TOML config and Starlark rules, standard library only.

Python 3.9 has no TOML parser, so this reader handles the shapes Codex config uses (tables,
dotted keys, strings, numbers, booleans, arrays, inline tables) and records each assignment's
line span. When the interpreter ships tomllib (3.11+), validate() also proves the file parses;
without it the result is "unknown", never a guessed error.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import re
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable

TABLE = re.compile(r"^\s*\[\[?\s*(.+?)\s*\]\]?\s*(?:#.*)?$")
BARE_KEY = re.compile(r"[A-Za-z0-9_-]+")
INTEGER = re.compile(r"^[+-]?\d[\d_]*$")
EMPTY_ARRAY = re.compile(r"^\[\s*\]$")
CLOSERS = {"[": "]", "{": "}"}
TRIPLE = ('"""', "'''")
TRIPLE_PAIR = 2
KEY_PART = re.compile(r'"((?:[^"\\]|\\.)*)"|\'([^\']*)\'|([A-Za-z0-9_-]+)')


@dataclass(frozen=True)
class Entry:
    """One key assignment: its table, dotted key, decoded value and 1-based line span."""

    table: tuple[str, ...]
    key: tuple[str, ...]
    value: object
    start: int
    end: int

    @property
    def path(self) -> str:
        """Return the full dotted name."""
        return ".".join((*self.table, *self.key))


def split_key(text: str) -> tuple[str, ...]:
    """Split a dotted TOML key, honoring quoted parts."""
    return tuple(
        next(group for group in match.groups() if group is not None)
        for match in KEY_PART.finditer(text)
    )


def _string_end(text: str, start: int) -> int:
    """Index just past the string literal opening at start (or the end of text)."""
    quote = text[start]
    index = start + 1
    while index < len(text):
        if quote == '"' and text[index] == "\\":
            index += 2
            continue
        if text[index] == quote:
            return index + 1
        index += 1
    return len(text)


def _balanced(text: str) -> bool:
    """True when every [ and { outside strings is closed."""
    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if char in "\"'":
            index = _string_end(text, index)
            continue
        if char == "#":
            newline = text.find("\n", index)
            index = len(text) if newline == -1 else newline
            continue
        depth += 1 if char in CLOSERS else -1 if char in CLOSERS.values() else 0
        index += 1
    return depth <= 0


def _decode_string(raw: str) -> str:
    if raw.startswith(TRIPLE):
        return raw[3:-3].removeprefix("\n")
    if raw.startswith("'"):
        return raw[1:-1]
    return raw[1:-1].encode("utf-8").decode("unicode_escape", errors="replace")


def _strings_in(raw: str) -> list[str]:
    values: list[str] = []
    index = 0
    while index < len(raw):
        if raw[index] in "\"'":
            end = _string_end(raw, index)
            values.append(_decode_string(raw[index:end]))
            index = end
        else:
            index += 1
    return values


def decode(raw: str) -> object:
    """Decode the value shapes the audit checks; anything else stays as its source text."""
    text = raw.strip()
    if text.startswith(TRIPLE) or text[:1] in "\"'":
        return _decode_string(text)
    if text in {"true", "false"}:
        return text == "true"
    if INTEGER.match(text):
        return int(text.replace("_", ""))
    if text.startswith("["):
        strings = _strings_in(text)
        return strings if strings or EMPTY_ARRAY.match(text) else text
    return text


def _without_comment(line: str) -> str:
    index = 0
    while index < len(line):
        if line[index] in "\"'":
            index = _string_end(line, index)
            continue
        if line[index] == "#":
            return line[:index]
        index += 1
    return line


def _value_span(lines: list[str], index: int, first: str) -> tuple[str, int]:
    """Collect a value that may continue over several lines; returns (raw, last index)."""
    raw = first
    last = index
    opened = first.lstrip()
    if opened.startswith(TRIPLE):
        marker = opened[:3]
        while opened.count(marker) < TRIPLE_PAIR and last + 1 < len(lines):
            last += 1
            raw += "\n" + lines[last]
            opened = raw.lstrip()
        return raw, last
    while not _balanced(raw) and last + 1 < len(lines):
        last += 1
        raw += "\n" + lines[last]
    return raw, last


def entries(lines: list[str]) -> tuple[list[Entry], list[str]]:
    """Read every assignment with its table; returns (entries, lines that could not be read)."""
    found: list[Entry] = []
    unreadable: list[str] = []
    table: tuple[str, ...] = ()
    index = 0
    while index < len(lines):
        line = _without_comment(lines[index]).strip()
        header = TABLE.match(lines[index])
        if not line:
            index += 1
            continue
        if header:
            table = split_key(header.group(1))
            index += 1
            continue
        if "=" not in line:
            unreadable.append(f"line {index + 1}: {lines[index].strip()}")
            index += 1
            continue
        key_text, _, rest = line.partition("=")
        raw, last = _value_span(lines, index, rest)
        found.append(Entry(table, split_key(key_text), decode(raw), index + 1, last + 1))
        index = last + 1
    return found, unreadable


def validate(text: str) -> str | None:
    """Prove the TOML parses with tomllib: '' when valid, the error when not, None if unknown."""
    try:
        module = importlib.import_module("tomllib")
    except ImportError:
        return None
    parse = cast("Callable[[str], object]", module.loads)
    error_type = cast("type[Exception]", module.TOMLDecodeError)
    try:
        _ = parse(text)
    except error_type as error:
        return str(error)
    return ""


def starlark_calls(lines: list[str]) -> list[tuple[int, int, str]]:
    """Top-level statements of a Codex .rules file, as (start, end, text) with balanced parens."""
    found: list[tuple[int, int, str]] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        start = index
        text = lines[index]
        depth = text.count("(") - text.count(")")
        while depth > 0 and index + 1 < len(lines):
            index += 1
            text += "\n" + lines[index]
            depth += lines[index].count("(") - lines[index].count(")")
        found.append((start + 1, index + 1, text))
        index += 1
    return found
