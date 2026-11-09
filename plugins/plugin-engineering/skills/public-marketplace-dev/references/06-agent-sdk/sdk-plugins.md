# Plugins in the SDK

> Covers loading custom plugins through the Agent SDK to extend Claude Code with skills, agents, hooks, and MCP servers. This pruned copy keeps only the plugin directory layout and the fix for plugin skills that do not appear.

## Contents

- [Plugin structure reference](#plugin-structure-reference)
  - [Skills not appearing](#skills-not-appearing)
- [Documentation References](#documentation-references)

## Plugin structure reference

A plugin directory typically contains a `.claude-plugin/plugin.json` manifest file. The manifest is optional: when it is omitted, Claude Code auto-discovers components from the directory layout. The directory can include:

```text theme={null}
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest (optional, components auto-discovered without it)
├── skills/                   # Agent Skills (invoked autonomously or via /plugin-name:skill-name)
│   └── my-skill/
│       └── SKILL.md
├── commands/                 # Skills as flat .md files
│   └── custom-cmd.md
├── agents/                   # Custom agents
│   └── specialist.md
├── hooks/                    # Event handlers
│   └── hooks.json
└── .mcp.json                # MCP server definitions
```

> **Note:** The `commands/` directory holds skills as flat Markdown files. Use `skills/` for new plugins. Claude Code supports both locations.

### Skills not appearing

When plugin skills don't work, check the following:

1. **Use the namespace**: invoke plugin skills as `/plugin-name:skill-name`.
2. **Validate skill files**: ensure each skill has a `SKILL.md` file in its own subdirectory under `skills/`, for example `skills/my-skill/SKILL.md`.

## Documentation References

- Source page: https://code.claude.com/docs/en/agent-sdk/plugins (loading plugins in the Agent SDK, plugin structure, and troubleshooting)
