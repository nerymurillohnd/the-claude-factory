"""frontmatter.field-values: the values Claude Code documents for its typed fields.

The booleans take a documented boolean form, `context` is `fork`, `effort` is a documented
level, `model` is an alias /model accepts, `inherit` or a full model id, and `disallowed-tools`,
`paths` and `arguments` are a string or a list of strings. A non-string `allowed-tools` and an
unknown `shell` are left to claude plugin validate, which rejects both.
"""

from dataclasses import replace
import re
from typing import Final

from common.context import Context
from common.fields import BOOLEAN_FIELDS, BOOLEAN_FORMS, EFFORT_LEVELS, MODEL_VALUES
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import Basis, CheckResult, Finding
from common.text_field import not_run
from common.yaml_reader import Node
from common.yaml_types import yaml11_tag

CHECK: Final = "frontmatter.field-values"
LIST_FIELDS: Final = ("disallowed-tools", "paths", "arguments")
CHECKED_FIELDS: Final = (*BOOLEAN_FIELDS, "context", "effort", "model", *LIST_FIELDS)
MODEL_ID: Final = re.compile(r"^(claude-|anthropic\.|[a-z]{2,4}\.anthropic\.|arn:)")
QUOTED_CONDITION: Final = "quoted: unverified whether Claude Code reads it as a boolean"
LEFT_TO_VALIDATE: Final = ("allowed-tools", "shell")


def _finding(rule: str, field: str, node: Node, expected: str, basis: Basis) -> Finding:
    """A finding on a field's value, quoting its source text."""
    return Finding(
        check=CHECK,
        rule=rule,
        line=node.line,
        column=node.column,
        field=field,
        found=node.raw or None,
        expected=expected,
        basis=basis,
        surfaces=("claude-code",),
    )


def _is_null(node: Node) -> bool:
    """True when the value is empty or YAML 1.1 reads it as null."""
    if node.kind != "scalar":
        return False
    if node.style == "plain" and node.value == "" and node.tag is None:
        return True
    return yaml11_tag(node) == "null"


def _is_string(node: Node) -> bool:
    """True when YAML 1.1 reads the node as a non-empty-plain string."""
    return node.kind == "scalar" and not _is_null(node) and yaml11_tag(node) == "str"


def _boolean(field: str, node: Node) -> list[Finding]:
    """A boolean-form finding for a value outside the documented forms, or a quoted one."""
    forms = ", ".join(f"`{form}`" for form in sorted(BOOLEAN_FORMS))
    expected = f"A boolean form, unquoted: one of {forms}, in any case."
    if node.kind == "scalar" and node.style != "plain":
        finding = _finding("boolean-form", field, node, expected, "inference")
        return [replace(finding, condition=QUOTED_CONDITION)]
    plain = node.kind == "scalar" and node.style == "plain"
    if (
        plain
        and node.value.lower() in BOOLEAN_FORMS
        and (node.tag is None or yaml11_tag(node) == "bool")
    ):
        return []
    return [_finding("boolean-form", field, node, expected, "official")]


def _one_of(field: str, node: Node, allowed: tuple[str, ...], rule: str) -> list[Finding]:
    """A finding unless the value is a string among the allowed ones."""
    if _is_string(node) and node.value in allowed:
        return []
    choices = ", ".join(f"`{value}`" for value in allowed)
    return [_finding(rule, field, node, f"One of {choices}.", "official")]


def _string_or_list(field: str, node: Node) -> list[Finding]:
    """A finding unless the value is a string or a list of strings."""
    if _is_string(node):
        return []
    if node.kind == "seq" and all(_is_string(item) for item in node.items):
        return []
    expected = "A string, or a list of strings; quote any item YAML 1.1 reads as another type."
    return [_finding("string-or-list", field, node, expected, "official")]


def _model(node: Node) -> tuple[list[Finding], bool]:
    """The model finding, and whether the value is a full model id left unchecked."""
    if _is_string(node) and node.value in MODEL_VALUES:
        return [], False
    if _is_string(node) and MODEL_ID.match(node.value) is not None:
        return [], True
    aliases = ", ".join(f"`{value}`" for value in MODEL_VALUES)
    expected = f"An alias /model accepts ({aliases}) or a full Claude model id."
    return [_finding("model-value", "model", node, expected, "inference")], False


def _field_findings(field: str, node: Node) -> list[Finding]:
    """The findings of one checked field other than model."""
    if field in BOOLEAN_FIELDS:
        return _boolean(field, node)
    if field == "context":
        return _one_of(field, node, ("fork",), "context-value")
    if field == "effort":
        return _one_of(field, node, EFFORT_LEVELS, "effort-value")
    return _string_or_list(field, node)


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.field-values on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    findings: list[Finding] = []
    model_id_unchecked = False
    for field in CHECKED_FIELDS:
        pair = loaded.fields.get(field)
        if pair is None:
            continue
        node = pair[1]
        if _is_null(node):
            expected = "A value, or no field at all."
            findings.append(_finding("empty-value", field, node, expected, "official"))
        elif field == "model":
            found, model_id_unchecked = _model(node)
            findings.extend(found)
        else:
            findings.extend(_field_findings(field, node))
    data: dict[str, object] = {
        "model_id_unchecked": model_id_unchecked,
        "left_to_validate": list(LEFT_TO_VALIDATE),
    }
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
