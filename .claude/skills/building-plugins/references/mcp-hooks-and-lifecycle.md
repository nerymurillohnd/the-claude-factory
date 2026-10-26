# MCP hooks, connection lifecycle and timeouts

Read this when the work involves a hook that matches MCP tools, an `mcp_tool` hook handler, a server's connection state, authentication or MCP timeouts, or when you answer a question about how they behave. Read the official section behind each claim before you rely on it, and when the docs and the release notes (read raw from <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>) disagree, the release notes win.

## Before you start

- Inspect the plugin's manifest, MCP configuration, hook definitions, README, permissions and tests before proposing a change.
- Identify the target Claude Code version before you rely on a version-specific feature.
- Distinguish servers a project or user configures from servers a plugin bundles, and declarative hooks from a mod's in-process function hooks: they do not share a schema or a lifecycle.
- Distinguish project policy, documented behavior and observed runtime behavior. Report a conflict instead of changing policy silently.
- Inspect configuration statically: never launch plugin code, connect a server or authenticate while building. Runtime checks are the `testing-plugins` skill's live MCP checks, once Nery says the plugin is ready.

## The three MCP identities

- A server a project or user configures is named by its configuration key where a server name is required.
- A plugin-bundled server's identifier is `plugin:<plugin-name>:<server-name>`.
- A plugin tool's callable name is `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`, with any character outside `A-Z`, `a-z`, `0-9`, `_` and `-` replaced by `_`.
- An `mcp_tool` handler's `tool` field takes the tool's server-local name, never the full callable name.

For plugin `my-plugin`, server `db` and tool `security_scan`:

| Purpose | Value |
| --- | --- |
| Plugin MCP configuration key | `db` |
| `mcp_tool.server` | `plugin:my-plugin:db` |
| `mcp_tool.tool` | `security_scan` |
| Callable tool name | `mcp__plugin_my-plugin_db__security_scan` |
| Matcher for all tools on that server | `^mcp__plugin_my-plugin_db__.*$` |

## Hook directions

- An MCP tool matcher observes or controls Claude's calls to MCP tools.
- `type: "mcp_tool"` is a hook that itself calls a configured server's tool.
- Keep the triggering tool separate from the tool the handler calls: `matcher: "Write|Edit"` observes file edits, while its `mcp_tool` handler can call a separate `security_scan`.
- Never put a callable tool name where a server identifier is required.

## `mcp_tool` handlers

- Set `type` to `"mcp_tool"`; `server` and `tool` are required; add `input` only when the tool needs arguments, and check them against the tool's real input schema.
- `${path}` in a string value of `input` takes the event's JSON input, such as `${tool_input.file_path}`. Check that each path exists for the event and the triggering tool. It is not shell expansion or environment interpolation.
- Use only the documented common fields and the fields `mcp_tool` supports. Never copy command-only fields (`command`, `args`, `shell`, `async`) into it.
- `onFailure: "block"` exists for `command` and `http` hooks only (`/en/hooks` → Block the action when a hook fails); do not assume it for `mcp_tool`.
- Set an explicit `timeout` suited to the task.

## Common fields

- `timeout` is in seconds. Events have their own defaults and shared budgets, so hooks do not all get the same effective timeout.
- `statusMessage` is a progress message, never a result or a decision.
- `if` works only on documented tool events; a handler with `if` on another event does not run. It is one permission-pattern condition, not a Boolean language.
- `once` has its documented meaning in skill frontmatter only; do not expect it in settings or agent frontmatter.
- Keep the event → matcher group → handlers nesting.

## Matching MCP tool calls

- Use the full callable name in matchers, a handler's `if`, permission rules, a skill's `allowed-tools` and a subagent's `tools`. Never match a plugin server by its bare key, such as `mcp__db__.*`.
- A bare prefix is not a wildcard: include a tool suffix or a regex. Anchor a whole-name regex with `^` and `$`, and escape metacharacters when you build a pattern from an outside name.
- Check that the event supports a matcher and which input field it matches.
- Review the related matchers, permissions and hook references whenever a plugin or server is renamed.

## Results and failures

- An MCP tool result's text is read with command-hook stdout semantics for exit code 0. Read the current exit-code-0 rule and the event's output schema before generating decision JSON. An MCP tool result has no process exit code.
- Tell a successful response that carries a decision apart from a transport failure or `isError: true`. `isError: true` is a non-blocking hook error: execution continues. An unavailable connection is a possible non-blocking failure, not a denial.
- Never build a mandatory security boundary on an MCP hook failing closed. Document the failure policy you chose and any gap between it and what the handler supports.
- A Stop hook that can ask for more work needs the event's documented recursion controls.

## Startup and connection state

- `SessionStart` at launch (with `--continue` or `--resume` too) and every `Setup` event fire before the session's servers are available: their `mcp_tool` hooks are skipped, and the debug log records `mcp_tool hooks are not available for the 'SessionStart' hook event (no MCP client context)` or the same naming `Setup` (`/en/hooks` → Events that fire before MCP servers are available). For launch-time work use a `command` hook. A later `SessionStart`, after `/clear` or compaction, can run `mcp_tool` hooks.
- Decision-capable events such as `PreToolUse` and `Stop` wait for a connecting server within both `MCP_TIMEOUT` and the hook's timeout; observational events such as `Notification` and `SessionEnd` do not wait.
- `cached` is a deferred connection, not a broken server: it connects when its tool is called, and a hook gets a non-blocking error if it is still unavailable then. An `mcp_tool` hook never starts an OAuth flow: authenticate the server from `/mcp` first.
- Let Claude Code manage a plugin server's connection; never add startup or reconnect loops that duplicate it.

## Timeout layers

- `MCP_TIMEOUT` (server startup) and `MCP_TOOL_TIMEOUT` (tool execution) are in milliseconds (`/en/env-vars`). A server configuration's `timeout` and a hook handler's `timeout` differ in unit and scope.
- Check the current environment-variable reference before relying on defaults, per-server overrides, transport timers or idle timeouts.
- Never raise an execution timeout to hide an authentication, startup or missing-server failure.

## Validate and debug

1. Parse the configuration without executing plugin code.
2. Check hook nesting, handler type, common fields and event compatibility.
3. Resolve the plugin name, server key, scoped server identifier and callable tool name.
4. Check the tool exists and its argument schema, from trusted docs or discovery already authorized.
5. Check event input paths, substitution and the event's output.
6. Check authentication, connection state, timeout units and failure behavior.
7. Review permissions, matching and possible hook feedback loops.
8. Run the skill's static checks (`check-manifest-schema.py`, and `check-mcp-schema.py` for a server config) and `claude plugin validate --strict`, without starting servers.
9. Report the checks run, the checks not run, version requirements and remaining risks. The runtime cases (identifiers, matching, inputs, outputs, connection states, startup events, timeouts) are verified live by `testing-plugins`, not here.

- Read the debug log before changing configuration for a skipped hook: `claude --debug-file <path>` for a known location, or `claude --debug`. The "no MCP client context" lines are lifecycle limits, not malformed identifiers. Redact secrets before quoting a log.
- A hook does not work because its JSON parses or its configuration validates.

## Example

This plugin hook applies only when plugin `my-plugin` bundles server `db` and that server exposes `security_scan` taking a string `file_path`:

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
            "input": { "file_path": "${tool_input.file_path}" },
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

It inspects after the edit; it cannot block a Write or Edit that already ran.

## Answering

- Answer the question before the implementation details, and cite the official section behind each claim about product behavior.
- Label assumptions, project policy and unverified runtime behavior, and report incompatible requirements instead of weakening validation.

## Official sources

| Topic | Page |
| :-- | :-- |
| `mcp_tool` fields, common fields, input and output, exit code 0, decision control, matching MCP tools, debugging | `https://code.claude.com/docs/en/hooks.md` (sections: MCP tool hook fields, Common fields, Hook input and output, Exit code 0, Decision control, Match MCP tools, Debug hooks) |
| Plugin-provided servers, `cached` status, authentication | `https://code.claude.com/docs/en/mcp.md` (Plugin-provided MCP servers, Server status detail, Authenticate with remote MCP servers) |
| Timeouts and environment variables | `https://code.claude.com/docs/en/env-vars.md` |
| MCP components, path variables, persistent data | `https://code.claude.com/docs/en/plugins/components.md`, `https://code.claude.com/docs/en/plugins/manifest-reference.md` |
| Reload | `https://code.claude.com/docs/en/plugins/cli-reference.md` (reload-plugins) |
| Changes since the docs | <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md> |
