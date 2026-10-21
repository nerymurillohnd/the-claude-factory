# Exit codes, stdout parsing, timeouts and failure

Read when you need the exact rule for an exit code, how stdout is parsed, what a timeout or a crash does, onFailure, Windows without Git Bash, or HTTP hooks. Source: <https://code.claude.com/docs/en/hooks#exit-code-output>.

## Contents

- The outcome matrix
- Exit code 0
- Exit code 2
- Other exit codes
- Exit code 2 per event
- Timeouts
- Hooks that start a background process
- onFailure: block the action when a hook fails
- Windows without Git Bash
- MCP tool hooks
- HTTP hooks

## The outcome matrix

Docs: [exit code output](https://code.claude.com/docs/en/hooks#exit-code-output) · [exit code 0](https://code.claude.com/docs/en/hooks#exit-code-0) · [exit code 2](https://code.claude.com/docs/en/hooks#exit-code-2) · [other exit codes](https://code.claude.com/docs/en/hooks#other-exit-codes)

Find the row for what the hook printed to stdout, then the column for its exit code. Events with their own rules are listed under it.

| Stdout | Exit 0 | Exit 2 | Any other exit |
| :-- | :-- | :-- | :-- |
| One JSON object that passes validation | Success, fields apply | Blocking error; fields read but can't override the block | Success, exit code ignored, fields decide; a **failure** if `onFailure: "block"` |
| JSON that doesn't parse or fails validation | Non-blocking error; action goes ahead | Blocking error; stderr is the reason | Non-blocking error |
| Plain text or nothing | Success | Blocking error; stderr is the reason | Non-blocking error; notice shows stderr's first line |

Events with their own rules: WorktreeCreate and WorktreeRemove (any non-zero exit fails them); Stop, SubagentStop, TaskCompleted and a plugin's UserPromptSubmit (exit 2 + empty stdout + a "No such file or directory" stderr is non-blocking); Elicitation and ElicitationResult (`hookSpecificOutput` applies only on exit 0); events that discard output, such as StopFailure (only `terminalSequence` fires).

## Exit code 0

Docs: [exit code output](https://code.claude.com/docs/en/hooks#exit-code-output) · [exit code 0](https://code.claude.com/docs/en/hooks#exit-code-0)

- Success. Claude Code applies the JSON fields the hook printed; the action goes ahead unless those fields block or deny it.
- The intended code when printing JSON for structured control.
- Exit 0 with JSON that doesn't parse or fails schema validation is a **non-blocking error**: the action goes ahead (unless onFailure is block), the fields are not applied, and the `<hook name> hook error` notice carries the parse or validation message.
- How stdout is read, for a hook that is not async:
  - Doesn't start with `{`, or starts with `{` and doesn't end with `}`: plain text. A JSON array and a quoted string are plain text.
  - Two or more lines that each parse as JSON, the first starting with `{` and the last ending with `}`: plain text when no line is a JSON output object that sets a field; a parse failure when one is.
  - Anything else that starts with `{` and ends with `}` but isn't valid JSON: a parse failure.
- Plain stdout is added to Claude's context only on UserPromptSubmit, UserPromptExpansion, SessionStart and PostModelSwitch. On every other event it goes to the debug log. On those four events, stdout that failed to parse is not added.
- Claude never sees stderr from a hook that exits 0.

## Exit code 2

Docs: [exit code 2](https://code.claude.com/docs/en/hooks#exit-code-2)

- Blocks the action on events that can block (see the per-event table).
- The block message is stderr. If the hook also printed JSON that makes a blocking decision, that decision's reason is used instead.
- With JSON that passes validation, the fields are still read but can't override the block: even `permissionDecision: "allow"` doesn't let the call through. On Elicitation and ElicitationResult, an exit-2 hook's `hookSpecificOutput` is ignored.
- With JSON that fails validation, the hook still blocks; stderr is the reason and the validation failure goes to the debug log.
- On PreToolUse, Claude receives the stderr as the tool's error, prefixed with the event, tool and command: `PreToolUse:Bash hook error: [<command>]: <stderr>`.
- On PostToolUse and PostToolUseFailure, exit 2 is the way to make Claude read a warning: the tool already ran, but Claude sees the stderr.

## Other exit codes

Docs: [other exit codes](https://code.claude.com/docs/en/hooks#other-exit-codes)

- Exit code other than 0 or 2 with plain or empty stdout: non-blocking error. The notice reads `Failed with non-blocking status code: <first line of stderr>`.
- Exit 1 without valid JSON is a non-blocking error, even though 1 is the Unix failure code, unless the hook is one whose failure blocks (onFailure block, or Windows without Git Bash). A policy hook uses exit 2.
- With a valid JSON object on stdout, the exit code is ignored and the fields decide, unless onFailure is block, where it counts as a failure.
- A notice carrying `No such file or directory` (for example `/bin/sh: /path/to/hook.sh: No such file or directory`) means the hook never ran: the path in the configuration is wrong. In shell form a missing or non-executable script exits with a code like 127.

## Exit code 2 per event

Docs: [exit code 2 behavior per event](https://code.claude.com/docs/en/hooks#exit-code-2-behavior-per-event)

| Event | Can block | Exit 2 does |
| :-- | :-- | :-- |
| PreToolUse | Yes | Blocks the tool call |
| PermissionRequest | No | Not honored; the permission flow proceeds. Deny through the decision object |
| UserPromptSubmit | Yes | Blocks the prompt so it never reaches Claude |
| UserPromptExpansion | Yes | Blocks the expansion |
| Stop | Yes | Prevents Claude from stopping; the conversation continues |
| SubagentStop | Yes | Prevents the subagent from stopping |
| TeammateIdle | Yes | Keeps the teammate working |
| TaskCreated | Yes | Rolls back the task creation |
| TaskCompleted | Yes | Keeps the task from being marked completed |
| ConfigChange | Yes | Blocks the change from taking effect (not `policy_settings`) |
| StopFailure | No | Output and exit code ignored, except `terminalSequence` |
| PostToolUse | No | Shows stderr to Claude; the tool already ran |
| PostToolUseFailure | No | Shows stderr to Claude; the tool already failed |
| PostToolBatch | Yes | Stops the agentic loop before the next model call |
| PermissionDenied | No | Exit code and stderr ignored; use `retry: true` |
| Notification | No | Exit code and stderr ignored |
| SubagentStart | No | stderr shown to the user only |
| SessionStart | No | stderr shown to the user only |
| Setup | No | Exit code and stderr ignored |
| SessionEnd | No | stderr shown to the user only |
| CwdChanged | No | stderr shown to the user only |
| DirectoryAdded | No | stderr goes to the debug log |
| FileChanged | No | stderr shown to the user only |
| PreCompact | Yes | Blocks compaction |
| PostCompact | No | stderr shown to the user only |
| PreModelSwitch | Yes | Blocks the model switch; stderr shown to the user |
| PostModelSwitch | No | stderr shown to the user only |
| Elicitation | Yes | Declines the request; no dialog appears |
| ElicitationResult | Yes | Blocks the response (action becomes decline) |
| WorktreeCreate | Yes | Any non-zero exit fails creation |
| WorktreeRemove | Yes | Any non-zero exit fails removal if the directory still exists |
| InstructionsLoaded | No | Exit code ignored |
| MessageDisplay | No | The original text is displayed |

On SessionStart, SubagentStart and PostModelSwitch the exit-2 stderr appears as a hook error notice; Claude doesn't see it. For SubagentStart the notice is in the subagent's own transcript.

## Timeouts

Docs: [timeouts](https://code.claude.com/docs/en/hooks#timeouts) · [UserPromptSubmit](https://code.claude.com/docs/en/hooks#userpromptsubmit) · [MessageDisplay](https://code.claude.com/docs/en/hooks#messagedisplay) · [PreModelSwitch](https://code.claude.com/docs/en/hooks#premodelswitch) · [SessionEnd](https://code.claude.com/docs/en/hooks#sessionend)

- Default timeouts per hook type and event: the `timeout` row in `handler-fields.md` → Common fields (source: the `timeout` row of [common fields](https://code.claude.com/docs/en/hooks#common-fields)).
- A command, http or mcp_tool hook that reaches its timeout is canceled and its output discarded, so on most events it renders no decision. Command hooks with `async: true` are the exception.
- PreToolUse: a timed-out hook does not block; the call continues through the normal permission flow. Never rely on a stalled hook as a gate. Set `onFailure: "block"` to block on timeout. An Agent SDK callback hook that exceeds its timeout does block.
- PreModelSwitch: a timeout blocks the switch. Its default timeout is 30 seconds.
- SessionEnd: default budget 1.5 seconds; raise it with a per-hook `timeout` (up to 60 s overall; plugin hooks' timeouts don't raise the budget) or `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`.

## Hooks that start a background process

Docs: [background processes](https://code.claude.com/docs/en/hooks#hooks-that-start-a-background-process)

- For a hook that isn't async, Claude Code stops reading output shortly after the hook's own process exits. A deny printed later by a background child doesn't block.
- Print the decision first, then start the background work with its stdout and stderr redirected.
- If a script prints an allow and then starts a background process without redirecting its output, Claude Code blocks the call; the error includes `refusing to honor the suspect capture`.

```bash
#!/usr/bin/env bash
"$CLAUDE_PROJECT_DIR"/.claude/hooks/policy-check.sh || exit $?
"$CLAUDE_PROJECT_DIR"/.claude/hooks/upload-metrics.sh >/dev/null 2>&1 &
```

`|| exit $?` keeps the check's exit 2; without it the script exits with the last line's 0.

## onFailure: block the action when a hook fails

Docs: [onFailure](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)

- `"onFailure": "block"` on a command or http hook. Requires Claude Code v2.1.295 or later. `"onFailure": "continue"` keeps the action going.
- Counts as a failure: the hook can't start; an exit code other than 0 or 2 (even with JSON that allows); an HTTP connection error or non-2xx status; a timeout; invalid output (unparseable JSON, failed schema validation, or an HTTP 2xx body that is neither empty nor a JSON object). Plain-text stdout from a command hook is **not** a failure.
- With block set, a failure does what exit 2 does on that event, except PermissionRequest, where it denies the request.
- No effect on Stop, SubagentStop, TaskCompleted and TeammateIdle (exit 2 there sends Claude back to work, and Claude can't repair a hook that won't run), nor on command hooks with `async` or `asyncRewake`.
- Error text: `failed; blocking because onFailure is "block"`, or `timed out` instead of `failed`.
- A hook that wants to return a JSON decision with onFailure set must exit 0.
- Set it on hooks that enforce a policy only. A failure does what exit 2 does on that event, so on an advisory or observing hook it turns a crash or a timeout into a block: a reminder on `UserPromptSubmit` that fails would block every prompt. Advisory hooks keep `"continue"`. The docs offer `block` on `UserPromptSubmit` as a choice for a hook whose prompt must not go through without it, not as a default.

## Windows without Git Bash

Docs: [Windows without Git Bash](https://code.claude.com/docs/en/hooks#failed-hooks-on-windows-without-git-bash)

- Error text: `blocking because Git Bash wasn't found and this hook doesn't set "shell" to "powershell", so only exit code 0 or 2 counts as its verdict.` A PreToolUse or PermissionRequest shell-form command hook failed or timed out and blocked the call.
- With onFailure unset, such a hook can block on failure; any exit code other than 0 or 2 counts as a failure even with JSON that doesn't deny.
- Fixes: Bash script → install Git for Windows or set `CLAUDE_CODE_GIT_BASH_PATH`, then start a new session. One `.exe` → exec form (`command` + `args`) plus `onFailure: "block"`. PowerShell script → `"shell": "powershell"` plus `onFailure: "block"`. Action should proceed on failure → `onFailure: "continue"`.

## MCP tool hooks

Docs: [how the tool's result is read](https://code.claude.com/docs/en/hooks#how-the-tools-result-is-read) · [when the server is still connecting](https://code.claude.com/docs/en/hooks#when-the-server-is-still-connecting) · [events before MCP servers are available](https://code.claude.com/docs/en/hooks#events-that-fire-before-mcp-servers-are-available)

- The tool's text content is read like command-hook stdout, by the exit code 0 parsing rules. `isError: true` is a non-blocking error.
- On events that can block or change a result (PreToolUse, Stop…), Claude Code waits for a connecting server up to `MCP_TIMEOUT`, within the hook's own timeout. On observational events it doesn't wait. A server not connected when called gives a non-blocking error; the hook never starts OAuth.
- SessionStart at launch (including `--continue`/`--resume`) and every Setup event fire before MCP servers are available: their mcp_tool hooks are skipped, and the debug log says `mcp_tool hooks are not available for the '<event>' hook event (no MCP client context)`. Use a command hook there.

## HTTP hooks

Docs: [HTTP response handling](https://code.claude.com/docs/en/hooks#http-response-handling)

The JSON input arrives as the POST body. The outcome comes from the status and body, not an exit code:

| Response | Result |
| :-- | :-- |
| 2xx, empty body | Success, like exit 0 with no output |
| 2xx, JSON object body | Parsed with the same output schema as command hooks; a body that fails validation is a non-blocking error |
| 2xx, any other body (plain text) | Non-blocking error; the text never reaches Claude |
| Non-2xx | Non-blocking error |
| Connection failure | Non-blocking error |
| Timeout | Canceled, as under Timeouts |

To block, return 2xx with a JSON decision. To block when the request fails, set `onFailure: "block"`. Events with their own contract, such as WorktreeCreate, keep it.
