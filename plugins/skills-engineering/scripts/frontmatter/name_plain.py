"""frontmatter.name-plain: the name written as one plain line, so its text is the parsed name.

A project convention, not an official rule: tools that read the name as text and YAML parsers
agree only when the name is plain, on one line, with no anchor, alias or tag, and not a value
PyYAML, which uploads load with, reads as a number or a date. Booleans and null are
frontmatter.plain-values' findings.
"""

from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import CheckResult, Finding
from common.yaml_reader import Node
from common.yaml_types import pyyaml_tag

CHECK: Final = "frontmatter.name-plain"
YAML11_TYPES: Final = frozenset({"int", "float", "timestamp"})


def _finding(rule: str, node: Node, expected: str) -> Finding:
    """A convention finding on the name's value."""
    return Finding(
        check=CHECK,
        rule=rule,
        line=node.line,
        column=node.column,
        field="name",
        found=node.raw,
        expected=expected,
        basis="convention",
        surfaces=(),
    )


def _findings(node: Node) -> list[Finding]:
    """Every way the name's value isn't one plain line."""
    found: list[Finding] = []
    if node.style in {"single", "double"}:
        found.append(_finding("quoted", node, "Write the name without quotes."))
    if node.style in {"literal", "folded"}:
        found.append(_finding("block-scalar", node, "Write the name on the key's line."))
    if node.style in {"plain", "single", "double"} and node.line != node.end_line:
        found.append(_finding("multi-line", node, "Write the name on one line."))
    if node.kind == "alias" or node.anchor is not None or node.tag is not None:
        found.append(_finding("anchor-alias-tag", node, "Write the name with no anchor or tag."))
    if node.kind == "scalar" and node.style == "plain" and node.tag is None:
        tag = pyyaml_tag(node)
        if tag in YAML11_TYPES:
            expected = (
                f"A name PyYAML, which uploads use, reads as text; this one reads as a {tag}."
            )
            found.append(
                Finding(
                    check=CHECK,
                    rule="yaml11-type",
                    line=node.line,
                    column=node.column,
                    field="name",
                    found=node.raw,
                    expected=expected,
                    basis="inference",
                    surfaces=("upload",),
                )
            )
    return found


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.name-plain on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return CheckResult(
            check=CHECK,
            status="not_run",
            reason=NO_BLOCK_REASON,
            skill=ctx.folder_name,
            findings=[],
            data={},
        )
    pair = loaded.fields.get("name")
    findings = [] if pair is None else _findings(pair[1])
    return CheckResult(
        check=CHECK, status="ran", reason=None, skill=ctx.folder_name, findings=findings, data={}
    )
