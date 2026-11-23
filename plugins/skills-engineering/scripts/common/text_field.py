"""The rules every free-text field shares: a string, not blank, and within a length limit."""

from dataclasses import dataclass

from common.report import CheckResult, Finding, Surface
from common.yaml_reader import Node
from common.yaml_types import pyyaml_tag


@dataclass(frozen=True, slots=True)
class TextField:
    """A free-text field: the check that owns it, its key, its limit and its surfaces.

    `upload_strips` is true for a field the upload validator strips of surrounding whitespace
    before it counts the length (`quick_validate.py` does so for `description` only); the open
    specification's validator counts the raw value on every field.
    """

    check: str
    field: str
    limit: int
    surfaces: tuple[Surface, ...]
    upload_strips: bool = False

    def finding(
        self, node: Node, rule: str, expected: str, surfaces: tuple[Surface, ...] | None = None
    ) -> Finding:
        """An official finding on the field's value, on its surfaces unless others are given."""
        return Finding(
            check=self.check,
            rule=rule,
            line=node.line,
            column=node.column,
            field=self.field,
            found=node.value if node.kind == "scalar" else node.raw or None,
            expected=expected,
            basis="official",
            surfaces=self.surfaces if surfaces is None else surfaces,
        )

    def findings(self, node: Node) -> list[Finding]:
        """not-a-string, empty and too-long findings for the field's value.

        A scalar of another type fails uploads only: the open-spec validator, skills-ref, reads
        every scalar as a string through strictyaml. A collection or an alias fails both.
        """
        text = as_text(node)
        if text is None:
            surfaces = self.surfaces
            if node.kind == "scalar":
                surfaces = tuple(surface for surface in surfaces if surface != "open-spec")
            return [self.finding(node, "not-a-string", "A string.", surfaces)]
        if not text.strip():
            return [self.finding(node, "empty", "Some text, not only blanks.")]
        if len(text) > self.limit:
            expected = f"At most {self.limit:,} characters; this one has {len(text):,}."
            surfaces: tuple[Surface, ...] = self.surfaces
            if self.upload_strips and len(text.strip()) <= self.limit:
                surfaces = tuple(surface for surface in surfaces if surface != "upload")
            return [self.finding(node, "too-long", expected, surfaces)]
        return []


def as_text(node: Node) -> str | None:
    """The node's text when PyYAML, which uploads load with, reads it as a string, else None.

    An empty plain value reads as null, but it is reported as empty, not as another type.
    """
    if node.kind != "scalar":
        return None
    if node.style == "plain" and node.value == "" and node.tag is None:
        return ""
    return node.value if pyyaml_tag(node) == "str" else None


def not_run(check: str, skill: str, reason: str) -> CheckResult:
    """A result that didn't run."""
    return CheckResult(
        check=check, status="not_run", reason=reason, skill=skill, findings=[], data={}
    )
