# Hook lifecycle and how a hook resolves

Read when choosing the event for a hook or explaining why it fired, or didn't, at a given moment. Source: <https://code.claude.com/docs/en/hooks#hook-lifecycle>.

## Contents

- Cadences
- When each event fires
- How a hook resolves
- Common input fields

## Cadences

Docs: [hook lifecycle](https://code.claude.com/docs/en/hooks#hook-lifecycle)

- Hooks fire wherever Claude Code runs: terminal, IDE extensions, the Desktop app and cloud sessions.
- Per session: SessionStart and SessionEnd.
- Per turn: UserPromptSubmit, Stop and StopFailure.
- Per tool call inside the agentic loop: PreToolUse and PostToolUse. `EndConversation` calls skip both.
- Setup feeds into SessionStart. Inside the agentic loop also sit PermissionRequest, PostToolUseFailure, PostToolBatch, SubagentStart/SubagentStop, TaskCreated and TaskCompleted. PermissionDenied branches from PermissionRequest for auto-mode denials. Elicitation and ElicitationResult nest inside MCP tool execution.
- Standalone async events: WorktreeCreate, WorktreeRemove, Notification, ConfigChange, InstructionsLoaded, CwdChanged, FileChanged, DirectoryAdded, PostModelSwitch. PreModelSwitch is standalone and sequential. MessageDisplay is display-only, while assistant text streams.
- A plugin can also register hooks as JavaScript functions (a mod); those are a different system, documented under React to events.
- How a mod's hooks change what these hooks run or decide is in `mods-and-hooks.md`.

## When each event fires

Docs: [hook lifecycle](https://code.claude.com/docs/en/hooks#hook-lifecycle) · [hook events](https://code.claude.com/docs/en/hooks#hook-events)

| Event | Fires |
| :-- | :-- |
| SessionStart | When a session begins or resumes |
| Setup | `--init-only`, or `--init` / `--maintenance` in `-p` mode; one-time preparation in CI or scripts |
| UserPromptSubmit | When a prompt is submitted, before Claude processes it; also on turns Claude Code starts on its own |
| UserPromptExpansion | When a user-typed command expands into a prompt; can block the expansion |
| PreToolUse | Before a tool call executes; can block it |
| PermissionRequest | When a tool call needs a permission decision |
| PermissionDenied | When auto mode denies a tool call, including no-verdict denials |
| PostToolUse | After a tool call succeeds |
| PostToolUseFailure | After a tool call fails |
| PostToolBatch | After a batch of parallel tool calls resolves, before the next model call |
| Notification | When Claude Code sends a notification |
| MessageDisplay | While assistant message text is displayed |
| SubagentStart / SubagentStop | When a subagent is spawned / finishes |
| TaskCreated / TaskCompleted | When a task is created via TaskCreate / marked completed |
| Stop | When Claude finishes responding |
| StopFailure | When the turn ends due to an API error |
| TeammateIdle | When an agent-team teammate is about to go idle |
| InstructionsLoaded | When a CLAUDE.md or `.claude/rules/*.md` file loads, at start or lazily |
| ConfigChange | When a configuration file changes during a session |
| CwdChanged | When the working directory changes, such as after `cd` |
| DirectoryAdded | When a directory is added via `/add-dir` or the SDK `register_repo_root` request |
| FileChanged | When a watched file changes; the matcher names the files to watch |
| WorktreeCreate | When a worktree is created via `--worktree`, `isolation: "worktree"` or a background session; replaces default git behavior |
| WorktreeRemove | When a worktree a WorktreeCreate hook made is removed |
| PreCompact / PostCompact | Before / after context compaction |
| PreModelSwitch | Before a requested model switch applies; can block it |
| PostModelSwitch | After the session's model changes, including changes Claude Code makes itself |
| Elicitation / ElicitationResult | When an MCP server requests input / after the user responds |
| SessionEnd | When a session terminates |

Choosing an event:

- To see every file change, an Edit/Write hook is not enough: Claude can change files with shell commands. Add a Stop hook that scans the tree per turn, or also match `Bash|PowerShell` (see the hooks guide, Filter hooks with matchers).
- PreToolUse runs on every tool call; PermissionRequest only when a permission dialog would show. Pick PermissionRequest to answer prompts, PreToolUse to guard calls.
- UserPromptSubmit sees a typed command as typed; UserPromptExpansion sees its name and arguments.

## How a hook resolves

Docs: [how a hook resolves](https://code.claude.com/docs/en/hooks#how-a-hook-resolves) · [configuration](https://code.claude.com/docs/en/hooks#configuration)

Terms: **hook event** (the lifecycle point), **matcher group** (the filter), **hook handler** (the command, HTTP endpoint, MCP tool, prompt or agent that runs).

1. The event fires and Claude Code builds the JSON input.
2. Each matcher group's `matcher` is tested against the event's match field (the tool name for tool events). Omitted or `"*"` matches everything.
3. For tool events, each handler's `if` (one permission rule) is tested against the tool name and arguments. No `if` means every handler in the group runs. A failed check means the process never spawns.
4. Matching handlers run in parallel. More than 12 prompt or agent hooks on one event run 12 at a time (v2.1.302+); a waiting hook's timeout starts when it starts.
5. Claude Code acts on the results: what the handler returns is in `exit-codes.md` and `json-output.md`.
6. When several handlers return decisions for one event, Claude Code merges them. The precedence is documented for three events only: PreToolUse `deny` > `defer` > `ask` > `allow` ([decision control](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)); PreModelSwitch `deny` > `ask` > `allow` ([decision control](https://code.claude.com/docs/en/hooks#premodelswitch-decision-control)); Elicitation, where a decline from any hook beats accept or cancel ([output](https://code.claude.com/docs/en/hooks#elicitation-output)). Every hook's `additionalContext` is delivered. For any other event no merge rule is documented: handlers run in parallel, so don't design around their order or assume the strictest one wins.

A handler that stays silent doesn't approve anything; the normal permission flow continues.

## Common input fields

Docs: [common input fields](https://code.claude.com/docs/en/hooks#common-input-fields)

Every event: `session_id`, `transcript_path`, `cwd`, `hook_event_name`. Usually also:

- `prompt_id`: UUID of the prompt in progress; absent until the first user input. Matches the OpenTelemetry `prompt.id`.
- `scratchpad_dir`: the session's scratchpad; absent when there is none (v2.1.257+).
- `permission_mode`: `default`, `plan`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`. "Manual" arrives as `default`. Not every event gets it.
- `effort.level`: `low` to `max`, on tool-context events such as PreToolUse, PostToolUse, Stop, SubagentStop, when the model supports effort. Also `$CLAUDE_EFFORT`.
- `agent_id`, `agent_type`: present when the hook fires inside a subagent, an in-process teammate, or a session started with `--agent`.

Notes:

- `transcript_path` is written asynchronously and can lag. For the final assistant text use `last_assistant_message` on Stop and SubagentStop.
- Only SessionStart can receive `model`, and not always. There is no `$CLAUDE_MODEL`; `$ANTHROPIC_MODEL` doesn't follow `/model`. Use PreModelSwitch/PostModelSwitch `from_model`/`to_model`.
- The hook inherits the parent environment minus the `OTEL_*` exporter variables, minus the variables `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips, and minus Anthropic credentials under the HIPAA configuration.
