"""frontmatter.name: the name's format, its folder, refused characters and reserved words.

The open specification and uploads require a name of 1 to 64 characters with no leading,
trailing or consecutive hyphen, equal to the folder name; uploads allow only `a-z`, `0-9` and
`-`, while the open-spec validator also accepts lowercase letters and digits of any script.
Claude Code makes the name optional, using the folder name, and refuses a name holding `<`,
`>`, control, format, private-use or unassigned characters, or any blank but one space between
words. The Claude API and claude.ai reject `anthropic` and `claude` in a name.
"""

import re
from typing import Final
import unicodedata

from common.context import Context
from common.frontmatter import NO_BLOCK_REASON, load
from common.report import Basis, CheckResult, Finding, Surface
from common.text import utf16_len
from common.yaml_reader import Node
from common.yaml_types import yaml11_tag

CHECK: Final = "frontmatter.name"
MAX_LENGTH: Final = 64
CHARSET: Final = re.compile(r"[a-z0-9-]*")
RESERVED_WORDS: Final = ("anthropic", "claude")
REFUSED_CATEGORIES: Final = frozenset({"Cc", "Cf", "Co", "Cn", "Zl", "Zp"})
SPEC: Final[tuple[Surface, ...]] = ("open-spec", "upload")


def _finding(
    rule: str, expected: str, node: Node | None, surfaces: tuple[Surface, ...], basis: Basis
) -> Finding:
    """A finding on the name's value, or with no position when the name is missing."""
    return Finding(
        check=CHECK,
        rule=rule,
        line=None if node is None else node.line,
        column=None if node is None else node.column,
        field="name",
        found=None if node is None else node.value,
        expected=expected,
        basis=basis,
        surfaces=surfaces,
    )


def _refused(name: str) -> bool:
    """True when Claude Code refuses a character or a blank in the name."""
    if "<" in name or ">" in name or "  " in name or name != name.strip(" "):
        return True
    return any(
        unicodedata.category(ch) in REFUSED_CATEGORIES
        or (unicodedata.category(ch) == "Zs" and ch != " ")
        for ch in name
    )


def _open_spec_letters(name: str) -> bool:
    """True when the open-spec validator, skills-ref, accepts the name's characters.

    It wants the name lowercase and, after NFKC, made only of letters and digits of any script
    and hyphens.
    """
    normalized = unicodedata.normalize("NFKC", name)
    return name == name.lower() and all(ch.isalnum() or ch == "-" for ch in normalized)


def _format_findings(name: str, node: Node, folder: str) -> list[Finding]:
    """The format, folder and refused-character findings of a name that is a string."""
    found: list[Finding] = []
    if not 1 <= len(name) <= MAX_LENGTH:
        found.append(_finding("length", "1 to 64 characters.", node, SPEC, "official"))
    if CHARSET.fullmatch(name) is None:
        expected = "Only lowercase letters, digits and hyphens."
        surfaces = ("upload",) if _open_spec_letters(name) else SPEC
        found.append(_finding("charset", expected, node, surfaces, "official"))
    if name.startswith("-") or name.endswith("-") or "--" in name:
        expected = "No leading, trailing or consecutive hyphen."
        found.append(_finding("hyphen", expected, node, SPEC, "official"))
    if name != folder:
        expected = f"The same text as the skill's folder name, `{folder}`."
        found.append(_finding("folder-mismatch", expected, node, SPEC, "official"))
    if _refused(name):
        expected = (
            "No `<`, `>`, control, format, private-use or unassigned character, "
            "and no blank but one space between words."
        )
        found.append(_finding("refused-character", expected, node, ("claude-code",), "official"))
    return found


def _reserved(text: str, node: Node | None) -> list[Finding]:
    """A reserved-word finding when the text holds `anthropic` or `claude`."""
    lowered = text.lower()
    if not any(word in lowered for word in RESERVED_WORDS):
        return []
    expected = "Neither `anthropic` nor `claude` in the name."
    return [_finding("reserved-word", expected, node, ("upload",), "official")]


def _not_run(ctx: Context) -> CheckResult:
    """No mapping to read."""
    return CheckResult(
        check=CHECK,
        status="not_run",
        reason=NO_BLOCK_REASON,
        skill=ctx.folder_name,
        findings=[],
        data={},
    )


def _is_string(node: Node) -> bool:
    """True when YAML 1.1 reads the name as a string."""
    return node.kind == "scalar" and node.value != "" and yaml11_tag(node) == "str"


def check(ctx: Context) -> CheckResult:
    """Run frontmatter.name on the audited SKILL.md."""
    loaded = load(ctx)
    if loaded.root is None or loaded.root.kind != "map":
        return _not_run(ctx)
    folder = ctx.folder_name
    pair = loaded.fields.get("name")
    findings: list[Finding] = []
    if pair is None:
        name, source = folder, "folder"
        expected = "A `name`: the open specification and uploads require one."
        findings.append(_finding("missing", expected, None, SPEC, "official"))
        findings.extend(_reserved(folder, None))
    else:
        node = pair[1]
        name, source = node.value, "name"
        if _is_string(node):
            findings.extend(_format_findings(name, node, folder))
        else:
            expected = "A string; this value reads as another type or a collection."
            findings.append(_finding("not-a-string", expected, node, SPEC, "official"))
        findings.extend(_reserved(name, node))
    data: dict[str, object] = {
        "name": name,
        "name_source": source,
        "length": len(name),
        "utf16_length": utf16_len(name),
        "folder_name": folder,
        "matches_folder": name == folder,
        "unicode_version": unicodedata.unidata_version,
    }
    return CheckResult(
        check=CHECK,
        status="ran",
        reason=None,
        skill=ctx.folder_name,
        findings=findings,
        data=data,
    )
