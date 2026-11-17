"""frontmatter.yaml: the strict-YAML failures claude plugin validate passes, and non-UTF-8 bytes.

validate already reports an unclosed quote, a tab in the indentation, a missing block and a root
that isn't a mapping, so those give `not_run` with the reason to read validate instead. The four
failures it passes, and Claude Code accepts, are findings: packaging and upload reject them.
"""

from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, VALIDATE_REASON, Loaded, load
from common.report import Basis, CheckResult, Finding
from common.yaml_reader import ReadError
from common.yaml_source import colon_at

CHECK: Final = "frontmatter.yaml"
CONDITION: Final = "Claude Code accepted it when tested; packaging and upload reject it"

LATIN1_CONDITION: Final = "claude plugin validate reported nothing for such a byte when tested"
UTF16_CONDITION: Final = "claude plugin validate reports only that it found no frontmatter block"

# The reader's rules this check reports, with the basis and what each one expects.
REPORTED: Final[dict[str, tuple[Basis, str]]] = {
    "duplicate-key": (
        "inference",
        "Each key appears once: Claude Code keeps the last value, and strict parsers reject it.",
    ),
    "colon-in-value": (
        "official",
        "Quote a value that holds `: ` or ends with `:`, so strict parsers read it as text.",
    ),
    "unclosed-flow": (
        "official",
        "Close the `[` or `{`, or quote the value if the bracket is text.",
    ),
    "key-under-scalar": (
        "official",
        "Indent a key only under a key that has no value of its own.",
    ),
}
# The reader's rules validate reports; any other rule means the reader can't read the YAML.
VALIDATE_RULES: Final = frozenset({"unclosed-quote", "tab-indent"})


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
    """The finding for one of the four reported failures."""
    basis, expected = REPORTED[error.rule]
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
        condition=CONDITION,
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
        if error.rule in VALIDATE_RULES:
            return _not_run(ctx, VALIDATE_REASON)
        return _not_run(
            ctx,
            f"the reader can't read this YAML: {error}; read claude plugin validate's output",
        )
    if loaded.root is None or loaded.root.kind != "map":
        return _not_run(ctx, NO_BLOCK_REASON)
    return _result(ctx, loaded, [])
