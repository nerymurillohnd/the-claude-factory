# Notification, agent, task and turn-ending events

Notification · SubagentStart · SubagentStop · TaskCreated · TaskCompleted · Stop · StopFailure · TeammateIdle

Sources: https://code.claude.com/docs/en/hooks (read 2026-10-20) and the Claude Code CHANGELOG.md through v2.1.305; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields.

---

## Contents

- Notification
- SubagentStart
- SubagentStop
- TaskCreated
- TaskCompleted
- Stop
- StopFailure
- TeammateIdle

## Notification

Docs: [event](https://code.claude.com/docs/en/hooks#notification) · [input](https://code.claude.com/docs/en/hooks#notification-input)

**Fires:** Claude Code sends a notification. Runs even with desktop notifications off (`preferredNotifChannel`, incl. `notifications_disabled`, only changes how the user is alerted).

**Handlers:** `command`, `http`, `mcp_tool`.

**Matcher → `notification_type`:**

| Value | When |
|---|---|
| `permission_prompt` | approval needed for a tool or a sandboxed network request, after ~6 s waiting (network-request case v2.1.246+ in terminals) |
| `idle_prompt` | ~60 s after Claude finished, no typing since, no background agent running; not sent while waiting on a usage-limit reset |
| `auth_success` | authentication completes |
| `elicitation_dialog` / `elicitation_url_dialog` | MCP form / URL request, after ~6 s without typing |
| `elicitation_complete` | MCP server reports a URL elicitation complete |
| `elicitation_response` | an elicitation response is sent back |
| `agent_needs_input` | a background session starts waiting while agent view is open; also a teammate's terminal setup question (v2.1.248+) or auto-mode charge notice after ~6 s |
| `agent_completed` | a background session finishes or fails, while agent view is open |
| `quota_auto_resume_fired` | task continued after a claude.ai usage limit (v2.1.234+) |
| `quota_auto_resume_stale` | limit reset while the computer slept >~30 min; waits for Enter (v2.1.234+) |
| `quota_auto_resume_disabled` | the wait ended without continuing (setting off, reset moved >24 h, kept hitting the limit, blocked); not on Esc/Ctrl+C (v2.1.234+) |

**6-second gate:** in terminals, `permission_prompt`, `elicitation_dialog`, `elicitation_url_dialog` fire only after ~6 s with no keystroke; each keystroke defers them. A request queued behind another dialog keeps the gate from its arrival. In SDK-hosted sessions (Desktop, VS Code): `permission_prompt` fires ~6 s after the request regardless of typing, not at all if answered sooner; disable with `CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS=1`; before v2.1.233 it didn't fire there. For an immediate signal use PermissionRequest.

**Input:** `message`, `title?`, `notification_type`.

**Output:** can't block or modify; `systemMessage` and `continue` discarded; `terminalSequence` still emitted (desktop-notification pattern). Exit code and stderr ignored. Use for forwarding to external services.

---

## SubagentStart

Docs: [event](https://code.claude.com/docs/en/hooks#subagentstart) · [input](https://code.claude.com/docs/en/hooks#subagentstart-input)

**Fires:** Claude spawns a subagent via the Agent tool, resumes one, and each time an in-process agent-team teammate handles a new message.

**Handlers:** `command`, `http`, `mcp_tool`.

**Matcher → agent type:** built-ins `general-purpose`, `Explore`, `Plan`; custom agents by frontmatter `name` (not filename); plugin agents as `my-plugin:reviewer` (the `:` forces regex: use `^my-plugin:reviewer$`).

**Input:** `agent_id`, `agent_type`.

**Output:** can't block. `hookSpecificOutput.additionalContext` goes into the subagent's context before its first prompt. On re-runs for the same subagent it's injected only if the earlier copy is gone (e.g. after auto-compaction), protecting the subagent's prompt cache. Exit 2 shows stderr as a hook-error notice in the subagent's own transcript.

---

## SubagentStop

Docs: [event](https://code.claude.com/docs/en/hooks#subagentstop) · [input](https://code.claude.com/docs/en/hooks#subagentstop-input)

**Fires:** a subagent finishes responding. Also for Claude Code's internal agents (prompt suggestions, `/btw`); for those `agent_type` is the session's own agent name (`--agent` / `agent` setting) or `""`. A named matcher never matches `""`; omitted, `""`, `*`, or a regex matching empty does.

**Handlers:** all five. **Matcher:** same as SubagentStart.

**Input:** `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path` (subagent's own transcript under `subagents/`; `transcript_path` is the parent's), `last_assistant_message`, `background_tasks[]`, `session_crons[]` (both scoped to the parent session; shapes under Stop). With `SubagentHandback` (v2.1.271+), `last_assistant_message` is only closing text; the report is that tool call's `tool_input.message` (match `SubagentHandback` in Pre/PostToolUse).

**Output:** same format as Stop: top-level `decision: "block"` + `reason` keeps the subagent running with `reason` as its next instruction; `hookSpecificOutput.additionalContext` (`hookEventName: "SubagentStop"`) gives non-error feedback. Exit 2 delivers stderr the same way. To inject context into the parent after a subagent returns, use PostToolUse on `Agent`.

---

## TaskCreated

Docs: [event](https://code.claude.com/docs/en/hooks#taskcreated) · [input](https://code.claude.com/docs/en/hooks#taskcreated-input) · [decision control](https://code.claude.com/docs/en/hooks#taskcreated-decision-control)

**Fires:** a task is being created via `TaskCreate`. Not in sessions without Task tools.

**Matcher:** none. **Handlers:** all five.

**Input:** `task_id`, `task_subject`, `task_description?`, `teammate_name?`, `team_name` (deprecated), `agent_id?` (creator; v2.1.290+).

**Output:** exit 2 (stderr) or `{"decision":"block","reason":"..."}` deletes the task and returns the message to Claude as the tool error. `continue: false` is ignored; Claude keeps working. Use to enforce naming (`[TICKET-123] …`) or required descriptions.

---

## TaskCompleted

Docs: [event](https://code.claude.com/docs/en/hooks#taskcompleted) · [input](https://code.claude.com/docs/en/hooks#taskcompleted-input) · [decision control](https://code.claude.com/docs/en/hooks#taskcompleted-decision-control)

**Fires:** a task is being marked completed: explicit `TaskUpdate`, or an agent-team teammate finishing its turn with in-progress tasks.

**Matcher:** none. **Handlers:** all five.

**Input:** same fields as TaskCreated (`agent_id` = completer).

**Output:** exit 2 → not completed, stderr fed back to the model (works for both triggers). `{"continue": false, "stopReason": "..."}` stops the teammate entirely only when a teammate's turn end triggered it; ignored for `TaskUpdate`. Use to require passing tests or lint before closing.

---

## Stop

Docs: [event](https://code.claude.com/docs/en/hooks#stop) · [input](https://code.claude.com/docs/en/hooks#stop-input) · [decision control](https://code.claude.com/docs/en/hooks#stop-decision-control)

**Fires:** the main agent finishes responding. Not on user interrupt; API errors fire StopFailure instead. `/goal` is a built-in session-scoped prompt-based Stop hook.

**Matcher:** none. **Handlers:** all five.

**Input:**

| Field | Notes |
|---|---|
| `stop_hook_active` | `true` when already continuing because of a stop hook. Check it to avoid blocking on a condition that never resolves |
| `last_assistant_message` | final response text. Use this, not `transcript_path`, which may not include it yet |
| `background_tasks[]` | in-flight tasks: `id`, `type` (`shell`, `subagent`, `monitor`, `workflow`, `teammate`, `cloud session`, `MCP task`, or raw value), `status`, `description` (≤1000 chars, `… [+N chars]`), `command` (shell), `agent_type` (subagent), `server`/`tool` (monitor, MCP task), `name` (workflow) |
| `session_crons[]` | session wakeups from CronCreate, ScheduleWakeup, `/loop`: `id`, `schedule`, `recurring`, `prompt` (≤1000 chars) |

Empty arrays = nothing in flight. They let a hook tell "done" from "paused waiting for background work".

**Output:**

| Field | Effect |
|---|---|
| top-level `decision: "block"` + `reason` (required) | Claude continues; `reason` tells it why. Shown as a hook error |
| `hookSpecificOutput.additionalContext` | Claude continues, shown as `Stop hook feedback`, no error notice |

Exit 2 = block with stderr as the reason. Both continue paths share the loop guards: `stop_hook_active` and the cap of 8 consecutive continuations (reset whenever Claude calls a tool; raise with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). After the cap, the next block is overridden and the turn ends.

---

## StopFailure

Docs: [event](https://code.claude.com/docs/en/hooks#stopfailure) · [input](https://code.claude.com/docs/en/hooks#stopfailure-input)

**Fires:** instead of Stop, when the turn ends on an API error.

**Handlers:** `command`, `http`, `mcp_tool`.

**Matcher → `error`:** `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error` (v2.1.267+), `unknown`. Exact-match set is letters, digits, `_`, `|` only; a hyphen or comma makes the matcher a regex.

**Input:** `error`, `error_details?`, `last_assistant_message?` (here the rendered API error string, e.g. `API Error: Rate limit reached`, not Claude's output).

**Output:** none; output and exit code ignored except `terminalSequence`. Logging and alerts only.

---

## TeammateIdle

Docs: [event](https://code.claude.com/docs/en/hooks#teammateidle) · [input](https://code.claude.com/docs/en/hooks#teammateidle-input) · [decision control](https://code.claude.com/docs/en/hooks#teammateidle-decision-control)

**Fires:** an agent-team teammate is about to go idle after its turn.

**Matcher:** none. **Handlers:** all five.

**Input:** `teammate_name`, `team_name` (deprecated), `agent_id?` (v2.1.290+).

**Output:** exit 2 → teammate gets stderr as feedback and keeps working. `{"continue": false, "stopReason": "..."}` stops the teammate entirely. Use as a quality gate (lint passes, build artifact exists).
