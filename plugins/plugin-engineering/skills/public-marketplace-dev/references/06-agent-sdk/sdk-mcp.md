# Connect to external tools with MCP

> Covers configuring MCP servers to extend an Agent SDK agent with external tools: transport types, tool search for large tool sets, authentication, and error handling. This pruned copy keeps only how MCP tools are allowed and named.

## Contents

- [Allow MCP tools](#allow-mcp-tools)
  - [Tool naming convention](#tool-naming-convention)
- [Documentation References](#documentation-references)

## Allow MCP tools

MCP tools require explicit permission before Claude can use them. Without permission, Claude sees that the tools are available but cannot call them.

### Tool naming convention

MCP tools are named `mcp__<server-name>__<tool-name>`, where `<server-name>` is the name the server is registered under, such as its key in `mcpServers`.

Claude Code replaces characters in the server name such as `.` and spaces with `_`. This table shows the full name of a `list_issues` tool for two server keys:

| Key in `mcpServers` | Full tool name |
| :- | :- |
| `github` | `mcp__github__list_issues` |
| `my.server` | `mcp__my_server__list_issues` |

Use the full tool names in `allowedTools` and in [MCP permission rules](https://code.claude.com/docs/en/permissions.md#mcp). For a server that a [plugin](https://code.claude.com/docs/en/agent-sdk/plugins.md) provides, `<server-name>` takes the [plugin-scoped form](https://code.claude.com/docs/en/mcp.md#plugin-provided-mcp-servers) and starts with `plugin_`.

## Documentation References

- Source page: https://code.claude.com/docs/en/agent-sdk/mcp (MCP servers in the Agent SDK: transports, tool search, authentication, error handling)
- https://code.claude.com/docs/en/permissions.md (permission rule syntax, including MCP rules)
- https://code.claude.com/docs/en/agent-sdk/plugins.md (loading plugins in the Agent SDK)
- https://code.claude.com/docs/en/mcp.md (MCP in Claude Code, including the plugin-scoped server name form)
