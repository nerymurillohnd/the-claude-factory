"""frontmatter.field-combinations: fields that cancel each other, so part of the skill does nothing.

`agent` and `background` apply only with `context: fork`, as the frontmatter reference says.
That `disable-model-invocation: true` with `user-invocable: false` leaves nobody to invoke the
skill, and that it makes `paths` do nothing, follow from what each field means: inferences.
"""

from typing import Final

from common.context import Context
from common.fields import BOOLEAN_FORMS
from common.frontmatter import NO_BLOCK_REASON, Loaded, load
from common.report import Basis, CheckResult, Finding
from common.text_field import not_run
from common.yaml_reader import Node
from common.yaml_types import yaml11_tag

CHECK: Final = "frontmatter.field-combinations"
TRUE_FORMS: Final = frozenset({"true", "yes", "on", "1"})
FORK_ONLY_FIELDS: Final = ("agent", "background")


def _finding(rule: str, field: str, node: Node, expected: str, basis: Basis) -> Finding:
    """A finding on one field of the combination."""
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


def _flag(loaded: Loaded, field: str) -> bool | None:
    """A boolean field's value when it is a plain boolean form, else None."""
    pair = loaded.fields.get(field)
    if pair is None or pair[1].kind != "scalar" or pair[1].style != "plain":
        return None
    text = pair[1].value.lower()
    return text in TRUE_FORMS if text in BOOLEAN_FORMS else None


def _present(loaded: Loaded, field: str) -> Node | None:
    """The field's value when the field is present with a value that isn't null."""
    pair = loaded.fields.get(field)
    if pair is None:
        return None
    node = pair[1]
    empty = node.style == "plain" and node.value == "" and node.tag is None
    if node.kind == "scalar" and (empty or yaml11_tag(node) == "null"):
        return None
    return node


def _invocation_findings(loaded: Loaded) -> list[Finding]:
    """The uninvocable and paths-ignored findings, both from disable-model-invocation: true."""
    pair = loaded.fields.get("disable-model-invocation")
    if pair is None or _flag(loaded, "disable-model-invocation") is not True:
        return []
    found: list[Finding] = []
    if _flag(loaded, "user-invocable") is False:
        expected = (
            "Let Claude or the user invoke the skill: with `disable-model-invocation: true` "
            "and `user-invocable: false`, nobody can."
        )
        found.append(
            _finding("uninvocable", "disable-model-invocation", pair[1], expected, "inference")
        )
    paths = _present(loaded, "paths")
    if paths is not None:
        expected = (
            "Drop `paths` or `disable-model-invocation: true`: `paths` limits when Claude "
            "loads the skill on its own, which it never does here."
        )
        found.append(_finding("paths-ignored", "paths", paths, expected, "inference"))
    return found


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.field-combinations on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    findings = _invocation_findings(loaded)
    context = _present(loaded, "context")
    forked = context is not None and context.kind == "scalar" and context.value == "fork"
    if not forked:
        for field in FORK_ONLY_FIELDS:
            node = _present(loaded, field)
            if node is not None:
                expected = f"`context: fork`, or no `{field}`: it applies only to a forked skill."
                findings.append(_finding("fork-only-field", field, node, expected, "official"))
    data: dict[str, object] = {
        "disable_model_invocation": _flag(loaded, "disable-model-invocation"),
        "user_invocable": _flag(loaded, "user-invocable"),
        "forked": forked,
    }
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
