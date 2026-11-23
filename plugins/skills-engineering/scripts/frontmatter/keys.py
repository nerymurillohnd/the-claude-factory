"""frontmatter.keys: keys Claude Code ignores, keys uploads reject, and a BOM or CRLF line ends.

Claude Code ignores a frontmatter field it doesn't recognize without reporting an error, so a
misspelled key, or one borrowed from subagents such as `tools`, silently sets nothing. Uploads
accept only the six Agent Skills fields and fail a file that starts with a UTF-8 byte-order mark
or ends its lines with CRLF.
"""

from typing import Final

from common.context import Context
from common.fields import CLAUDE_CODE_FIELDS, SPEC_FIELDS
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import CheckResult, Finding, Surface
from common.text_field import not_run
from common.yaml_reader import Node

CHECK: Final = "frontmatter.keys"
MAX_EDITS: Final = 2
# Keys from other Claude features that mean a skill field, checked before any spelling match:
# `tools` is a subagent's field and is two edits from `hooks`, which it never means.
ALIASES: Final[dict[str, str]] = {
    "tools": "allowed-tools",
    "version": "metadata.version",
}
UPLOAD: Final[tuple[Surface, ...]] = ("upload",)


def _distance(a: str, b: str) -> int:
    """The Levenshtein distance between two strings."""
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def suggestion(key: str) -> str | None:
    """The field a key most likely means: an alias first, else the field within two edits."""
    if key in ALIASES:
        return ALIASES[key]
    scored = [(_distance(key.lower(), field), field) for field in CLAUDE_CODE_FIELDS]
    best = min(scored)
    return best[1] if best[0] <= MAX_EDITS else None


def _key_finding(rule: str, key: Node, expected: str, surfaces: tuple[Surface, ...]) -> Finding:
    """An official finding on a top-level key."""
    return Finding(
        check=CHECK,
        rule=rule,
        line=key.line,
        column=key.column,
        field=key.value,
        found=key.value,
        expected=expected,
        basis="official",
        surfaces=surfaces,
    )


def _file_finding(rule: str, line: int, expected: str) -> Finding:
    """An official upload finding on the file's bytes."""
    return Finding(
        check=CHECK,
        rule=rule,
        line=line,
        column=1,
        field=None,
        found=None,
        expected=expected,
        basis="official",
        surfaces=UPLOAD,
    )


def _unknown(key: Node) -> Finding:
    """A key Claude Code doesn't recognize, with the field it most likely means."""
    meant = suggestion(key.value)
    expected = "A field Claude Code recognizes; it ignores this one without an error."
    if meant is not None:
        expected = (
            f"`{meant}`, which this key most likely means; Claude Code ignores `{key.value}`."
        )
    return _key_finding("unknown-key", key, expected, ("claude-code",))


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.keys on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    findings: list[Finding] = []
    unknown: list[dict[str, object]] = []
    for name, (key, _value) in loaded.fields.items():
        if name not in CLAUDE_CODE_FIELDS:
            findings.append(_unknown(key))
            unknown.append({"key": name, "line": key.line, "suggestion": suggestion(name)})
        if name not in SPEC_FIELDS:
            expected = (
                f"Only the Agent Skills fields ({', '.join(SPEC_FIELDS)}): uploads reject the "
                "skill for any other key, and the open-spec validator reports it."
            )
            findings.append(_key_finding("non-spec-key", key, expected, ("open-spec", "upload")))
    if loaded.file.had_bom:
        expected = "No UTF-8 byte-order mark: uploads fail a SKILL.md that starts with one."
        findings.append(_file_finding("bom", 1, expected))
    if loaded.file.had_crlf:
        expected = "LF line ends: uploads fail a SKILL.md with CRLF line ends."
        findings.append(_file_finding("crlf", 1, expected))
    data: dict[str, object] = {
        "keys": list(loaded.fields),
        "unknown_keys": unknown,
        "bom": loaded.file.had_bom,
        "crlf": loaded.file.had_crlf,
    }
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
