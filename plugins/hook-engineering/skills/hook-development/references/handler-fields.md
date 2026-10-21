# Hook handler fields

Read when writing or reviewing a handler object: its type, common fields, command, http, mcp_tool, prompt and agent fields, exec and shell form, and path placeholders. Source: <https://code.claude.com/docs/en/hooks#hook-handler-fields>.

## Contents

- Handler types and how they run
- Common fields
- Command hook fields
- Exec form and shell form
- HTTP hook fields
- MCP tool hook fields
- Prompt and agent hook fields
- Reference scripts by path

## Handler types and how they run

Docs: [hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields)

| `type` | Runs |
| :-- | :-- |
| `command` | A shell command or executable; JSON input on stdin |
| `http` | A POST of the JSON input to a URL |
| `mcp_tool` | A tool on a configured MCP server; its text output is read like command stdout |
| `prompt` | A single-turn evaluation by a Claude model |
| `agent` | A subagent that can use tools such as Read, Grep and Glob (experimental) |

- Matching handlers run in parallel; the limit for prompt and agent hooks is in `lifecycle.md` → How a hook resolves.
- Handlers run in the current directory with Claude Code's environment. If it no longer exists, command hooks run from the first that does: the session's start directory, the project root, the home directory, the system temp directory (a warning goes to the debug log).
- `$CLAUDE_CODE_REMOTE` is `"true"` in remote web environments. `$CLAUDE_CODE_BRIDGE_SESSION_ID` holds the Remote Control session ID while connected (v2.1.199+).

**Handler types per event:**
- All five (`command`, `http`, `mcp_tool`, `prompt`, `agent`): `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionDenied`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`.
- `PermissionRequest`: all but `agent` (an agent hook there is skipped).
- `SessionStart`: `command` and `mcp_tool` only. `Setup`: `command` only (an `mcp_tool` hook there is always skipped).
- Every other event: `command`, `http`, `mcp_tool` only.

## Common fields

Docs: [common fields](https://code.claude.com/docs/en/hooks#common-fields)

| Field | Required | Notes |
| :-- | :-- | :-- |
| `type` | yes | `command`, `http`, `mcp_tool`, `prompt`, `agent` |
| `if` | no | One permission rule; tool events only (see `matchers-and-if.md`) |
| `timeout` | no | Seconds. Defaults: 600 for command, http, mcp_tool; 30 for prompt; 60 for agent. Command, http and mcp_tool drop to 30 on UserPromptSubmit, PreModelSwitch and PostModelSwitch, and to 10 on MessageDisplay. SessionEnd shares a 1.5 s budget, raised to the longest per-hook timeout in your settings, up to 60 s. Not enforced on `async: true` command hooks |
| `statusMessage` | no | Spinner text while the hook runs |
| `once` | no | Remove after the first successful run. Skill frontmatter only; ignored elsewhere |

## Command hook fields

Docs: [command hook fields](https://code.claude.com/docs/en/hooks#command-hook-fields)

| Field | Notes |
| :-- | :-- |
| `command` | Required. With `args`, the executable to spawn |
| `args` | Argument list; switches to exec form |
| `async` | Background run; what it delivers and its limits are in `background-hooks.md` |
| `asyncRewake` | Background run that can wake Claude; see `background-hooks.md` |
| `shell` | `"bash"` or `"powershell"`. Default `"bash"`, or `"powershell"` on Windows without Git Bash. Ignored when `args` is set |
| `onFailure` | `"continue"` or `"block"` (v2.1.295+). Use `block` on policy hooks only: a failure does what exit 2 does on that event. No effect on Stop, SubagentStop, TaskCompleted, TeammateIdle or async hooks |

## Exec form and shell form

Docs: [exec form and shell form](https://code.claude.com/docs/en/hooks#exec-form-and-shell-form)

- **Exec form** (`args` present): `command` is resolved as an executable on `PATH` and spawned directly; each `args` element is one argument, verbatim. Placeholders are substituted as plain strings; no quoting needed. The docs prefer it whenever a placeholder appears, but for a hook that ships to others the Windows rule below decides.
- **Shell form** (no `args`): the string goes to `sh -c` on macOS and Linux, Git Bash on Windows, or PowerShell without Git Bash. Use it for pipes, `&&`, redirects or globs. Wrap each placeholder in double quotes: `"node \"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.js --fix"`.
- Windows exec form needs a real executable such as `.exe`. `.cmd` and `.bat` shims can't be spawned without a shell: run `node` with the script path, or use shell form.
- In exec form, `command` is one executable. A bare name with whitespace (`node script.js`) logs a warning and fails; move the extra words into `args`. An absolute path with spaces is fine.
- Both forms export `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` as environment variables.
- Plugin hooks substitute `${user_config.*}` in **exec form only**. A shell-form plugin hook that references it fails (since v2.1.207); read `$CLAUDE_PLUGIN_OPTION_<KEY>` instead, or switch to exec form.

A plugin guard on Bash and PowerShell, in shell form so it runs on macOS, Linux and Windows through Git Bash, failing closed:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/guard.sh",
            "timeout": 10,
            "onFailure": "block"
          }
        ]
      }
    ]
  }
}
```

`onFailure` needs Claude Code v2.1.295 or later. Exec form (`"command": "${CLAUDE_PLUGIN_ROOT}/hooks/guard.sh", "args": []`) would fail on Windows, where it needs a real `.exe`, and with `onFailure: "block"` that failure would block every Bash and PowerShell call. Use exec form for a hook that ships to others only when `command` is a real executable everywhere, such as `node` with the script path in `args`.

## HTTP hook fields

Docs: [HTTP hook fields](https://code.claude.com/docs/en/hooks#http-hook-fields)

| Field | Notes |
| :-- | :-- |
| `url` | Required. POST target; body is the JSON input with `Content-Type: application/json` |
| `headers` | Key-value pairs; `$VAR` / `${VAR}` interpolated only for variables in `allowedEnvVars` |
| `allowedEnvVars` | Variables allowed in headers; unlisted references become empty strings |
| `onFailure` | `"continue"` (default) or `"block"` (v2.1.295+; policy hooks only) |

Response handling is in `exit-codes.md` → HTTP hooks. Settings-level `allowedHttpHookUrls` and `httpHookAllowedEnvVars` also apply (see `locations-and-scope.md`).

## MCP tool hook fields

Docs: [MCP tool hook fields](https://code.claude.com/docs/en/hooks#mcp-tool-hook-fields)

| Field | Notes |
| :-- | :-- |
| `server` | Required. A configured server name. For a plugin-bundled server: `plugin:<plugin>:<server>`, not the bare key |
| `tool` | Required. Tool name on that server |
| `input` | Arguments; string values support `${path}` substitution from the input JSON, such as `"${tool_input.file_path}"` |

- The hook never starts OAuth: authenticate the server in `/mcp` first.
- How the tool's result is read, a server still connecting, and the events that fire before MCP servers are available (SessionStart at launch, Setup): `exit-codes.md` → MCP tool hooks.

## Prompt and agent hook fields

Docs: [prompt and agent hook fields](https://code.claude.com/docs/en/hooks#prompt-and-agent-hook-fields)

The fields (`prompt`, `$ARGUMENTS` and `\$` escaping, `model`, `timeout`, `continueOnBlock`) are in `prompt-and-agent-hooks.md` → Fields, and how these hooks evaluate and what they return in the rest of that file: <https://code.claude.com/docs/en/hooks#prompt-based-hooks>, <https://code.claude.com/docs/en/hooks#agent-based-hooks>.

## Reference scripts by path

Docs: [reference scripts by path](https://code.claude.com/docs/en/hooks#reference-scripts-by-path) · [plugin environment variables](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables)

| Placeholder | Points to |
| :-- | :-- |
| `${CLAUDE_PROJECT_DIR}` | The project root where the session started; also set for stdio MCP servers and plugin LSP servers |
| `${CLAUDE_PLUGIN_ROOT}` | The plugin's installation directory |
| `${CLAUDE_PLUGIN_DATA}` | The plugin's persistent data directory, kept across updates |

- In a worktree, `${CLAUDE_PROJECT_DIR}` stays at the original root; the input's `cwd` follows Claude into the worktree and after `cd`.
- Prefer exec form for any hook that references a placeholder. In shell form, wrap each placeholder in double quotes.
