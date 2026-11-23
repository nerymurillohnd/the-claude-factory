"""frontmatter.compatibility: when present, a string of 1 to 500 characters.

The open specification and Claude Code both limit `compatibility` to 500 characters.
"""

from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import CheckResult
from common.text import utf16_len
from common.text_field import TextField, as_text, not_run

CHECK: Final = "frontmatter.compatibility"
MAX_LENGTH: Final = 500
FIELD: Final = TextField(CHECK, "compatibility", MAX_LENGTH, ("open-spec", "upload"))


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.compatibility on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    pair = loaded.fields.get("compatibility")
    if pair is None:
        data: dict[str, object] = {"length": None, "utf16_length": None}
        return CheckResult(CHECK, "ran", None, ctx.folder_name, [], data)
    node = pair[1]
    findings = FIELD.findings(node)
    text = as_text(node) or ""
    data = {"length": len(text), "utf16_length": utf16_len(text)}
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
