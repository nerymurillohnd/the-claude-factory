"""frontmatter.listing-cap: where the skill listing cuts `description` plus `when_to_use`.

Claude Code lists `description` and `when_to_use` joined by " - " and cuts the joined text at
1,536 characters, configurable with skillListingMaxDescChars; the text past the cut never
reaches Claude. Offsets are 0-based, in characters, within the field the cut falls in.
"""

import argparse
from typing import Final

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, Loaded, load
from common.report import CheckResult, Finding
from common.text import snippet, utf16_len
from common.text_field import as_text, not_run
from common.yaml_reader import Node

CHECK: Final = "frontmatter.listing-cap"
DEFAULT_CAP: Final = 1536
SEPARATOR: Final = " - "
CAP_SETTING: Final = "skillListingMaxDescChars"
ONE_LINE_STYLES: Final = frozenset({"plain", "single"})


def _positive(value: str) -> int:
    """A cap of at least one character."""
    try:
        cap = int(value)
    except ValueError:
        cap = 0
    if cap < 1:
        msg = f"expected a whole number of at least 1, got {value!r}"
        raise argparse.ArgumentTypeError(msg)
    return cap


def options(parser: argparse.ArgumentParser) -> None:
    """`--cap N`: the listing cap in characters, 1,536 by default."""
    _ = parser.add_argument("--cap", type=_positive, default=DEFAULT_CAP)


def _field(loaded: Loaded, name: str) -> tuple[Node | None, str]:
    """A field's value node and its text; "" when it is absent or not a string."""
    pair = loaded.fields.get(name)
    if pair is None:
        return None, ""
    return pair[1], as_text(pair[1]) or ""


def _cap(ctx: Context) -> int:
    """The cap from the options, or the default."""
    cap = ctx.options.get("cap", DEFAULT_CAP)
    return cap if isinstance(cap, int) else DEFAULT_CAP


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.listing-cap on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return not_run(CHECK, ctx.folder_name, NO_BLOCK_REASON)
    cap = _cap(ctx)
    description_node, description = _field(loaded, "description")
    when_node, when = _field(loaded, "when_to_use")
    combined = SEPARATOR.join(part for part in (description, when) if part)
    when_start = len(combined) - len(when)
    data: dict[str, object] = {
        "description_length": len(description),
        "when_to_use_length": len(when),
        "combined_length": len(combined),
        "combined_utf16_length": utf16_len(combined),
        "cap": cap,
        "first_lost_field": None,
        "first_lost_offset": None,
        "around_cut": None,
        "line": None,
        "cap_setting": CAP_SETTING,
    }
    if len(combined) <= cap:
        return CheckResult(CHECK, "ran", None, ctx.folder_name, [], data)
    if cap < len(description):
        field, node, offset = "description", description_node, cap
    else:
        field, node, offset = "when_to_use", when_node, max(cap - when_start, 0)
    one_line = node is not None and node.style in ONE_LINE_STYLES and node.line == node.end_line
    line = node.line if one_line and node is not None else None
    data.update(
        first_lost_field=field,
        first_lost_offset=offset,
        around_cut=snippet(combined, cap),
        line=line,
    )
    finding = Finding(
        check=CHECK,
        rule="over-cap",
        line=line if line is not None else (None if node is None else node.line),
        column=None,
        field=field,
        found=combined[cap:],
        expected=f"At most {cap:,} characters of description and when_to_use together.",
        basis="official",
        surfaces=("claude-code",),
    )
    return CheckResult(CHECK, "ran", None, ctx.folder_name, [finding], data)
