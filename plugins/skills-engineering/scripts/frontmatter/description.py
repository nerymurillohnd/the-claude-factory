"""frontmatter.description: present, a non-blank string, at most 1,024 characters, no `<` or `>`.

Claude chooses the skill by its description. The open specification and uploads require one of
1 to 1,024 characters (the upload validator counts it after stripping surrounding whitespace),
the upload validator rejects `<` and `>`, and Claude Code shows them as `&lt;` and `&gt;` in
`description` and `when_to_use`. Without one, Claude Code uses the first non-empty line of the
body.
"""

import re
from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import CheckResult, Finding
from common.text import utf16_len
from common.text_field import TextField, as_text, not_run

CHECK: Final = "frontmatter.description"
MAX_LENGTH: Final = 1024
FIELD: Final = TextField(
    CHECK, "description", MAX_LENGTH, ("open-spec", "upload"), upload_strips=True
)
XML_TAG: Final = re.compile(r"<[A-Za-z/!?][^<>]*>")


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.description on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    pair = loaded.fields.get("description")
    if pair is None:
        missing = Finding(
            check=CHECK,
            rule="missing",
            line=None,
            column=None,
            field="description",
            found=None,
            expected="A `description`: the open specification and uploads require one.",
            basis="official",
            surfaces=("open-spec", "upload"),
        )
        data: dict[str, object] = {
            "length": None,
            "utf16_length": None,
            "xml_tags": [],
            "claude_code_fallback": "first non-empty body line",
        }
        return CheckResult(CHECK, "ran", None, ctx.folder_name, [missing], data)
    node = pair[1]
    findings = FIELD.findings(node)
    text = as_text(node) or ""
    if "<" in text or ">" in text:
        findings.append(
            Finding(
                check=CHECK,
                rule="angle-bracket",
                line=node.line,
                column=node.column,
                field="description",
                found=text,
                expected="No `<` or `>`: uploads reject them and Claude Code shows them escaped.",
                basis="official",
                surfaces=("claude-code", "upload"),
            )
        )
    when = loaded.fields.get("when_to_use")
    when_text = as_text(when[1]) if when is not None else None
    if when is not None and when_text is not None and ("<" in when_text or ">" in when_text):
        findings.append(
            Finding(
                check=CHECK,
                rule="angle-bracket",
                line=when[1].line,
                column=when[1].column,
                field="when_to_use",
                found=when_text,
                expected="No `<` or `>`: Claude Code shows them escaped in the skill listing.",
                basis="official",
                surfaces=("claude-code",),
            )
        )
    data = {
        "length": len(text),
        "utf16_length": utf16_len(text),
        "xml_tags": XML_TAG.findall(text),
        "claude_code_fallback": None,
    }
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
