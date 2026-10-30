# Tool events

PreToolUse · PermissionRequest · PostToolUse · PostToolUseFailure · PostToolBatch · PermissionDenied

Sources: https://code.claude.com/docs/en/hooks and the Claude Code CHANGELOG.md; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields.

**Matcher (all except PostToolBatch) → tool name:** built-ins such as `Bash`, `PowerShell`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `Workflow`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `ExitPlanMode`, `SubagentHandback`, and MCP tools (`mcp__<server>__<tool>`). `EndConversation` never fires any of these events. Use the handler `if` field (`Bash(git *)`, `Edit(*.ts)`) to filter on arguments too.

**MCP provenance:** for MCP tools, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure and PermissionDenied receive `mcp_server` `{ name, source }` (v2.1.274+). `source` is `plugin`, `sdk`, or a config scope (`user`, `project`, …). Base trust decisions on `source`, not on the name or the `mcp__` prefix.

---

## Contents

- PreToolUse
- PermissionRequest
- PostToolUse
- PostToolUseFailure
- PostToolBatch
- PermissionDenied

## PreToolUse

Docs: [event](https://code.claude.com/docs/en/hooks#pretooluse) · [input](https://code.claude.com/docs/en/hooks#pretooluse-input) · [decision control](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)

**Fires:** after Claude builds tool parameters, before the call runs. Only when Claude calls a tool: `@file` mentions are inlined without a tool call, so no `Read` hook fires. Block them with a `Read` deny rule, or set `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1` (v2.1.299+, user/managed settings or shell; ignored in project/local settings) so Claude must read them with tools. To react to a file changing on disk whatever wrote it, use FileChanged instead.

**Handlers:** all five. An Agent SDK callback that times out blocks the call.

**Input:** `tool_name`, `tool_input`, `tool_use_id` (+ `mcp_server` for MCP).

File tools (`Write`, `Edit`, `Read`): `tool_input.file_path` is always absolute (`~` and relative spellings expanded first, so they can't bypass path checks). On Windows it uses backslashes even under Git Bash; normalize (`"${FILE_PATH//\\//}"` / `.replace("\\", "/")`) and match a segment like `/src/` rather than anchoring with `^`.

`tool_input` by tool:

| Tool | Fields |
|---|---|
| `Bash` | `command`, `description?`, `timeout?` (ms; values over max are reduced, not rejected), `run_in_background?` |
| `PowerShell` | same as Bash. On Windows it is the primary shell where enabled; without Git Bash, Bash isn't registered at all. Match `Bash\|PowerShell` |
| `Write` | `file_path`, `content` |
| `Edit` | `file_path`, `old_string`, `new_string`, `replace_all?` |
| `Read` | `file_path`, `offset?`, `limit?` |
| `Glob` | `pattern`, `path?` |
| `Grep` | `pattern`, `path?`, `glob?`, `output_mode?` (`content`/`files_with_matches`/`count`), `-i?`, `multiline?` |
| `WebFetch` | `url`, `prompt`, `offset?` (v2.1.290+) |
| `WebSearch` | `query`, `allowed_domains?`, `blocked_domains?` |
| `Agent` | `prompt`, `description`, `subagent_type`, `model?` |
| `AskUserQuestion` | `questions[]` (`question`, `header`, `options[{label, description}]`, `multiSelect`), `answers?` (question text → label; multi-select labels comma-joined; Claude never sets it) |
| `ExitPlanMode` | Claude's literal input is usually empty; Claude Code injects `plan` (Markdown) and `planFilePath`. `allowedPrompts` is deprecated and ignored |

**Decision control (`hookSpecificOutput`, `hookEventName: "PreToolUse"`):**

| Field | Effect |
|---|---|
| `permissionDecision: "allow"` | skips the prompt, except for actions no mode auto-approves and network-path reads. Deny/ask rules still apply |
| `"deny"` | prevents the call; reason goes to Claude |
| `"ask"` | prompts the user; reason shown in the prompt. Labeled `[settings]`, `[plugin:<name>]` or `[skill]`. Forces a prompt even in auto mode |
| `"defer"` | pause for an external caller (see below) |
| `permissionDecisionReason` | ask → user; deny → Claude (in `-p` with no one to answer, Claude reads it in the tool result); allow/defer → debug log only |
| `updatedInput` | replaces the whole input object (include unchanged fields). Permission rules and Bash auto-background eligibility are evaluated on it. Pair with allow or ask; ignored with defer. Validated like Claude's own input: unknown keys are dropped, and input the tool rejects denies the call *(changelog v2.1.300)* |
| `additionalContext` | added with the tool result; ignored with defer |

Precedence across hooks: deny > defer > ask > allow. Exit 2 = deny with stderr as reason. Top-level `decision`/`reason` is deprecated here (`approve`→allow, `block`→deny).

Version notes *(changelog)*:
- Before v2.1.299, a write (MCP tool, file, shell command) that a PreToolUse hook allowed could run in plan mode; fixed in v2.1.299.
- Before v2.1.304, a deny reason could be replaced by a timeout error when an Agent SDK callback hook on the same call timed out.
- On Windows without Git for Windows, PreToolUse and PermissionRequest hooks that set no `shell` fail closed since v2.1.299 (a failing guard blocks the call).

**Tools needing user interaction** (`AskUserQuestion`, `ExitPlanMode`): in `-p` they're offered only with a permission host (e.g. SDK `canUseTool`, `--permission-prompt-tool`). A hook satisfies them only with `allow` + `updatedInput` holding the answer (for AskUserQuestion: echo `questions` and add `answers`). `allow` alone isn't enough. MCP tools marked `_meta["anthropic/requiresUserInteraction"]` can't be auto-approved by a hook at all.

**Defer:** honored only in `-p`; interactive sessions log a warning and ignore it. Only works when Claude made a single tool call in the turn (otherwise ignored with a warning). Flow: hook returns `defer` → process exits with `stop_reason: "tool_deferred"` and `deferred_tool_use {id, name, input}` → caller collects input → `claude -p --resume <id>` with the same permission host → PreToolUse fires again → hook returns `allow` + `updatedInput`. No timeout; the session lives until `cleanupPeriodDays` (30 days default). If the tool is gone on resume (MCP server not connected): `stop_reason: "tool_deferred_unavailable"`, `is_error: true`, before the hook fires. Resuming with `-p` doesn't restore the stored permission mode: pass `--permission-mode` again. Plan mode resume needs `--permission-prompt-tool` (v2.1.246+).

---

## PermissionRequest

Docs: [event](https://code.claude.com/docs/en/hooks#permissionrequest) · [input](https://code.claude.com/docs/en/hooks#permissionrequest-input) · [decision control](https://code.claude.com/docs/en/hooks#permissionrequest-decision-control)

**Fires:** Claude Code is about to show a permission prompt. Also in sessions that can't prompt (background subagents in `-p`): if no hook decides, the call is denied. With `--permission-prompt-tool` or SDK `canUseTool`, hooks run alongside the host and the first decision wins. Fires immediately, unlike `Notification` `permission_prompt` (~6 s). Not run for a sandboxed command's network request (use the `permission_prompt` notification).

**Handlers:** `command`, `http`, `mcp_tool`, `prompt`; an `agent` hook is skipped.

**Input:** `tool_name`, `tool_input` (no `tool_use_id`), `mcp_server` for MCP, optional `permission_suggestions[]`. The suggestions aren't the exact options shown: some dialogs (file edits) ignore them, some withhold them (`allowManagedPermissionRulesOnly`), some offer options without entries (switch to auto mode).

**Output (`hookSpecificOutput.decision`):**

| Field | Effect |
|---|---|
| `behavior` | `allow` or `deny`. Deny/ask rules still apply over an allow |
| `updatedInput` | allow only; replaces whole input; re-checked against deny/ask rules. Unknown keys are dropped and input the tool rejects denies the call *(changelog v2.1.300)* |
| `updatedPermissions` | allow only; array of permission update entries |
| `message` | deny only; tells Claude why |
| `interrupt` | deny only; `true` stops Claude |

**Exit 2 is not honored**: stderr discarded, flow unchanged. Return the decision object.

**Cowork cloud sessions** *(changelog)*: a `setMode` update in an allow is ignored, though the rest of the approval applies (v2.1.300). In auto mode there, a PermissionRequest hook can't approve shell commands or subagents; those prompts wait or are denied (v2.1.299).

**Permission update entries** (also the shape of `permission_suggestions`):

| `type` | Fields |
|---|---|
| `addRules` / `replaceRules` / `removeRules` | `rules[{toolName, ruleContent?}]`, `behavior` (`allow`/`deny`/`ask`), `destination` |
| `setMode` | `mode` (`default`, `auto`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`, `manual`=default), `destination` |
| `addDirectories` / `removeDirectories` | `directories[]`, `destination` |

`destination`: `session` (memory), `localSettings` (`.claude/settings.local.json`), `projectSettings` (`.claude/settings.json`), `userSettings` (`~/.claude/settings.json`). `setMode bypassPermissions` is a no-op unless the session launched with bypass available and it isn't disabled; it's never persisted as `defaultMode`. A hook may echo a received suggestion back as `updatedPermissions`.

---

## PostToolUse

Docs: [event](https://code.claude.com/docs/en/hooks#posttooluse) · [input](https://code.claude.com/docs/en/hooks#posttooluse-input) · [decision control](https://code.claude.com/docs/en/hooks#posttooluse-decision-control)

**Fires:** right after a tool succeeds. `*` or no matcher runs after every tool; pair with `git status --porcelain` to find changes (also lists untracked files). Doesn't fire when Bash or an outside process rewrites a file; use FileChanged for that. Failures go to PostToolUseFailure.

**Handlers:** all five.

**Input:** `tool_name`, `tool_input`, `tool_response` (tool-specific structured output, e.g. Write → `{filePath, type: "create"}`), `tool_use_id`, `duration_ms?` (excludes permission prompts and PreToolUse hooks), `mcp_server` for MCP.

Special `tool_response` shapes:
- **Bash `bashEditDiff`** (v2.1.269+, public beta, best effort): recorded in every mode when `bashEditDiffEnabled` is on, otherwise only in auto/bypassPermissions when Claude is directed to edit via Bash. Fields: `changedFiles` (≤200 absolute paths), `files` (≤5 diffs, `created`/`deleted`), `moreFiles`, `unavailable`, `skipped` (git checkout/stash), `shared` (another Bash call ran concurrently). Ignored and submodule files aren't listed; background and read-only commands carry none. Use it to decide what to review, not to enforce policy.
- **Agent:** foreground → `status: "completed"`, `agentId`, `content`, `resolvedModel`, `modelsUsed?`, `totalTokens`/`usage` (final request only, not run totals), `totalDurationMs`, `totalToolUseCount`. Background → `status: "async_launched"`, `agentId`, `description`, `prompt`, `outputFile`, `resolvedModel`, no usage. A subagent that hands back via `SubagentHandback` (auto mode, v2.1.271+) puts its report in that tool's `tool_input.message`, not in `content`.
- **ExitPlanMode:** read `tool_response.plan` rather than the file.

**Output:**

| Field | Effect |
|---|---|
| top-level `decision: "block"` + `reason` | adds the reason next to the result; Claude still sees the original output |
| `hookSpecificOutput.additionalContext` | added with the result |
| `hookSpecificOutput.updatedToolOutput` | replaces what Claude sees; must match the tool's output shape (Bash: `stdout`, `stderr`, `interrupted`, `isImage`). A mismatched value for a built-in tool is ignored; MCP output isn't validated |
| `updatedMCPToolOutput` | MCP-only legacy; prefer `updatedToolOutput` |
| `classifierContext` | short note to the auto-mode classifier (v2.1.236+) |

The tool already ran: side effects happened, and telemetry captured the original output. To prevent or change a call, use PreToolUse. Exit 2 only shows stderr to Claude.

**`classifierContext`:** the classifier never sees tool results; this is how to tell it about one. Hooks from settings, plugins, skills and agent frontmatter count as unverified context and never establish user intent; only an in-process TypeScript SDK callback can relay a user statement as intent, and not after resume. Cap 2,000 characters per call across hooks; ignored from background hooks and on calls the classifier doesn't record (reads, searches); dropped if paired `updatedToolOutput` is rejected or overridden. Never copy untrusted tool output into it.

---

## PostToolUseFailure

Docs: [event](https://code.claude.com/docs/en/hooks#posttoolusefailure) · [input](https://code.claude.com/docs/en/hooks#posttoolusefailure-input) · [decision control](https://code.claude.com/docs/en/hooks#posttoolusefailure-decision-control)

**Fires:** a tool that started executing failed (threw, or MCP returned an error result). Not for calls rejected before execution: unknown tool, schema/validation failure (`tool_use_error`, no hooks at all), or permission denial (fires PreToolUse, then PermissionDenied in auto mode). Cancelling a running tool doesn't fire it.

**Handlers:** all five.

**Input:** `tool_name`, `tool_input`, `tool_use_id`, `error`, `is_interrupt?` (aborted rather than tool-reported), `duration_ms?`, `mcp_server` for MCP.

`error` is roughly what Claude sees; format varies. Bash/PowerShell: first line `Exit code N`, then interleaved stdout+stderr; may be a bare message if the shell couldn't start; long text is middle-truncated (`... [N characters truncated] ...`); Claude Code may insert lines like `Command timed out after 2m 0s`. Key on `tool_name`, `is_interrupt` and the `Exit code` line; treat the rest as display text.

**Output:** `hookSpecificOutput.additionalContext` only. Exit 2 shows stderr to Claude.

---

## PostToolBatch

Docs: [event](https://code.claude.com/docs/en/hooks#posttoolbatch) · [input](https://code.claude.com/docs/en/hooks#posttoolbatch-input) · [decision control](https://code.claude.com/docs/en/hooks#posttoolbatch-decision-control)

**Fires:** once after every call in a batch resolves, before the next model request. Use it for context that depends on the set of calls (PostToolUse runs per tool and concurrently).

**Matcher:** none. **Handlers:** all five.

**Input:** `tool_calls[]` of `{tool_name, tool_input, tool_use_id, tool_response}`. Here `tool_response` is the serialized `tool_result` content the model sees (Read → line-number-prefixed text), not PostToolUse's structured object. Can be large; parse only what you need.

**Output:** `hookSpecificOutput.additionalContext`, injected once before the next model call. Top-level `decision: "block"` or `continue: false` (or exit 2) stops the agentic loop before the next model call; the message (`reason`/`stopReason`/stderr) shows as a transcript warning and stays in the conversation.

---

## PermissionDenied

Docs: [event](https://code.claude.com/docs/en/hooks#permissiondenied) · [input](https://code.claude.com/docs/en/hooks#permissiondenied-input) · [decision control](https://code.claude.com/docs/en/hooks#permissiondenied-decision-control)

**Fires:** only in auto mode, when it denies a call, including no-verdict denials (a separate safety check refused the classifier's request, or its response didn't parse). Not for manual denials, PreToolUse blocks, or deny rules.

**Handlers:** all five.

**Input:** `tool_name`, `tool_input`, `tool_use_id`, `reason`, `mcp_server` for MCP. `reason` is usually a rule in brackets (`[Data Exfiltration]`); no-verdict denials start with `Auto mode could not evaluate this action and is blocking it for safety`; classifier unavailable is `Classifier unavailable`.

**Output:** `hookSpecificOutput.retry: true` adds a message telling the model it may retry; it doesn't reverse the denial. Ignored for no-verdict denials. Exit code and stderr are ignored.
