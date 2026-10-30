# JSON output fields

Read when writing or checking a hook's JSON output: universal fields, size caps, `terminalSequence`, where `additionalContext` lands, and which events rewrite content. Source: <https://code.claude.com/docs/en/hooks#json-output>.

## Contents

- Rules
- Universal fields
- Size caps
- terminalSequence
- additionalContext
- Decision patterns by event
- Content rewrites

## Rules

Docs: [JSON output](https://code.claude.com/docs/en/hooks#json-output) · [exit code 0](https://code.claude.com/docs/en/hooks#exit-code-0) · [async hooks](https://code.claude.com/docs/en/hooks#how-async-hooks-execute)

- Exit 0 and print **one** JSON object, on one line or several, with nothing else on stdout but whitespace.
- Use exit codes alone or exit 0 + JSON, not both. If mixed, exit 2 keeps blocking and the fields are still read (except `hookSpecificOutput` on Elicitation and ElicitationResult).
- Three kinds of fields: universal fields (below); top-level `decision` and `reason` on events that use them; `hookSpecificOutput`, which requires `hookEventName` set to the exact event name.
- The only value of top-level `decision` is `"block"`. To allow, omit it or print no JSON.
- Build JSON with a JSON tool (`jq -n --arg`, `json.dumps`), not string concatenation, so quotes, backslashes and newlines are escaped.
- Async hooks: the response may be alone on stdout (several lines allowed from v2.1.295) or on one line of its own among other text. Fields with the wrong type are dropped, with a warning under `--debug`. `additionalContext` and `systemMessage` are delivered to Claude on the next turn and aren't shown to the user.

## Universal fields

Docs: [JSON output](https://code.claude.com/docs/en/hooks#json-output)

| Field | Default | Effect |
| :-- | :-- | :-- |
| `continue` | `true` | `false` stops Claude entirely after the hook. Overrides any event-specific decision. On PreToolUse and PostToolUse the stop applies even when the call fails or completes while Claude is still streaming |
| `stopReason` | none | Shown to the user when `continue` is false; stays in the conversation, so Claude sees it if it continues |
| `suppressOutput` | `false` | No effect. A successful hook's stdout is never shown in the transcript |
| `systemMessage` | none | Warning shown to the user; in the Agent SDK and stream-json it can arrive as an `SDKInformationalMessage` |
| `terminalSequence` | none | Escape sequence Claude Code emits for the hook (see below) |

Some events discard universal fields. Check the event's own entry before relying on `systemMessage` or `continue` there. Known discards: Notification, StopFailure, SessionEnd, MessageDisplay (`systemMessage`, `continue`), Elicitation and ElicitationResult (`reason`, `systemMessage`, `continue`), ConfigChange (`systemMessage`, `continue`), CwdChanged and FileChanged (`continue`; `systemMessage` shown as a brief terminal notification), DirectoryAdded (`continue`), PreCompact and PostCompact (`systemMessage`, `continue`), WorktreeCreate (`systemMessage`, `continue`), and Setup, InstructionsLoaded and WorktreeRemove (all JSON output fields).

## Size caps

Docs: [JSON output](https://code.claude.com/docs/en/hooks#json-output) · [add context for Claude](https://code.claude.com/docs/en/hooks#add-context-for-claude)

- `additionalContext`, `systemMessage`, `initialUserMessage` and plain stdout: 10,000 characters each, measured separately per field and per hook.
- Over the cap: saved to a file in the session directory and replaced by the path plus a preview of up to 2,000 characters. Claude isn't told to read the file. No setting raises the cap.

## terminalSequence

Docs: [emit terminal notifications](https://code.claude.com/docs/en/hooks#emit-terminal-notifications)

- Hooks have no controlling terminal; writing to `/dev/tty` fails. Return the sequence in `terminalSequence` and Claude Code writes it.
- Allowlist: OSC 0, 1, 2 (titles); OSC 9 (iTerm2, ConEmu, Windows Terminal, WezTerm notifications, including `9;4` progress); OSC 99 (Kitty); OSC 777 (urxvt, Ghostty, Warp); bare BEL. Terminated with BEL or ST.
- Anything else (CSI, palette, OSC 8, OSC 52, OSC 1337) makes the whole field ignored.
- Works on events that discard `systemMessage` and `continue`, such as Notification and StopFailure.
- Ignored in `-p` mode and the Agent SDK. A WorktreeCreate command hook can't return JSON, so it can't use it; an HTTP WorktreeCreate hook can.

```bash
#!/usr/bin/env bash
input=$(cat)
body=$(jq -r '.message // "Needs your attention"' <<<"$input")
seq=$(printf '\033]777;notify;%s;%s\007' "Claude Code" "$body")
jq -nc --arg seq "$seq" '{terminalSequence: $seq}'
```

## additionalContext

Docs: [add context for Claude](https://code.claude.com/docs/en/hooks#add-context-for-claude)

- Goes inside `hookSpecificOutput` with `hookEventName`. Claude Code wraps it in a system reminder at the point the hook fired; it isn't shown as a chat message.
- Where it lands: SessionStart and SubagentStart, before the first prompt; UserPromptSubmit and UserPromptExpansion, alongside the prompt; PreToolUse, PostToolUse, PostToolUseFailure and PostToolBatch, next to the tool result; Stop and SubagentStop, at the end of the turn, and the conversation continues; PostModelSwitch, with the next request.
- Several hooks' values are all delivered.
- A `<system-reminder>` tag inside the string arrives with `<` replaced by `&lt;`.
- Write facts ("The deployment target is production"), not imperative system commands, which can trip prompt-injection defenses and get surfaced to the user instead.
- Saved in the transcript and replayed on `--resume`/`--continue` for mid-session events, so timestamps and SHAs go stale. SessionStart reruns on resume with `source` `"resume"` or `"fork"`.
- Ignored on PreToolUse when `permissionDecision` is `"defer"`. Not accepted on PreModelSwitch.
- For static rules, CLAUDE.md is the place, not a hook.

## Decision patterns by event

Docs: [decision control](https://code.claude.com/docs/en/hooks#decision-control)

| Events | How to decide |
| :-- | :-- |
| PreToolUse | `hookSpecificOutput.permissionDecision`: `allow`, `deny`, `ask`, `defer`; plus `permissionDecisionReason`, `updatedInput`, `additionalContext`. Top-level `decision` is deprecated here |
| PermissionRequest | `hookSpecificOutput.decision.behavior`: `allow` or `deny`. Exit 2 is **not** honored |
| PreModelSwitch | `permissionDecision` (`allow`, `deny`, `ask`) or top-level `decision: "block"` |
| UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop, ConfigChange, PreCompact | Top-level `decision: "block"` + `reason` (PostToolUseFailure: unverified, see the note below) |
| TaskCreated | Exit 2 or top-level `decision: "block"` |
| TeammateIdle, TaskCompleted | Exit 2, or `{"continue": false, "stopReason": ...}` |
| PermissionDenied | `hookSpecificOutput.retry: true` |
| Elicitation, ElicitationResult | `hookSpecificOutput.action` (`accept`, `decline`, `cancel`) + `content` |
| MessageDisplay | `hookSpecificOutput.displayContent` (display only) |
| WorktreeCreate | Command hook prints the path as the last non-empty stdout line |
| WorktreeRemove | Exit code only |
| SessionStart, SubagentStart, PostModelSwitch | Context only: `additionalContext` |
| Setup, Notification, SessionEnd, PostCompact, InstructionsLoaded, StopFailure, CwdChanged, DirectoryAdded, FileChanged | No decision control; side effects only |

`hookSpecificOutput` always needs `hookEventName` set to the exact event name. Every event accepts the universal fields `continue`, `stopReason`, `systemMessage`, `terminalSequence`, though some discard them: read Universal fields above before relying on one.

Elicitation and ElicitationResult also decline on exit 2 or top-level `decision: "block"` (`events-mcp-elicitation.md`). The deprecated PreToolUse top-level `decision`/`reason` maps `approve` to `allow` and `block` to `deny` (`events-tools.md`).

PostToolUseFailure is unverified here: the docs' [decision control](https://code.claude.com/docs/en/hooks#decision-control) table lists it with top-level `decision`, while its own [decision control](https://code.claude.com/docs/en/hooks#posttoolusefailure-decision-control) section lists only `additionalContext` (both at the docs baseline in `sources.md`). Rely on `additionalContext`, and confirm a `decision: "block"` in the debug log before depending on it.

## Content rewrites

Docs: [decision control](https://code.claude.com/docs/en/hooks#decision-control) · [PreToolUse](https://code.claude.com/docs/en/hooks#pretooluse-decision-control) · [PermissionRequest](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control) · [PostToolUse](https://code.claude.com/docs/en/hooks#posttooluse-decision-control) · [changelog](https://code.claude.com/docs/en/changelog)

| Event | Field | Notes |
| :-- | :-- | :-- |
| PreToolUse | `hookSpecificOutput.updatedInput` | Replaces the whole input object: include unchanged fields. Permission rules are evaluated against the rewritten input. Ignored with `defer` |
| PermissionRequest | `hookSpecificOutput.decision.updatedInput` | Only with `allow`; re-evaluated against deny and ask rules |
| PostToolUse | `hookSpecificOutput.updatedToolOutput` | Must match the tool's output shape (Bash: `stdout`, `stderr`, `interrupted`, `isImage`); a mismatch on a built-in tool is ignored. Changes only what Claude sees; the tool already ran |
| UserPromptSubmit | none | Can't replace the prompt; only `additionalContext` |

Since v2.1.300, `updatedInput` from PreToolUse and PermissionRequest is validated like Claude's own input: unknown keys are dropped, and input the tool rejects denies the call.

Redact or transform outbound input at PreToolUse and inbound results at PostToolUse.
