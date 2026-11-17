"""frontmatter.allowed-tools: the tools a skill pre-approves, entry by entry.

Claude Code accepts a space- or comma-separated string or a YAML list; the open specification
defines a space-separated string, so a list is flagged for a skill meant to work elsewhere. A
bare `Bash`, `Bash(*)` or `Bash(:*)` pre-approves every command the skill's turn runs.
"""

from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import Basis, CheckResult, Finding
from common.text_field import not_run
from common.yaml_reader import Node

CHECK: Final = "frontmatter.allowed-tools"
SEPARATORS: Final = frozenset(" \t\n,")
# The permissions docs say "`Bash(*)` is equivalent to `Bash`"; `:*` is "an equivalent way to
# write a trailing wildcard", so `Bash(:*)` with its empty prefix is an inference.
UNSCOPED_BASH: Final[dict[str, Basis]] = {
    "Bash": "official",
    "Bash(*)": "official",
    "Bash(:*)": "inference",
}
LIST_CONDITION: Final = "for a skill meant to work outside Claude Code"


def split_entries(text: str) -> tuple[list[str], list[str]]:
    """Split on blanks and commas outside parentheses: the entries, and those left unparsed."""
    entries: list[str] = []
    unparsed: list[str] = []
    current: list[str] = []
    depth = 0
    broken = False

    def close() -> None:
        nonlocal broken
        if current:
            (unparsed if broken else entries).append("".join(current))
        current.clear()
        broken = False

    for ch in text:
        if depth == 0 and ch in SEPARATORS:
            close()
            continue
        current.append(ch)
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                depth, broken = 0, True
    broken = broken or depth > 0
    close()
    return entries, unparsed


def _entry_finding(entry: str, node: Node) -> Finding | None:
    """An unscoped-bash finding when the entry approves every Bash command."""
    basis = UNSCOPED_BASH.get("".join(entry.split()))
    if basis is None:
        return None
    return Finding(
        check=CHECK,
        rule="unscoped-bash",
        line=node.line,
        column=node.column,
        field="allowed-tools",
        found=entry,
        expected="A Bash rule scoped to the commands the skill runs, such as `Bash(git diff *)`.",
        basis=basis,
        surfaces=("claude-code",),
    )


def _entries(node: Node) -> tuple[list[tuple[str, Node]], list[str]]:
    """Each entry with the node it came from, and the text left unparsed."""
    if node.kind == "seq":
        parsed = [(item.value, item) for item in node.items if item.kind == "scalar" and item.value]
        unparsed = [item.raw for item in node.items if item.kind != "scalar" and item.raw]
        return parsed, unparsed
    if node.kind != "scalar":
        return [], [node.raw] if node.raw else []
    entries, unparsed = split_entries(node.value)
    return [(entry, node) for entry in entries], unparsed


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.allowed-tools on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    pair = loaded.fields.get("allowed-tools")
    findings: list[Finding] = []
    entries: list[tuple[str, Node]] = []
    unparsed: list[str] = []
    if pair is not None:
        node = pair[1]
        entries, unparsed = _entries(node)
        if node.kind == "seq":
            expected = "A space-separated string, as the open specification defines it."
            findings.append(
                Finding(
                    check=CHECK,
                    rule="list-form",
                    line=node.line,
                    column=node.column,
                    field="allowed-tools",
                    found=node.raw or None,
                    expected=expected,
                    basis="official",
                    surfaces=("open-spec", "upload"),
                    condition=LIST_CONDITION,
                )
            )
        for entry, source in entries:
            found = _entry_finding(entry, source)
            if found is not None:
                findings.append(found)
    data: dict[str, object] = {
        "entries": [entry for entry, _source in entries],
        "unparsed_entries": unparsed,
    }
    return CheckResult(CHECK, "ran", None, ctx.folder_name, findings, data)
