# Customize your status line

> A custom status bar in Claude Code monitors context window usage, costs, and git status. This copy covers the `subagentStatusLine` setting (which plugins can ship a default for), its input task fields, and troubleshooting for status line scripts.

## Contents

- [Subagent status lines](#subagent-status-lines)
  - [Task fields](#task-fields)
- [Troubleshooting](#troubleshooting)
  - [OSC 8 links not clickable](#osc-8-links-not-clickable)
  - [Display glitches with escape sequences](#display-glitches-with-escape-sequences)
  - [Workspace trust required](#workspace-trust-required)
  - [Script errors or hangs](#script-errors-or-hangs)
- [Documentation References](#documentation-references)

## Subagent status lines

The `subagentStatusLine` setting renders a custom row body for each [subagent](https://code.claude.com/docs/en/sub-agents.md) shown in the agent panel below the prompt. It replaces the default `name · description · token count` row with custom formatting.

```json theme={null}
{
  "subagentStatusLine": {
    "type": "command",
    "command": "~/.claude/subagent-statusline.sh"
  }
}
```

Input: the command runs once per refresh tick and receives all visible subagent rows as a single JSON object on stdin. The input includes the [base hook fields](https://code.claude.com/docs/en/hooks.md#common-input-fields), a `columns` field with the usable row width, and a `tasks` array with one entry per row, described in [Task fields](#task-fields).

Output: write one JSON line to stdout per row to override, in the form `{"id": "<task id>", "content": "<row body>"}`.

- The `content` string is rendered as-is, including ANSI colors and OSC 8 hyperlinks.
- To keep the default rendering for a row, omit that task's `id`.
- To hide a row, emit an empty `content` string.

Gates and plugins:

- The same trust, `disableAllHooks`, and [`allowManagedHooksOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedhooksonly) gates that apply to `statusLine` apply here.
- Plugins can ship a default `subagentStatusLine` in their [`settings.json`](https://code.claude.com/docs/en/plugins/manifest-reference#standard-layout), but unlike hooks, plugin values do not run under `allowManagedHooksOnly` even when the plugin is force-enabled in managed settings `enabledPlugins`.

### Task fields

Each entry in the `tasks` array describes one subagent row with the fields below. Fields marked optional are omitted when they have no value, so the script must guard for their absence.

| Field | Type | Description |
| :- | :- | :- |
| `id` | string | Identifier of the task. Echo it as `id` in the line you write back for this row |
| `name` | string, optional | Name the subagent is [addressed by](https://code.claude.com/docs/en/sub-agents.md#subagent-names), when it has one |
| `type` | string | Kind of task: `local_agent` |
| `agentType` | string | Subagent type the task runs as, such as the built-in [`Explore`](https://code.claude.com/docs/en/sub-agents#built-in-subagents) or a custom `code-reviewer`. Holds the same value that hooks receive as [`agent_type`](https://code.claude.com/docs/en/hooks#subagentstart). Requires Claude Code v2.1.293 or later |
| `status` | string | State of the task, such as `running`, `completed`, `failed`, or `killed` |
| `description` | string | Short description of the task, such as the one Claude gave when it spawned the subagent |
| `label` | string | Short progress summary of the task when Claude Code has one, otherwise the same text as `description` |
| `startTime` | number | When the task started, in milliseconds since the Unix epoch |
| `model` | string, optional | ID of the resolved model the task runs on. Omitted until the model is resolved |
| `effort` | string or number, optional | Reasoning effort set for the subagent in its [definition frontmatter](https://code.claude.com/docs/en/sub-agents.md#frontmatter-reference) or on the individual invocation: `low`, `medium`, `high`, `xhigh`, `max`, or a numeric token budget. This is the configured value, and the effort Claude Code applies can differ when the model doesn't support that level. Omitted when no effort is set |
| `contextWindowSize` | number, optional | Context window of `model` in tokens, computed the same way as the main status line's [`context_window.context_window_size`](https://code.claude.com/docs/en/statusline#context-window-fields), so you can render a per-row percentage from `tokenCount`. Omitted when `model` is |
| `tokenCount` | number | Running token count of the subagent, the figure the default row shows |
| `tokenSamples` | array of numbers | Up to the last 16 `tokenCount` readings, one per refresh tick, oldest first and ending with the current one |
| `cwd` | string | Working directory of the subagent: its own directory when it runs in one, such as an isolated worktree, otherwise the session's working directory |

## Troubleshooting

### OSC 8 links not clickable

Whether a link is clickable depends on the terminal, on whether Claude Code detects hyperlink support in it, on whether SSH or tmux strips the escape sequence, and on how the script prints it. Check each:

* Verify the terminal supports OSC 8 hyperlinks (iTerm2, Kitty, WezTerm)

* Terminal.app does not support clickable links

* If link text appears but is not clickable, Claude Code may not have detected hyperlink support in the terminal. Set the `FORCE_HYPERLINK` environment variable to override detection before launching Claude Code:

  ```bash theme={null}
  FORCE_HYPERLINK=1 claude
  ```

  In PowerShell, set the variable in the current session first:

  ```powershell theme={null}
  $env:FORCE_HYPERLINK = "1"; claude
  ```

* SSH and tmux sessions may strip OSC sequences depending on configuration

* If escape sequences appear as literal text like `\e]8;;`, use `printf '%b'` instead of `echo -e` for more reliable escape handling

### Display glitches with escape sequences

Complex escape sequences (ANSI colors, OSC 8 links) can occasionally cause garbled output if they overlap with other UI updates. Multi-line status lines with escape codes are more prone to rendering issues than single-line plain text.

If the output is corrupted, simplify the script to plain text output.

### Workspace trust required

Until the workspace trust dialog is accepted, the status line stays blank. Because `statusLine` executes a shell command, Claude Code runs it under the same [workspace trust rule as hooks in settings files](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder). Accepting the dialog for the folder, or for a parent directory whose trust extends to it, is enough.

Until then, `claude --debug` logs `Status line command skipped: workspace trust not accepted`. To enable the status line, restart Claude Code and accept the trust dialog.

### Script errors or hangs

Claude Code displays the script's output only after the script exits with code 0:

* Scripts that exit with non-zero codes or produce no output cause the status line to go blank
* Slow scripts block the status line from updating until they complete. Keep scripts fast to avoid stale output.
* If a new update triggers while a slow script is running, the in-flight script is cancelled
* Test the script independently with mock input before configuring it

## Documentation References

- Source page: https://code.claude.com/docs/en/statusline (full status line guide, including the main `statusLine` setting and its context window fields)
- https://code.claude.com/docs/en/sub-agents.md - subagents, subagent names, built-in subagents, and supported frontmatter fields (also linked as https://code.claude.com/docs/en/sub-agents)
- https://code.claude.com/docs/en/hooks.md - common hook input fields and the `SubagentStart` event's `agent_type` (also linked as https://code.claude.com/docs/en/hooks)
- https://code.claude.com/docs/en/settings-reference - the `allowManagedHooksOnly` setting
- https://code.claude.com/docs/en/plugins/manifest-reference - a plugin's standard layout, including its `settings.json`
- https://code.claude.com/docs/en/permissions.md - what runs before a folder is trusted
