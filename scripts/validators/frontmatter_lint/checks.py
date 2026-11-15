#!/usr/bin/env python3
"""The value rules of frontmatter-lint.

A colon goes only after a field name: no value holds a colon (FM-02) or is wrapped in quotes
(FM-03). The frontmatter must parse as strict YAML first (FM-01); a value with ": " fails here,
since Claude Code's own parser accepts it and `claude plugin validate --strict` passes it.
The one exception is a `<plugin>:<skill>` item of the top-level `skills` list, the qualified
name Claude Code requires for a plugin's skill.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import MarkedYAMLError, YAMLError
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, SingleQuotedScalarString

FENCE = "---"
BOM = "﻿"
YAML_START_LINE = 2
"""The file line where the YAML text begins, right after the opening fence."""
QUALIFIED_SKILL = re.compile(r"[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9-]*")
QUOTED = (SingleQuotedScalarString, DoubleQuotedScalarString)


@dataclass(frozen=True)
class Finding:
    """One rule broken at one file line."""

    rule: str
    line: int
    message: str


def _error_line(exc: YAMLError) -> int:
    """Return the file line a YAML error points at, or the first YAML line."""
    if isinstance(exc, MarkedYAMLError) and exc.problem_mark is not None:
        return exc.problem_mark.line + YAML_START_LINE
    return YAML_START_LINE


def _error_text(exc: YAMLError) -> str:
    """Return the first line of a YAML error."""
    problem = exc.problem if isinstance(exc, MarkedYAMLError) else None
    return (problem or str(exc)).strip().splitlines()[0]


def _value_findings(value: str, line: int, where: str) -> list[Finding]:
    """Check one text value."""
    found: list[Finding] = []
    if ":" in value:
        found.append(Finding("FM-02", line, f"{where} holds a colon; reword it"))
    if isinstance(value, QUOTED):
        found.append(Finding("FM-03", line, f"{where} is wrapped in quotes; write it plain"))
    return found


def _walk(node: object, line: int, where: str, *, in_skills: bool = False) -> list[Finding]:
    """Check every text value under node; line is node's own file line."""
    if isinstance(node, CommentedMap):
        found: list[Finding] = []
        for key, value in node.items():
            child_line = node.lc.value(key)[0] + YAML_START_LINE
            found += _walk(value, child_line, f"`{key}`")
        return found
    if isinstance(node, CommentedSeq):
        found = []
        for index, item in enumerate(node):
            item_line = node.lc.item(index)[0] + YAML_START_LINE
            if in_skills and isinstance(item, str) and QUALIFIED_SKILL.fullmatch(item):
                continue
            found += _walk(item, item_line, f"{where} item {index + 1}")
        return found
    if isinstance(node, str):
        return _value_findings(node, line, where)
    return []


def _parse(yaml_text: str) -> CommentedMap | Finding:
    """Parse the YAML between the fences, keeping how each value was quoted."""
    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    try:
        loaded = yaml.load(yaml_text)
    except YAMLError as exc:
        return Finding("FM-01", _error_line(exc), f"not strict YAML: {_error_text(exc)}")
    if not isinstance(loaded, CommentedMap):
        return Finding("FM-01", YAML_START_LINE, "frontmatter is not a mapping")
    return loaded


def check_text(text: str) -> list[Finding]:
    """Return the findings of one Markdown file; a file with no frontmatter has none."""
    lines = text.removeprefix(BOM).replace("\r\n", "\n").split("\n")
    if lines[0].rstrip() != FENCE:
        return []
    close = next((i for i, line in enumerate(lines[1:], 1) if line.rstrip() == FENCE), None)
    if close is None:
        return [Finding("FM-01", 1, "frontmatter is never closed with ---")]
    parsed = _parse("\n".join(lines[1:close]) + "\n")
    if isinstance(parsed, Finding):
        return [parsed]
    found: list[Finding] = []
    for key, value in parsed.items():
        line = parsed.lc.value(key)[0] + YAML_START_LINE
        found += _walk(value, line, f"`{key}`", in_skills=str(key) == "skills")
    return sorted(found, key=lambda finding: (finding.line, finding.rule))
