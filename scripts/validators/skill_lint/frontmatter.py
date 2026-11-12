"""Strict parsing of the YAML frontmatter at the top of a SKILL.md."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import MarkedYAMLError, StreamMark as Mark, YAMLError

if TYPE_CHECKING:
    from collections.abc import Mapping

FENCE = "---"
BOM = "﻿"
YAML_START_LINE = 2
"""The file line where the YAML text begins, right after the opening fence."""


@dataclass(frozen=True)
class Frontmatter:
    """The parsed frontmatter of a SKILL.md, or the reason it could not be parsed."""

    data: Mapping[str, object] | None
    key_lines: Mapping[str, int]
    """The 1-based file line of each top-level key."""
    body_start: int
    """The first line after the closing fence."""
    error: tuple[int, str] | None


def _failure(line: int, message: str, body_start: int = 1) -> Frontmatter:
    """Build the result for a frontmatter that cannot be used."""
    return Frontmatter(None, {}, body_start, (line, message))


def _find_close(lines: list[str]) -> int | None:
    """Return the 0-based index of the closing fence, or None when it is missing."""
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip() == FENCE:
            return index
    return None


def _error_line(exc: YAMLError) -> int:
    """Return the file line a YAML error points at, or the first YAML line."""
    if isinstance(exc, MarkedYAMLError):
        mark = cast("Mark | None", exc.problem_mark)
        if mark is not None:
            return mark.line + YAML_START_LINE
    return YAML_START_LINE


def _error_text(exc: YAMLError) -> str:
    """Return a one-line message for a YAML error, naming duplicate keys as such."""
    problem = cast("str | None", exc.problem) if isinstance(exc, MarkedYAMLError) else None
    return (problem or str(exc)).strip().splitlines()[0]


def _load(yaml_text: str) -> Frontmatter:
    """Parse the YAML text between the fences into a Frontmatter."""
    yaml = YAML(typ="rt")
    yaml.allow_duplicate_keys = False
    try:
        loaded = cast("object", yaml.load(yaml_text))  # pyright: ignore[reportUnknownMemberType]
    except YAMLError as exc:
        return _failure(_error_line(exc), _error_text(exc))
    if not isinstance(loaded, CommentedMap):
        kind = "empty" if loaded is None else type(loaded).__name__
        return _failure(YAML_START_LINE, f"frontmatter must be a mapping, found {kind}")
    data: dict[str, object] = {}
    key_lines: dict[str, int] = {}
    mapping = loaded
    for key in cast("list[object]", list(mapping)):
        name = str(key)
        data[name] = cast("object", mapping[key])
        line = cast("tuple[int, int]", mapping.lc.key(key))[0]  # pyright: ignore[reportUnknownMemberType]
        key_lines[name] = line + YAML_START_LINE
    return Frontmatter(data, key_lines, 1, None)


def parse_frontmatter(text: str) -> Frontmatter:
    """Parse the frontmatter of a SKILL.md, after stripping a BOM and normalizing CRLF."""
    text = text.removeprefix(BOM).replace("\r\n", "\n")
    lines = text.split("\n")
    if lines[0].rstrip() != FENCE:
        return _failure(1, "frontmatter must open with --- on line 1")
    close = _find_close(lines)
    if close is None:
        return _failure(1, "frontmatter is never closed with ---")
    parsed = _load("\n".join(lines[1:close]) + "\n")
    if parsed.error is not None:
        return Frontmatter(None, {}, close + 2, parsed.error)
    return Frontmatter(parsed.data, parsed.key_lines, close + 2, None)
