"""frontmatter.yaml: the frontmatter against strict YAML, and bytes that aren't UTF-8.

validate reports a missing block and a root that isn't a mapping, so those give `not_run`. Four
failures it passes, and Claude Code accepts, are findings: packaging and upload reject them. An
unclosed quote, a tab in the indentation and other syntax errors are findings too, because
validate reports them only in some positions (on 2.1.326, not a quote inside `[ ]`, a tab before
a nested key, or a value starting with `[`, `` ` `` or `@`). YAML the reader doesn't support,
and nesting past its depth limit, give `not_run`.
"""

from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, Loaded, load
from common.report import Basis, CheckResult, Finding
from common.yaml_reader import ReadError
from common.yaml_source import colon_at

CHECK: Final = "frontmatter.yaml"
CONDITION: Final = "Claude Code accepted it when tested; packaging and upload reject it"
VALIDATE_POSITION_CONDITION: Final = (
    "claude plugin validate reports it in some positions, and then Claude Code loads the skill "
    "with no fields set; read its output for this file"
)

LATIN1_CONDITION: Final = "claude plugin validate reported nothing for such a byte when tested"
UTF16_CONDITION: Final = "claude plugin validate reports only that it found no frontmatter block"

# The reader's rules this check reports, with the basis, what each expects and its condition.
REPORTED: Final[dict[str, tuple[Basis, str, str]]] = {
    "duplicate-key": (
        "inference",
        "Each key appears once: Claude Code keeps the last value, and strict parsers reject it.",
        CONDITION,
    ),
    "colon-in-value": (
        "official",
        "Quote a value that holds `: ` or ends with `:`, so strict parsers read it as text.",
        CONDITION,
    ),
    "unclosed-flow": (
        "official",
        "Close the `[` or `{`, or quote the value if the bracket is text.",
        CONDITION,
    ),
    "key-under-scalar": (
        "official",
        "Indent a key only under a key that has no value of its own.",
        CONDITION,
    ),
    "unclosed-quote": (
        "official",
        "Close the quote, or escape a quote character that is part of the text.",
        VALIDATE_POSITION_CONDITION,
    ),
    "tab-indent": (
        "official",
        "Indent with spaces: YAML forbids tabs in indentation.",
        VALIDATE_POSITION_CONDITION,
    ),
    "syntax-error": (
        "official",
        "Valid YAML here; quote a value that is meant as text.",
        VALIDATE_POSITION_CONDITION,
    ),
}


def _top_key(loaded: Loaded, line: int) -> str | None:
    """The top-level key whose entry holds a 1-based file line, read from the lines alone."""
    owner: str | None = None
    for text in loaded.lines[: max(line - 1, 0)]:
        if not text or text[0] in " \t#-":
            continue
        colon = colon_at(text)
        if colon is not None:
            owner = text[:colon].strip(" \t").strip("'\"") or None
    return owner


def _result(ctx: Context, loaded: Loaded, findings: list[Finding]) -> CheckResult:
    """A result that ran, with the closing marker's line as data."""
    block = loaded.file.block
    return CheckResult(
        check=CHECK,
        status="ran",
        reason=None,
        skill=ctx.folder_name,
        findings=findings,
        data={"close_line": None if block is None else block.close_line},
    )


def _not_run(ctx: Context, reason: str) -> CheckResult:
    """A result that didn't run, with the reason."""
    return CheckResult(
        check=CHECK, status="not_run", reason=reason, skill=ctx.folder_name, findings=[], data={}
    )


def _error_finding(loaded: Loaded, error: ReadError) -> Finding:
    """The finding for one of the reported failures."""
    basis, expected, condition = REPORTED[error.rule]
    if error.rule == "syntax-error":
        expected = f"Valid YAML, not {error.message}; quote a value that is meant as text."
    return Finding(
        check=CHECK,
        rule=error.rule,
        line=error.line,
        column=error.column,
        field=_top_key(loaded, error.line),
        found=loaded.line_text(error.line).rstrip(" \t"),
        expected=expected,
        basis=basis,
        surfaces=("open-spec", "upload"),
        condition=condition,
    )


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.yaml on the audited SKILL.md."""
    loaded = load(ctx)
    undecodable = loaded.file.decode_error
    if undecodable is not None:
        finding = Finding(
            check=CHECK,
            rule="not-utf8",
            line=undecodable.line,
            column=undecodable.column,
            field=None,
            found=undecodable.found,
            expected="Save SKILL.md as UTF-8; Claude Code replaces each byte it can't decode.",
            basis="inference",
            surfaces=("claude-code", "open-spec", "upload"),
            condition=UTF16_CONDITION if undecodable.kind == "utf16-bom" else LATIN1_CONDITION,
        )
        return _result(ctx, loaded, [finding])
    error = loaded.error
    if error is not None:
        if error.rule in REPORTED:
            return _result(ctx, loaded, [_error_finding(loaded, error)])
        return _not_run(
            ctx,
            f"the reader can't read this YAML: {error}; read claude plugin validate's output",
        )
    if loaded.root is None or loaded.root.kind != "map":
        return _not_run(ctx, NO_BLOCK_REASON)
    return _result(ctx, loaded, [])
