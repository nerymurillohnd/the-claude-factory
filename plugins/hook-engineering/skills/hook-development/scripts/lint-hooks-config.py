#!/usr/bin/env python3
"""Check a hooks configuration file against the documented Claude Code hook configuration rules.

Usage:
    lint-hooks-config.py FILE [FILE...]

FILE is a settings file (~/.claude/settings.json, .claude/settings.json,
.claude/settings.local.json) or a plugin's hooks/hooks.json. Only the "hooks" object is read.
Hooks in skill or agent frontmatter are YAML: check those by hand with the same rules.

Each finding names the rule's section in https://code.claude.com/docs/en/hooks. ERROR means the
hook never runs or never does what it says; WARN means it runs but likely not as intended; INFO
is a fact worth knowing. Exit code: 1 if any ERROR, else 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import cast

DOCS = "https://code.claude.com/docs/en/hooks"
MIN_ARGS = 2
USER_CONFIG_MESSAGE = "shell form: ${user_config.*} fails; use args or $CLAUDE_PLUGIN_OPTION_<KEY>"

EVENTS = frozenset(
    {
        "SessionStart",
        "Setup",
        "InstructionsLoaded",
        "UserPromptSubmit",
        "UserPromptExpansion",
        "MessageDisplay",
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "PostToolUseFailure",
        "PostToolBatch",
        "PermissionDenied",
        "Notification",
        "SubagentStart",
        "SubagentStop",
        "TaskCreated",
        "TaskCompleted",
        "Stop",
        "StopFailure",
        "TeammateIdle",
        "ConfigChange",
        "CwdChanged",
        "DirectoryAdded",
        "FileChanged",
        "WorktreeCreate",
        "WorktreeRemove",
        "PreCompact",
        "PostCompact",
        "PreModelSwitch",
        "PostModelSwitch",
        "SessionEnd",
        "Elicitation",
        "ElicitationResult",
    }
)
TOOL_EVENTS = frozenset(
    {"PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest", "PermissionDenied"}
)
NO_MATCHER = frozenset(
    {
        "UserPromptSubmit",
        "PostToolBatch",
        "Stop",
        "TeammateIdle",
        "TaskCreated",
        "TaskCompleted",
        "WorktreeCreate",
        "WorktreeRemove",
        "MessageDisplay",
        "CwdChanged",
    }
)
NARROW_EXACT = frozenset({"FileChanged", "StopFailure"})
NO_ON_FAILURE = frozenset({"Stop", "SubagentStop", "TaskCompleted", "TeammateIdle"})
TYPES = {
    "command": ("command",),
    "http": ("url",),
    "mcp_tool": ("server", "tool"),
    "prompt": ("prompt",),
    "agent": ("prompt",),
}
EXACT = re.compile(r"^[A-Za-z0-9_\- ,|]*$")
EXACT_NARROW = re.compile(r"^[A-Za-z0-9_|]*$")
PLACEHOLDER = re.compile(r"\$\{(CLAUDE_PLUGIN_ROOT|CLAUDE_PROJECT_DIR|CLAUDE_PLUGIN_DATA)\}")
ENV_REF = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")


@dataclass
class Report:
    """Collected findings for one file."""

    path: str
    findings: list[tuple[str, str, str, str]] = field(default_factory=list)

    def add(self, level: str, where: str, message: str, anchor: str) -> None:
        """Record a finding."""
        self.findings.append((level, where, message, f"{DOCS}#{anchor}"))


@dataclass(frozen=True)
class PluginInfo:
    """What the file's plugin declares, when the file is a plugin's hooks/hooks.json."""

    name: str
    servers: frozenset[str]


def out(line: str) -> None:
    """Write one line to stdout."""
    _ = sys.stdout.write(line + "\n")


def load_json(path: Path) -> object:
    """Parse a JSON file."""
    return cast("object", json.loads(path.read_text(encoding="utf-8")))


def server_keys(source: object, root: Path) -> set[str]:
    """Server names from an mcpServers value: a map, a path to a JSON file, or a list of those."""
    if isinstance(source, str):
        target = root / source
        return server_keys(load_json(target), root) if target.is_file() else set()
    if isinstance(source, list):
        keys: set[str] = set()
        for item in cast("list[object]", source):
            keys |= server_keys(item, root)
        return keys
    if not isinstance(source, dict):
        return set()
    data = cast("dict[str, object]", source)
    if "mcpServers" in data:
        return server_keys(data["mcpServers"], root)
    return {str(key) for key, value in data.items() if isinstance(value, dict)}


def plugin_info(path: Path) -> PluginInfo | None:
    """Read the plugin name and bundled MCP server keys for a plugin hooks.json."""
    root = path.parent.parent
    manifest = root / ".claude-plugin" / "plugin.json"
    if path.name != "hooks.json" or not manifest.is_file():
        return None
    loaded = load_json(manifest)
    if not isinstance(loaded, dict):
        message = f"{manifest} is not a JSON object"
        raise TypeError(message)
    data = cast("dict[str, object]", loaded)
    servers = server_keys(data.get("mcpServers"), root)
    mcp_file = root / ".mcp.json"
    if mcp_file.is_file():
        servers |= server_keys(load_json(mcp_file), root)
    return PluginInfo(str(data.get("name", "")), frozenset(servers))


def check_matcher(report: Report, where: str, event: str, matcher: str) -> None:
    """Apply the matcher rules."""
    if not matcher or matcher == "*":
        return
    if event in NO_MATCHER:
        report.add(
            "WARN",
            where,
            f"{event} has no matcher support; the matcher is ignored",
            "matcher-patterns",
        )
        return
    exact = EXACT_NARROW if event in NARROW_EXACT else EXACT
    if exact.match(matcher):
        bare = [
            item.strip()
            for item in re.split(r"[|,]", matcher)
            if item.strip().startswith("mcp__") and "__" not in item.strip()[len("mcp__") :]
        ]
        if bare:
            report.add(
                "ERROR",
                where,
                f"'{bare[0]}' is a bare server name and matches no tool; append __.*",
                "match-mcp-tools",
            )
        if (
            event in TOOL_EVENTS
            and re.search(r"(^|[|, ])Bash($|[|, ])", matcher)
            and "PowerShell" not in matcher
        ):
            report.add(
                "INFO", where, "'Bash' doesn't cover the PowerShell tool", "matcher-patterns"
            )
        return
    report.add(
        "INFO",
        where,
        f"'{matcher}' is an unanchored regex: it matches anywhere; use ^...$ for a whole name",
        "matcher-patterns",
    )
    if event in NARROW_EXACT and re.search(r"[- ,]", matcher):
        report.add(
            "WARN",
            where,
            f"on {event}, '-', ' ' and ',' make the matcher a regex; only | separates",
            "matcher-patterns",
        )


def check_mcp_names(report: Report, where: str, text: str, plugin: PluginInfo | None) -> None:
    """Flag bare server keys for the plugin's own MCP servers."""
    if plugin is None:
        return
    for server in plugin.servers:
        if f"mcp__{server}__" in text:
            scoped = f"mcp__plugin_{plugin.name}_{server}__"
            report.add(
                "ERROR",
                where,
                f"a bare 'mcp__{server}__' never fires for this plugin's server; use '{scoped}'",
                "match-mcp-tools",
            )


def check_command(
    report: Report, where: str, handler: dict[str, object], plugin: PluginInfo | None
) -> None:
    """Apply the command hook field rules."""
    command = str(handler.get("command", ""))
    args = handler.get("args")
    if args is not None:
        if " " in command and "/" not in command and "\\" not in command:
            report.add(
                "ERROR",
                where,
                f"exec form: '{command}' is not one executable; move extra words into args",
                "exec-form-and-shell-form",
            )
        if "shell" in handler:
            report.add(
                "WARN", where, "'shell' is ignored when 'args' is set", "command-hook-fields"
            )
        return
    for match in PLACEHOLDER.finditer(command):
        before = command[max(0, match.start() - 1) : match.start()]
        if before != '"':
            report.add(
                "WARN",
                where,
                f"shell form: wrap {match.group(0)} in double quotes, or use exec form",
                "reference-scripts-by-path",
            )
            break
    if plugin is not None and "${user_config." in command:
        report.add(
            "ERROR",
            where,
            USER_CONFIG_MESSAGE,
            "exec-form-and-shell-form",
        )


def check_http(report: Report, where: str, handler: dict[str, object]) -> None:
    """Apply the HTTP hook field rules."""
    headers = handler.get("headers")
    allowed = handler.get("allowedEnvVars")
    allowed_set: set[str] = set()
    if isinstance(allowed, list):
        allowed_set = {str(item) for item in cast("list[object]", allowed)}
    if isinstance(headers, dict):
        for value in cast("dict[str, object]", headers).values():
            for name in cast("list[str]", ENV_REF.findall(str(value))):
                if name not in allowed_set:
                    report.add(
                        "WARN",
                        where,
                        f"${name} in a header resolves to empty: not in allowedEnvVars",
                        "http-hook-fields",
                    )


def check_mcp_tool(
    report: Report, where: str, handler: dict[str, object], plugin: PluginInfo | None
) -> None:
    """Apply the MCP tool hook field rules."""
    server = str(handler.get("server", ""))
    if plugin is not None and server in plugin.servers:
        report.add(
            "ERROR",
            where,
            f"server '{server}' is this plugin's key; use 'plugin:{plugin.name}:{server}'",
            "mcp-tool-hook-fields",
        )


def check_if(report: Report, where: str, event: str, rule: object) -> None:
    """Apply the rules for the 'if' field."""
    if rule is not None:
        if event not in TOOL_EVENTS:
            report.add(
                "ERROR",
                where,
                f"'if' is only evaluated on tool events; on {event} this hook never runs",
                "common-fields",
            )
        elif re.search(r"&&|\|\||\)\s*[,|]\s*\w+\(", str(rule)):
            report.add(
                "ERROR",
                where,
                "'if' holds exactly one permission rule; split into separate handlers",
                "common-fields",
            )


def check_common(report: Report, where: str, event: str, handler: dict[str, object]) -> None:
    """Apply the common field rules."""
    kind = str(handler.get("type", ""))
    check_if(report, where, event, handler.get("if"))
    if "once" in handler:
        report.add(
            "WARN",
            where,
            "'once' is honored only in skill frontmatter; ignored here",
            "common-fields",
        )
    if "timeout" not in handler:
        report.add("INFO", where, f"no timeout: the {kind} default applies", "common-fields")
    if "onFailure" in handler:
        if kind not in {"command", "http"}:
            report.add(
                "WARN",
                where,
                f"onFailure applies to command and http hooks, not {kind}",
                "block-the-action-when-a-hook-fails",
            )
        elif event in NO_ON_FAILURE or handler.get("async") or handler.get("asyncRewake"):
            report.add(
                "WARN",
                where,
                "onFailure has no effect on this event or on async hooks",
                "block-the-action-when-a-hook-fails",
            )
        elif handler["onFailure"] == "block" and event == "UserPromptSubmit":
            report.add(
                "INFO",
                where,
                'onFailure "block" here blocks every prompt when the hook fails: policy hooks only',
                "block-the-action-when-a-hook-fails",
            )
    if (handler.get("async") or handler.get("asyncRewake")) and kind != "command":
        report.add(
            "WARN", where, "async and asyncRewake are command hook fields", "command-hook-fields"
        )


def check_handler(
    report: Report, where: str, event: str, handler: object, plugin: PluginInfo | None
) -> None:
    """Check one hook handler."""
    if not isinstance(handler, dict):
        report.add("ERROR", where, "a hook handler must be an object", "hook-handler-fields")
        return
    data = cast("dict[str, object]", handler)
    kind = str(data.get("type", ""))
    if kind not in TYPES:
        report.add(
            "ERROR",
            where,
            f"type '{kind}' is not command, http, mcp_tool, prompt or agent",
            "common-fields",
        )
        return
    for required in TYPES[kind]:
        if required not in data:
            report.add("ERROR", where, f"{kind} hook needs '{required}'", "hook-handler-fields")
    check_common(report, where, event, data)
    check_mcp_names(report, where, str(data.get("if", "")), plugin)
    checks = {"command": check_command, "mcp_tool": check_mcp_tool}
    if kind in checks:
        checks[kind](report, where, data, plugin)
    elif kind == "http":
        check_http(report, where, data)


def check_group(
    report: Report, where: str, event: str, group: object, plugin: PluginInfo | None
) -> None:
    """Check one matcher group."""
    if not isinstance(group, dict):
        report.add("ERROR", where, "a matcher group must be an object", "configuration")
        return
    data = cast("dict[str, object]", group)
    handlers = data.get("hooks")
    if "type" in data or "command" in data:
        report.add(
            "ERROR",
            where,
            "handler outside a group's 'hooks' array: skipped with a warning; never runs",
            "configuration",
        )
        return
    if not isinstance(handlers, list):
        report.add("ERROR", where, "matcher group needs a 'hooks' array", "configuration")
        return
    matcher = str(data.get("matcher", ""))
    check_matcher(report, where, event, matcher)
    check_mcp_names(report, where, matcher, plugin)
    for index, handler in enumerate(cast("list[object]", handlers)):
        check_handler(report, f"{where}.hooks[{index}]", event, handler, plugin)


def read_plugin(report: Report, path: Path) -> PluginInfo | None:
    """Read the plugin next to a hooks.json, reporting an unreadable manifest or MCP config."""
    try:
        return plugin_info(path)
    except (OSError, ValueError, TypeError) as error:
        report.add(
            "ERROR",
            "plugin",
            f"cannot read the plugin manifest or MCP config next to this file: {error}",
            "configuration",
        )
        return None


def lint(path: Path) -> Report:
    """Lint one file."""
    report = Report(str(path))
    try:
        data = load_json(path)
    except OSError as error:
        report.add(
            "ERROR", "file", f"cannot read the file: {error.strerror or error}", "configuration"
        )
        return report
    except ValueError as error:
        report.add("ERROR", "file", f"not valid JSON: {error}", "configuration")
        return report
    hooks = cast("dict[str, object]", data).get("hooks") if isinstance(data, dict) else None
    if not isinstance(hooks, dict):
        report.add("ERROR", "hooks", "no 'hooks' object at the top level", "configuration")
        return report
    plugin = read_plugin(report, path)
    for event, groups in cast("dict[str, object]", hooks).items():
        if event not in EVENTS:
            report.add(
                "ERROR",
                event,
                f"unknown event '{event}': skipped with a Settings Warning; it never fires",
                "hook-lifecycle",
            )
            continue
        if not isinstance(groups, list):
            report.add(
                "ERROR", event, "an event maps to an array of matcher groups", "configuration"
            )
            continue
        for index, group in enumerate(cast("list[object]", groups)):
            check_group(report, f"{event}[{index}]", event, group, plugin)
    return report


def main() -> int:
    """Lint every file given and print the findings."""
    if len(sys.argv) < MIN_ARGS:
        out(__doc__ or "")
        return 2
    errors = 0
    for name in sys.argv[1:]:
        report = lint(Path(name))
        out(f"== {report.path}: {len(report.findings)} finding(s)")
        for level, where, message, url in report.findings:
            out(f"{level:5} {where}: {message}\n      {url}")
            errors += level == "ERROR"
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
