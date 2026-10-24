---
name: mcp-hooks-plugins
description: Use before answering MCP questions or working on .mcp.json, plugin mcpServers, mcp_tool handlers, MCP hook matchers,scoped tool names, authentication, connection lifecycle, or MCP timeouts.
---

# MCP Hooks and Plugins

## Required Context

1. Read the project's `CLAUDE.md` and applicable ADRs.
2. Read `.claude/rules/plugins/mcp-component.md` explicitly, even when no
   `.mcp.json` file is being opened.
3. Follow that rule's configuration, portability, lifecycle, naming, security,
   and validation requirements.
4. Report a missing rule file; do not claim to have read it or reconstruct its
   current contents from memory.
5. Inspect the relevant plugin manifest, MCP configuration, hook definitions,
   README, permissions, and tests before proposing changes.
6. Read the official reference sections relevant to the task before asserting
   schema, lifecycle, authentication, or version-dependent behavior.
7. Corroborate every documented behavior against the changelog and the release
   notes for the installed `claude --version`; when they disagree with the docs,
   the changelog and release notes win.
8. Distinguish project policy, documented product behavior, and observed runtime
   behavior. Report conflicts instead of silently changing policy.

## Establish Scope

- Classify the work as maintainer infrastructure or distributed plugin code.
- Keep plugin runtime requirements independent of maintainer tools and environments.
- Distinguish project/user-configured MCP servers from plugin-bundled servers.
- Identify the target Claude Code version before relying on version-specific features.
- Distinguish declarative hooks from in-process mod function hooks; do not assume
  they share the same schema or lifecycle.
- Separate metadata inspection from runtime testing; never launch plugin code,
  connect servers, or authenticate solely to validate configuration.

## Distinguish the Three MCP Identities

- Use the configured server key for a non-plugin server where a server name is required.
- Use `plugin:<plugin-name>:<server-name>` for a plugin-bundled server identifier.
- Use `mcp__plugin_<plugin-name>_<server-name>__<tool-name>` for a plugin tool's
  callable name.
- Replace characters outside `A-Z`, `a-z`, `0-9`, `_`, and `-` with `_` when
  deriving callable plugin tool names.
- Keep the tool's server-local name in an `mcp_tool` handler's `tool` field;
  do not put the full callable name there.

Example identities for plugin `my-plugin`, server `db`, and tool `security_scan`:

| Purpose | Value |
| --- | --- |
| Plugin MCP configuration key | `db` |
| `mcp_tool.server` | `plugin:my-plugin:db` |
| `mcp_tool.tool` | `security_scan` |
| Callable tool name | `mcp__plugin_my-plugin_db__security_scan` |
| Matcher for all tools on that server | `^mcp__plugin_my-plugin_db__.*$` |

## Distinguish Hook Directions

- Use an MCP tool matcher when observing or controlling Claude's calls to MCP tools.
- Use `type: "mcp_tool"` when the hook itself must call a configured MCP server tool.
- Keep the triggering tool name separate from the MCP tool invoked by the handler.
- Never substitute a callable tool name for a configured server identifier.

For example, `matcher: "Write|Edit"` observes file edits, while its
`mcp_tool` handler can call a separate `security_scan` tool.

## Configure MCP Tool Handlers

- Set `type` to `"mcp_tool"`.
- Require `server` and `tool`.
- Add `input` only when arguments are needed.
- Validate arguments against the target MCP tool's actual input schema.
- Use `${path}` substitution in string values of `input` to reference the event's
  JSON input, such as `${tool_input.file_path}`.
- Verify that every referenced input path exists for the selected event and
  triggering tool.
- Do not assume hook-input substitution is shell expansion or environment-variable
  interpolation.
- Use only documented common fields and fields supported by `mcp_tool`.
- Never copy command-only fields such as `command`, `args`, `shell`, or `async`
  into an MCP tool handler.
- Do not assume `onFailure: "block"` is supported for MCP tool hooks merely because
  command or HTTP hooks support it.
- Set an explicit hook timeout appropriate to the task.

## Apply Common Fields Correctly

- Express hook `timeout` in seconds.
- Account for event-specific defaults and shared event budgets; do not assume every
  hook receives the same effective timeout.
- Use `statusMessage` only as a progress message, not as a result or decision.
- Use `if` only on documented tool events; a handler with `if` on another event
  does not run.
- Treat `if` as one permission-pattern condition, not a Boolean expression language.
- Use `once` only when its documented skill-frontmatter semantics apply; do not
  expect it to work in settings or agent frontmatter.
- Preserve the event → matcher group → handlers nesting.

## Match MCP Tool Calls

- Use full plugin-scoped callable names in matchers, a handler's `if` field,
  permission references, skill `allowed-tools`, and subagent `tools`.
- Never match a plugin-bundled server through its bare key, such as
  `mcp__db__.*`.
- Include a tool suffix or regex when matching a server's tools; a bare prefix is
  not an implicit wildcard.
- Anchor regex matchers with `^` and `$` when a whole-name match is required.
- Escape regex metacharacters when constructing patterns from external names.
- Verify matcher support and the matched input field for the selected event.
- Review related matchers, permissions, and hook references whenever a plugin or
  server is renamed.

## Interpret Results and Failures

- Read an MCP tool result's text content using command-hook stdout semantics for
  exit code 0.
- Consult the current exit-code-0 parsing rule and the selected event's output
  schema before generating decision JSON.
- Do not assume an MCP tool result has a command process exit code.
- Distinguish a successful tool response containing an event-supported decision
  from a transport failure or `isError: true`.
- Treat `isError: true` as a non-blocking hook error; execution continues.
- Treat an unavailable connection as a possible non-blocking failure, not an
  implicit denial.
- Never implement a mandatory security boundary that depends on MCP hook failures
  automatically blocking execution.
- Document the chosen failure policy and any gap between that policy and the
  handler's supported behavior.
- Prevent recursive Stop behavior when designing a Stop hook that can request
  continued work; inspect the event's documented recursion controls.

## Handle Startup and Connection State

- Expect launch-time `SessionStart`, including `--continue` and `--resume`, to run
  before MCP servers are available to hooks.
- Expect every `Setup` event to lack MCP client context.
- Do not rely on `mcp_tool` handlers for launch-time initialization; use a
  `type: "command"` SessionStart hook when launch-time work is required.
- Distinguish launch-time SessionStart from later SessionStart events after
  `/clear` or compaction, when MCP tool hooks can run.
- Expect decision-capable events such as `PreToolUse` and `Stop` to wait for a
  connecting server within both `MCP_TIMEOUT` and the hook's timeout.
- Expect observational events such as `Notification` and `SessionEnd` not to wait
  for a connecting server.
- Treat `cached` as deferred connection, not proof of a broken server.
- Account for a cached server beginning connection when its tool is called.
- Report a non-blocking error if the server is still unavailable when required.
- Require authentication before relying on a hook; MCP tool hooks never initiate
  an OAuth flow.
- Preserve Claude Code's plugin connection lifecycle rather than duplicating it
  with custom startup or reconnect loops.
- Apply the local MCP component rule when diagnosing reloads, directory changes,
  cloud-session wake-up, and recent stdio connection failures.

## Keep Timeout Layers Separate

- Use `MCP_TIMEOUT` for server startup and connection waiting; express it in milliseconds.
- Use `MCP_TOOL_TIMEOUT` for MCP tool execution; express it in milliseconds.
- Distinguish an MCP server configuration's `timeout` from a hook handler's
  `timeout`; their units and scope differ.
- Check the current environment-variable reference before relying on defaults,
  per-server overrides, transport timers, or idle-timeout behavior.
- Do not increase execution timeouts to conceal authentication, startup, or
  missing-server failures.

## Preserve Plugin Configuration Requirements

- Read `.claude/rules/plugins/mcp-component.md` for all `.mcp.json` changes.
- Apply its relevant requirements when MCP servers are declared inline in
  `plugin.json`, even though that file does not trigger its path scope.
- Verify server definition precedence before introducing overlapping definitions.
- Use plugin path variables only in fields where their substitution is documented.
- Keep credentials out of committed configuration, examples, logs, and reports.
- Verify README prerequisites for every executable, runtime, environment variable,
  authentication step, and optional feature.
- Keep persistent state outside the plugin installation directory.

## Validate and Debug

1. Parse configuration without executing plugin code.
2. Check hook nesting, handler type, common fields, and event compatibility.
3. Resolve plugin name, server key, scoped server identifier, and callable tool name.
4. Verify tool existence and argument schema using trusted documentation or
   previously authorized discovery.
5. Verify event input paths, substitution behavior, and event-specific output.
6. Check authentication, connection state, timeout units, and failure behavior.
7. Review permissions, matching, and potential hook feedback loops.
8. Run existing static repository checks without starting servers.
9. Run runtime integration checks only when authorized; distinguish them from
   static validation.
10. Report checks performed, checks not performed, version requirements, and
    remaining risks.

- Inspect debug logs before changing configuration to address skipped hooks.
- Use `claude --debug-file <path>` for a known log location or `claude --debug`
  for the default debug log.
- Look for `mcp_tool hooks are not available for the 'SessionStart' hook event
  (no MCP client context)` or the corresponding `Setup` message.
- Treat those messages as lifecycle constraints, not malformed server identifiers.
- Redact secrets before quoting logs.
- Do not claim a hook works because its JSON parses or its configuration validates.

## Configuration Example

Use this plugin hook only when plugin `my-plugin` bundles server `db`, and that
server exposes `security_scan` accepting a string `file_path`.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "mcp_tool",
            "server": "plugin:my-plugin:db",
            "tool": "security_scan",
            "input": {
              "file_path": "${tool_input.file_path}"
            },
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Treat this as post-edit inspection, not prevention of the edit. Do not claim the
scanner can retroactively block an already completed Write or Edit.

## Required Verification Cases

- Check correct and incorrect plugin-scoped server identifiers.
- Check full tool-name matching and rejection of bare-server assumptions.
- Check valid arguments and missing or invalid event input paths.
- Check successful text output, event-supported JSON decisions, and `isError: true`.
- Check connected, connecting, cached, unavailable, and unauthenticated states.
- Check launch-time SessionStart, later SessionStart, and Setup separately.
- Check hook timeout versus startup and execution timeout behavior.
- Check that static validation never launches plugin code.
- Use mocks or fixtures for unavailable runtime states; label untested live behavior.
- Add evals only when explicitly requested by the user.

## Response Requirements

- Answer the specific question before presenting implementation details.
- Cite official sections supporting material product-behavior claims.
- Return complete updated files when changing configuration or code.
- Label assumptions, project policies, and unverified runtime behavior.
- Report incompatible requirements instead of silently weakening validation.

## Official Reference Map

Read the relevant sections before answering or implementing; use the current
official page when an anchor has moved.

### Changelog and release notes
- Changelog:
  https://code.claude.com/docs/en/changelog
  https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- Release notes:
  https://github.com/anthropics/claude-code/releases

### MCP hook contract and event data
- MCP tool fields:
  https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields
- Common handler fields:
  https://code.claude.com/docs/en/hooks#common-fields
- Hook input and output:
  https://code.claude.com/docs/en/hooks#hook-input-and-output
- Exit-code-0 output parsing:
  https://code.claude.com/docs/en/hooks#exit-code-0
- Event-specific decisions:
  https://code.claude.com/docs/en/hooks#decision-control
- MCP tool matching:
  https://code.claude.com/docs/en/hooks#match-mcp-tools
- Hook diagnostics:
  https://code.claude.com/docs/en/hooks#debug-hooks

### Server configuration, connection, and authentication
- Plugin-provided servers:
  https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers
- Cached status and connection diagnostics:
  https://code.claude.com/docs/en/mcp#server-status-detail
- Remote-server authentication:
  https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers
- Environment variables and timeout definitions:
  https://code.claude.com/docs/en/env-vars

### Plugin integration
- MCP components:
  https://code.claude.com/docs/en/plugins/components#mcp-servers
- Path variables and persistent data:
  https://code.claude.com/docs/en/plugins/components#path-variables-and-persistent-data
- Plugin reload behavior:
  https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins
