"""frontmatter.plain-values: plain values a YAML parser reads differently than they are written.

A ` #` cuts the value there; a leading `-`, `?` or `:` reads as YAML syntax in strict parsers;
a text field written as a collection, or with an anchor, alias or tag, isn't plain text; and
text such as `yes` or `~` becomes a boolean or null. `: ` inside a value is frontmatter.yaml's.
"""

from dataclasses import replace
from typing import Final

from common.context import Context
from common.fields import SPEC_FIELDS, TEXT_FIELDS
from common.frontmatter import NO_BLOCK_REASON, Loaded, load, values
from common.report import CheckResult, Finding, Surface
from common.yaml_reader import Node
from common.yaml_types import pyyaml_tag

CHECK: Final = "frontmatter.plain-values"
YAML11_BOOLEANS: Final = frozenset({"yes", "no", "on", "off"})
BOOLEANS: Final = frozenset({"true", "false"}) | YAML11_BOOLEANS
NULLS: Final = frozenset({"null", "~"})
LEADING_INDICATORS: Final = "-?:"
UPLOAD: Final[tuple[Surface, ...]] = ("upload",)
YAML11_CONDITION: Final = (
    "YAML 1.1 parsers, such as PyYAML, read it as a boolean; YAML 1.2 keeps it as text"
)


def _finding(rule: str, node: Node, field: str, expected: str) -> Finding:
    """A finding at the node's position, quoting its source text.

    A specification field is read by open-spec and upload, any other field by Claude Code.
    """
    surfaces: tuple[Surface, ...] = (
        ("open-spec", "upload") if field in SPEC_FIELDS else ("claude-code",)
    )
    return Finding(
        check=CHECK,
        rule=rule,
        line=node.line,
        column=node.column,
        field=field,
        found=node.raw,
        expected=expected,
        basis="inference",
        surfaces=surfaces,
    )


def _comment(loaded: Loaded, node: Node, field: str) -> Finding | None:
    """A comment after a plain value on its last line."""
    last = node.raw.split("\n")[-1]
    end = node.column - 1 + len(last) if node.line == node.end_line else len(last)
    text = loaded.line_text(node.end_line)
    rest = text[end:]
    stripped = rest.lstrip(" \t")
    if not stripped.startswith("#") or rest[:1] not in {" ", "\t"}:
        return None
    start = node.column - 1 if node.line == node.end_line else 0
    expected = "Quote the value: ` #` starts a comment, so the text after it is dropped."
    return replace(
        _finding("comment-truncates", node, field, expected),
        line=node.end_line,
        column=end + len(rest) - len(stripped) + 1,
        found=text[start:].rstrip(" \t"),
    )


def _boolean_or_null(node: Node, field: str) -> Finding | None:
    """A plain value read as a boolean or null.

    The open-spec validator, skills-ref, reads every scalar of a specification field as a string
    through strictyaml, so there the finding is on uploads only, and only when PyYAML, which
    uploads load with, types the value; `yEs` stays text to PyYAML and gives none.
    """
    if field in SPEC_FIELDS:
        tag = pyyaml_tag(node)
        if tag not in {"bool", "null"}:
            return None
        rule = "reads-as-boolean" if tag == "bool" else "reads-as-null"
        expected = "Quote the value so uploads read it as text."
        return replace(_finding(rule, node, field, expected), surfaces=UPLOAD)
    lowered = node.value.lower()
    if lowered in BOOLEANS:
        return replace(
            _finding("reads-as-boolean", node, field, "Quote the value so it stays text."),
            condition=YAML11_CONDITION if lowered in YAML11_BOOLEANS else None,
        )
    if lowered in NULLS:
        return _finding("reads-as-null", node, field, "Quote the value so it stays text.")
    return None


def _plain_findings(loaded: Loaded, node: Node, field: str) -> list[Finding]:
    """The comment and leading-indicator findings of one plain scalar."""
    found: list[Finding] = []
    comment = _comment(loaded, node, field)
    if comment is not None:
        found.append(comment)
    if node.value[:1] in LEADING_INDICATORS and node.value:
        # YAML 1.2 and PyYAML read `-x` as plain text; quoting it is a convention, not a fix.
        found.append(
            replace(
                _finding(
                    "leading-indicator",
                    node,
                    field,
                    "Quote a value that starts with `-`, `?` or `:`.",
                ),
                basis="convention",
            )
        )
    return found


def _text_field(field: str, value: Node) -> list[Finding]:
    """The findings of a field whose value should be plain text."""
    if value.kind in {"seq", "map"}:
        expected = "Quote the value: brackets or braces make it a list or a mapping, not text."
        if value.style != "flow":
            expected = "Write the value as text on the key's line, not as a list or a mapping."
        return [
            replace(
                _finding("reads-as-collection", value, field, expected), found=value.raw or None
            )
        ]
    if value.kind == "alias" or value.anchor is not None or value.tag is not None:
        expected = "Write the text itself, with no anchor, alias or tag."
        return [
            replace(
                _finding("anchor-alias-tag", value, field, expected), found=_with_properties(value)
            )
        ]
    if value.style == "plain" and value.value:
        found = _boolean_or_null(value, field)
        return [] if found is None else [found]
    return []


def _with_properties(value: Node) -> str:
    """The value's text, with its anchor or tag when it has one."""
    parts = [f"&{value.anchor}" if value.anchor else "", value.tag or "", value.raw]
    return " ".join(part for part in parts if part)


def _not_run(ctx: Context) -> CheckResult:
    """No mapping to read."""
    return CheckResult(
        check=CHECK,
        status="not_run",
        reason=NO_BLOCK_REASON,
        skill=ctx.folder_name,
        findings=[],
        data={},
    )


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.plain-values on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return _not_run(ctx)
    findings: list[Finding] = []
    for field, (_key, value) in loaded.fields.items():
        if field in TEXT_FIELDS:
            findings.extend(_text_field(field, value))
        for node in values(value):
            if node.kind == "scalar" and node.style == "plain" and node.value:
                findings.extend(_plain_findings(loaded, node, field))
                if field == "metadata":
                    extra = _boolean_or_null(node, field)
                    findings.extend([] if extra is None else [extra])
    return CheckResult(
        check=CHECK,
        status="ran",
        reason=None,
        skill=ctx.folder_name,
        findings=findings,
        data={"colon_cases": "reported by frontmatter.yaml"},
    )
