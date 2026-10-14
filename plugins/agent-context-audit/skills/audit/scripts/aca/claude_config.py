"""Claude Code on-demand components and behavior-shaping config, plus what stays out of scope.

Subagents, output styles, subagent memory and loop.md are domain D2; settings files, .mcp.json
and the MCP part of ~/.claude.json are domain D4. Skills, commands, saved workflows and every
plugin-provided component load too, but the audit only records them (the brief excludes them).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from aca import markdown
from aca.claude_sources import Place, add, markdown_files
from aca.jsonutil import JsonObj, as_obj, dumps, get_obj, read_json
from aca.sources import (
    ALWAYS,
    CONFIG,
    NOT_LOADED,
    ON_DEMAND,
    SHADOWED,
    TRUNCATED,
    Source,
    load_text,
)

if TYPE_CHECKING:
    from pathlib import Path

    from aca.claude_sources import Context

LOOP_LIMIT_BYTES = 25_000
OWN_PLUGIN = "agent-context-audit@"


def _declared_name(path: Path) -> str:
    probe = Source(path=path, display="", kind="subagent", scope="", domain="D2")
    load_text(probe)
    front = markdown.find_frontmatter(probe.lines)
    name = front.data.get("name") if front is not None else None
    return name if isinstance(name, str) and name else path.stem


def subagents(context: Context) -> None:
    """User and project subagents; a project agent shadows a user agent with the same name."""
    project = {
        _declared_name(path): path for path in markdown_files(context.repo / ".claude" / "agents")
    }
    user = {
        _declared_name(path): path for path in markdown_files(context.env.claude_dir / "agents")
    }
    for scope, agents in (("project", project), ("user", user)):
        for name, path in sorted(agents.items()):
            if scope == "user" and name in project:
                how = (SHADOWED, f"the project agent named {name} takes precedence")
            elif name == context.facts.agent:
                how = (ALWAYS, "the agent setting runs it as the main thread")
            else:
                how = (ON_DEMAND, "loads when Claude delegates to it or you mention it")
            _ = add(context, path, Place("subagent", scope, "D2"), how)


def output_styles(context: Context) -> None:
    """Output styles: the active one loads every session, the others never do."""
    active = context.facts.output_style
    project_dir = context.repo / ".claude" / "output-styles"
    project = {_declared_name(path): path for path in markdown_files(project_dir)}
    user_dir = context.env.claude_dir / "output-styles"
    user = {_declared_name(path): path for path in markdown_files(user_dir)}
    for scope, styles in (("project", project), ("user", user)):
        for name, path in sorted(styles.items()):
            if scope == "user" and name in project:
                how = (SHADOWED, f"the project output style named {name} takes precedence")
            elif name == active:
                how = (ALWAYS, "the active output style (outputStyle setting)")
            else:
                shown = active or "default"
                how = (NOT_LOADED, f"not the active output style (outputStyle is {shown})")
            _ = add(context, path, Place("output-style", scope, "D2"), how)


def agent_memory(context: Context) -> None:
    """Subagent memory folders: MEMORY.md loads into that subagent when it runs."""
    for scope, root in (
        ("user", context.env.claude_dir / "agent-memory"),
        ("project", context.repo / ".claude" / "agent-memory"),
        ("local", context.repo / ".claude" / "agent-memory-local"),
    ):
        for path in markdown_files(root):
            agent = path.parent.name
            reason = f"loads into the {agent} subagent when it runs"
            if path.name != "MEMORY.md":
                reason = f"memory topic file of the {agent} subagent, read on demand"
            _ = add(context, path, Place("agent-memory", scope, "D2"), (ON_DEMAND, reason))


def loop_md(context: Context) -> None:
    """loop.md: the default prompt of a bare /loop (project shadows user)."""
    project = context.repo / ".claude" / "loop.md"
    user = context.env.claude_dir / "loop.md"
    for scope, path in (("project", project), ("user", user)):
        if not path.is_file():
            continue
        how = (ON_DEMAND, "the prompt a bare /loop runs")
        if scope == "user" and project.is_file():
            how = (SHADOWED, "the project's .claude/loop.md takes precedence")
        elif path.stat().st_size > LOOP_LIMIT_BYTES:
            how = (TRUNCATED, "content beyond 25,000 bytes is truncated")
        _ = add(context, path, Place("loop-md", scope, "D2"), how)


def config_files(context: Context) -> None:
    """Settings files and .mcp.json (domain D4)."""
    candidates = (
        ("user", context.env.claude_dir / "settings.json", "settings"),
        ("project", context.repo / ".claude" / "settings.json", "settings"),
        ("local", context.repo / ".claude" / "settings.local.json", "settings"),
        ("project", context.repo / ".mcp.json", "mcp-json"),
    )
    for scope, path, kind in candidates:
        if path.is_file():
            reason = "settings layer" if kind == "settings" else "project MCP servers"
            _ = add(context, path, Place(kind, scope, "D4"), (CONFIG, reason))


def mcp_subset(claude_json: Path, repo: Path) -> JsonObj:
    """The audited part of ~/.claude.json: user-scope and this project's local-scope servers."""
    try:
        root = as_obj(read_json(claude_json))
    except (OSError, ValueError):
        return {}
    subset: JsonObj = {}
    servers = get_obj(root, "mcpServers")
    if servers:
        subset["mcpServers"] = servers
    local = get_obj(get_obj(get_obj(root, "projects"), str(repo)), "mcpServers")
    if local:
        subset["projects"] = {str(repo): {"mcpServers": local}}
    return subset


def claude_json_subset(context: Context) -> None:
    """The MCP servers in ~/.claude.json (user and local scope), audited as a stable subset.

    Claude Code rewrites the rest of that file during every session, so only the subset is
    hashed and audited; the report says so.
    """
    path = context.env.claude_json
    if not path.is_file():
        return
    subset = mcp_subset(path, context.repo)
    if not subset:
        return
    source = add(context, path, Place("claude-json-mcp", "user", "D4"), (CONFIG, "MCP servers"))
    source.subset = "mcpServers (user scope) and this project's mcpServers (local scope) only"
    load_text(source, dumps(subset))


def _count(directory: Path, pattern: str) -> int:
    return sum(1 for _ in directory.rglob(pattern)) if directory.is_dir() else 0


def out_of_scope(context: Context) -> None:
    """Record what loads but is excluded from the audit, with counts."""
    found = context.found
    reason_skill = "skills are out of scope (the brief excludes them)"
    reason_command = "commands are skills since Claude Code merged them; out of scope"
    reason_workflow = "saved workflows are excluded like skills"
    for scope, base in (("user", context.env.claude_dir), ("project", context.repo / ".claude")):
        for what, folder, pattern, reason in (
            ("skills", "skills", "SKILL.md", reason_skill),
            ("commands", "commands", "*.md", reason_command),
            ("workflows", "workflows", "*", reason_workflow),
        ):
            total = _count(base / folder, pattern)
            if total:
                found.note_out_of_scope(
                    context.show(base / folder), f"{scope} {what}", total, reason
                )
    plugins = sorted(plugin for plugin, enabled in context.facts.enabled_plugins.items() if enabled)
    if plugins:
        found.note_out_of_scope(
            "enabledPlugins",
            "plugin-provided skills, agents, hooks and MCP servers",
            len(plugins),
            "provided by installed plugins (this one included): cited as evidence only",
        )


def own_plugin_entries(source: Source) -> list[int]:
    """Line numbers of this plugin's own enabledPlugins entries (never a defect on their own)."""
    return [number for number, line in enumerate(source.lines, start=1) if f'"{OWN_PLUGIN}' in line]


def discover(context: Context) -> None:
    """Run every Claude component and config discovery step."""
    subagents(context)
    output_styles(context)
    agent_memory(context)
    loop_md(context)
    config_files(context)
    claude_json_subset(context)
    out_of_scope(context)
