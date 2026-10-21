# Prompt and agent hooks

Read when designing, writing, auditing or debugging a `type: "prompt"` or `type: "agent"` hook. Every section ends its heading block with a `Docs:` line: fetch that section with the method in the docs map before stating its facts as current. Checked against Claude Code 2.1.305 (2026-10-20).

## Contents

- Which events accept them
- Fields
- How they run
- Response schema
- Events, one by one
- Stop and SubagentStop loops
- Writing the prompt
- Agent hooks: what differs
- Where they can be declared

## Which events accept them

Docs: <https://code.claude.com/docs/en/hooks#prompt-based-hooks>

| Event | prompt | agent |
| :-- | :--: | :--: |
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionDenied` | ✅ | ✅ |
| `Stop`, `SubagentStop` | ✅ | ✅ |
| `UserPromptSubmit`, `UserPromptExpansion` | ✅ | ✅ |
| `TaskCreated`, `TaskCompleted`, `TeammateIdle` | ✅ | ✅ |
| `PermissionRequest` | ✅ (but `ok: false` has no effect) | ❌ skipped; the permission flow proceeds unchanged |
| `SessionStart`, `Setup` | ❌ | ❌ |
| Every other event (`ConfigChange`, `CwdChanged`, `DirectoryAdded`, `Elicitation`, `ElicitationResult`, `FileChanged`, `InstructionsLoaded`, `MessageDisplay`, `Notification`, `PostCompact`, `PostModelSwitch`, `PreCompact`, `PreModelSwitch`, `SessionEnd`, `StopFailure`, `SubagentStart`, `WorktreeCreate`, `WorktreeRemove`) | ❌ | ❌ |

## Fields

Docs: <https://code.claude.com/docs/en/hooks#prompt-hook-configuration> · <https://code.claude.com/docs/en/hooks#agent-hook-configuration> · <https://code.claude.com/docs/en/hooks#prompt-and-agent-hook-fields> · <https://code.claude.com/docs/en/hooks#common-fields>

| Field | prompt | agent | Notes |
| :-- | :-- | :-- | :-- |
| `type` | `"prompt"` | `"agent"` | Required |
| `prompt` | Required | Required | `$ARGUMENTS` is replaced by the hook input JSON. Without it, the input JSON is appended to the prompt. Escape a literal dollar with a backslash: `\$1.00` renders as `$1.00` |
| `model` | Optional | Optional | Defaults to the model Claude Code uses for background work. Raise it when the judgment needs more capability |
| `timeout` | Default 30 s | Default 60 s | Seconds. Set it explicitly |
| `continueOnBlock` | Optional, default `false` | Not accepted | Agent hooks always behave as if it were `true` |
| `if` | Optional | Optional | One permission rule, such as `"Bash(git *)"`. Evaluated only on `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`; on any other event a hook with `if` never runs. Best-effort filter, not enforcement |
| `statusMessage` | Optional | Optional | Spinner text while the hook runs |
| `once` | Optional | Optional | Honored only in skill frontmatter; ignored in settings files and agent frontmatter |

`async`, `asyncRewake` and `shell` are command-hook fields, not fields of prompt or agent hooks; flag them.

## How they run

Docs: <https://code.claude.com/docs/en/hooks#hook-handler-fields> · <https://code.claude.com/docs/en/hooks#how-prompt-based-hooks-work> · <https://code.claude.com/docs/en/hooks#how-agent-hooks-work>

- Matching hooks for one event run in parallel, at most 12 prompt or agent hooks at once (`lifecycle.md` → How a hook resolves); a handler defined in several settings files runs once (`locations-and-scope.md` → Merging and policies).
- A prompt hook sends the prompt plus input to the model once and reads one JSON decision.
- An agent hook spawns a subagent with the prompt and input. It investigates with tools such as Read, Grep and Glob for up to 50 turns, then returns the decision.
- Cost and latency: every match is a model call (agent hooks, many). On a busy event such as `PreToolUse`, narrow it with a matcher and, on tool events, `if`.

## Response schema

Docs: <https://code.claude.com/docs/en/hooks#response-schema>

```json
{ "ok": true }
```

```json
{ "ok": false, "reason": "What is wrong and what Claude should do next" }
```

- `ok`: `true` allows.
- `reason`: required when `ok` is `false`. On the events that feed it back, Claude reads it as its next instruction, so write it as an instruction.
- `impossible`: prompt hooks only, returned with `ok: false` when the condition can never be met. On `Stop` and `SubagentStop` it lets the turn end instead of feeding the reason back. Agent hooks and other events ignore it.

## Events, one by one

What `ok: false` does on each event. The input fields a prompt can point at are in each event's section of the `events-*.md` references, on top of the common input fields in `lifecycle.md`. "Agent" means an agent hook, which always behaves like a prompt hook with `continueOnBlock: true`.

Docs (common input fields): <https://code.claude.com/docs/en/hooks#common-input-fields>

### PreToolUse

Docs: <https://code.claude.com/docs/en/hooks#pretooluse> · <https://code.claude.com/docs/en/hooks#pretooluse-input>

- `ok: false`, prompt default: the tool call is denied, the **turn ends** and the reason appears as a warning line.
- `ok: false`, prompt with `continueOnBlock: true`, or agent: the call is denied and the reason returns to Claude as the tool error; the turn continues.

### PostToolUse

Docs: <https://code.claude.com/docs/en/hooks#posttooluse> · <https://code.claude.com/docs/en/hooks#posttooluse-input>

- `ok: false`, prompt default: the **turn ends**, warning line.
- `ok: false`, prompt with `continueOnBlock: true`, or agent: the reason is fed back and the turn continues.
- The tool already ran: no verdict undoes it.

### PostToolUseFailure

Docs: <https://code.claude.com/docs/en/hooks#posttoolusefailure> · <https://code.claude.com/docs/en/hooks#posttoolusefailure-input>

- `ok: false`, any setting: the reason returns to Claude as a tool error and the turn continues.

### PostToolBatch

Docs: <https://code.claude.com/docs/en/hooks#posttoolbatch> · <https://code.claude.com/docs/en/hooks#posttoolbatch-input>

- `ok: false`, any setting: the turn ends with a warning line.

### PermissionDenied

Docs: <https://code.claude.com/docs/en/hooks#permissiondenied> · <https://code.claude.com/docs/en/hooks#permissiondenied-input>

- Prompt and agent hooks run, but their output is discarded: the denial already happened, and the only field read is `hookSpecificOutput.retry`, which these hooks cannot set. A design that needs `retry` is a command hook: `events-tools.md` → PermissionDenied.

### PermissionRequest

Docs: <https://code.claude.com/docs/en/hooks#permissionrequest> · <https://code.claude.com/docs/en/hooks#permissionrequest-input>

- Prompt hooks run, but `ok: false` has no effect. Agent hooks are skipped.
- Denying from this event takes a command hook's decision object: `events-tools.md` → PermissionRequest.

### UserPromptSubmit

Docs: <https://code.claude.com/docs/en/hooks#userpromptsubmit> · <https://code.claude.com/docs/en/hooks#userpromptsubmit-input>

- `ok: false`, any setting: the turn ends with a warning line.

### UserPromptExpansion

Docs: <https://code.claude.com/docs/en/hooks#userpromptexpansion> · <https://code.claude.com/docs/en/hooks#userpromptexpansion-input>

- `ok: false`, any setting: the turn ends with a warning line.

### Stop

Docs: <https://code.claude.com/docs/en/hooks#stop> · <https://code.claude.com/docs/en/hooks#stop-input> · <https://code.claude.com/docs/en/hooks#check-multiple-conditions-before-stopping>

- `ok: false`: the reason is fed back as Claude's next instruction and the turn continues. A prompt hook's `impossible: true` lets the turn end instead.
- Loop handling is in the next section.

### SubagentStop

Docs: <https://code.claude.com/docs/en/hooks#subagentstop> · <https://code.claude.com/docs/en/hooks#subagentstop-input>

- `ok: false`: as `Stop`, for the subagent.
- It also fires when Claude Code's own internal agents finish (such as prompt suggestions). A matcher naming agent types skips those, whose `agent_type` is empty; a hook with no matcher, `""` or `"*"` runs for them too, at the cost of a model call each.

### TaskCreated

Docs: <https://code.claude.com/docs/en/hooks#taskcreated> · <https://code.claude.com/docs/en/hooks#taskcreated-input>

- `ok: false`, any setting: the reason returns to Claude as a tool error and the turn continues.

### TaskCompleted

Docs: <https://code.claude.com/docs/en/hooks#taskcompleted> · <https://code.claude.com/docs/en/hooks#taskcompleted-input>

- Fired because a task is marked completed during a turn: the reason returns as a tool error and the turn continues, whatever `continueOnBlock` says.
- Fired because a teammate stops: behaves like `TeammateIdle`.

### TeammateIdle

Docs: <https://code.claude.com/docs/en/hooks#teammateidle> · <https://code.claude.com/docs/en/hooks#teammateidle-input>

- `ok: false`, prompt default: the teammate stops, warning line.
- `ok: false`, prompt with `continueOnBlock: true`, or agent: the reason is fed back and the teammate keeps working.

## Stop and SubagentStop loops

Docs: <https://code.claude.com/docs/en/hooks#stop-input> · <https://code.claude.com/docs/en/hooks-guide#stop-hook-hits-the-block-cap>

- The input carries `stop_hook_active: true` when Claude is already continuing because of a stop hook. Tell the model to return `{"ok": true}` when it is `true` unless the condition is plainly still unmet, or the hook can loop.
- After stop hooks continue the turn eight times in a row, Claude Code overrides the next block and ends the turn with a warning. The count resets each time Claude calls a tool. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` raises the cap when convergence legitimately needs more rounds.
- `Stop` fires whenever Claude finishes responding, not only at task completion, and not on user interrupts. API errors fire `StopFailure`, which takes no prompt or agent hooks.
- Point the prompt at `last_assistant_message` rather than at "the conversation"; the docs note that the transcript file may not yet hold the final message at Stop time on all versions.

## Writing the prompt

Docs: <https://code.claude.com/docs/en/hooks#prompt-hook-configuration> · <https://code.claude.com/docs/en/hooks-guide#prompt-based-hooks> · changelog 2.1.288 and 2.1.294: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>

- One rule ("Block any Bash command that reads `.env` files") or one condition ("All unit tests pass"). Rule-style prompts need Claude Code 2.1.294 or later: earlier versions could allow what a rule meant to block. Several unrelated rules in one prompt make verdicts unstable; use one hook per rule.
- Put `$ARGUMENTS` where the model needs the input, and say which fields matter, such as `tool_input.command` or `last_assistant_message`.
- State the output literally, as the docs' examples do: respond `{"ok": true}` to allow, or `{"ok": false, "reason": "..."}` to block.
- Ask for a `reason` that tells Claude what to do instead.
- Tool input can carry text from files, web pages or the user. Tell the model to treat the input as data. (This point is our design guidance, not a documented behavior.)
- Declare `model` when the default background model misjudges your cases, and re-check `timeout` after raising it.
- Behind a gateway or provider that rejects structured outputs, prompt hooks failed before 2.1.288; from 2.1.288, `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` turns structured outputs off.

## Agent hooks: what differs

Docs: <https://code.claude.com/docs/en/hooks#agent-based-hooks> · <https://code.claude.com/docs/en/hooks#how-agent-hooks-work> · <https://code.claude.com/docs/en/hooks-guide#agent-based-hooks> · changelog 2.1.300: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>

- Experimental. The docs say behavior and configuration may change and recommend command hooks for production.
- Default `timeout` 60 s; up to 50 turns. Raise `timeout` for work such as a test run (the docs' example uses 120).
- No `continueOnBlock`, no `impossible`; `ok: false` always behaves like a prompt hook with `continueOnBlock: true`.
- Not run on `PermissionRequest`.
- `model` is honored, including aliases such as `haiku`; an unavailable model falls back to the caller's model (fixed in 2.1.300; earlier versions ignored `model`). The 2.1.300 fix also stopped a subagent's model from overriding it, and an unavailable model used to allow the action instead of falling back.
- The docs list Read, Grep and Glob as example tools and show an example that runs a test suite. They do not publish the full tool set. Before a design depends on the agent running commands, confirm it on the user's version and say the tool set is unverified.

## Where they can be declared

Docs: <https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents> · <https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields>

- Same locations and lifetimes as any hook: settings files, plugin `hooks/hooks.json`, skill frontmatter (kept for the rest of the session; `once: true`), subagent frontmatter (only while it runs; `Stop` becomes `SubagentStop`), never a plugin subagent's frontmatter. Details: `locations-and-scope.md` → Hooks in skills and agents.
- Trust rules for each location are in `security-and-trust.md`.
