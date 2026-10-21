# Matchers, MCP tool names and the if field

Read when writing or fixing a `matcher` or an `if`, or when a hook fires on the wrong calls or none. Source: <https://code.claude.com/docs/en/hooks#matcher-patterns>.

## Contents

- How a matcher is evaluated
- What each event matches on
- Matching MCP tools
- The if field
- How if patterns match Bash commands

## How a matcher is evaluated

Docs: [matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns) · [filter hooks with matchers](https://code.claude.com/docs/en/hooks-guide#filter-hooks-with-matchers)

| Matcher value | Evaluated as |
| :-- | :-- |
| `"*"`, `""` or omitted | Match all |
| Only letters, digits, `_`, `-`, spaces, `,` and `\|` | Exact string, or a list split by `\|` or `,` (whitespace around them allowed) |
| Any other character | JavaScript regular expression, **unanchored** (`RegExp.prototype.test`) |

- `Edit.*` matches both `Edit` and `NotebookEdit`. Use `^Edit$` for a whole-string match.
- FileChanged and StopFailure use a narrower exact set: letters, digits, `_` and `|`. A hyphen, space or comma there sends the matcher down the regex path, and only `|` separates alternatives.
- FileChanged builds its watch list differently: see [FileChanged](https://code.claude.com/docs/en/hooks#filechanged).
- A matcher on an event without matcher support is silently ignored.

## What each event matches on

Docs: [matcher patterns](https://code.claude.com/docs/en/hooks#matcher-patterns)

| Event | Matcher filters | Example values |
| :-- | :-- | :-- |
| PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied | Tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| SessionStart | How the session started | `startup`, `resume`, `clear`, `compact`, `fork` |
| Setup | CLI flag | `init`, `maintenance` |
| SessionEnd | Why it ended | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |
| Notification | Notification type | `permission_prompt`, `idle_prompt`, `agent_completed`… |
| SubagentStart, SubagentStop | Agent type | `Explore`, custom names, `^my-plugin:reviewer$` |
| PreCompact, PostCompact | Trigger | `manual`, `auto` |
| PreModelSwitch, PostModelSwitch | Canonical name of the target model | `claude-opus-5`, `.*opus.*` |
| ConfigChange | Configuration source | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| DirectoryAdded | How it was added | `slash_command`, `register_repo_root` |
| FileChanged | Literal filenames to watch | `.envrc\|.env` |
| StopFailure | Error type | `rate_limit`, `overloaded`, `cloud_credential_error` (v2.1.267+)… |
| InstructionsLoaded | Load reason | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| UserPromptExpansion | Command name | your skill or command names |
| Elicitation, ElicitationResult | MCP server name | your configured server names |
| UserPromptSubmit, PostToolBatch, Stop, TeammateIdle, TaskCreated, TaskCompleted, WorktreeCreate, WorktreeRemove, MessageDisplay, CwdChanged | No matcher support | always fires |

- Most events test the matcher against a field of the JSON input; tool events use `tool_name`. Model-switch events use the canonical name derived from `to_model`.
- A plugin-scoped agent name contains `:`, so it is a regex: anchor it, as in `^my-plugin:db-agent$`.
- `Bash` doesn't cover the `PowerShell` tool. A hook that guards shell commands matches `Bash|PowerShell`.

## Matching MCP tools

Docs: [match MCP tools](https://code.claude.com/docs/en/hooks#match-mcp-tools) · [plugin-provided MCP servers](https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers)

- MCP tools appear in tool events as `mcp__<server>__<tool>`.
- Every tool of one server: `mcp__memory__.*`. The `.*` is required: `mcp__memory` is an exact string and matches no tool.
- `mcp__.*__write.*` matches tools starting with `write` on any server.
- A plugin-bundled server's tools are `mcp__plugin_<plugin>_<server>__<tool>` (characters outside `A-Za-z0-9_-` become `_`). A matcher on the bare key never fires for them; use `mcp__plugin_<plugin>_<server>__.*`, in matchers and in `if`.

## The if field

Docs: [common fields](https://code.claude.com/docs/en/hooks#common-fields) · [filter by tool name and arguments with the if field](https://code.claude.com/docs/en/hooks-guide#filter-by-tool-name-and-arguments-with-the-if-field)

- Permission rule syntax, such as `Bash(git *)` or `Edit(*.ts)`. The handler spawns only if the tool call matches.
- Evaluated only on PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest and PermissionDenied. **On any other event a handler with `if` never runs.**
- Exactly one rule. No `&&`, `||` or lists: write one handler per condition.
- For file tools, `Edit(src/**)` matches only `src` in the working directory; `Edit(**/src/**)` matches a `src` at any depth.
- It saves process spawns. It is best-effort: enforce a hard allow or deny with permission rules, and filter inside the script for a guard.

## How if patterns match Bash commands

Docs: [how if patterns match Bash commands](https://code.claude.com/docs/en/hooks#bash-if-matching)

| `if` | Command | Runs? | Why |
| :-- | :-- | :-- | :-- |
| `Bash(git *)` | `FOO=bar git push` | yes | Leading `VAR=value` assignments are stripped |
| `Bash(git *)` | `npm test && git push` | yes | Each subcommand is checked |
| `Bash(rm *)` | `echo $(rm -rf /)` | yes | Commands in `$()` and backticks are checked |
| `Bash(rm *)` | `echo $(date)` | no | No subcommand matches |
| `Bash(git push *)` | `echo $(date)` | yes | Patterns naming more than the command run anyway on `$()`, backticks or `$VAR` |

When Claude Code can't tell which commands the input runs, the hook runs regardless of the pattern.
