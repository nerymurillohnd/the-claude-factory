---
paths:
  - ".mcp.json"
  - "**/.mcp.json"
---

# MCP Configuration

## Scope and Ownership

- Determine whether the file configures project-level servers or plugin-provided servers before changing it.
- Apply plugin-specific lifecycle, path substitution, and naming rules only to plugin-provided servers.
- Keep plugin MCP configuration independent of maintainer tools, environments, and machine-specific paths.
- Consult the official references below before introducing fields or relying on version-specific behavior.
- Corroborate every documented behavior against the changelog and the release notes for the installed `claude --version`; when they disagree with the docs, the changelog and release notes win.
- Invoke `mcp-hooks-plugins` skill before answering questions or planning, implementing, reviewing, validating, or debugging MCP behavior in hooks or plugins; follow its required reading before proceeding.

## Configuration and Portability

- Keep plugin `.mcp.json` at the plugin root, not inside `.claude-plugin/`.
- Use a top-level `mcpServers` object as the repository's standard configuration shape.
- Give each server a stable, descriptive key.
- Keep stdio executable names in `command` and individual arguments in `args`.
- Specify the transport explicitly for remote servers: `http`, `sse`, or `ws`.
- Prefer HTTP over deprecated SSE when the server supports it.
- Verify transport support against the server's documentation and the supported Claude Code version.
- Use `${CLAUDE_PLUGIN_ROOT}` for bundled plugin files and executables.
- Use `${CLAUDE_PLUGIN_DATA}` for persistent plugin state; never write mutable state into the plugin installation directory.
- Use `${CLAUDE_PROJECT_DIR}` for the stable project root in plugin-provided configurations.
- Apply plugin path placeholders only in supported fields: `command`, `args`, and `env` for stdio; `url`, `headers`, and `headersHelper` for HTTP, SSE, and WebSocket.
- Keep each `args` element as a separate argument; do not add shell quoting to argument values.
- Reference credentials through supported environment or user-configuration mechanisms; never commit secret values.
- Document required binaries, runtime versions, environment variables, authentication, and feature-specific prerequisites in the owning plugin's README.
- Check the plugin manifest for overlapping server definitions; account for manifest entries overriding same-named `.mcp.json` entries.

## Lifecycle and Diagnostics

- Let Claude Code manage plugin server connections; do not add custom startup or reconnection logic merely to duplicate its lifecycle.
- Add or remove plugin-provided servers through plugin installation or uninstallation, not manual MCP registration commands.
- Use `/mcp` to inspect server status or disable an installed plugin server without uninstalling its plugin.
- Account for deferred connections: a cached remote server can connect on first tool use rather than at session startup.
- Account for the recent-failure cache when diagnosing plugin stdio servers; a failed connection can suppress new attempts for 15 minutes.
- Apply configuration changes through the documented plugin reload flow.
- Preserve the expectation that unchanged server configurations retain their live connections during reload.
- Account for non-interactive sessions applying plugin connection changes in the next session rather than through `/reload-plugins`.
- Verify documented directory-change and cloud-session behavior before treating deferred startup or reconnection as a configuration defect.
- Inspect the on-disk configuration when CLI output redacts stdio commands, arguments, environment values, or WebSocket URLs and headers.
- Never interpret redacted diagnostic output as missing configuration.

## Server and Tool Identity

- Reference plugin tools as `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`.
- Replace characters outside `A-Z`, `a-z`, `0-9`, `_`, and `-` with `_` when deriving callable plugin tool names.
- Use full callable names in permission rules, skill `allowed-tools`, subagent `tools`, and hook matchers.
- Never match a plugin tool using only the unscoped server key, such as `mcp__database-tools__.*`.
- Reference configured plugin servers as `plugin:<plugin-name>:<server-name>` where a server identifier is required, including an `mcp_tool` hook's `server` field.
- Check related permissions and hook references when renaming a server key.

## Validation

- Check JSON structure, transport fields, placeholder placement, referenced files, and documented prerequisites without launching servers.
- Separate static configuration validation from runtime connection testing.
- Never execute plugin code or connect to external services solely to validate metadata.
- Report unsupported fields, unresolved requirements, and version assumptions explicitly.

## Official References

- Corroborate documented behavior against the changelog and release notes:
  https://code.claude.com/docs/en/changelog
  https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
  https://github.com/anthropics/claude-code/releases
- Validate plugin ownership and packaging against:
  https://code.claude.com/docs/en/plugins/overview
- Validate plugin MCP behavior against:
  https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers
- Validate component configuration against:
  https://code.claude.com/docs/en/plugins/components#mcp-servers
- Validate path variables and persistent storage against:
  https://code.claude.com/docs/en/plugins/components#path-variables-and-persistent-data
- Validate server disabling behavior against:
  https://code.claude.com/docs/en/mcp#disable-a-server-without-removing-it
- Validate cached status interpretation against:
  https://code.claude.com/docs/en/mcp#server-status-detail
- Validate recent-failure connection suppression against:
  https://code.claude.com/docs/en/errors#skipping-connection-recent-failure-cached
- Validate reload behavior against:
  https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins
- Validate Agent SDK server-list replacement against:
  https://code.claude.com/docs/en/agent-sdk/typescript#mcpsetserversresult
- Validate directory-change behavior against:
  https://code.claude.com/docs/en/permissions#move-the-session-to-another-directory
- Validate cloud-session behavior against:
  https://code.claude.com/docs/en/claude-code-on-the-web
- Locate installed plugin configuration using:
  https://code.claude.com/docs/en/plugins/loading#find-plugins-on-disk
- Validate tool permission references against:
  https://code.claude.com/docs/en/permissions
- Validate subagent tool references against:
  https://code.claude.com/docs/en/sub-agents#available-tools
- Validate MCP hook matchers against:
  https://code.claude.com/docs/en/hooks#match-mcp-tools
- Validate MCP hook server identifiers against:
  https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields
