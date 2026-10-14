"""Deterministic checks of behavior-shaping configuration (domain D4).

Claude Code settings are checked against the Settings index of the settings reference (fetched
live when online, bundled otherwise): undocumented keys, deprecated keys, and keys placed in a
file that never reads them. Permission rules and hook commands are checked against the
documented matching rules; Codex config.toml against the Codex config reference.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import TYPE_CHECKING

from aca import jsonpos, paths, tomlish
from aca.checks import fact
from aca.findings import Conflict, Finding, Location
from aca.jsonutil import JsonObj, as_obj, get_obj, get_str, read_json, str_list
from aca.knowledge import KNOWLEDGE

if TYPE_CHECKING:
    from aca.checks import Context
    from aca.jsonpos import Node
    from aca.knowledge import Knowledge
    from aca.sources import Source

SETTINGS_DOCS = "https://code.claude.com/docs/en/settings-reference"
SETTINGS_PAGE = "https://code.claude.com/docs/en/settings"
PERMISSIONS_DOCS = "https://code.claude.com/docs/en/permissions"
CODEX_CONFIG_DOCS = "https://developers.openai.com/codex/config-reference"
IGNORED_KEYS = frozenset({"$schema"})
UNCONSULTED_RULE = re.compile(r"^(Write|NotebookEdit|Glob|MultiEdit)\((?!\)).+\)$")
CONTENT_TOOLS = "Bash|PowerShell|Read|Edit|Write|Grep|Glob|WebFetch"
CONTENT_FIELDS = "command|file_path|path|url|notebook_path"
CONTENT_FIELD_RULE = re.compile(rf"^({CONTENT_TOOLS})\(({CONTENT_FIELDS}):")
LINE_NUMBER = re.compile(r"line (\d+)")
HOOK_EXTENSIONS = "sh|py|js|mjs|cjs|ts|rb|pl|bash|zsh"
HOOK_SCRIPT = re.compile(
    rf"^(?:\$\{{?CLAUDE_PROJECT_DIR\}}?/|~/)?[A-Za-z0-9_./@+-]*/[A-Za-z0-9_.@+-]+\.(?:{HOOK_EXTENSIONS})$"
)
COMMAND_SPLIT = re.compile(r"[\s;|&()<>]+")
QUOTES = re.compile(r"[\"']")
HOOK_PATHS_DOCS = "https://code.claude.com/docs/en/hooks#reference-scripts-by-path"
FILE_SCOPES = frozenset({"user", "project", "local"})
PROJECT_PREFIXES = ("${CLAUDE_PROJECT_DIR}/", "$CLAUDE_PROJECT_DIR/")


def items(node: Node | None) -> list[Node]:
    """The array items of a node (none when the node is missing or not an array)."""
    return node.items if node is not None else []


def _record(ctx: Context, finding: Finding, conflict: Conflict, impact: str) -> None:
    finding.conflicts_with = [conflict]
    finding.impact = [impact]
    ctx.add(finding)


def _parse_error(ctx: Context, source: Source, error: str) -> None:
    match = LINE_NUMBER.search(error)
    line = min(int(match.group(1)), max(source.line_count, 1)) if match else 1
    why = f"the file is not valid JSON ({error}); Claude Code ignores the whole file"
    finding = fact("wrong", "high", (source.sid, line, line), (why, "revise"))
    _record(
        ctx, finding, Conflict("doc", "https://code.claude.com/docs/en/settings"), "correctness"
    )


def key_verdict(scope: str, key: str, info: JsonObj | None) -> tuple[str, str, str] | None:
    """(category, rationale, disposition) for a top-level settings key, or None when fine."""
    if info is None:
        return "wrong", f"`{key}` is not a documented setting, so it has no effect", "investigate"
    if info.get("deprecated") is True:
        note = get_str(info, "description")
        return "obsolete", f"`{key}` is deprecated: {note}", "revise"
    files = str_list(info.get("files"))
    if not files or scope not in FILE_SCOPES or scope in files:
        return None
    if files == ["global"]:
        return "misplaced", f"`{key}` belongs in ~/.claude.json, not in a settings file", "move"
    readers = ", ".join(files)
    return "dead", f"`{key}` is read only from {readers} settings, so it has no effect here", "move"


def _keys(ctx: Context, source: Source, root: Node, keys: dict[str, JsonObj]) -> None:
    for key, node in root.members.items():
        if key in IGNORED_KEYS:
            continue
        verdict = key_verdict(source.scope, key, keys.get(key))
        if verdict is None:
            continue
        category, why, disposition = verdict
        severity = "low" if category == "obsolete" else "medium"
        start = node.key_line or node.start
        where = (source.sid, start, max(node.end, start))
        finding = fact(category, severity, where, (why, disposition))
        finding.ladder = "b"
        _record(ctx, finding, Conflict("doc", f"{SETTINGS_DOCS}#settings-index"), "correctness")


def _rule_verdict(rule: str) -> str:
    if UNCONSULTED_RULE.match(rule):
        return f"`{rule}`: Claude Code never consults path rules for this tool (use Edit or Read)"
    if CONTENT_FIELD_RULE.match(rule):
        return f"`{rule}` targets the tool's primary content field, which Claude Code ignores"
    return ""


def _rule_findings(ctx: Context, source: Source, permissions: Node) -> None:
    allowed = {str(item.value): item for item in items(permissions.members.get("allow"))}
    for list_name, values in permissions.members.items():
        for item in values.items:
            rule = item.value if isinstance(item.value, str) else ""
            why = _rule_verdict(rule)
            if why:
                finding = fact(
                    "wrong", "medium", (source.sid, item.start, item.end), (why, "revise")
                )
            elif list_name == "deny" and rule in allowed:
                other = allowed[rule]
                why = f"`{rule}` is allowed and denied; deny wins, so the allow entry never applies"
                where = (source.sid, other.start, other.end)
                finding = fact("contradictory", "medium", where, (why, "remove"))
                finding.related = [Location(source.sid, item.start, item.end)]
            else:
                continue
            finding.ladder = "b"
            _record(ctx, finding, Conflict("doc", PERMISSIONS_DOCS), "correctness")


def hook_scripts(command: str) -> list[str]:
    """The script paths a shell-form command names: words with a folder and a script extension."""
    words = COMMAND_SPLIT.split(QUOTES.sub("", command))
    return [word for word in words if HOOK_SCRIPT.match(word)]


def resolve_hook_path(token: str, repo: Path, home: Path) -> tuple[Path, bool]:
    """Where a hook script path points, and whether it depends on the current directory."""
    for prefix in PROJECT_PREFIXES:
        if token.startswith(prefix):
            return repo / token[len(prefix) :], False
    if token.startswith("~/"):
        return home / token[2:], False
    if token.startswith("/"):
        return Path(token), False
    return repo / token.removeprefix("./"), True


def _hook_finding(ctx: Context, where: tuple[str, int, int], token: str) -> None:
    repo, home = ctx.inventory.repo, ctx.inventory.env.home
    path, relative = resolve_hook_path(token, repo, home)
    shown = paths.display(path, repo, home)
    if not path.exists():
        why = f"the hook runs `{token}`, and {shown} does not exist"
        finding = fact("wrong", "high", where, (why, "revise"))
        _record(ctx, finding, Conflict("repo-fact", shown, "no such file"), "reliability")
        return
    if relative:
        why = (
            f"the hook runs `{token}` by a relative path, which resolves against the current"
            " directory and breaks once Claude changes directory"
        )
        finding = fact("non-conformant", "medium", where, (why, "revise"))
        finding.replacement = f'"$CLAUDE_PROJECT_DIR"/{token.removeprefix("./")}'
        _record(ctx, finding, Conflict("doc", HOOK_PATHS_DOCS), "reliability")


def _hook_paths(ctx: Context, source: Source, hooks: Node) -> None:
    for groups in hooks.members.values():
        for group in groups.items:
            for handler in items(group.members.get("hooks")):
                value = as_obj(handler.value)
                words = hook_scripts(get_str(value, "command"))
                words += [arg for arg in str_list(value.get("args")) if HOOK_SCRIPT.match(arg)]
                for token in words:
                    _hook_finding(ctx, (source.sid, handler.start, handler.end), token)


def check_settings(ctx: Context, knowledge: Knowledge) -> None:
    """Every Claude Code settings file: parse errors, keys, permission rules, hook scripts."""
    for source in ctx.inventory.audited:
        if source.kind != "settings":
            continue
        root, error = jsonpos.parse("\n".join(source.lines))
        if root is None:
            _parse_error(ctx, source, error)
            continue
        _keys(ctx, source, root, knowledge.settings_keys)
        permissions = root.members.get("permissions")
        if permissions is not None:
            _rule_findings(ctx, source, permissions)
        hooks = root.members.get("hooks")
        if hooks is not None:
            _hook_paths(ctx, source, hooks)


def codex_rules() -> JsonObj:
    """The bundled Codex config knowledge (deprecated, reserved and unsupported values)."""
    return as_obj(read_json(KNOWLEDGE / "codex-config.json"))


def codex_verdict(entry: tomlish.Entry, rules: JsonObj) -> tuple[str, str] | None:
    """(category, rationale) for one config.toml assignment, or None when fine."""
    deprecated = get_obj(rules, "deprecated_keys")
    if entry.path in deprecated:
        return "obsolete", f"`{entry.path}` is deprecated; use `{get_str(deprecated, entry.path)}`"
    reserved = get_obj(rules, "reserved_keys")
    if entry.path in reserved:
        return "wrong", f"`{entry.path}`: {get_str(reserved, entry.path)}"
    values = get_obj(get_obj(rules, "values"), entry.path)
    if isinstance(entry.value, str) and entry.value in values:
        return "obsolete", f'`{entry.path} = "{entry.value}"`: {get_str(values, entry.value)}'
    return None


def check_codex_config(ctx: Context) -> None:
    """Codex config.toml: TOML validity (when tomllib exists), deprecated and reserved keys."""
    rules = codex_rules()
    for source in ctx.inventory.audited:
        if source.kind != "codex-config":
            continue
        error = tomlish.validate("\n".join(source.lines) + "\n")
        if error:
            why = f"config.toml does not parse ({error}); Codex cannot load it"
            where = (source.sid, 1, max(source.line_count, 1))
            finding = fact("wrong", "high", where, (why, "revise"))
            _record(ctx, finding, Conflict("doc", CODEX_CONFIG_DOCS), "correctness")
            continue
        for entry in tomlish.entries(source.lines)[0]:
            verdict = codex_verdict(entry, rules)
            if verdict is None:
                continue
            category, why = verdict
            where = (source.sid, entry.start, entry.end)
            finding = fact(category, "medium", where, (why, "revise"))
            finding.ladder = "b"
            _record(ctx, finding, Conflict("doc", CODEX_CONFIG_DOCS), "correctness")
