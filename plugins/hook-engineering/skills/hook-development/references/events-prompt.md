# Prompt and display events

UserPromptSubmit · UserPromptExpansion · MessageDisplay

Sources: https://code.claude.com/docs/en/hooks (read 2026-10-20) and the Claude Code CHANGELOG.md through v2.1.305; changelog-only facts are tagged *(changelog vX.Y.Z)*. Fields listed are in addition to the common input fields.

---

## UserPromptSubmit

Docs: [event](https://code.claude.com/docs/en/hooks#userpromptsubmit) · [input](https://code.claude.com/docs/en/hooks#userpromptsubmit-input) · [decision control](https://code.claude.com/docs/en/hooks#userpromptsubmit-decision-control)

**Fires:** a prompt is submitted, before Claude processes it. Not only typed prompts: also a session-scoped scheduled task firing (including each `/loop` iteration), a background subagent reporting back to its session, and a message another session sends to the main conversation. A hook that should act only on human input must tell these apart from the `prompt` text.

**Matcher:** none; fires on every prompt.

**Handlers:** all five types.

**Timeout:** default 30 s for `command`, `http`, `mcp_tool` (vs 600 s on most events). It blocks model processing, so a stuck hook stalls the session. On timeout (except `async: true` command hooks) the hook is canceled, its output including `additionalContext` is discarded, and the prompt still reaches Claude; the transcript shows a notice. Set `onFailure: "block"` on a command or HTTP hook to block instead, only when the hook enforces a policy: on an advisory hook, any failure would then block every prompt. An Agent SDK callback hook that times out here blocks the prompt (fails closed).

**Skill frontmatter:** a skill's own `UserPromptSubmit` hook first runs on the prompt *after* the one that invokes the skill, not on the invoking prompt *(changelog v2.1.299)*.

**Input:** `prompt` (pasted `[Pasted text #N]` placeholders arrive expanded; in some sessions wrapped between `<pasted_content id="…">` and `</pasted_content id="…">` lines). `session_title` when a custom title is set. A typed skill/command (`/deploy staging`) arrives as typed, not expanded; blocking it means the command and its `` !`cmd` `` injections never run. To match on command name or args, use UserPromptExpansion.

Since v2.1.299 the hook runs before expansion, so blocking also stops the skill's embedded shell commands.

**Output:**

| Field | Effect |
|---|---|
| top-level `decision: "block"` | prompt never reaches Claude |
| top-level `reason` | shown to the user on block; not added to context |
| `hookSpecificOutput.additionalContext` | added to context with the prompt |
| `hookSpecificOutput.sessionTitle` | sets the session title |
| `hookSpecificOutput.suppressOriginalPrompt` | on block, omit the prompt text from the block message |

Plain-text stdout on exit 0 is also added as context. Neither channel creates a visible transcript entry; both arrive as a system reminder starting with the hook's name. Confirm delivery in the debug log.

Exit 2 blocks the same way; stderr goes to the user, not to context.

**What a blocked prompt leaves behind:** by default the block message ends with `Original prompt:` + the text and is written to the transcript file on disk. `suppressOriginalPrompt: true` removes it from that message only; the text can still be in the session transcript and prompt history. A blocking hook is not a way to keep a secret off disk.

---

## UserPromptExpansion

Docs: [event](https://code.claude.com/docs/en/hooks#userpromptexpansion) · [input](https://code.claude.com/docs/en/hooks#userpromptexpansion-input) · [decision control](https://code.claude.com/docs/en/hooks#userpromptexpansion-decision-control)

**Fires:** a user-typed command expands into a prompt, before reaching Claude. Covers the path PreToolUse misses: PreToolUse on the `Skill` tool fires only when Claude calls the tool; typing `/skillname` directly bypasses it.

**Matcher → `command_name`.** Empty matcher fires on every prompt-type command.

**Handlers:** all five types.

**Input:** `expansion_type` (`slash_command` for skills and custom commands, `mcp_prompt` for MCP server prompts), `command_name`, `command_args`, `command_source` (e.g. `plugin`), `prompt` (the original typed line).

**Output:** top-level `decision: "block"` + `reason` (shown to the user) prevents expansion; `hookSpecificOutput.additionalContext` is added alongside the expanded prompt. Exit 2 blocks with stderr shown to the user. Plain stdout is context.

Typical uses: block `/deploy` unless an approval file exists; append a team checklist as context when a review skill runs; log command usage.

---

## MessageDisplay

Docs: [event](https://code.claude.com/docs/en/hooks#messagedisplay) · [input](https://code.claude.com/docs/en/hooks#messagedisplay-input) · [output](https://code.claude.com/docs/en/hooks#messagedisplay-output)

**Fires:** while an assistant message streams to screen. Interactive: once per batch of newly completed lines, so a long message yields several calls. Non-interactive (`-p`, Agent SDK): once per message after it completes, with `index: 0`, `final: true`, and the whole text in `delta`.

**Matcher:** none. Messages with no text (tool-call-only) don't trigger it. Receives assistant text only; tool results and user text render unchanged.

**Handlers:** `command`, `http`, `mcp_tool`.

**Display-only:** the replacement changes the screen only. The transcript, what Claude sees, and verbose mode keep the original. Claude never sees the replacement.

**Timing:** each batch is held until the hook returns. Default timeout 10 s. On failure or timeout the original text is shown, and the failure appears only in debug output.

**Input:**

| Field | Notes |
|---|---|
| `turn_id` | UUID of the turn |
| `message_id` | UUID, stable across batches of one message; not the API `msg_…` id |
| `index` | zero-based batch index |
| `final` | `true` on exactly one batch per message; use it, not a non-empty delta, as end-of-message |
| `delta` | newly completed lines incl. newlines; the final batch may end mid-line and is empty when the message ends on a newline |

Batch boundaries depend on streaming; don't assume grouping.

**Output:** `hookSpecificOutput.displayContent` replaces the delta on screen; omit it to show the original. No decision control; `systemMessage` and `continue` discarded.

Uses: strip markdown for a plain display, redact keys or internal hostnames from what's shown, transform text in an SDK app.
