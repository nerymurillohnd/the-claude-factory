"""frontmatter.metadata: when present, a map of string keys to string values, no field names.

Claude Code drops a `metadata` value that isn't a map, and the open specification defines it as
a map from string keys to string values. Its validator reads every scalar as a string, so only
uploads, which load with PyYAML, type a scalar: `1.0` is a float and `yes` a boolean, while `y`
and `1e3` stay strings. A key named like a frontmatter field, such as `paths`, sets nothing.
"""

from typing import Final

from common.context import Context
from common.fields import CLAUDE_CODE_FIELDS
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import CheckResult, Finding, Surface
from common.text_field import not_run
from common.yaml_reader import Node
from common.yaml_types import pyyaml_tag

CHECK: Final = "frontmatter.metadata"
SPEC: Final[tuple[Surface, ...]] = ("open-spec", "upload")
UPLOAD: Final[tuple[Surface, ...]] = ("upload",)


def _finding(rule: str, node: Node, expected: str, surfaces: tuple[Surface, ...]) -> Finding:
    """An official finding on a node of the metadata map."""
    return Finding(
        check=CHECK,
        rule=rule,
        line=node.line,
        column=node.column,
        field="metadata",
        found=node.raw or None,
        expected=expected,
        basis="official",
        surfaces=surfaces,
    )


def _is_string(node: Node) -> bool:
    """True when PyYAML reads the node as a string."""
    if node.kind != "scalar":
        return False
    if node.style == "plain" and node.value == "" and node.tag is None:
        return False
    return pyyaml_tag(node) == "str"


def _surfaces(node: Node) -> tuple[Surface, ...]:
    """A collection breaks the map of strings everywhere; a typed scalar only on upload."""
    return SPEC if node.kind in {"map", "seq"} else UPLOAD


def _pair_findings(key: Node, value: Node) -> list[Finding]:
    """The findings of one key and its value."""
    found: list[Finding] = []
    if not _is_string(key):
        expected = "A string key; PyYAML, which uploads use, reads this one as another type."
        found.append(_finding("non-string-key", key, expected, _surfaces(key)))
    elif key.value in CLAUDE_CODE_FIELDS:
        expected = (
            f"A key that isn't a frontmatter field name: `{key.value}` here sets nothing; "
            "write it at the top level of the frontmatter."
        )
        found.append(_finding("reused-field-name", key, expected, ("claude-code",)))
    if not _is_string(value):
        expected = "A string value; quote it so PyYAML, which uploads use, keeps it as text."
        if value.kind in {"map", "seq"}:
            expected = "A string value, not a list or a mapping."
        found.append(_finding("non-string-value", value, expected, _surfaces(value)))
    return found


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.metadata on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    pair = loaded.fields.get("metadata")
    findings: list[Finding] = []
    if pair is not None:
        node = pair[1]
        if node.kind == "map":
            for key, value in node.pairs:
                findings.extend(_pair_findings(key, value))
        else:
            expected = "A map of string keys to string values; Claude Code drops anything else."
            surfaces: tuple[Surface, ...] = ("claude-code", "open-spec", "upload")
            findings.append(_finding("not-a-map", node, expected, surfaces))
    data: dict[str, object] = {
        "present": pair is not None,
        "keys": 0 if pair is None else len(pair[1].pairs),
        "schema": "pyyaml",
    }
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
