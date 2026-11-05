---
paths:
  - "plugins/*/hooks/**"
---

# Plugin hooks

Apply this whenever you write or change a plugin hook: its entry in `hooks/hooks.json` or the script it runs.

## Failure

- A policy hook sets `"onFailure": "block"`. An advisory or observing hook leaves it at `"continue"`.
- `onFailure: "block"` needs v2.1.295+ and works on `command` and `http` only. It has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, `TeammateIdle`, or `async`/`asyncRewake` hooks.
- Failure means: can't start, exit code other than 0 or 2, timeout, or invalid JSON. Exit 1 never blocks.
- A hook that runs an interpreter checks it first. If it is missing, print `systemMessage` and exit 0. Exception: a deny guard denies and names what to install.
- On Windows without Git Bash, a shell-form hook runs in PowerShell. A failing `PreToolUse` or `PermissionRequest` hook with `onFailure` unset then blocks the call.

## Matchers and `if`

- A matcher made only of letters, digits, `_`, `-`, spaces, `,` and `|` is an exact name: `Bash` doesn't match `PowerShell`.
- Bundled MCP tools are `mcp__plugin_<plugin>_<server>__<tool>`; a bare server key never matches. Use `.*` for all its tools.
- `if` holds exactly one permission rule; `&&`, `||` and lists don't work.
- `if` is best-effort: when Claude Code can't tell what a Bash command runs, the hook runs anyway. A policy hook never uses `if`; it filters inside the script, on the lexed words, never on raw text (`g"i"t commit` runs git).
- Tool hooks also fire inside subagents; the input then has `agent_id` and `agent_type`.

## PreToolUse

- A guard that can't read or parse its input denies the call and says why.
- To block: one JSON object on stdout and exit 0, or exit 2 with the reason on stderr. Any extra stdout line breaks the JSON.
- To pass: print nothing and exit 0. Silence never approves; the permission flow decides.
- Matching hooks run in parallel. The strictest decision wins: `deny`, then `defer`, `ask`, `allow`.

## Other events

- `UserPromptSubmit`: a failing hook with `"onFailure": "block"` blocks every prompt.
- `SessionEnd`: hooks share a 1.5 s budget. A plugin hook's `timeout` doesn't raise it.

## Commands

- Shell form: quote `"${CLAUDE_PLUGIN_ROOT}"` paths. Exec form (`args`): no quotes, or they become part of the path.
