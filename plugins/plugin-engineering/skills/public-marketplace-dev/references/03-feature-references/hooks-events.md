# Hooks reference: hook events

This file holds the per-event part of the Claude Code hooks reference: when each hook event fires, what its matcher filters, its JSON input, and the decision control it accepts. Configuration, exit codes, JSON output, prompt and agent hooks, async hooks, security and debugging are in [hooks.md](hooks.md), which also opens with the [things to know about hooks in plugins](hooks.md#things-to-know-about-hooks-in-plugins).

## Contents

- [Hook events](#hook-events)
  - [SessionStart](#sessionstart)
    - [SessionStart input](#sessionstart-input)
    - [SessionStart decision control](#sessionstart-decision-control)
    - [Reload skills that a hook installs](#reload-skills-that-a-hook-installs)
    - [Persist environment variables](#persist-environment-variables)
  - [Setup](#setup)
    - [Setup input](#setup-input)
    - [Setup decision control](#setup-decision-control)
  - [InstructionsLoaded](#instructionsloaded)
    - [InstructionsLoaded input](#instructionsloaded-input)
    - [InstructionsLoaded decision control](#instructionsloaded-decision-control)
  - [UserPromptSubmit](#userpromptsubmit)
    - [`Esc` during a prompt check](#esc-during-a-prompt-check)
    - [UserPromptSubmit input](#userpromptsubmit-input)
    - [UserPromptSubmit decision control](#userpromptsubmit-decision-control)
    - [What a blocked prompt leaves behind](#what-a-blocked-prompt-leaves-behind)
  - [UserPromptExpansion](#userpromptexpansion)
    - [UserPromptExpansion input](#userpromptexpansion-input)
    - [UserPromptExpansion decision control](#userpromptexpansion-decision-control)
  - [MessageDisplay](#messagedisplay)
    - [MessageDisplay input](#messagedisplay-input)
    - [MessageDisplay output](#messagedisplay-output)
  - [PreToolUse](#pretooluse)
    - [PreToolUse input](#pretooluse-input)
    - [PreToolUse decision control](#pretooluse-decision-control)
    - [PreToolUse `updatedInput` in auto mode](#pretooluse-updatedinput-in-auto-mode)
    - [PreToolUse `ask` decisions in auto mode](#pretooluse-ask-decisions-in-auto-mode)
  - [PermissionRequest](#permissionrequest)
    - [PermissionRequest input](#permissionrequest-input)
    - [PermissionRequest decision control](#permissionrequest-decision-control)
    - [Permission update entries](#permission-update-entries)
  - [PostToolUse](#posttooluse)
    - [PostToolUse after an interrupt](#posttooluse-after-an-interrupt)
    - [PostToolUse input](#posttooluse-input)
    - [PostToolUse decision control](#posttooluse-decision-control)
    - [Annotate a result for the auto mode classifier](#annotate-a-result-for-the-auto-mode-classifier)
  - [PostToolUseFailure](#posttoolusefailure)
    - [PostToolUseFailure input](#posttoolusefailure-input)
    - [PostToolUseFailure decision control](#posttoolusefailure-decision-control)
  - [PostToolBatch](#posttoolbatch)
    - [PostToolBatch input](#posttoolbatch-input)
    - [PostToolBatch decision control](#posttoolbatch-decision-control)
  - [PermissionDenied](#permissiondenied)
    - [PermissionDenied input](#permissiondenied-input)
    - [PermissionDenied decision control](#permissiondenied-decision-control)
  - [Notification](#notification)
    - [Notification input](#notification-input)
  - [SubagentStart](#subagentstart)
    - [SubagentStart input](#subagentstart-input)
  - [SubagentStop](#subagentstop)
    - [SubagentStop input](#subagentstop-input)
  - [TaskCreated](#taskcreated)
    - [TaskCreated input](#taskcreated-input)
    - [TaskCreated decision control](#taskcreated-decision-control)
  - [TaskCompleted](#taskcompleted)
    - [TaskCompleted input](#taskcompleted-input)
    - [TaskCompleted decision control](#taskcompleted-decision-control)
  - [Stop](#stop)
    - [Stop input](#stop-input)
    - [Stop decision control](#stop-decision-control)
  - [StopFailure](#stopfailure)
    - [StopFailure input](#stopfailure-input)
  - [TeammateIdle](#teammateidle)
    - [TeammateIdle input](#teammateidle-input)
    - [TeammateIdle decision control](#teammateidle-decision-control)
  - [ConfigChange](#configchange)
    - [ConfigChange input](#configchange-input)
    - [ConfigChange decision control](#configchange-decision-control)
  - [CwdChanged](#cwdchanged)
    - [CwdChanged input](#cwdchanged-input)
    - [CwdChanged output](#cwdchanged-output)
  - [DirectoryAdded](#directoryadded)
    - [DirectoryAdded input](#directoryadded-input)
  - [FileChanged](#filechanged)
    - [FileChanged input](#filechanged-input)
    - [FileChanged output](#filechanged-output)
  - [WorktreeCreate](#worktreecreate)
    - [WorktreeCreate input](#worktreecreate-input)
    - [WorktreeCreate output](#worktreecreate-output)
  - [WorktreeRemove](#worktreeremove)
    - [WorktreeRemove input](#worktreeremove-input)
  - [PreCompact](#precompact)
    - [PreCompact input](#precompact-input)
    - [PreCompact output](#precompact-output)
  - [PostCompact](#postcompact)
    - [PostCompact input](#postcompact-input)
  - [PreModelSwitch](#premodelswitch)
    - [PreModelSwitch input](#premodelswitch-input)
    - [PreModelSwitch decision control](#premodelswitch-decision-control)
    - [PreModelSwitch timeouts and other exit codes](#premodelswitch-timeouts-and-other-exit-codes)
  - [PostModelSwitch](#postmodelswitch)
    - [PostModelSwitch input](#postmodelswitch-input)
    - [PostModelSwitch decision control](#postmodelswitch-decision-control)
  - [SessionEnd](#sessionend)
    - [SessionEnd input](#sessionend-input)
  - [Elicitation](#elicitation)
    - [Elicitation input](#elicitation-input)
    - [Elicitation output](#elicitation-output)
    - [Other ways to decline an elicitation](#other-ways-to-decline-an-elicitation)
    - [Answer a form request from a script](#answer-a-form-request-from-a-script)
  - [ElicitationResult](#elicitationresult)
    - [ElicitationResult input](#elicitationresult-input)
    - [ElicitationResult output](#elicitationresult-output)
- [Documentation References](#documentation-references)

## Hook events

Each event corresponds to a point in Claude Code's lifecycle where hooks can run. The sections below are ordered to match the lifecycle: from session setup through the agentic loop to session end. Each section describes when the event fires, what matchers it supports, the JSON input it receives, and how to control behavior through output.

### SessionStart

Runs when Claude Code starts a new session or resumes an existing session. Useful for loading development context like existing issues or recent changes to your codebase, or setting up environment variables. For static context that doesn't require a script, use [CLAUDE.md](https://code.claude.com/docs/en/memory.md) instead.

SessionStart runs on every session, so keep these hooks fast. Only `type: "command"` and `type: "mcp_tool"` hooks are supported. See [MCP tool hook fields](hooks.md#mcp-tool-hook-fields) for when `mcp_tool` hooks run.

The matcher value corresponds to how the session was initiated:

| Matcher | When it fires |
| :- | :- |
| `startup` | New session |
| `resume` | `--resume`, `--continue`, or `/resume` |
| `clear` | `/clear` |
| `compact` | Auto or manual compaction |
| `fork` | A new session forked from an existing one: `--fork-session` with `--resume` or `--continue`, the `/fork` background copy, `/branch`, or a conversation you [move to the background](https://code.claude.com/docs/en/agent-view.md#from-inside-a-session) |

When you start an interactive session, resume a conversation at launch with `--continue` or `--resume`, or run `/clear`, SessionStart hooks run in the background. You can type right away, and a conversation you resumed appears without waiting for the hooks. Claude's first response still waits for the hooks to finish, so their context reaches Claude.

When you switch conversations with `/resume` inside a session, the switch waits for the hooks to finish instead. If you run `/clear` or switch to another conversation while background hooks are still running, nothing they return applies to the session.

The same wait applies at launch, including a resumed session: a prompt you send while SessionStart hooks are still running doesn't reach Claude until they finish.

During either wait, press `Esc` to take the prompt back into the input without sending it. The hooks keep running.

#### SessionStart input

In addition to the [common input fields](hooks.md#common-input-fields), SessionStart hooks receive `source` and optionally `model`, `agent_type`, and `session_title`:

| Field | Description |
| :- | :- |
| `source` | How the session started: `"startup"` for new sessions, `"resume"` for resumed sessions, `"clear"` after `/clear`, `"compact"` after compaction, or `"fork"` for a new session forked from an existing one |
| `model` | The active model identifier. It can be omitted, for example after `/clear` or when a session is restored through conversation recovery, so check for the field before reading it |
| `agent_type` | The agent name, present when you start Claude Code with `claude --agent <name>` |
| `session_title` | The session's custom title, present when one is set, for example with `--name`, `/rename`, a hook's `sessionTitle` output, or the Agent SDK's `renameSession()`. A hook that emits `sessionTitle` can check this field first to avoid overwriting an existing custom title |

A session you haven't named can still have a [generated title](https://code.claude.com/docs/en/sessions.md#name-your-sessions). That title isn't a custom title and doesn't appear in `session_title`.

When `source` is `"resume"` or `"fork"` and the transcript contains at least one response from Claude, SessionStart hooks also receive the four fields below. Your hook can use them to report what resuming a stale conversation costs before the first request, for example in a [`systemMessage`](hooks.md#json-output). These fields require Claude Code v2.1.251 or later.

| Field | Description |
| :- | :- |
| `seconds_since_last_response` | Wall-clock seconds since the last response in the resumed transcript |
| `context_tokens` | Tokens the first request of the resumed session re-sends as its prompt |
| `prompt_cache_likely_expired` | `true` when the last response is older than the session's [prompt cache lifetime](https://code.claude.com/docs/en/prompt-caching.md#cache-lifetime) or a later compaction replaced the cached conversation |
| `estimated_cache_write_usd` | Estimated cost in US dollars of writing `context_tokens` to the prompt cache on the session's model, excluding the response |

#### SessionStart decision control

A SessionStart hook can add context for Claude, supply the first user message, set the session title, watch files, and reload skills. Return the field for each one, in addition to the [JSON output fields](hooks.md#json-output) available to all hooks:

| Field | Description |
| :- | :- |
| `additionalContext` | String added to Claude's context at the start of the conversation, before the first prompt. See [Add context for Claude](hooks.md#add-context-for-claude) for how the text is delivered and what to put in it |
| `initialUserMessage` | String used as the first user message of the session, in [non-interactive mode](https://code.claude.com/docs/en/headless.md) with the `-p` flag. It becomes the first turn even if you pass no prompt. A prompt you do pass follows as the next turn |
| `sessionTitle` | Sets the session title, with the same effect as `/rename`. Applies when `source` is `"startup"`, `"resume"`, or `"fork"` |
| `watchPaths` | Array of absolute paths to watch for [FileChanged](#filechanged) events during this session |
| `reloadSkills` | Boolean. When `true`, Claude Code re-scans the [skill](https://code.claude.com/docs/en/skills.md) and command directories after the SessionStart hooks complete. See [Reload skills that a hook installs](#reload-skills-that-a-hook-installs) |

This output adds context and names the session:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted changes: src/auth.ts, src/login.tsx\nActive issue: #4211 Migrate to OAuth2",
    "sessionTitle": "auth-refactor"
  }
}
```

A hook that only adds context can print it without building JSON, because Claude Code adds a SessionStart hook's [plain-text stdout](hooks.md#exit-code-0) to Claude's context.

If your plugin's SessionStart hook supplies `initialUserMessage` or `sessionTitle`, install the plugin before the session starts. Claude Code ignores both fields from a plugin that finishes installing after the SessionStart hooks have run.

#### Reload skills that a hook installs

To make skills that a SessionStart hook installs available in the same session, return `reloadSkills`. Skill discovery normally runs before SessionStart hooks finish, so without it, files a hook writes into `~/.claude/skills/` or `.claude/skills/` can be missing when the first prompt runs.

#### Persist environment variables

SessionStart hooks have access to the `CLAUDE_ENV_FILE` environment variable, which provides a file path where you can persist environment variables for the shell commands Claude runs later in the session.

To set individual environment variables, write `export` statements to `CLAUDE_ENV_FILE`. Use append (`>>`) to preserve variables set by other hooks:

```bash theme={null}
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
  echo 'export PATH="$PATH:./node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

To capture all environment changes from setup commands, compare the exported variables before and after:

```bash theme={null}
#!/bin/bash

ENV_BEFORE=$(export -p | sort)

# Run your setup commands that modify the environment
source ~/.nvm/nvm.sh
nvm use 20

if [ -n "$CLAUDE_ENV_FILE" ]; then
  ENV_AFTER=$(export -p | sort)
  comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

Each Bash command runs the file's contents as shell code before the command itself, so a line there can use anything Bash evaluates, such as the `$PATH` reference in `export PATH="$PATH:./node_modules/.bin"`.

##### Persisted variables in PowerShell commands

[PowerShell](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) commands receive the variables from `CLAUDE_ENV_FILE` too, in Claude Code v2.1.296 or later, but PowerShell never runs the file. Claude Code reads the assignments out of it and copies them into the PowerShell command's environment instead. It does so only when every line is one of the following, across what every hook in this session wrote and any script you [set `CLAUDE_ENV_FILE` to](https://code.claude.com/docs/en/env-vars) before launch:

* A blank line or a `#` comment
* One assignment at the start of the line, written `export NAME=value`, `declare -x NAME=value`, or `NAME=value`, with a value Bash would use exactly as written, made of any mix of these parts: unquoted text that uses only letters, digits, and the characters `_ @ % + = : , . / -`, text in single quotes, and text in double quotes where any `$`, backtick, or `"` inside is escaped with a backslash

If any line is of another kind, such as `export PATH="$PATH:./node_modules/.bin"` with its unescaped `$PATH`, a `source` command, or the `$'...'` strings that `direnv export bash` prints, PowerShell commands receive none of the variables, and `claude --debug` logs `Session environment is not all plain assignments`. Bash commands still receive all of them. On Windows, PowerShell commands also don't receive a variable whose value contains `/` or `\`, because Git Bash and Windows write paths differently. A [sandboxed](https://code.claude.com/docs/en/sandboxing.md) PowerShell command receives none of the variables.

> [!NOTE]
>
> `CLAUDE_ENV_FILE` is available for SessionStart, [Setup](#setup), [CwdChanged](#cwdchanged), and [FileChanged](#filechanged) hooks. Other hook events don't have access to this variable, and neither does a hook that runs in PowerShell, whether through [`"shell": "powershell"`](hooks.md#command-hook-fields) or by default on Windows without Git Bash.

### Setup

Fires only when you launch Claude Code with `--init-only`, or with `--init` or `--maintenance` in [non-interactive mode](https://code.claude.com/docs/en/headless.md) with the `-p` flag. It doesn't fire on normal startup. Use it for one-time dependency installation or scheduled cleanup that you trigger explicitly from CI or scripts, separate from normal session startup. For per-session initialization, use [SessionStart](#sessionstart) instead.

The matcher value corresponds to the CLI flag that triggered the hook:

| Matcher | When it fires |
| :- | :- |
| `init` | `claude --init-only` or `claude -p --init` |
| `maintenance` | `claude -p --maintenance` |

When you run `claude --init-only`, Claude Code runs Setup hooks and `SessionStart` hooks with the `startup` matcher, then exits without starting a conversation.

When you start or continue a conversation with `-p`, you also need to supply a prompt, as an argument or piped on stdin. You can skip the prompt when a `SessionStart` hook supplies [`initialUserMessage`](#sessionstart-decision-control) or when you resume a session with a [deferred tool call](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later).

On success, `--init-only` prints nothing to the terminal. To confirm the hooks ran, start with `claude --debug-file <path> --init-only`, replacing `<path>` with a log file location, and check the log for the Setup and SessionStart hook entries.

Because Setup doesn't fire on every launch, a plugin that needs a dependency installed can't rely on Setup alone. The practical pattern is to check for the dependency on first use and install on miss, for example a hook or skill that tests for `${CLAUDE_PLUGIN_DATA}/node_modules` and runs `npm install` if absent. See the [persistent data directory](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data) for where to store installed dependencies. If you distribute your plugin through a marketplace, you may not need this pattern: Claude Code [installs eligible Node.js package dependencies automatically](https://code.claude.com/docs/en/plugins/loading.md#node-js-package-dependencies) when it caches the plugin.

#### Setup input

In addition to the [common input fields](hooks.md#common-input-fields), Setup hooks receive a `trigger` field set to either `"init"` or `"maintenance"`.

#### Setup decision control

Setup hooks can't block; execution continues on any exit code. On every exit code, Claude Code discards a Setup hook's [JSON output fields](hooks.md#json-output), such as `systemMessage`, `continue`, and `hookSpecificOutput.additionalContext`. With `-p`, a Setup hook's stdout, stderr, and exit code appear in the run's output only as [`hook_response` events](https://code.claude.com/docs/en/headless#read-session-metadata) when you launch with `--output-format stream-json --verbose`.

Setup hooks have access to `CLAUDE_ENV_FILE`. If your hook writes variables to that file, they persist into subsequent Bash commands for the session, as in [SessionStart hooks](#persist-environment-variables). Only `type: "command"` hooks run on `Setup`. A `type: "mcp_tool"` hook on `Setup` is always skipped, as described under [MCP tool hook fields](hooks.md#mcp-tool-hook-fields).

### InstructionsLoaded

Fires when a `CLAUDE.md` or `.claude/rules/*.md` file is loaded into context. This event fires at session start for eagerly loaded files and again later when files are lazily loaded, for example when Claude accesses a subdirectory that contains a nested `CLAUDE.md` or when conditional rules with `paths:` frontmatter match. The hook doesn't support blocking or decision control. It runs asynchronously for observability purposes.

This event doesn't fire when Claude [reads `AGENTS.md` directly](https://code.claude.com/docs/en/memory#agents-md) through the **Project instructions** setting. It does fire when a `CLAUDE.md` imports your `AGENTS.md`, with `load_reason` set to `include` as for any other imported file, and when `CLAUDE.md` is a symlink to it, as a normal `CLAUDE.md` load.

The matcher runs against `load_reason`. For example, use `"matcher": "session_start"` to fire only for files loaded at session start, or `"matcher": "path_glob_match|nested_traversal"` to fire only for lazy loads.

#### InstructionsLoaded input

In addition to the [common input fields](hooks.md#common-input-fields), InstructionsLoaded hooks receive these fields:

| Field | Description |
| :- | :- |
| `file_path` | Absolute path to the instruction file that was loaded |
| `memory_type` | Scope of the file: `"User"`, `"Project"`, `"Local"`, or `"Managed"` |
| `load_reason` | Why the file was loaded: `"session_start"`, `"nested_traversal"`, `"path_glob_match"`, `"include"`, or `"compact"`. The `"compact"` value fires when instruction files are re-loaded after a compaction event |
| `globs` | Path glob patterns from the file's `paths:` frontmatter, if any. Present only for `path_glob_match` loads |
| `trigger_file_path` | Path to the file whose access triggered this load, for lazy loads |
| `parent_file_path` | Path to the parent instruction file that included this one, for `include` loads |

#### InstructionsLoaded decision control

InstructionsLoaded hooks have no decision control. They can't block or modify instruction loading. Claude Code discards their [JSON output fields](hooks.md#json-output), such as `systemMessage` and `continue`. Use this event for audit logging, compliance tracking, or observability.

### UserPromptSubmit

Runs when a prompt is submitted, before Claude processes it. This allows you
to add additional context based on the prompt/conversation, validate prompts, or
block certain types of prompts.

`UserPromptSubmit` hooks don't fire only on prompts you type. Claude Code also runs them on:

* A [session-scoped scheduled task](https://code.claude.com/docs/en/scheduled-tasks.md) firing, including a `/loop` iteration
* A [background subagent](https://code.claude.com/docs/en/sub-agents.md#run-subagents-in-foreground-or-background) reporting back to the session that started it
* A [message another session sends](https://code.claude.com/docs/en/cross-session-messaging.md) to your main conversation

`UserPromptSubmit` hooks have a default timeout of 30 seconds for `command`, `http`, and `mcp_tool` types, shorter than the 600-second default for those types on most other events. Because this hook runs before every prompt and blocks model processing until it completes, a stuck hook stalls the session. If your hook needs more time, set the `timeout` field in the hook entry.

Apart from a command hook you run with [`async: true`](hooks.md#run-hooks-in-the-background), a `UserPromptSubmit` command, HTTP, or MCP tool hook that reaches its timeout is canceled and its output, including any `additionalContext`, is discarded. The prompt still reaches Claude without that context. To block the prompt instead, set [`onFailure: "block"`](hooks.md#block-the-action-when-a-hook-fails) on a command or HTTP hook. The transcript shows a notice naming the hook, the timeout that fired, and that the output was discarded.

#### `Esc` during a prompt check

If you press `Esc` or interrupt the session while hooks are still checking a prompt, the check stops and the prompt doesn't reach Claude. Text you typed at the terminal returns to the prompt input, and the hooks check it again when you resend it.

A hook can block the prompt at the same moment you interrupt. The prompt then stays blocked: you see that hook's [block message](#what-a-blocked-prompt-leaves-behind), and the text doesn't return to the input.

#### UserPromptSubmit input

In addition to the [common input fields](hooks.md#common-input-fields), UserPromptSubmit hooks receive the `prompt` field containing the submitted text. Pasted content that collapsed to a `[Pasted text #N]` placeholder arrives expanded in place. In sessions where Claude Code [marks pasted text for Claude](https://code.claude.com/docs/en/terminal-config.md#how-claude-treats-pasted-text), that expanded content sits between a `<pasted_content id="…">` line and a `</pasted_content id="…">` line, so account for those lines if your hook parses the prompt.

UserPromptSubmit hooks also receive `session_title` when the session has a custom title, with the same meaning as the [SessionStart `session_title` field](#sessionstart-input).

When the prompt is a [skill](https://code.claude.com/docs/en/skills.md) or custom command you typed, such as `/deploy staging`, the hook receives that line as you typed it rather than the expanded skill content. If the hook blocks the prompt, the command doesn't run, so shell commands the skill [injects with `` !`<command>` ``](https://code.claude.com/docs/en/skills#inject-dynamic-context) don't run either. To match on the command's name or arguments instead, use [UserPromptExpansion](#userpromptexpansion).

#### UserPromptSubmit decision control

`UserPromptSubmit` hooks can control whether a submitted prompt is processed and add context. All [JSON output fields](hooks.md#json-output) are available.

There are two ways to add context to the conversation on exit code 0:

* **Plain text stdout**: Claude Code adds stdout it [treats as plain text](hooks.md#exit-code-0) to Claude's context
* **JSON with `additionalContext`**: use the JSON format below for more control. The `additionalContext` field is added as context

Neither channel produces a visible transcript entry. Plain stdout and the `additionalContext` value are each injected as a system reminder that starts with the hook's name; Claude reads both. To confirm delivery, check the [debug log](hooks.md#debug-hooks).

To block a prompt, return a JSON object with `decision` set to `"block"`:

| Field | Description |
| :- | :- |
| `decision` | `"block"` stops the prompt before it reaches Claude. Omit to allow the prompt to proceed |
| `reason` | Shown to the user when `decision` is `"block"`. Not added to context |
| `additionalContext` | String added to Claude's context alongside the submitted prompt. See [Add context for Claude](hooks.md#add-context-for-claude) |
| `sessionTitle` | Sets the session title. Use to name sessions automatically based on the prompt content |
| `suppressOriginalPrompt` | If `true` when the hook blocks the prompt, leaves the prompt text out of the block message. See [What a blocked prompt leaves behind](#what-a-blocked-prompt-leaves-behind) |

A hook that blocks by exiting 2 routes the same way as `reason`: the block message shows the stderr text to the user, and it isn't added to context.

```json theme={null}
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here",
    "sessionTitle": "My session title",
    "suppressOriginalPrompt": true
  }
}
```

#### What a blocked prompt leaves behind

A blocked prompt never reaches Claude, but its text isn't removed everywhere. By default the block message shown to the user ends with `Original prompt:` followed by the submitted text, and Claude Code writes that message to the session's transcript file on disk. To leave the text out of the message, print JSON with `"suppressOriginalPrompt": true` inside `hookSpecificOutput`. This works whether the hook blocks with `decision: "block"` or by exiting 2.

`suppressOriginalPrompt` changes only the block message. The submitted text can still appear in local files such as the session transcript and your prompt history, so a blocking hook isn't a way to keep a secret off disk. To limit or remove those files, see [Plaintext storage](https://code.claude.com/docs/en/claude-directory.md#plaintext-storage) and [Clear local data](https://code.claude.com/docs/en/claude-directory.md#clear-local-data).

### UserPromptExpansion

Runs when a user-typed command expands into a prompt before reaching Claude. Use this to block specific commands from direct invocation, inject context for a particular skill, or log which commands users invoke. For example, a hook matching `deploy` can block `/deploy` unless an approval file is present, or a hook matching a review skill can append the team's review checklist as `additionalContext`.

This event covers the path `PreToolUse` doesn't: a `PreToolUse` hook matching the `Skill` tool fires only when Claude calls the tool, but typing `/skillname` directly bypasses `PreToolUse`. `UserPromptExpansion` fires on that direct path.

Matches on `command_name`. Leave the matcher empty to fire on every prompt-type command.

#### UserPromptExpansion input

In addition to the [common input fields](hooks.md#common-input-fields), UserPromptExpansion hooks receive `expansion_type`, `command_name`, `command_args`, `command_source` (such as `"plugin"`), and the original `prompt` string. The `expansion_type` field is `slash_command` for skill and custom commands, or `mcp_prompt` for MCP server prompts.

#### UserPromptExpansion decision control

`UserPromptExpansion` hooks can block the expansion or add context. All [JSON output fields](hooks.md#json-output) are available.

| Field | Description |
| :- | :- |
| `decision` | `"block"` prevents the command from expanding. Omit to allow it to proceed |
| `reason` | Shown to the user when `decision` is `"block"` |
| `additionalContext` | String added to Claude's context alongside the expanded prompt. See [Add context for Claude](hooks.md#add-context-for-claude) |

A hook that blocks by exiting 2 routes the same way as `reason`: the block message shows the stderr text to the user.

```json theme={null}
{
  "decision": "block",
  "reason": "This slash command is not available",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptExpansion",
    "additionalContext": "Additional context for this expansion"
  }
}
```

### MessageDisplay

Runs while an assistant message streams to the screen. Claude Code displays the message in increments: each time a batch of newly completed lines is ready to render, the hook runs once with those lines and Claude Code renders the hook's replacement text in their place. A long message produces several calls; a short message may produce only one.

Use MessageDisplay to:

* strip markdown for a minimal display
* redact API keys or internal hostnames from Claude's responses

Claude Code holds each batch until your hook returns, so keep the hook fast. If the hook fails or times out, Claude Code displays the original text. The default timeout for this event is 10 seconds; if your hook needs more time, set the `timeout` field in the hook entry.

MessageDisplay is display-only: the replacement text changes only what is rendered on screen. The transcript and what Claude sees keep the original text, so Claude never sees the replacement, and verbose mode shows the original. The hook receives assistant message text only, so tool results and the text you type render unchanged.

MessageDisplay doesn't support matchers and fires for every assistant message that streams text; messages with no text, such as tool-call-only responses, don't trigger it.

In non-interactive runs, including Agent SDK queries and `claude -p`, MessageDisplay runs once per assistant message instead of once per batch of lines. The single call arrives after the message completes and carries the full message text: `index` is `0`, `final` is `true`, and `delta` holds the entire message. A hook that collects the `delta` text for each message receives the same total text in both modes.

#### MessageDisplay input

In addition to the [common input fields](hooks.md#common-input-fields), MessageDisplay hooks receive identifiers for the turn and message, the position of this call within the message, and the new text in `delta`. Batch boundaries depend on how the text streams, so use `index` and `final` to track progress through a message rather than expecting lines to be grouped a particular way.

| Field | Description |
| :- | :- |
| `turn_id` | UUID of the current turn |
| `message_id` | UUID of the assistant message being displayed. Stable across every batch of the same message. This is not the API `msg_…` id, so it can't be correlated with transcript message ids |
| `index` | Zero-based index of this batch within the message |
| `final` | `true` on the message's last batch. Each message has exactly one final batch |
| `delta` | The newly completed lines since the prior batch, terminating newlines included. Always whole lines, except the final batch which may end mid-line. In interactive runs, the final batch's delta is empty when the message ends on a newline, so treat `final`, not a non-empty delta, as the end-of-message signal. In Agent SDK and `claude -p` runs, the single call carries the entire message |

#### MessageDisplay output

In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, MessageDisplay hooks can return `displayContent` to replace the delta on screen:

| Field | Description |
| :- | :- |
| `displayContent` | Text displayed in place of the delta. Omit it to display the original |

MessageDisplay hooks have no decision control. They can't block the message or change what is stored in the transcript or sent to Claude. Claude Code acts on `displayContent` from their JSON output and discards `systemMessage` and `continue`.

> **Official example**: [MessageDisplay output](https://code.claude.com/docs/en/hooks#messagedisplay-output) strips bold markers and inline-code backticks from each batch, in Bash and PowerShell. The Bash version is one line: `jq '{hookSpecificOutput: {hookEventName: "MessageDisplay", displayContent: (.delta | gsub("\\*\\*"; "") | gsub("`"; ""))}}'`.

**Key facts:** `displayContent` goes inside `hookSpecificOutput`, next to `"hookEventName": "MessageDisplay"`. Batches with no markdown pass through unchanged. If the script fails, for example because `jq` is missing, Claude Code displays the original text and notes the failure only in [debug output](hooks.md#debug-hooks), not in the session.

### PreToolUse

Runs after Claude creates tool parameters and before processing the tool call. Matches on any tool name except `EndConversation`: built-in tools such as `Bash`, `PowerShell`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `Workflow`, `WebFetch`, `WebSearch`, `AskUserQuestion`, and `ExitPlanMode`, and any [MCP tool names](hooks.md#match-mcp-tools).

To run a hook when a specific file changes on disk, whatever wrote it, use [FileChanged](#filechanged) instead of matching file-editing tools by name. Unlike PreToolUse, Claude Code runs FileChanged hooks after the change, and they have no decision control, so they can't block the write.

> [!WARNING]
>
> PreToolUse runs only when Claude calls a tool. By default, files you [reference with `@` in your prompt](https://code.claude.com/docs/en/common-workflows#reference-files-and-directories) are added without any tool call. Claude Code inserts their contents while building the prompt, so no PreToolUse hook fires for them, including hooks matching `Read`. PreToolUse also doesn't fire for [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior).
>
> You can block specific paths from `@` references, or turn the insertion off:
>
> * **Block specific paths**: add a [`Read` deny rule](https://code.claude.com/docs/en/permissions#read-and-edit) for them
> * **Turn the insertion off**: set [`CLAUDE_CODE_DISABLE_FILE_MENTIONS=1`](https://code.claude.com/docs/en/env-vars#variables) in your shell, user settings, or managed settings. Claude then gets the mentioned paths with a note to read them using its file tools. If it does, your matching PreToolUse hooks run. The variable requires Claude Code v2.1.299 or later, and Claude Code ignores it in project and local settings.

Use [PreToolUse decision control](#pretooluse-decision-control) to allow, deny, ask, or defer the tool call.

#### PreToolUse input

In addition to the [common input fields](hooks.md#common-input-fields), PreToolUse hooks receive `tool_name`, `tool_input`, and `tool_use_id`.

For an [MCP tool](hooks.md#match-mcp-tools), the input also carries `mcp_server`, an object with the server's `name` and a `source` that says where the server's definition came from. The `source` values include `plugin`, `sdk`, and configuration scopes such as `user` and `project`. [`McpServerProvenance`](https://code.claude.com/docs/en/agent-sdk/typescript#mcpserverprovenance) in the Agent SDK reference lists them all and says how to treat one you don't recognize. Base trust decisions on `source` rather than on `name` or the `mcp__<server>__` tool-name prefix. The `mcp_server` field requires Claude Code v2.1.274 or later.

For the file tools `Write`, `Edit`, and `Read`, `tool_input.file_path` is always absolute:

* Claude Code expands `~` and relative paths before hooks run, so a hook that matches on paths can't be bypassed via `~` or a relative spelling of the same path
* On Windows, the path arrives with backslash separators, even when your hook runs under Git Bash where `$PWD` looks like `/c/project`
* A comparison written with forward slashes, such as a `/src/` check, never matches a backslash path, and the tool call proceeds as if the hook had nothing to block
* Normalize separators before comparing: `FILE_PATH="${FILE_PATH//\\//}"` in Bash, or `file_path.replace("\\", "/")` in Python, then match a path segment such as `/src/` rather than anchoring with `^`, since the path is absolute

A `Write` call on Windows delivers:

```json theme={null}
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "C:\\project\\src\\index.ts",
    "content": "..."
  },
  ...
}
```

The `tool_input` fields depend on the tool:

##### Bash

Executes shell commands.

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `command` | string | `"npm test"` | The shell command to execute |
| `description` | string | `"Run test suite"` | Optional description of what the command does |
| `timeout` | number | `120000` | Optional timeout in milliseconds. Values above the [maximum](https://code.claude.com/docs/en/tools-reference.md#bash-tool-behavior) are reduced to the maximum rather than rejected |
| `run_in_background` | boolean | `false` | Whether to run the command in background |

When a Bash command changes files in a Git repository, Claude Code can record what changed. It records the changes in every permission mode when the [`bashEditDiffEnabled`](https://code.claude.com/docs/en/settings-reference#basheditdiffenabled) setting turns recording on; that setting's entry says which files can set it. Otherwise it records them only in auto mode and `bypassPermissions` mode, and only when Claude Code directs Claude to edit files through Bash. Set `bashEditDiffEnabled` to `false` to turn the recording off. Background commands and read-only commands carry no diff.

Your [PostToolUse hook](#posttooluse) then receives the changed files in `tool_response.bashEditDiff`. The list covers what changed under the repository while the command ran. Files that Git ignores and files in submodules aren't listed. Requires Claude Code v2.1.269 or later.

> [!NOTE]
>
> The list is best effort and in public beta. Claude Code can miss a change, include a file that another process changed at the same time, or stop at its size limits. The field shape may change. Use the list to find what to review, not to enforce a policy.

`changedFiles` and `files` list what the command changed; the remaining fields say how complete and how reliable that list is.

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `changedFiles` | array | `["/path/to/src/app.ts"]` | Absolute paths of the files the command changed, at most 200. Present whenever `files` holds a diff or `moreFiles` is above zero |
| `files` | array | `[{"filePath": "/path/to/src/app.ts", "hunks": [...]}]` | Diffs of up to 5 changed files, for display. `created` or `deleted` is `true` for a file the command added or removed |
| `moreFiles` | number | `2` | Count of changed files with no diff in `files` |
| `unavailable` | boolean | `true` | Set when the diff is incomplete or couldn't be taken |
| `skipped` | boolean | `true` | Set for a Git command that moves the working tree, such as `git checkout` or `git stash`, so Claude Code takes no diff |
| `shared` | boolean | `true` | Set when another Bash tool call, such as a subagent's, ran in the same repository at the same time, so some listed changes may be that command's |

##### PowerShell

Executes PowerShell commands. See the [PowerShell tool](https://code.claude.com/docs/en/tools-reference.md#powershell-tool) for availability by platform.

The fields match the Bash tool, with the command string in `command`:

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `command` | string | `"Get-ChildItem -Recurse"` | The PowerShell command to execute |
| `description` | string | `"List files recursively"` | Optional description of what the command does |
| `timeout` | number | `120000` | Optional timeout in milliseconds |
| `run_in_background` | boolean | `false` | Whether to run the command in background |

Match `Bash|PowerShell` in hooks that inspect shell commands, so they cover both tools:

* On Windows, wherever the PowerShell tool is enabled, Claude treats PowerShell as the primary shell and routes shell commands through it.
* On Windows without Git Bash, the tool is enabled automatically and Claude Code doesn't register the Bash tool at all.
* A hook that matches only `Bash` never fires there.

##### Write, Edit, Read, Glob and Grep

These tools take their usual parameters, and `file_path` is always absolute:

* **Write**: `file_path`, `content`
* **Edit**: `file_path`, `old_string`, `new_string`, `replace_all` (boolean)
* **Read**: `file_path`, optional `offset` (line to start from) and `limit` (number of lines)
* **Glob**: `pattern`, optional `path` (defaults to the working directory)
* **Grep**: `pattern`, optional `path` (a file or a directory), `glob`, `output_mode` (`"content"`, `"files_with_matches"` or `"count"`, default `"files_with_matches"`), `-i` and `multiline` (booleans)

Read the official tables under [PreToolUse input](https://code.claude.com/docs/en/hooks#pretooluse-input) for the field types and examples.

##### WebFetch

Fetches and processes web content.

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `url` | string | `"https://example.com/api"` | URL to fetch content from |
| `prompt` | string | `"Extract the API endpoints"` | Prompt to run on the fetched content |
| `offset` | number | `100000` | Optional number of characters to skip from the start of the page. Claude sets it to keep reading a long page. Requires Claude Code v2.1.290 or later |

##### WebSearch

Searches the web.

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `query` | string | `"react hooks best practices"` | Search query |
| `allowed_domains` | array | `["docs.example.com"]` | Optional: only include results from these domains |
| `blocked_domains` | array | `["spam.example.com"]` | Optional: exclude results from these domains |
| `mode` | string | `"extended"` | Optional: search type. `"standard"` requests a lighter search and `"extended"` the full search. Some sessions don't send `mode`, and a call without it runs the full search. Requires Claude Code v2.1.282 or later |

##### Agent

Spawns a [subagent](https://code.claude.com/docs/en/sub-agents.md).

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `prompt` | string | `"Find all API endpoints"` | The task for the agent to perform |
| `description` | string | `"Find API endpoints"` | Short description of the task |
| `subagent_type` | string | `"Explore"` | Type of specialized agent to use |
| `model` | string | `"sonnet"` | Optional model alias to override the default |

When a foreground Agent call completes, your [PostToolUse hook](#posttooluse) receives the subagent's result and run telemetry in `tool_response`. Read these fields to inspect the run; for token and cost rollups across subagents, use the [token and cost counters](https://code.claude.com/docs/en/monitoring-usage.md#token-counter) filtered to `query_source` `"subagent"`, since `totalTokens` and `usage` cover the final request only:

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `status` | string | `"completed"` | `"completed"` for foreground subagents, `"async_launched"` for background subagents. For which subagents run each way, see [Run subagents in foreground or background](https://code.claude.com/docs/en/sub-agents.md#run-subagents-in-foreground-or-background) |
| `agentId` | string | `"a4d2c8f1e0b3a297"` | Identifier for the subagent run |
| `content` | array | `[{"type": "text", "text": "Found 12 endpoints..."}]` | The subagent's final text blocks, or, for a subagent whose report goes through `SubagentHandback`, a short note about that hand-back in their place |
| `resolvedModel` | string | `"claude-sonnet-4-5"` | Model the subagent started on, which may differ from the requested model |
| `modelsUsed` | array | `["claude-sonnet-4-5", "claude-haiku-4-5"]` | Models used in order, with consecutive repeats collapsed; set only when the model was swapped mid-run |
| `totalTokens` | number | `12450` | Token count from the subagent's final API request: input, output, and cache tokens combined. This isn't a total across the whole run |
| `totalDurationMs` | number | `48211` | Wall-clock duration of the subagent run |
| `totalToolUseCount` | number | `7` | Count of tool calls the subagent made |
| `usage` | object | `{"input_tokens": 8320, ...}` | Per-type token breakdown of the final API request: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` |

On Claude Code v2.1.271 or later, a subagent that runs with the [`SubagentHandback`](https://code.claude.com/docs/en/tools-reference) tool, which Claude Code provides in [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), delivers its report through that tool rather than returning it as text. The `content` field of its `completed` result then carries a short note about that hand-back rather than the report itself. To read the report, match a `PreToolUse` or `PostToolUse` hook on `SubagentHandback` and read `tool_input.message`.

For background subagents, the tool returns when the task moves to the background, so `tool_response` carries no usage fields: a background launch returns immediately, and a foreground task that Claude Code backgrounds mid-run returns at that transition. It has `status: "async_launched"`, `agentId`, `description`, `prompt`, `outputFile`, and `resolvedModel`.

On a `completed` response, `resolvedModel` names the model the subagent started on, which can differ from the `model` value in `tool_input`, such as when `availableModels` or another override applies. On an `async_launched` response, `resolvedModel` names the model in use when the agent moved to the background, so a swap that happened before backgrounding is reflected there.

##### AskUserQuestion

Asks the user one to four multiple-choice questions.

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `questions` | array | `[{"question": "Which framework?", "header": "Framework", "options": [{"label": "React", "description": "Component library"}, {"label": "Vue", "description": "Progressive framework"}], "multiSelect": false}]` | Questions to present, each with a `question` string, short `header`, `options` array, and optional `multiSelect` flag |
| `answers` | object | `{"Which framework?": "React"}` | Optional. Maps question text to the selected option label. Multi-select answers join labels with commas. Claude doesn't set this field; supply it via `updatedInput` to answer programmatically |

##### ExitPlanMode

Presents a plan and asks the user to approve it before Claude leaves [plan mode](https://code.claude.com/docs/en/permission-modes.md#analyze-before-you-edit-with-plan-mode). Claude writes the plan to a file on disk before calling the tool, so the literal `tool_input` from the model is typically empty. Claude Code injects the plan content and file path before passing the input to hooks.

| Field | Type | Example | Description |
| :- | :- | :- | :- |
| `plan` | string | `"## Refactor auth\n1. Extract..."` | Plan content in Markdown. Injected from the plan file on disk |
| `planFilePath` | string | `"/Users/.../plans/refactor-auth.md"` | Path to the plan file. Injected |
| `allowedPrompts` | array | `[{"tool": "Bash", "prompt": "run tests"}]` | Deprecated. Claude Code accepts the field but ignores it. Before v2.1.205, it carried prompt-based permissions Claude requested to implement the plan |

In `PostToolUse`, `tool_response` is an object with `plan` and `filePath` fields holding the approved plan, plus internal status flags. Read `tool_response.plan` for the plan content rather than re-reading the file from disk.

#### PreToolUse decision control

`PreToolUse` hooks can control whether a tool call proceeds. Unlike other hooks that use a top-level `decision` field, PreToolUse returns its decision inside a `hookSpecificOutput` object. This gives it richer control: four outcomes (allow, deny, ask, or defer) plus the ability to modify tool input before execution. To allow or rewrite a Monitor command, see [Match Monitor commands](hooks.md#match-monitor-commands).

| Field | Description |
| :- | :- |
| `permissionDecision` | `"allow"` skips the permission prompt, except for [actions no mode auto-approves](https://code.claude.com/docs/en/permission-modes.md#actions-no-mode-auto-approves) and [reads from network paths](https://code.claude.com/docs/en/permissions.md#network-paths). It doesn't skip approval for calls to [tools an Agent SDK app marks `always_ask`](https://code.claude.com/docs/en/agent-sdk/custom-tools#require-approval-for-specific-tools) either, unless the [permission mode approves the call](https://code.claude.com/docs/en/agent-sdk/typescript.md#permission-modes-that-can-approve-an-always_ask-call). `AskUserQuestion` and `ExitPlanMode` need [`updatedInput` paired with `"allow"`](https://code.claude.com/docs/en/hooks#allow-with-updatedinput). For plan mode, see [Hook approvals in plan mode](https://code.claude.com/docs/en/permissions.md#hook-approvals-in-plan-mode). `"deny"` prevents the tool call. `"ask"` prompts the user to confirm. `"defer"` ends the turn so the tool can be resumed later, and requires [non-interactive mode](https://code.claude.com/docs/en/hooks#defer-a-tool-call-for-later) with the `-p` flag. [Deny and ask rules](https://code.claude.com/docs/en/permissions.md#manage-permissions) are still evaluated regardless of what the hook returns |
| `permissionDecisionReason` | For `"ask"`, shown to the user in the permission prompt. When Claude Code [denies the call](https://code.claude.com/docs/en/headless.md#turn-off-permission-prompts-in-unattended-runs) in a `-p` run where no one can answer that prompt, Claude reads the reason in the tool result instead. For `"deny"`, shown to Claude. For `"allow"` and `"defer"`, written to the [debug log](hooks.md#debug-hooks) only |
| `updatedInput` | Modifies the tool's input parameters before execution. Replaces the entire input object, so include unchanged fields alongside modified ones. Claude Code evaluates permission rules and a Bash command's [auto-background eligibility](https://code.claude.com/docs/en/tools-reference.md#foreground-commands-that-move-to-the-background) against the input your hook returns, not the input Claude sent. Combine with `"allow"` to auto-approve, or `"ask"` to show the modified input to the user. For `"defer"`, ignored. With no `permissionDecision`, [auto mode can deny the changed call](#pretooluse-updatedinput-in-auto-mode) |
| `additionalContext` | String added to Claude's context alongside the tool result. Ignored when `permissionDecision` is `"defer"`. See [Add context for Claude](hooks.md#add-context-for-claude) |

When multiple PreToolUse hooks return different decisions, precedence is `deny` > `defer` > `ask` > `allow`.

A hook that blocks by exiting 2 routes the same way as `"deny"`: Claude sees the stderr message as the denial reason.

When a hook returns `"ask"`, the permission prompt displayed to the user includes a label identifying where the hook came from: `[settings]` for a hook from any settings file or from agent frontmatter, `[plugin:<name>]` for a plugin's hook, or `[skill]` for a hook from skill frontmatter. This helps users understand which configuration source is requesting confirmation.

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "My reason here",
    "updatedInput": {
      "field_to_modify": "new value"
    },
    "additionalContext": "Current environment: production. Proceed with caution."
  }
}
```

> [!NOTE]
>
> PreToolUse previously used top-level `decision` and `reason` fields, but these are deprecated for this event. Use `hookSpecificOutput.permissionDecision` and `hookSpecificOutput.permissionDecisionReason` instead. The deprecated values `"approve"` and `"block"` map to `"allow"` and `"deny"` respectively. Other events like PostToolUse and Stop continue to use top-level `decision` and `reason` as their current format.

#### PreToolUse `updatedInput` in auto mode

When your hook returns `updatedInput` with no `permissionDecision` in [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), Claude Code can deny the changed call. [The server reviewed](https://code.claude.com/docs/en/permission-modes.md#server-side-classifier-review) the input Claude wrote, not the input your hook returned. In interactive terminal sessions and VS Code sessions on a direct connection to the Anthropic API, the denial includes this text:

```text theme={null}
a hook changed this call's input after auto mode reviewed it
```

After a denial with this text, Claude can issue the changed call again so that the server reviews it. If Claude repeats the changed input exactly in its next response, your hook still runs:

* It can deny the call or send it to the permission prompt
* Any `updatedInput` it returns is dropped, so what runs is what the server reviewed

You don't need to change your hook for this denial unless [Claude tells you in its reply that auto mode couldn't check the call](https://code.claude.com/docs/en/errors.md#hook-changed-input-after-review).

In the sessions that show this text, a [`command` hook](hooks.md#command-hook-fields) in settings or a plugin's hooks file can change Bash, PowerShell, Monitor, Edit, Write, and NotebookEdit calls without this denial. The denial can still appear, such as when any hook changed an earlier call in the same Claude response or a Bash command asks to run outside the sandbox.

#### PreToolUse `ask` decisions in auto mode

In [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode), a PreToolUse hook's `"ask"` normally sends the tool call to the permission prompt, and the [classifier](https://code.claude.com/docs/en/permission-modes.md#how-the-classifier-evaluates-actions) doesn't decide it. Some calls take a different path:

* **Calls that Claude Code's own checks flag too**: these include writes to [protected paths](https://code.claude.com/docs/en/permission-modes.md#protected-paths) and commands that ask to [run outside the sandbox](https://code.claude.com/docs/en/sandboxing.md#the-unsandboxed-retry-escape-hatch). The classifier can deny one of these calls before any prompt appears. If it approves, the call normally still goes to the prompt.
* **`SubagentHandback` calls**: this tool delivers a subagent's report. No prompt appears for it, and the call runs even if the classifier objects.

To stop a `SubagentHandback` call, return `"deny"`. Claude Code then tells the subagent, up to three times, that its report wasn't delivered and to call the tool again. If your hook keeps denying, the subagent ends without delivering a report through this tool, and the conversation waiting on it gets a note saying so.

### PermissionRequest

Runs when Claude Code is about to ask you for permission to use a tool. In sessions that can't show a prompt, such as background subagents in [non-interactive mode](https://code.claude.com/docs/en/headless.md), Claude Code still runs these hooks, and if no hook returns a decision, it denies the tool call. For a call that reaches a `--permission-prompt-tool` or the Agent SDK's [`canUseTool` callback](https://code.claude.com/docs/en/agent-sdk/permissions), the hooks run alongside your host, and whichever decides first applies.
Use [PermissionRequest decision control](#permissionrequest-decision-control) to allow or deny on behalf of the user.

Use this event when you need a signal the moment Claude asks for permission to use a tool. Claude Code runs a [Notification](#notification) hook with the `permission_prompt` type only after the prompt has waited about six seconds.

Claude Code doesn't run PermissionRequest hooks for a sandboxed command's [network request](https://code.claude.com/docs/en/sandboxing.md#network-isolation). To get a signal for that prompt, use the `permission_prompt` notification type.

Matches on tool name, same values as PreToolUse.

#### PermissionRequest input

PermissionRequest hooks receive `tool_name` and `tool_input` fields like PreToolUse hooks, but without `tool_use_id`. For an MCP tool, they also receive the [`mcp_server`](#pretooluse-input) object. An optional `permission_suggestions` array contains the [permission updates](#permission-update-entries) Claude Code suggests for this request, such as adding an allow rule or changing the permission mode.

The `permission_suggestions` array isn't an exact list of the options you see, because each permission dialog builds its own options. Some dialogs, such as the one for file edits, don't read the array at all and derive their options from the request itself. A dialog that does read it can still withhold an option whose suggestion stays in the array, for example when [`allowManagedPermissionRulesOnly`](https://code.claude.com/docs/en/settings-reference#allowmanagedpermissionrulesonly) hides rule-saving options. It can also offer options that have no suggestion entry, such as [**Yes, and switch to auto mode**](https://code.claude.com/docs/en/permission-modes.md#switch-permission-modes), which changes the permission mode directly rather than through a permission update.

PreToolUse hooks run before every tool call, whether or not it needs permission. PermissionRequest hooks run only when Claude Code is about to ask you for permission, or when it would otherwise auto-deny a call that can't prompt. Neither event fires for [`EndConversation`](https://code.claude.com/docs/en/tools-reference#endconversation-tool-behavior).

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf node_modules",
    "description": "Remove node_modules directory"
  },
  "permission_suggestions": [
    {
      "type": "addRules",
      "rules": [{ "toolName": "Bash", "ruleContent": "rm -rf node_modules" }],
      "behavior": "allow",
      "destination": "localSettings"
    }
  ]
}
```

#### PermissionRequest decision control

`PermissionRequest` hooks can allow or deny permission requests. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, your hook script can return a `decision` object with these event-specific fields:

| Field | Description |
| :- | :- |
| `behavior` | `"allow"` grants the permission, `"deny"` denies it. [Deny and ask rules](https://code.claude.com/docs/en/permissions.md#manage-permissions) are still evaluated, so a hook returning `"allow"` doesn't override a matching deny rule |
| `updatedInput` | For `"allow"` only: modifies the tool's input parameters before execution. Replaces the entire input object, so include unchanged fields alongside modified ones. The modified input is re-evaluated against deny and ask rules. `AskUserQuestion` and `ExitPlanMode` [need this field](https://code.claude.com/docs/en/hooks#allow-with-updatedinput) |
| `updatedPermissions` | For `"allow"` only: array of [permission update entries](#permission-update-entries) to apply, such as adding an allow rule or changing the session permission mode |
| `message` | For `"deny"` only: tells Claude why the permission was denied |
| `interrupt` | For `"deny"` only: if `true`, stops Claude |

To allow or rewrite a Monitor command, see [Match Monitor commands](hooks.md#match-monitor-commands).

A hook that exits 2 without a `decision` object leaves the permission flow unchanged, and its stderr is discarded. To grant or deny the request, return the `decision` object.

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}
```

#### Permission update entries

The `updatedPermissions` output field and the [`permission_suggestions` input field](#permissionrequest-input) both use the same array of entry objects. Each entry has a `type` that determines its other fields, and a `destination` that controls where the change is written.

| `type` | Fields | Effect |
| :- | :- | :- |
| `addRules` | `rules`, `behavior`, `destination` | Adds permission rules. `rules` is an array of `{toolName, ruleContent?}` objects. Omit `ruleContent` to match the whole tool. `behavior` is `"allow"`, `"deny"`, or `"ask"` |
| `replaceRules` | `rules`, `behavior`, `destination` | Replaces all rules of the given `behavior` at the `destination` with the provided `rules` |
| `removeRules` | `rules`, `behavior`, `destination` | Removes matching rules of the given `behavior` |
| `setMode` | `mode`, `destination` | Changes the permission mode. Valid modes are `default`, `auto`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan`, and `manual` as an alias for `default` |
| `addDirectories` | `directories`, `destination` | Adds working directories. `directories` is an array of path strings |
| `removeDirectories` | `directories`, `destination` | Removes working directories |

> [!NOTE]
>
> `setMode` with `bypassPermissions` only takes effect if you launched the session with bypass mode already available: `--dangerously-skip-permissions`, `--permission-mode bypassPermissions`, `--allow-dangerously-skip-permissions`, or `permissions.defaultMode: "bypassPermissions"` in [user, `--settings`, or managed settings](https://code.claude.com/docs/en/settings-reference#permissions-defaultmode). Otherwise the update is a no-op. The update is also a no-op when [`permissions.disableBypassPermissionsMode`](https://code.claude.com/docs/en/permissions#managed-settings) disables the mode, or when the session starts in [restricted mode](https://code.claude.com/docs/en/cli-reference.md#cli-flags).
>
> `bypassPermissions` is never persisted as `defaultMode` regardless of `destination`.

The `destination` field on every entry determines whether the change stays in memory or persists to a settings file.

| `destination` | Writes to |
| :- | :- |
| `session` | in-memory only, discarded when the session ends |
| `localSettings` | `.claude/settings.local.json` |
| `projectSettings` | `.claude/settings.json` |
| `userSettings` | `~/.claude/settings.json` |

A hook can echo one of the `permission_suggestions` it received as its own `updatedPermissions` output.

### PostToolUse

Runs immediately after a tool completes successfully.

Matches on tool name, same values as PreToolUse.

Match more broadly when the tool name isn't the right filter:

* To run a hook after any tool completes successfully, omit the `matcher` or set it to `"*"`. Your hook can then discover what changed itself, for example by running `git status --porcelain`, which also lists untracked files that `git diff` misses. For tool calls that fail, add the same hook under [PostToolUseFailure](#posttoolusefailure).
* To run a hook when a specific file changes on disk, whatever wrote it, use [FileChanged](#filechanged). Claude Code doesn't run a `PostToolUse` hook matching `Edit|Write` when a `Bash` command or a process outside Claude Code rewrites the same file.

#### PostToolUse after an interrupt

If a `PostToolUse` hook stops early after you send a message or interrupt during a tool call, check whether you pressed `Ctrl+Enter`, `Enter`, or `Esc`:

* **`Ctrl+Enter`**: if pressing it [ends the turn](https://code.claude.com/docs/en/interactive-mode.md#when-claude-code-sends-what-you-queued) while a tool is running and the tool finishes, your `PostToolUse` hooks run on its result and have 10 seconds to finish. The key acts as `Esc` if you queued a `!` command ahead of your messages or background tasks are disabled, for example with [`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`](https://code.claude.com/docs/en/env-vars#variables).
* **`Enter`**: a message you queue with `Enter` doesn't interrupt the turn, so the hooks keep their usual `timeout`.
* **`Esc`**: you cancel the hooks at once, so send the message with `Enter` or `Ctrl+Enter` when the hooks have to run.

When the 10 seconds are up, Claude Code kills a command hook that is still running, whatever its [`timeout`](hooks.md#common-fields). To let a longer command hook finish, run it with [`async: true`](hooks.md#run-hooks-in-the-background), which means the hook can't block or rewrite the result.

Before v2.1.319, the hooks didn't start after you interrupted the turn with a message, and a running hook was stopped.

#### PostToolUse input

`PostToolUse` hooks fire after a tool has already executed successfully. The input includes both `tool_input`, the arguments sent to the tool, and `tool_response`, the result it returned. The exact schema for both depends on the tool. File-tool `tool_input` paths arrive in the same format as for [PreToolUse](#pretooluse-input): always absolute, with the platform's native separators, so backslashes on Windows. For an MCP tool, the input also carries the [`mcp_server`](#pretooluse-input) object.

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "type": "create"
  },
  "tool_use_id": "toolu_01ABC123...",
  "duration_ms": 12
}
```

| Field | Description |
| :- | :- |
| `duration_ms` | Optional. Tool execution time in milliseconds. Excludes time spent in permission prompts and PreToolUse hooks |

#### PostToolUse decision control

`PostToolUse` hooks can provide feedback to Claude after tool execution. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, your hook script can return these event-specific fields:

| Field | Description |
| :- | :- |
| `decision` | `"block"` adds the `reason` next to the tool result. Claude still sees the original output; to replace it, use `updatedToolOutput` |
| `reason` | Explanation shown to Claude when `decision` is `"block"` |
| `additionalContext` | String added to Claude's context alongside the tool result. See [Add context for Claude](hooks.md#add-context-for-claude) |
| `classifierContext` | Short note about this call's result for the [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode) classifier rather than for Claude. See [Annotate a result for the auto mode classifier](#annotate-a-result-for-the-auto-mode-classifier). Requires Claude Code v2.1.236 or later |
| `updatedToolOutput` | Replaces the tool's output with the provided value before it is sent to Claude. The value must match the tool's output shape |
| `updatedMCPToolOutput` | Replaces the output for [MCP tools](hooks.md#match-mcp-tools) only. Prefer `updatedToolOutput`, which works for all tools |

The example below replaces the output of a `Bash` call. The replacement value matches the `Bash` tool's output shape:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude",
    "updatedToolOutput": {
      "stdout": "[redacted]",
      "stderr": "",
      "interrupted": false,
      "isImage": false
    }
  }
}
```

> [!WARNING]
>
> `updatedToolOutput` only changes what Claude sees. The tool has already run by the time the hook fires, so any files written, commands executed, or network requests sent have already taken effect. Telemetry such as OpenTelemetry tool spans and analytics events also captures the original output before the hook runs. To prevent or modify a tool call before it runs, use a [PreToolUse](#pretooluse) hook instead.
>
> The replacement value must match the tool's output shape. Built-in tools return structured objects rather than plain strings. For example, `Bash` returns an object with `stdout`, `stderr`, `interrupted`, and `isImage` fields. For built-in tools, a value that doesn't match the tool's output schema is ignored and the original output is used. MCP tool output is passed through without schema validation. Stripping error details that Claude needs can cause it to proceed on a false assumption.

#### Annotate a result for the auto mode classifier

Return `classifierContext` to send a short note about the tool call's result to the [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode) classifier rather than to Claude. The classifier [never receives tool results themselves](https://code.claude.com/docs/en/permission-modes.md#how-the-classifier-evaluates-actions), so this field is the supported way to tell it something about what a call returned before it reviews later actions. The field requires Claude Code v2.1.236 or later.

The example below tells the classifier where a query's output came from:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "classifierContext": "This query ran against the staging database, not production."
  }
}
```

How much weight the classifier gives the note depends on where you configured the hook:

* **Hooks configured in Claude Code**: for hooks from settings files, plugins, skills, and agent frontmatter, the classifier treats the note as unverified, application-provided context. The note never establishes user intent, and if it claims you approved or requested something, the classifier checks that claim against your own messages in the conversation

Claude Code applies these limits when delivering the note:

* **Length**: Claude Code caps the notes for one tool call at 2,000 characters and truncates the rest. The cap is shared across every hook that responds to that call
* **Synchronous responses only**: Claude Code ignores the field in the response of a hook that [runs in the background](hooks.md#run-hooks-in-the-background), because that response arrives after Claude Code records the tool result
* **Calls that the classifier doesn't record**: the classifier's transcript omits read-only lookups such as file reads and searches. Claude Code discards a note attached to one of those calls
* **Interaction with rewrites**: when the note describes output you're replacing with `updatedToolOutput`, return both fields in the same hook response. Claude Code drops the note if that rewrite is rejected or another hook's rewrite replaces it. Claude Code delivers a note you return without a rewrite even when another hook rewrites the output

> [!WARNING]
>
> The classifier reads content you place in `classifierContext` as information from the application hosting the session, so don't copy untrusted tool output or third-party text into it. Keep the note to a short assertion about this one call, such as a fact about its origin or a user statement about it; don't use the field to deliver unrelated messages or a stream of events.

### PostToolUseFailure

Runs when a tool that started executing fails: the tool threw an error, or an MCP tool returned an error result. Use this to log failures, send alerts, or provide corrective feedback to Claude.

Matches on tool name, same values as PreToolUse.

> [!NOTE]
>
> This event doesn't fire for tool calls rejected before execution: an unknown tool name, input that fails schema or tool-specific validation, or a permission denial. Validation rejections are returned as `tool_use_error` results and happen before hooks run, so they fire neither `PreToolUse` nor `PostToolUseFailure`. Permission denials fire `PreToolUse` but not this event; see [PermissionDenied](#permissiondenied).

#### PostToolUseFailure input

PostToolUseFailure hooks receive the same `tool_name` and `tool_input` fields as PostToolUse, along with error information as top-level fields. For an MCP tool, they also receive the [`mcp_server`](#pretooluse-input) object. For example, a failed `npm test` command might deliver:

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test",
    "description": "Run test suite"
  },
  "tool_use_id": "toolu_01ABC123...",
  "error": "Exit code 1\nError: Cannot find module 'express'",
  "is_interrupt": false,
  "duration_ms": 4187
}
```

| Field | Description |
| :- | :- |
| `error` | String describing what went wrong. The format depends on the tool that failed |
| `is_interrupt` | Optional boolean. True when the failure reached Claude Code as an abort rather than as an error the tool reported. Cancelling a running tool does not fire this hook; the tool result carries the interruption message instead |
| `duration_ms` | Optional. Tool execution time in milliseconds. Excludes time spent in permission prompts and PreToolUse hooks |

The `error` string is generally the same text Claude receives as the failed tool's result. Its format varies by tool and failure. Key your hook on `tool_name`, `is_interrupt`, and the `Exit code N` first line; treat the rest of the string as display text, not a stable format.

* For Bash and PowerShell, a command that ran and exited produces a first line `Exit code N`, then any output the command produced as one block with stdout and stderr interleaved
* A payload may also carry a bare failure message with no exit-code line, when Claude Code could not start the shell process itself
* Claude Code middle-truncates long strings around a `... [N characters truncated] ...` marker, and can insert lines of its own, such as `Command timed out after 2m 0s`

#### PostToolUseFailure decision control

`PostToolUseFailure` hooks can provide context to Claude after a tool failure. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, your hook script can return these event-specific fields:

| Field | Description |
| :- | :- |
| `additionalContext` | String added to Claude's context alongside the error. See [Add context for Claude](hooks.md#add-context-for-claude) |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUseFailure",
    "additionalContext": "Additional information about the failure for Claude"
  }
}
```

### PostToolBatch

Runs once after every tool call in a batch has resolved, before Claude Code sends the next request to the model. `PostToolUse` fires once per tool, which means it fires concurrently when Claude makes parallel tool calls. `PostToolBatch` fires exactly once with the full batch, so it is the right place to inject context that depends on the set of tools that ran rather than on any single tool. There is no matcher for this event.

#### PostToolBatch input

In addition to the [common input fields](hooks.md#common-input-fields), PostToolBatch hooks receive `tool_calls`, an array describing every tool call in the batch:

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PostToolBatch",
  "tool_calls": [
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "/.../ledger/accounts.py"},
      "tool_use_id": "toolu_01...",
      "tool_response": "1\tfrom __future__ import annotations\n2\t..."
    },
    {
      "tool_name": "Read",
      "tool_input": {"file_path": "/.../ledger/transactions.py"},
      "tool_use_id": "toolu_02...",
      "tool_response": "1\tfrom __future__ import annotations\n2\t..."
    }
  ]
}
```

`tool_response` contains the same content the model receives in the corresponding `tool_result` block. The value is a serialized string or content-block array, exactly as the tool emitted it. For `Read`, that means line-number-prefixed text rather than raw file contents. Responses can be large, so parse only the fields you need.

> [!NOTE]
>
> The `tool_response` shape differs from `PostToolUse`'s. `PostToolUse` passes the tool's structured `Output` object, such as `{filePath: "...", type: "create"}` for `Write`; `PostToolBatch` passes the serialized `tool_result` content the model sees.

#### PostToolBatch decision control

`PostToolBatch` hooks can inject context for Claude. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, your hook script can return these event-specific fields:

| Field | Description |
| :- | :- |
| `additionalContext` | Context string injected once before the next model call. See [Add context for Claude](hooks.md#add-context-for-claude) for delivery details, what to put in it, and how resumed sessions handle past values |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolBatch",
    "additionalContext": "These files are part of the ledger module. Run pytest before marking the task complete."
  }
}
```

Returning `decision: "block"` or `continue: false` stops the agentic loop before the next model call. The blocking message comes from the JSON `reason` or `stopReason`, or from stderr on exit 2. You see it as a warning in the transcript, and it stays in the conversation, so Claude sees it when the conversation continues.

### PermissionDenied

Runs when [auto mode](https://code.claude.com/docs/en/permission-modes.md#eliminate-prompts-with-auto-mode) denies a tool call, including when it denies without a classifier verdict because [a safety check separate from auto mode refused the classifier's own request](https://code.claude.com/docs/en/errors.md#auto-mode-cannot-determine-the-safety-of-an-action) or its response didn't parse. This hook only fires in auto mode: it doesn't run when you manually deny a permission dialog, when a `PreToolUse` hook blocks a call, or when a `deny` rule matches. Use it to log denials, adjust configuration, or tell the model it may retry the tool call.

Matches on tool name, same values as PreToolUse.

#### PermissionDenied input

In addition to the [common input fields](hooks.md#common-input-fields), PermissionDenied hooks receive `tool_name`, `tool_input`, `tool_use_id`, and `reason`. For an MCP tool, they also receive the [`mcp_server`](#pretooluse-input) object.

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "auto",
  "hook_event_name": "PermissionDenied",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/build",
    "description": "Clean build directory"
  },
  "tool_use_id": "toolu_01ABC123...",
  "reason": "[Irreversible Local Destruction]"
}
```

| Field | Description |
| :- | :- |
| `reason` | The denial reason. For a classifier verdict, in most sessions it names the matched rule in square brackets, such as `[Data Exfiltration]`; see [Review denials](https://code.claude.com/docs/en/auto-mode-config.md#review-denials) for the other forms. For a [no-verdict denial](#permissiondenied-decision-control), it starts with `Auto mode could not evaluate this action and is blocking it for safety`. For a denial because the classifier model was unavailable, it is the fixed text `Classifier unavailable` |

#### PermissionDenied decision control

PermissionDenied hooks can tell the model it may retry the denied tool call. Return a JSON object with `hookSpecificOutput.retry` set to `true`:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionDenied",
    "retry": true
  }
}
```

When `retry` is `true`, Claude Code adds a message to the conversation telling the model it may retry the tool call. Claude Code doesn't reverse the denial itself. If your hook doesn't return JSON, or returns `retry: false`, the denial stands and the model receives the original rejection message.

Claude Code ignores `retry: true` when the classifier produced [no verdict on the action](https://code.claude.com/docs/en/errors.md#auto-mode-cannot-determine-the-safety-of-an-action): its response didn't parse, or a safety check separate from auto mode refused the classifier's own request. For those denials, Claude Code already tells the model in the rejection message whether to retry later or move on.

### Notification

Runs when Claude Code sends notifications. Matches on notification type. Omit the matcher to run hooks for all notification types.

You receive these hook events even with desktop notifications turned off: the `preferredNotifChannel` setting, including `notifications_disabled`, changes only how you're alerted, not whether your hook runs.

| Matcher | When it fires |
| :- | :- |
| `permission_prompt` | Claude needs you to approve a tool use or a sandboxed command's [network request](https://code.claude.com/docs/en/sandboxing.md#network-isolation), and the prompt has waited about six seconds |
| `idle_prompt` | Claude finished responding about 60 seconds ago and you haven't typed since |
| `auth_success` | Authentication completes |
| `auth_storage_failure` | Your sign-in completes, but Claude Code can't save the new credentials to its [credential storage](https://code.claude.com/docs/en/authentication.md#credential-management). Fires in place of `auth_success` |
| `elicitation_dialog` | An MCP server opens an elicitation form and you haven't typed for about six seconds |
| `elicitation_url_dialog` | An MCP server asks you to open a browser URL and you haven't typed for about six seconds |
| `elicitation_complete` | An MCP server reports that a [URL-mode elicitation](#elicitation-input) is complete |
| `elicitation_response` | An MCP elicitation response is sent back to the server |
| `agent_needs_input` | A background session starts waiting on your input while [agent view](https://code.claude.com/docs/en/agent-view.md) is open in a terminal. Also fires when a terminal session shows you an [agent team teammate's terminal setup question](https://code.claude.com/docs/en/agent-teams.md#choose-a-display-mode) or auto mode's notice about [classifier request charges](https://code.claude.com/docs/en/auto-mode-classifier-billing.md) and you haven't typed for about six seconds |
| `agent_completed` | A background session finishes or fails. Fires only while [agent view](https://code.claude.com/docs/en/agent-view.md) is open in a terminal |
| `quota_auto_resume_fired` | Claude Code continues your task after a claude.ai usage limit paused it: at the reset, or sooner when something you do in Claude Code during the wait, such as adding usage credits, upgrading your plan, or switching models, makes usage available again, with the [model-setting exception](https://code.claude.com/docs/en/interactive-mode.md#wait-for-a-usage-limit-to-reset) |
| `quota_auto_resume_stale` | A claude.ai usage limit reset while your computer slept for more than about 30 minutes. Claude Code waits for you to press `Enter` instead of continuing. After a shorter sleep it continues and fires `quota_auto_resume_fired` instead |
| `quota_auto_resume_disabled` | Claude Code ends its wait for a claude.ai usage limit without continuing your task: [`autoContinueAtUsageLimit`](https://code.claude.com/docs/en/settings-reference#autocontinueatusagelimit) turned off or the reset moved more than 24 hours away during a wait Claude Code started on its own, the continued task kept hitting the limit, or the continuation was blocked before it reached the model. Doesn't fire when you press `Esc` or `Ctrl+C`, or pick **Don't continue automatically** |
| `plugin_notification` | A [mod](https://code.claude.com/docs/en/plugins/mods/api.md#show-something-without-starting-a-turn) raises a notification with `$.ui.notify`. The hook's `title` is the mod's name unless the mod set one |

The `quota_auto_resume_fired`, `quota_auto_resume_stale`, and `quota_auto_resume_disabled` types require Claude Code v2.1.234 or later. The `auth_storage_failure` type requires v2.1.288 or later.

In terminal sessions, `permission_prompt` for a sandboxed command's network request requires Claude Code v2.1.246 or later.

`agent_needs_input` for a teammate's terminal setup question requires Claude Code v2.1.248 or later.

> [!NOTE]
>
> The `permission_prompt`, `idle_prompt`, `elicitation_dialog`, and `elicitation_url_dialog` types share their timing with desktop notifications, so in terminal sessions you only see them when you appear to be away from the terminal:
>
> * Expect `permission_prompt` once you haven't typed for about six seconds. The timer starts when the permission prompt appears, and each keystroke defers it. To run a hook immediately when Claude asks for permission to use a tool, use [PermissionRequest](#permissionrequest) instead.
> * Expect `idle_prompt` about 60 seconds after Claude finishes responding, and only if you haven't typed since and no background agent, such as a background [subagent](https://code.claude.com/docs/en/sub-agents.md), is still running. Claude Code doesn't send `idle_prompt` while it waits for a claude.ai usage limit to reset. When the wait ends on its own, one of the `quota_auto_resume_*` types fires instead.
> * Expect `elicitation_dialog` for an elicitation form, or `elicitation_url_dialog` for a browser URL request, once you haven't typed for about six seconds. Both share the same six-second gate as `permission_prompt`: the timer starts when the dialog appears, and each keystroke defers it.
>
> A permission request or elicitation that arrives while another dialog is on screen keeps the same six-second gate, timed from when the request arrives. Its notification can reach you while the request still waits behind the open dialog.

Claude Code times `permission_prompt` differently in sessions where it sends permission requests to the Agent SDK's [`canUseTool` callback](https://code.claude.com/docs/en/agent-sdk/user-input), which is how Claude Desktop and the VS Code extension host Claude Code:

* Expect `permission_prompt` about six seconds after Claude asks for permission. Claude Code doesn't defer it while you type.
* If you or a [PermissionRequest](#permissionrequest) hook answer sooner, Claude Code doesn't run `permission_prompt`.
* Set [`CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS`](https://code.claude.com/docs/en/env-vars) to `1` to turn `permission_prompt` off in these sessions.

Before v2.1.233, `permission_prompt` didn't fire in these sessions.

Use a separate matcher group per notification type, such as `permission_prompt` and `idle_prompt`, to run different handlers.

#### Notification input

In addition to the [common input fields](hooks.md#common-input-fields), Notification hooks receive `message` with the notification text, an optional `title`, and `notification_type` indicating which type fired.

Notification hooks can't block or modify notifications. Claude Code discards their `systemMessage` and `continue` fields but still emits [`terminalSequence`](hooks.md#emit-terminal-notifications), which is what the desktop notification example relies on. Notification hooks are intended for side effects such as forwarding the notification to an external service.

### SubagentStart

Runs when Claude spawns a subagent with the Agent tool, when Claude [resumes a subagent](https://code.claude.com/docs/en/sub-agents.md#resume-subagents), and each time an in-process [agent team](https://code.claude.com/docs/en/agent-teams.md) teammate handles a new message. Supports matchers to filter by agent type name. For built-in agents, this is the agent name like `general-purpose`, `Explore`, or `Plan`. For [custom subagents](https://code.claude.com/docs/en/sub-agents.md), this is the `name` field from the agent's frontmatter, not the filename.

For subagents shipped by a [plugin](https://code.claude.com/docs/en/plugins/overview.md), the agent type is the plugin-scoped identifier such as `my-plugin:reviewer`, not the bare frontmatter name. The colon places a plugin-scoped name on the regular-expression path, so anchor the matcher with `^` and `$` for an exact match: `^my-plugin:reviewer$`.

#### SubagentStart input

In addition to the [common input fields](hooks.md#common-input-fields), SubagentStart hooks receive `agent_id` with the unique identifier for the subagent and `agent_type` with the agent name that the matcher filters on.

SubagentStart hooks can't block subagent creation, but they can inject context into the subagent. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, you can return:

| Field | Description |
| :- | :- |
| `additionalContext` | String added to the subagent's context at the start of its conversation, before its first prompt. See [Add context for Claude](hooks.md#add-context-for-claude) |

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Follow security guidelines for this task"
  }
}
```

When the hook runs again for the same subagent, Claude Code injects the returned context only when the subagent's context doesn't already hold the copy from an earlier run. The copy injected at launch stays in place, leaving the subagent's [prompt cache](https://code.claude.com/docs/en/prompt-caching.md#subagents-and-the-cache) intact. After [auto-compaction](https://code.claude.com/docs/en/sub-agents.md#auto-compaction) discards that copy, Claude Code injects the next run's context again.

### SubagentStop

Runs when a Claude Code subagent has finished responding. Matches on agent type, same values as SubagentStart.

#### SubagentStop input

In addition to the [common input fields](hooks.md#common-input-fields), SubagentStop hooks receive `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, and `last_assistant_message`. The `agent_type` field is the value used for matcher filtering. The `transcript_path` is the main session's transcript, while `agent_transcript_path` is the subagent's own transcript stored in a nested `subagents/` folder. The `last_assistant_message` field contains the text content of the subagent's final response, so hooks can access it without parsing the transcript file.

Not every SubagentStop event comes from a subagent Claude spawned. Claude Code also runs internal agents for some of its own features, such as [prompt suggestions](https://code.claude.com/docs/en/interactive-mode.md#prompt-suggestions) and [`/btw` side questions](https://code.claude.com/docs/en/interactive-mode#side-questions-with-%2Fbtw), and SubagentStop fires when one of those finishes too. For those events, `agent_type` is the agent name the session itself runs as, such as one set with [`--agent`](https://code.claude.com/docs/en/cli-reference#cli-flags) or the [`agent` setting](https://code.claude.com/docs/en/settings-reference#agent), and an empty string when the session runs without one.

A `matcher` that names agent types doesn't match an empty `agent_type`. A hook whose matcher is omitted, `""`, or `"*"`, or is a regular expression that matches an empty string, runs for events with an empty `agent_type` too.

On Claude Code v2.1.271 or later, a subagent that runs with the [`SubagentHandback`](https://code.claude.com/docs/en/tools-reference) tool delivers its report through that tool before it stops. The `last_assistant_message` field then holds the subagent's closing text, if any, which is not the delivered report. The report is that call's `message` input, which a `PreToolUse` or `PostToolUse` hook matched on `SubagentHandback` receives as `tool_input.message`.

SubagentStop hooks also receive the `background_tasks` and `session_crons` arrays described under [Stop input](#stop-input). Both arrays are scoped to the parent session, not the subagent.

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../abc123.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "def456",
  "agent_type": "Explore",
  "agent_transcript_path": "~/.claude/projects/.../abc123/subagents/agent-def456.jsonl",
  "last_assistant_message": "Analysis complete. Found 3 potential issues...",
  "background_tasks": [],
  "session_crons": []
}
```

SubagentStop hooks use the same decision control format as [Stop hooks](#stop-decision-control), including `hookSpecificOutput.additionalContext` with `hookEventName` set to `"SubagentStop"`, for non-error feedback that keeps the subagent running. Returning `decision: "block"` with a `reason` keeps the subagent running and delivers `reason` to the subagent as its next instruction. A hook that blocks by exiting 2 delivers its stderr message the same way. To inject context into the parent session after a subagent returns, use a [`PostToolUse`](#posttooluse) hook on the `Agent` tool instead.

### TaskCreated

Runs when a task is being created via the `TaskCreate` tool. Use this to enforce naming conventions, require task descriptions, or prevent certain tasks from being created. In a [session without the Task tools](https://code.claude.com/docs/en/tools-reference.md#task-tool-availability), this event doesn't fire.

TaskCreated hooks don't support matchers and fire on every occurrence.

#### TaskCreated input

In addition to the [common input fields](hooks.md#common-input-fields), TaskCreated hooks receive `task_id`, `task_subject`, and optionally `task_description`, `teammate_name`, and `team_name`.

| Field | Description |
| :- | :- |
| `task_id` | Identifier of the task being created |
| `task_subject` | Title of the task |
| `task_description` | Detailed description of the task. May be absent |
| `teammate_name` | Name of the teammate creating the task. May be absent |
| `team_name` | Deprecated. Session-derived team name; will be removed in a future release |
| `agent_id` | On this event, the [common input field](hooks.md#common-input-fields) identifies the subagent or [in-process teammate](https://code.claude.com/docs/en/agent-teams.md#choose-a-display-mode) creating the task. May be absent. Requires Claude Code v2.1.290 or later |

#### TaskCreated decision control

A TaskCreated hook can block the creation with exit code 2 or with a JSON decision. Either way, Claude Code deletes the task and returns your message to Claude as the tool's error. Claude Code ignores `continue: false` from this event and Claude keeps working.

* **Exit code 2**: Claude Code returns the stderr text as the message.
* **JSON `{"decision": "block", "reason": "..."}`**: Claude Code returns `reason` as the message.

This example blocks tasks whose subjects don't follow the required format:

```bash theme={null}
#!/bin/bash
INPUT=$(cat)
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

if [[ ! "$TASK_SUBJECT" =~ ^\[TICKET-[0-9]+\] ]]; then
  echo "Task subject must start with a ticket number, e.g. '[TICKET-123] Add feature'" >&2
  exit 2
fi

exit 0
```

### TaskCompleted

Runs when a task is being marked as completed. This fires in two situations: when any agent explicitly marks a task as completed through the TaskUpdate tool, or when an [agent team](https://code.claude.com/docs/en/agent-teams.md) teammate finishes its turn with in-progress tasks. Use this to enforce completion criteria like passing tests or lint checks before a task can close.

TaskCompleted hooks don't support matchers and fire on every occurrence.

#### TaskCompleted input

In addition to the [common input fields](hooks.md#common-input-fields), TaskCompleted hooks receive `task_id`, `task_subject`, and optionally `task_description`, `teammate_name`, and `team_name`.

| Field | Description |
| :- | :- |
| `task_id` | Identifier of the task being completed |
| `task_subject` | Title of the task |
| `task_description` | Detailed description of the task. May be absent |
| `teammate_name` | Name of the teammate completing the task. May be absent |
| `team_name` | Deprecated. Session-derived team name; will be removed in a future release |
| `agent_id` | On this event, the [common input field](hooks.md#common-input-fields) identifies the subagent or [in-process teammate](https://code.claude.com/docs/en/agent-teams.md#choose-a-display-mode) completing the task. May be absent. Requires Claude Code v2.1.290 or later |

#### TaskCompleted decision control

TaskCompleted hooks support two ways to control task completion:

* **Exit code 2**: the task is not marked as completed and the stderr message is fed back to the model as feedback.
* **JSON `{"continue": false, "stopReason": "..."}`**: when a teammate finishing its turn triggered the event, stops the teammate entirely, matching `Stop` hook behavior. The `stopReason` is shown to the user. When the `TaskUpdate` tool triggered the event, Claude Code ignores `continue: false`; exit code 2 still blocks the completion.

This example runs tests and blocks task completion if they fail:

```bash theme={null}
#!/bin/bash
INPUT=$(cat)
TASK_SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

# Run the test suite
if ! npm test 2>&1; then
  echo "Tests not passing. Fix failing tests before completing: $TASK_SUBJECT" >&2
  exit 2
fi

exit 0
```

### Stop

Runs when the main Claude Code agent has finished responding. Does not run if
the stoppage occurred due to a user interrupt. API errors fire
[StopFailure](#stopfailure) instead.

> [!TIP]
>
> The [`/goal`](https://code.claude.com/docs/en/goal) command is a built-in shortcut for a session-scoped prompt-based Stop hook. Use it when you want Claude to keep working toward a condition without writing hook configuration.

#### Stop input

In addition to the [common input fields](hooks.md#common-input-fields), Stop hooks receive `stop_hook_active`, `last_assistant_message`, `background_tasks`, and `session_crons`. The `stop_hook_active` field is `true` when Claude Code is already continuing as a result of a stop hook. Check this value or process the transcript to avoid blocking on a condition that will never resolve.

Claude Code applies an 8-consecutive-continuation cap: after stop hooks have continued the turn eight times in a row, Claude Code overrides the next block and ends the turn. The count of consecutive continuations resets each time Claude calls a tool. To raise the cap, set [`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`](https://code.claude.com/docs/en/env-vars).

The `last_assistant_message` field contains the text content of Claude's final response, so hooks can access it without parsing the transcript file. For hooks that act on the just-completed turn, such as read-aloud or notification hooks, use this field rather than reading `transcript_path`: the transcript file isn't guaranteed to include the final message at Stop time on all versions.

The `background_tasks` and `session_crons` arrays let hooks distinguish "session is done" from "session is paused waiting for background work to wake it back up". Both arrays are present when the task registry is reachable and are empty when nothing is in flight or scheduled.

Each entry in `background_tasks` describes one in-flight task and uses these fields:

| Field | Description |
| :- | :- |
| `id` | Task identifier |
| `type` | Friendly task-type label such as `shell`, `subagent`, `monitor`, `workflow`, `teammate`, `cloud session`, or `MCP task`. Each label identifies which Claude Code feature created the task. Falls back to the raw discriminant for unrecognized types |
| `status` | Current task status |
| `description` | Free-text description, capped at 1000 characters with an in-string `… [+N chars]` marker when clipped |
| `command` | Shell command line, capped at 1000 characters. Present only for `shell` tasks |
| `agent_type` | Subagent type name. Present only for `subagent` tasks |
| `server` | MCP server name. Present only for `monitor` and `MCP task` tasks |
| `tool` | MCP tool name. Present only for `monitor` and `MCP task` tasks |
| `name` | Workflow name. Present only for `workflow` tasks |

Each entry in `session_crons` describes one session-scoped scheduled wakeup, sourced from `CronCreate`, `ScheduleWakeup`, and `/loop`:

| Field | Description |
| :- | :- |
| `id` | Cron task identifier |
| `schedule` | Cron expression, for example `0 9 * * 1-5` |
| `recurring` | `false` for one-shot wakeups whose schedule encodes a single fire time, `true` for tasks that re-fire on every match |
| `prompt` | Prompt submitted when the cron fires, capped at 1000 characters with the same `… [+N chars]` marker |

#### Stop decision control

`Stop` and `SubagentStop` hooks can control whether Claude continues. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, your hook script can return these event-specific fields:

| Field | Description |
| :- | :- |
| `decision` | `"block"` prevents Claude from stopping. Omit to allow Claude to stop |
| `reason` | Required when `decision` is `"block"`. Tells Claude why it should continue |
| `hookSpecificOutput.additionalContext` | Non-error feedback for Claude. The conversation continues so Claude can act on it, but unlike `decision: "block"` it is shown in the transcript as hook feedback rather than a hook error |

A hook that blocks by exiting 2 routes the same way as `reason`: Claude receives the stderr message as the explanation for why it should continue.

```json theme={null}
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

Use `additionalContext` when the hook is working as designed and giving Claude guidance, such as "run the test suite before finishing". It keeps the conversation going through the same loop protections as `decision: "block"`, namely the `stop_hook_active` input and the 8-consecutive-continuation cap, but the transcript labels it `Stop hook feedback` and no hook error notification is shown:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "Please run the test suite before finishing"
  }
}
```

### StopFailure

Runs instead of [Stop](#stop) when the turn ends due to an API error. Claude Code ignores the hook's output and exit code, apart from [`terminalSequence`](hooks.md#emit-terminal-notifications). Use this to log failures, send alerts, or take recovery actions when Claude can't complete a response due to rate limits, authentication problems, or other API errors.

#### StopFailure input

In addition to the [common input fields](hooks.md#common-input-fields), StopFailure hooks receive `error`, optional `error_details`, and optional `last_assistant_message`. The `error` field identifies the error type and is used for matcher filtering.

| Field | Description |
| :- | :- |
| `error` | Error type: `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error`, or `unknown` |
| `error_details` | Additional details about the error, when available |
| `last_assistant_message` | The rendered error text shown in the conversation. Unlike `Stop` and `SubagentStop`, where this field holds Claude's conversational output, for `StopFailure` it contains the API error string itself, such as `"API Error: Rate limit reached"` |

StopFailure hooks have no decision control. They run for notification and logging purposes only.

### TeammateIdle

Runs when an [agent team](https://code.claude.com/docs/en/agent-teams.md) teammate is about to go idle after finishing its turn. Use this to enforce quality gates before a teammate stops working, such as requiring passing lint checks or verifying that output files exist.

TeammateIdle hooks don't support matchers and fire on every occurrence.

#### TeammateIdle input

In addition to the [common input fields](hooks.md#common-input-fields), TeammateIdle hooks receive `teammate_name` and `team_name`. In the official examples, `team_name` has the form `session-<8 hex digits>`, such as `session-a1b2c3d4`.

| Field | Description |
| :- | :- |
| `teammate_name` | Name of the teammate that is about to go idle |
| `team_name` | Deprecated. Session-derived team name; will be removed in a future release |
| `agent_id` | On this event, the [common input field](hooks.md#common-input-fields) identifies the [in-process teammate](https://code.claude.com/docs/en/agent-teams.md#choose-a-display-mode) that is about to go idle. May be absent. Requires Claude Code v2.1.290 or later |

#### TeammateIdle decision control

TeammateIdle hooks support two ways to control teammate behavior:

* **Exit code 2**: the teammate receives the stderr message as feedback and continues working instead of going idle.
* **JSON `{"continue": false, "stopReason": "..."}`**: stops the teammate entirely, matching `Stop` hook behavior. The `stopReason` is shown to the user.

This example checks that a build artifact exists before allowing a teammate to go idle:

```bash theme={null}
#!/bin/bash

if [ ! -f "./dist/output.js" ]; then
  echo "Build artifact missing. Run the build before stopping." >&2
  exit 2
fi

exit 0
```

### ConfigChange

Runs when a configuration file changes during a session. Use this to audit settings changes, enforce security policies, or block unauthorized modifications to configuration files.

Claude Code runs ConfigChange hooks when a settings file, a managed policy file, or a skill file changes. For managed policy, it runs them only when `managed-settings.json` or a file in `managed-settings.d/` changes. It applies [server-managed settings](https://code.claude.com/docs/en/server-managed-settings.md) and changes to macOS managed preferences or Windows registry policy without running them. On WSL with [`wslInheritsWindowsSettings`](https://code.claude.com/docs/en/settings-reference#wslinheritswindowssettings), it also applies a changed Windows-side managed settings file on its policy poll without running them.

The matcher filters on the configuration source:

| Matcher | When it fires |
| :- | :- |
| `user_settings` | `~/.claude/settings.json` changes |
| `project_settings` | `.claude/settings.json` changes |
| `local_settings` | `.claude/settings.local.json` changes |
| `skills` | A skill file in `.claude/skills/` changes |

This example logs all configuration changes for security auditing:

```json theme={null}
{
  "hooks": {
    "ConfigChange": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/audit-config-change.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

#### ConfigChange input

In addition to the [common input fields](hooks.md#common-input-fields), ConfigChange hooks receive `source` and optionally `file_path`. The `source` field indicates which configuration type changed, and `file_path` provides the path to the specific file that was modified.

#### ConfigChange decision control

ConfigChange hooks can block configuration changes from taking effect. Use exit code 2 or a JSON `decision` to prevent the change. When blocked, the new settings are not applied to the running session.

| Field | Description |
| :- | :- |
| `decision` | `"block"` prevents the configuration change from being applied. Omit to allow the change |
| `reason` | Accepted but never shown |

```json theme={null}
{
  "decision": "block",
  "reason": "Configuration changes to project settings require admin approval"
}
```

Claude Code acts on the blocking decision from a ConfigChange hook's JSON output and discards `systemMessage` and `continue`. A blocked change surfaces no message to you or to Claude, whether you block with `reason` or with stderr on exit 2. Claude Code only writes a line to the debug log.

### CwdChanged

Runs when a shell command in the main conversation changes the working directory, for example when Claude executes a `cd` command. Use this to react to directory changes: reload environment variables, activate project-specific toolchains, or run setup scripts automatically. Pairs with [FileChanged](#filechanged) for tools like [direnv](https://direnv.net/) that manage per-directory environment.

CwdChanged hooks have access to [`CLAUDE_ENV_FILE`](#persist-environment-variables). If your hook writes variables to that file, they persist into subsequent Bash commands until the next CwdChanged event, when Claude Code clears them.

CwdChanged doesn't support matchers and fires on every occurrence.

#### CwdChanged input

In addition to the [common input fields](hooks.md#common-input-fields), CwdChanged hooks receive `old_cwd` and `new_cwd`.

#### CwdChanged output

In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, CwdChanged hooks can return `watchPaths` to dynamically set which file paths [FileChanged](#filechanged) watches:

| Field | Description |
| :- | :- |
| `watchPaths` | Array of absolute paths. Replaces the current dynamic watch list. Paths from your `matcher` configuration are always watched. Returning an empty array clears the dynamic list, which is typical when entering a new directory |

CwdChanged hooks have no decision control. They can't block the directory change.

Claude Code reads `watchPaths` and `systemMessage` from their JSON output and discards `continue`. In interactive sessions, it shows the `systemMessage` as a brief terminal notification. The message doesn't reach the SDK message stream.

### DirectoryAdded

Runs after you add a working directory mid-session with the `/add-dir` command, or after an SDK client adds one with the `register_repo_root` control request. Use this to prepare a newly added repository, for example by installing its dependencies.

Claude Code doesn't fire this event when:

* You pass a directory with the `--add-dir` startup flag; [SessionStart](#sessionstart) covers those directories
* You add a directory on the `/permissions` Workspace tab
* You add a directory that is already a working directory or inside one

Claude Code fires DirectoryAdded after refreshing sandbox and permission state, so sandboxed tools already see the new directory when your hook runs. Hook commands themselves run unsandboxed.

Claude Code doesn't wait for the hook: the add completes immediately, and the hook runs in the background with the 600-second default timeout.

The matcher filters on how the directory was added:

| Matcher | When it fires |
| :- | :- |
| `slash_command` | You add a directory with `/add-dir` |

#### DirectoryAdded input

In addition to the [common input fields](hooks.md#common-input-fields), DirectoryAdded hooks receive `directory` and `source`.

| Field | Description |
| :- | :- |
| `directory` | Absolute path of the directory that was added |
| `source` | How the directory was added, `"slash_command"` for `/add-dir` or `"register_repo_root"` for the SDK control request |

DirectoryAdded hooks have no decision control. They can't block the add, which has already completed when the hook runs. Claude Code discards the `continue` field from their JSON output and surfaces the rest differently per source:

* `slash_command`: Claude Code delivers the hook's `systemMessage` to Claude as context on the next conversation turn, rather than showing it to you. A count of failed hooks appears in the transcript. Full failure output goes to the debug log

### FileChanged

Runs when a watched file changes on disk. Claude Code detects changes with a filesystem watcher, not by inspecting tool calls, so it runs the hook no matter what changed the file: an `Edit` or `Write` tool call, a script Claude runs with `Bash`, or a process outside Claude Code entirely. A common use is reloading environment variables when project configuration files change.

The `matcher` for this event serves two roles:

* **Build the watch list**: the value is split on `|` and each segment is registered as a literal filename in the working directory, so `".envrc|.env"` watches exactly those two files. Regex patterns are not useful here: a value like `^\.env` would watch a file literally named `^\.env`.
* **Filter which hooks run**: when a watched file changes, the same value filters which hook groups run using the standard [matcher rules](hooks.md#matcher-patterns) against the changed file's basename.

This example normalizes line endings in `data.csv` after any change, including a `Bash` command or an external script rewriting the file:

```json theme={null}
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": "data.csv",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/normalize-line-endings.sh"
          }
        ]
      }
    ]
  }
}
```

The hook reads the changed file's absolute path from the `file_path` field of the [JSON input](#filechanged-input) on stdin. Its `grep` guard tests for the same thing `perl` removes, a CR at the end of a line, so the run after a normalization exits without touching the file. A looser guard loops forever, because `perl -i` rewrites the file even when it substitutes nothing and Claude Code runs the hook again after every rewrite. Save this script at `/path/to/normalize-line-endings.sh` and make it executable:

```bash theme={null}
#!/bin/bash
FILE=$(jq -r .file_path)
if grep -q $'\r$' "$FILE"; then
  perl -pi -e 's/\r$//' "$FILE"
fi
```

To confirm the hook works, ask Claude to append a CRLF line to `data.csv` with a `Bash` command. Claude Code runs the hook and the file ends up with LF endings.

To watch files you can't name up front, return [`watchPaths`](#filechanged-output) from a hook to update the watch list dynamically. Claude Code starts the watcher only when something names a file to watch, so seed the list with a FileChanged group whose matcher names at least one file, or with a [SessionStart](#sessionstart-decision-control) or [CwdChanged](#cwdchanged) hook that returns `watchPaths`. The matcher still filters which hook groups run when a watched file changes, so give the group that handles dynamic paths an omitted matcher, which matches every watched file and adds nothing to the watch list. A `"*"` matcher also matches every file, but Claude Code registers it in the watch list like any other value, as a literal file named `*`.

FileChanged hooks have access to [`CLAUDE_ENV_FILE`](#persist-environment-variables). Variables written to that file persist into subsequent Bash commands until the next [CwdChanged](#cwdchanged) event, when Claude Code clears them.

#### FileChanged input

In addition to the [common input fields](hooks.md#common-input-fields), FileChanged hooks receive `file_path` and `event`.

| Field | Description |
| :- | :- |
| `file_path` | Absolute path to the file that changed |
| `event` | What happened: `"change"` for a modified file, `"add"` for a created file, or `"unlink"` for a deleted file |

#### FileChanged output

In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, FileChanged hooks can return `watchPaths` to dynamically update which file paths are watched:

| Field | Description |
| :- | :- |
| `watchPaths` | Array of absolute paths. Replaces the current dynamic watch list. Paths from your `matcher` configuration are always watched. Use this when your hook script discovers additional files to watch based on the changed file |

FileChanged hooks have no decision control. They can't block the file change from occurring.

Claude Code reads `watchPaths` and `systemMessage` from their JSON output and discards `continue`. In interactive sessions, it shows the `systemMessage` as a brief terminal notification. The message doesn't reach the SDK message stream.

### WorktreeCreate

Runs when Claude Code creates a worktree in cases such as these:

* You start a session with `claude --worktree`
* Claude creates a worktree during a session and switches into it with the [`EnterWorktree`](https://code.claude.com/docs/en/tools-reference) tool
* A [subagent uses `isolation: "worktree"`](https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope)
* A [workflow](https://code.claude.com/docs/en/workflows.md#migrate-many-files-in-parallel) runs an agent in its own worktree
* Claude Code isolates a [background session](https://code.claude.com/docs/en/agent-view.md#how-file-edits-are-isolated) in its own worktree
* [`claude remote-control`](https://code.claude.com/docs/en/remote-control#start-a-remote-control-session) in `worktree` mode starts a session in its own worktree

A WorktreeCreate hook doesn't run for a worktree Claude adds through Bash, and a plugin's hook doesn't run for the one created when you launch with `--worktree` and [`--tmux`](https://code.claude.com/docs/en/cli-reference#cli-flags):

* **`git worktree add` through Bash**: to inspect or block that command, add a [`PreToolUse`](#pretooluse) hook with the `Bash` matcher.
* **`--worktree` with `--tmux`**: Claude Code creates the worktree before it loads plugins, so a WorktreeCreate hook from a plugin doesn't run. To have your hook run with both flags, define it in a [settings file](hooks.md#configuration) instead. Before v2.1.300, a plugin's WorktreeCreate hook didn't run with `--worktree` alone either.

By default Claude Code creates the isolated working copy with `git worktree`. Configuring a WorktreeCreate hook replaces that default git behavior, letting you use a different version control system like SVN, Perforce, or Mercurial.

Because the hook replaces the default behavior entirely, [`.worktreeinclude`](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees) is not processed. If you need to copy local configuration files like `.env` into the new worktree, do it inside your hook script.

The hook must return the path to the created worktree directory. Claude Code uses this path as the working directory for the isolated session. See [WorktreeCreate output](#worktreecreate-output) for how each hook type returns the path.

Claude Code acts on the hook's success and the returned path, and discards `systemMessage` and `continue`.

This example creates an SVN working copy and prints the path for Claude Code to use. Replace the repository URL with your own:

```json theme={null}
{
  "hooks": {
    "WorktreeCreate": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'NAME=$(jq -r .name); DIR=\"$HOME/.claude/worktrees/$NAME\"; svn checkout https://svn.example.com/repo/trunk \"$DIR\" >&2 && echo \"$DIR\"'"
          }
        ]
      }
    ]
  }
}
```

The hook reads the worktree `name` from the JSON input on stdin, checks out a fresh copy into a new directory, and prints the directory path. The `echo` on the last line is what Claude Code reads as the worktree path. Redirect any other output to stderr so it doesn't interfere with the path.

#### WorktreeCreate input

In addition to the [common input fields](hooks.md#common-input-fields), WorktreeCreate hooks receive the `name` field. This is a slug identifier for the new worktree, either specified by the user or auto-generated, for example `bold-oak-a3f2`.

#### WorktreeCreate output

WorktreeCreate hooks don't use the standard allow/block decision model. Instead, the hook's success or failure determines the outcome. The hook must return the path to the created worktree directory:

* **Command hooks** (`type: "command"`): print the path as the last non-empty line of stdout. Claude Code strips ANSI escape codes before reading that line, so shell startup banners printed before your `echo` are ignored. Redirect any other hook output to stderr.
* **HTTP hooks** (`type: "http"`): return `{ "hookSpecificOutput": { "hookEventName": "WorktreeCreate", "worktreePath": "/absolute/path" } }` in the response body.

If the hook fails or produces no path, worktree creation fails with an error. Claude Code resolves a relative path against the directory the hook ran in, collapsing any `.` or `..` segments in it. If the resulting path isn't a directory Claude Code can enter, the session prints an error naming the path and exits with code 1.

Claude Code refuses an absolute path that contains `.` or `..` segments, and any path that passes through a symlink below the repository root. The error names the rejected component. A symlink committed to the repository could redirect the worktree outside it. Return a normalized path that doesn't pass through a symlink inside the repository.

### WorktreeRemove

Runs when Claude Code cleans up a worktree that your [`WorktreeCreate`](#worktreecreate) hook created. The event fires when:

* You exit an interactive [worktree session](https://code.claude.com/docs/en/worktrees.md#start-claude-in-a-worktree) and choose to remove the worktree when Claude Code prompts you
* You exit an interactive worktree session you haven't [named](https://code.claude.com/docs/en/sessions.md#name-your-sessions), Claude Code finds no changed or untracked files, and it removes the worktree without prompting you
* You delete a [background session](https://code.claude.com/docs/en/agent-view.md#what-deleting-a-session-removes) that runs in the worktree
* You ask Claude to exit and remove the worktree during a session, and Claude removes it with the [`ExitWorktree`](https://code.claude.com/docs/en/tools-reference) tool
* A session that [`claude remote-control`](https://code.claude.com/docs/en/remote-control#start-a-remote-control-session) started in `worktree` mode ends without crashing, and Claude Code finds no changed or untracked files and no new commits in its worktree
* You stop `claude remote-control` while sessions it started in `worktree` mode are still running, and Claude Code finds no changed or untracked files and no new commits in their worktrees

When a subagent or a workflow agent finishes, Claude Code keeps the worktree your WorktreeCreate hook made for it and doesn't run your WorktreeRemove hook. Remove those worktrees yourself when the work is done.

Claude Code doesn't prompt you before your hook runs for an `ExitWorktree` call or a `claude remote-control` cleanup. `ExitWorktree` refuses to remove a hook-created worktree unless the call passes [`discard_changes: true`](https://code.claude.com/docs/en/agent-sdk/typescript#exitworktree), which makes your hook the last check on that route.

Claude Code uses git to look for changed or untracked files, so it finds none in a worktree that isn't a git checkout or inside one, even when the directory holds uncommitted work. Check for that work in your WorktreeRemove hook before it deletes anything.

For git-based worktrees, Claude Code handles cleanup automatically with `git worktree remove`. If you configured a WorktreeCreate hook, pair it with a WorktreeRemove hook to control cleanup:

* **No WorktreeRemove hook**: Claude Code falls back to git for a removal at exit or through `ExitWorktree`, and keeps the worktree when `claude remote-control` cleans up:
  * **You exit a worktree session, or Claude calls `ExitWorktree`**: Claude Code removes the path your WorktreeCreate hook returned as `git worktree remove --force` would, so a worktree git recognizes is removed. A worktree git doesn't recognize, for example one your hook created with a non-git version control system, stays on disk.
  * **`claude remote-control` cleans up a session's worktree**: the worktree stays on disk, and the terminal running `claude remote-control` shows `worktree removal failed, kept: <path>`.
  * **You delete a background session**: see [What deleting a session removes](https://code.claude.com/docs/en/agent-view.md#what-deleting-a-session-removes).
* **Hook exits 0**: the worktree counts as removed. Claude Code reads nothing else from the hook, so make sure your hook deleted the directory.
* **Hook exits non-zero**: the removal fails if the directory at `worktree_path` still exists afterward, and the worktree stays on disk with no git fallback. A hook that deleted the directory before exiting non-zero counts as removed. For how the failure is reported, see [WorktreeRemove input](#worktreeremove-input).

Claude Code never deletes a branch belonging to a hook-created worktree, because it only knows the path your WorktreeCreate hook returned. If your WorktreeCreate hook creates a branch, delete it in your WorktreeRemove hook. Claude Code discards a WorktreeRemove hook's [JSON output fields](hooks.md#json-output), such as `systemMessage` and `continue`.

For a background-session delete, Claude Code verifies the stored worktree path before running the hook, refusing a path that is a symlink or passes through one below the repository root. On that route, the hook runs for a worktree that still contains files only when you confirm the delete in [agent view](https://code.claude.com/docs/en/agent-view.md#what-deleting-a-session-removes). For such a worktree, [`claude rm`](https://code.claude.com/docs/en/agent-view#manage-sessions-from-the-shell) keeps the session and worktree instead.

Claude Code passes the path returned by WorktreeCreate as `worktree_path` in the hook input. This example reads that path and removes the directory:

```json theme={null}
{
  "hooks": {
    "WorktreeRemove": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'jq -r .worktree_path | xargs rm -rf'"
          }
        ]
      }
    ]
  }
}
```

#### WorktreeRemove input

In addition to the [common input fields](hooks.md#common-input-fields), WorktreeRemove hooks receive the `worktree_path` field, which is the absolute path to the worktree being removed, such as `<project>/.claude/worktrees/feature-auth` for a worktree under the default location.

A WorktreeRemove hook's exit code decides the outcome. When a hook exits non-zero and the directory at `worktree_path` still exists afterward, the removal fails:

* The worktree stays on disk, and the hook's command and stderr go to the [debug log](hooks.md#debug-hooks).
* If you were deleting a background session, the session stays too. The refusal message in [agent view](https://code.claude.com/docs/en/agent-view.md#what-deleting-a-session-removes) reports how the hook ended, such as `exited 1`, quotes the start of its stderr, and says whether deleting the session again removes the directory anyway.
* If `claude remote-control` was cleaning up a session's worktree, the terminal running it shows `worktree removal failed, kept: <path>`.

### PreCompact

Runs before Claude Code is about to run a compact operation.

The matcher value indicates whether compaction was triggered manually or automatically:

| Matcher | When it fires |
| :- | :- |
| `manual` | `/compact` |
| `auto` | Auto-compact when the conversation reaches the [auto-compact window](https://code.claude.com/docs/en/model-config.md#set-the-auto-compact-window), and [idle compaction](https://code.claude.com/docs/en/settings-reference.md#idlecompaction) |

Exit with code 2 to block compaction. For a manual `/compact`, the stderr message is shown to the user. You can also block by returning JSON with `"decision": "block"`.

Blocking automatic compaction has different effects depending on when it fires. If compaction was triggered proactively before the context limit, Claude Code skips it and the conversation continues uncompacted. If compaction was triggered to recover from a context-limit error already returned by the API, the underlying error surfaces and the current request fails.

Claude Code discards a PreCompact hook's `systemMessage` and `continue` fields.

#### PreCompact input

In addition to the [common input fields](hooks.md#common-input-fields), PreCompact hooks receive `trigger` and `custom_instructions`. For `manual`, `custom_instructions` contains what the user passes into `/compact` and is `null` when they pass nothing. For `auto`, `custom_instructions` is `null`.

#### PreCompact output

When a PreCompact hook exits 0 and doesn't block, Claude Code uses its stdout as instructions for the compaction summary. Keep that stdout under 10,000 characters per hook. Claude Code cuts longer output at the cap and appends a marker.

### PostCompact

Runs after Claude Code completes a compact operation. Use this event to react to the new compacted state, for example to log the generated summary or update external state. Claude Code discards a PostCompact hook's `systemMessage` and `continue` fields.

The same matcher values apply as for `PreCompact`:

| Matcher | When it fires |
| :- | :- |
| `manual` | After `/compact` |
| `auto` | After auto-compact when the conversation reaches the [auto-compact window](https://code.claude.com/docs/en/model-config.md#set-the-auto-compact-window), and after [idle compaction](https://code.claude.com/docs/en/settings-reference.md#idlecompaction) |

#### PostCompact input

In addition to the [common input fields](hooks.md#common-input-fields), PostCompact hooks receive `trigger` and `compact_summary`. The `compact_summary` field contains the conversation summary generated by the compact operation.

PostCompact hooks have no decision control. They can't affect the compaction result but can perform follow-up tasks.

### PreModelSwitch

Runs before Claude Code applies a model switch that you or a client requested. Use it to block a switch, require confirmation, or show what the switch will cost before it happens.

PreModelSwitch requires Claude Code v2.1.251 or later. Claude Code runs it for these requests:

* `/model <name>` and the `/model` picker
* The `Option+P` or `Alt+P` model picker
* The Model setting in `/config`
* Turning on [fast mode](https://code.claude.com/docs/en/fast-mode.md) when that changes the session's model
* A `set_model` request, or a model change in an `apply_flag_settings` request, from an [Agent SDK](https://code.claude.com/docs/en/agent-sdk/typescript.md#query-object) host or [Remote Control](https://code.claude.com/docs/en/remote-control.md)

Claude Code doesn't run PreModelSwitch hooks for switches it makes on its own, such as an [automatic model fallback](https://code.claude.com/docs/en/model-config.md#automatic-model-fallback) or restoring the model when you resume a session. Those changes reach [PostModelSwitch](#postmodelswitch) only.

Claude Code compares the matcher against the canonical name of the model the session is switching to, ignoring any `[1m]` suffix. An alias such as `opus`, a dated model ID, and a provider-specific ID such as an Amazon Bedrock model ID all match the one canonical name they resolve to, so `claude-opus-5` covers every spelling of Opus 5.

When Claude Code can't determine a canonical name for the target, for example a custom model ID that only your [LLM gateway](https://code.claude.com/docs/en/llm-gateway) knows, it runs every PreModelSwitch hook regardless of matcher. A hook that blocks should therefore check `to_model` from its input rather than rely on the matcher alone.

Write the matcher as an exact name, a `|`-separated list such as `claude-opus-4-6|claude-opus-5`, or a regular expression such as `.*opus.*`.

> **Official example**: [PreModelSwitch](https://code.claude.com/docs/en/hooks#premodelswitch) refuses a switch to Opus 4.6 with an exact-name matcher plus a `to_model` check, in Bash and PowerShell. The Bash version is one shell-form command: `jq -e '.to_model | test("opus-4-6")' > /dev/null && { echo 'Opus 4.6 is retired for this project. Use a newer model.' >&2; exit 2; }; exit 0`. Running `/model claude-opus-4-6` then keeps the current model and reports that a PreModelSwitch hook blocked the switch, with the message as the reason.

#### PreModelSwitch input

In addition to the [common input fields](hooks.md#common-input-fields), PreModelSwitch hooks receive the fields in this table. The last five describe what re-sending the conversation to the new model costs, so a hook can show that figure before the switch happens.

| Field | Type | Description |
| :- | :- | :- |
| `from_model` | string | Model ID the switch changes from |
| `to_model` | string | Model ID the switch changes to. The matcher compares against this model's canonical name |
| `requested_model` | string or `null` | The model the request named: an alias such as `opus`, a full model ID, or `null` when the request was for the default model |
| `source` | string | Where the request came from: `"command"` for `/model <name>`, the Model setting in `/config`, or turning on fast mode; `"picker"` for a model picker; `"sdk"` for a `set_model` request, or a model change in an `apply_flag_settings` request, from an Agent SDK host or Remote Control |
| `context_tokens` | number | Tokens the next request re-sends as its prompt: the input, cache read, cache creation, and output tokens of the last response in the main conversation, combined. `0` before the first response |
| `prompt_cache_warm` | boolean | Whether the current model's prompt cache is likely still warm, meaning the switch forfeits it |
| `cache_ttl` | string | [Prompt cache lifetime](https://code.claude.com/docs/en/prompt-caching.md#cache-lifetime) of the main conversation at the time of this switch: `"5m"` or `"1h"` |
| `estimated_cache_write_usd` | number | Estimated cost in US dollars of writing `context_tokens` to the prompt cache on `to_model` at the `cache_ttl` rate, excluding the next response. The server may not need to re-cache the whole context, so treat it as an estimate |
| `pricing` | string | How Claude Code priced `estimated_cache_write_usd`: `"configured"` at your organization's own rates when it has configured them, `"catalog"` at list price, or `"default"` when `to_model` has no known price and Claude Code assumed a default rate |

#### PreModelSwitch decision control

`PreModelSwitch` hooks can cancel the switch, ask the user to confirm it, or let it proceed. Exit code 2 or a top-level `decision: "block"` cancels the switch.

For finer control, return `permissionDecision` and `permissionDecisionReason` in a `hookSpecificOutput` object, as on [PreToolUse](#pretooluse-decision-control). `PreModelSwitch` accepts `"allow"`, `"deny"`, and `"ask"`. It doesn't accept `"defer"`, `updatedInput`, or `additionalContext`. The table below describes both fields:

| Field | Description |
| :- | :- |
| `permissionDecision` | `"allow"` proceeds and skips the [confirmation Claude Code shows while the prompt cache is warm](https://code.claude.com/docs/en/prompt-caching.md#switching-models). `"deny"` cancels the switch. `"ask"` prompts the user to confirm it |
| `permissionDecisionReason` | For `"deny"`, shown to the user as the reason the switch was blocked, or returned as the error for a `set_model` request. For `"ask"`, shown in the confirmation prompt. Ignored for `"allow"` |

Only `/model` in an interactive session can show the `"ask"` prompt. On every other surface, including non-interactive mode with the `-p` flag, `/config`, and `set_model` requests, Claude Code treats `"ask"` as a refusal.

This example asks the user to confirm and quotes the token count from `context_tokens`:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PreModelSwitch",
    "permissionDecision": "ask",
    "permissionDecisionReason": "Switching now re-sends about 180k tokens to the new model. Continue?"
  }
}
```

When multiple PreModelSwitch hooks return different decisions, precedence is `deny` > `ask` > `allow`.

Claude Code shows the user any `systemMessage` your hook returns regardless of the decision, so a cost-report hook can return `{"systemMessage": "..."}` and exit 0.

#### PreModelSwitch timeouts and other exit codes

A PreModelSwitch hook that doesn't respond before its timeout blocks the switch. The default timeout for this event is 30 seconds.

An exit code other than 0 or 2 without valid JSON output is a [non-blocking error](hooks.md#other-exit-codes), so the switch goes ahead, except for hooks [whose failure blocks it](hooks.md#block-the-action-when-a-hook-fails).

### PostModelSwitch

Runs after the session's model changes. Use it to give Claude model-specific guidance without editing every CLAUDE.md, for example an organization-wide instruction that applies on certain models.

PostModelSwitch requires Claude Code v2.1.251 or later. It can't block, because the model has already changed. Claude Code runs PostModelSwitch hooks after any of these changes:

* A switch you or a client requested
* An [automatic model fallback](https://code.claude.com/docs/en/model-config.md#automatic-model-fallback), which changes the session's model
* A setting such as [`opusplan`](https://code.claude.com/docs/en/model-config#opusplan-model-setting) entering or leaving plan mode
* Claude Code restoring the model when you resume a session

Claude Code doesn't run PostModelSwitch hooks when a model from a [fallback model chain](https://code.claude.com/docs/en/model-config.md#fallback-model-chains) serves a turn, because that substitution lasts one turn and leaves the session's model unchanged.

The matcher follows the same rules as [PreModelSwitch](#premodelswitch): Claude Code compares it against the canonical name of the model the session switched to.

> **Official example**: [PostModelSwitch](https://code.claude.com/docs/en/hooks#postmodelswitch) adds guidance on any Opus model with `"matcher": ".*opus.*"` and a command that echoes the guidance; plain stdout reaches Claude with the next request.

#### PostModelSwitch input

PostModelSwitch hooks receive the same fields as [PreModelSwitch](#premodelswitch-input), with `hook_event_name` set to `"PostModelSwitch"` and two more `source` values: `"auto"` for an automatic fallback or other change Claude Code made on its own, and `"resume"` for the model restored when you resume a session.

`requested_model` is `null` when `source` is `"auto"`. When `source` is `"resume"`, it is the saved model setting Claude Code restored.

#### PostModelSwitch decision control

Claude Code takes your hook's [plain-text stdout](hooks.md#exit-code-0) on exit 0, or `additionalContext` from JSON output, and delivers it to Claude with the next request after the switch. In addition to the [JSON output fields](hooks.md#json-output) available to all hooks, you can return:

| Field | Description |
| :- | :- |
| `additionalContext` | String added to Claude's context with the next request. See [Add context for Claude](hooks.md#add-context-for-claude) |

If the hook hasn't finished within five seconds after you send the next prompt, Claude Code sends that request without the output and attaches it to the following request instead. If the model changes several times before the next request, Claude Code delivers only the output for the last switch's target model.

### SessionEnd

Runs when a Claude Code session ends. Useful for cleanup tasks, logging session
statistics, or saving session state. Supports matchers to filter by exit reason.

The `reason` field in the hook input indicates why the session ended:

| Reason | Description |
| :- | :- |
| `clear` | Session cleared with `/clear` command |
| `resume` | Session switched via interactive `/resume` |
| `logout` | User logged out |
| `prompt_input_exit` | User exited while prompt input was visible |
| `other` | Other exit reasons |
| `bypass_permissions_disabled` | Removed in v2.1.234; Claude Code doesn't send it. Drop it from your `SessionEnd` matchers |

#### SessionEnd input

In addition to the [common input fields](hooks.md#common-input-fields), SessionEnd hooks receive a `reason` field indicating why the session ended. See the [reason table](#sessionend) above for all values.

SessionEnd hooks have no decision control. They can't block session termination but can perform cleanup tasks. Claude Code discards their [JSON output fields](hooks.md#json-output), such as `systemMessage`.

SessionEnd hooks have a default timeout of 1.5 seconds. It applies when you exit, run `/clear`, or switch sessions with interactive `/resume`. You can give a hook more time in two ways:

* **Per-hook `timeout`**: set `timeout` in that hook's configuration. The overall budget rises automatically to match the highest per-hook `timeout` in your settings files, up to 60 seconds. If you raise the budget this way, a hook without its own `timeout` still keeps the default. Timeouts set on plugin-provided hooks don't raise the budget.
* **`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`**: set this environment variable in milliseconds to override the budget explicitly. The value you set also becomes the timeout for each hook without its own `timeout`.

This example sets the budget to 5 seconds:

```bash theme={null}
CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS=5000 claude
```

Before v2.1.268, `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` raised only the overall budget, and a hook without its own `timeout` was still canceled after 1.5 seconds.

### Elicitation

Runs when an MCP server requests user input mid-task. By default, Claude Code shows an interactive dialog for the user to respond. Hooks can intercept this request and respond programmatically, skipping the dialog entirely.

For a complete hook with its settings entry and script, see [Answer a form request from a script](#answer-a-form-request-from-a-script).

The matcher field matches against the MCP server name.

#### Elicitation input

In addition to the [common input fields](hooks.md#common-input-fields), Elicitation hooks receive `mcp_server_name`, `message`, and optional `mode`, `url`, `elicitation_id`, and `requested_schema` fields.

For form-mode elicitation, the most common case:

```json theme={null}
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "Elicitation",
  "mcp_server_name": "my-mcp-server",
  "message": "Please provide your credentials",
  "mode": "form",
  "requested_schema": {
    "type": "object",
    "properties": {
      "username": { "type": "string", "title": "Username" }
    }
  }
}
```

#### Elicitation output

An Elicitation hook can answer the request for the user, decline or cancel it, or leave it to the dialog. To answer, decline, or cancel, exit 0 and print a `hookSpecificOutput` object with an `action`. The server gets your answer and no dialog appears. Each row of this table shows what to return for one outcome and what the MCP server receives:

| To | Return | The server receives |
| :- | :- | :- |
| Answer for the user | `"action": "accept"`, with the form field values in `content` | `accept` with your `content` |
| Decline the request | `"action": "decline"` | `decline` |
| Cancel the request | `"action": "cancel"` | `cancel` |
| Leave the request to the user | No output, with exit code 0 | The user's answer from the [dialog](https://code.claude.com/docs/en/mcp.md#respond-to-mcp-elicitation-requests) |

This output answers the form-mode request shown under [Elicitation input](#elicitation-input). The keys in `content` are the property names from that request's `requested_schema`:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": {
      "username": "alice"
    }
  }
}
```

This output declines a request:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "decline"
  }
}
```

In the dialog, selecting **Decline** sends `decline` and pressing `Esc` sends `cancel`, so return the one you want the server to see.

For a URL-mode request, a hook that returns `accept` skips the dialog, so the URL never opens.

Claude Code discards `reason`, `systemMessage`, and `continue` from an Elicitation hook's JSON output, whichever `action` you return.

#### Other ways to decline an elicitation

Your hook can also decline in these ways. The server receives the same `decline` as for `"action": "decline"`:

* **Exits with code 2**: Claude Code ignores a `hookSpecificOutput` printed by the same hook
* **Prints a top-level `"decision": "block"`**: the block overrides an `action` in the same output

When several hooks match the same request, a decline from one of them overrides an `accept` or `cancel` from another.

This script declines URL-mode requests and leaves form requests to the dialog:

```bash theme={null}
#!/bin/bash
if [ "$(jq -r '.mode')" = "url" ]; then
  exit 2
fi
```

Neither the user nor the server sees why your hook declined, because Claude Code doesn't show your stderr or your `reason`.

Claude Code ignored a top-level `decision` from `Elicitation` and `ElicitationResult` hooks from v2.1.105 until the fix in v2.1.284.

#### Answer a form request from a script

> **Official example**: [Answer a form request from a script](https://code.claude.com/docs/en/hooks#answer-a-form-request-from-a-script) answers an `issue-tracker` server's one-field form with `project_key: "DOCS"`, in Bash and PowerShell, and prints nothing for any other request so the dialog appears.

**Key facts:**

* Register the hook with the MCP server name as the matcher, and read the form's field names from `.requested_schema.properties`.
* To answer, print `{"hookSpecificOutput": {"hookEventName": "Elicitation", "action": "accept", "content": {"project_key": "DOCS"}}}`; to leave the request to the user, print nothing.
* With `claude --debug`, the [debug log](hooks.md#debug-hooks) shows a line ending with `Elicitation resolved by hook: {"action":"accept","content":{"project_key":"DOCS"}}` and no dialog appears.

### ElicitationResult

Runs after a user responds to an MCP elicitation. Hooks can observe, modify, or block the response before it is sent back to the MCP server.

When an [Elicitation](#elicitation) hook answers a request, Claude Code sends that answer to the server without running ElicitationResult hooks.

The matcher field matches against the MCP server name.

#### ElicitationResult input

In addition to the [common input fields](hooks.md#common-input-fields), ElicitationResult hooks receive `mcp_server_name`, `action`, and optional `mode`, `elicitation_id`, and `content` fields.

#### ElicitationResult output

An ElicitationResult hook can let the user's response through, change its values, or block it. To change or block the response, exit 0 and print a `hookSpecificOutput` object with an `action`. Each row of this table shows what to return for one outcome and what the MCP server receives:

| To | Return | The server receives |
| :- | :- | :- |
| Let the response through | No output, with exit code 0 | The user's response, unchanged |
| Change the submitted values | `"action": "accept"`, with the new values in `content` | `accept` with your `content` in place of the user's values |
| Block the response | `"action": "decline"` | `decline`, without the user's values |
| Cancel the request | `"action": "cancel"` | `cancel`, along with the values the user submitted. To withhold them, return `"decline"` |

This output changes a form response whose `content` is `{"username": "alice"}`, so the server receives `alice@example.com` where the user submitted `alice`:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "ElicitationResult",
    "action": "accept",
    "content": {
      "username": "alice@example.com"
    }
  }
}
```

Your `content` replaces the user's whole `content` object, so include the fields you aren't changing. Return `action` along with it, because Claude Code ignores a `hookSpecificOutput` that has no `action`.

ElicitationResult hooks also run when the user declines or cancels, and your `action` replaces theirs. Check that the input's `action` is `accept` before you return `accept`, or your hook turns a declined request into an accepted one. This script makes the same change when the user accepted, keeps the other fields, and prints nothing otherwise:

```bash theme={null}
#!/bin/bash
input=$(cat)

if [ "$(jq -r '.action' <<<"$input")" = "accept" ]; then
  jq '{hookSpecificOutput: {hookEventName: "ElicitationResult", action: "accept", content: (.content + {username: (.content.username + "@example.com")})}}' <<<"$input"
fi
```

This output blocks the response:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "ElicitationResult",
    "action": "decline"
  }
}
```

Exit code 2 and a top-level `"decision": "block"` also block the response. [Other ways to decline an elicitation](#other-ways-to-decline-an-elicitation) covers which one takes effect when a hook combines them, what the user sees, and which versions ignored `decision`.

Claude Code discards `reason`, `systemMessage`, and `continue` from an ElicitationResult hook's JSON output, whichever `action` you return.

## Documentation References

- Source page: https://code.claude.com/docs/en/hooks (the Hook events section)
- [Hooks reference](https://code.claude.com/docs/en/hooks): the official examples this file points to instead of copying them, such as the MessageDisplay output, the PreToolUse input, PreModelSwitch, PostModelSwitch and Answer a form request from a script, and the section on `updatedInput` paired with `"allow"` for tools that require user interaction.
- [Memory](https://code.claude.com/docs/en/memory): CLAUDE.md, and how Claude Code reads `AGENTS.md`.
- [Agent view](https://code.claude.com/docs/en/agent-view): background sessions, moving a session to the background, `claude rm`, and what deleting a session removes.
- [Sessions](https://code.claude.com/docs/en/sessions): named sessions and generated titles.
- [Prompt caching](https://code.claude.com/docs/en/prompt-caching): the prompt cache and its lifetime.
- [Headless mode](https://code.claude.com/docs/en/headless): non-interactive mode, `hook_response` events, and calls it denies.
- [Skills](https://code.claude.com/docs/en/skills): skills, and the output a skill injects with `` !`<command>` ``.
- [Tools reference](https://code.claude.com/docs/en/tools-reference): the PowerShell tool, `EndConversation`, `SubagentHandback`, `EnterWorktree`, `ExitWorktree`, auto-background eligibility, and sessions without the Task tools.
- [Environment variables](https://code.claude.com/docs/en/env-vars): `CLAUDE_ENV_FILE`, `CLAUDE_CODE_DISABLE_FILE_MENTIONS`, `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS`, `CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS` and `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`.
- [Sandboxing](https://code.claude.com/docs/en/sandboxing): sandboxed commands, running outside the sandbox, and network requests.
- [Plugins components reference](https://code.claude.com/docs/en/plugins/components): the plugin's persistent data directory.
- [Plugin loading](https://code.claude.com/docs/en/plugins/loading): the Node.js package dependencies Claude Code installs automatically.
- [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks): session-scoped scheduled tasks.
- [Subagents](https://code.claude.com/docs/en/sub-agents): custom, foreground and background subagents, resuming a subagent, auto-compaction, and `isolation: "worktree"`.
- [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging): messages another session sends.
- [Terminal configuration](https://code.claude.com/docs/en/terminal-config): how Claude Code marks pasted text.
- [The .claude directory](https://code.claude.com/docs/en/claude-directory): plaintext storage and clearing local data.
- [Common workflows](https://code.claude.com/docs/en/common-workflows): referencing files with `@` in a prompt.
- [Permissions](https://code.claude.com/docs/en/permissions): deny and ask rules, a `Read` deny rule, reads from network paths, hook approvals in plan mode, and `permissions.disableBypassPermissionsMode`.
- [Agent SDK TypeScript reference](https://code.claude.com/docs/en/agent-sdk/typescript): `McpServerProvenance`, `discard_changes: true`, and the permission modes that approve a call.
- [Settings reference](https://code.claude.com/docs/en/settings-reference): `bashEditDiffEnabled`, `allowManagedPermissionRulesOnly`, `autoContinueAtUsageLimit`, `wslInheritsWindowsSettings`, the `agent` setting, idle compaction, and settings that count only from user, `--settings` or managed settings.
- [Monitoring usage](https://code.claude.com/docs/en/monitoring-usage): token and cost counters.
- [Permission modes](https://code.claude.com/docs/en/permission-modes): auto mode and its classifier, plan mode, protected paths, and actions no mode auto-approves.
- [Agent SDK custom tools](https://code.claude.com/docs/en/agent-sdk/custom-tools): tools an Agent SDK app marks `always_ask`.
- [Errors](https://code.claude.com/docs/en/errors): the messages when auto mode couldn't check a call or a safety check refused the classifier's request.
- [Agent SDK permissions](https://code.claude.com/docs/en/agent-sdk/permissions): the `canUseTool` callback.
- [CLI reference](https://code.claude.com/docs/en/cli-reference): restricted mode, `--agent` and `--tmux`.
- [Interactive mode](https://code.claude.com/docs/en/interactive-mode): how a turn ends, the model-setting exception, prompt suggestions, and `/btw` side questions.
- [Auto mode configuration](https://code.claude.com/docs/en/auto-mode-config): reviewing denials.
- [Authentication](https://code.claude.com/docs/en/authentication): credential storage.
- [Agent teams](https://code.claude.com/docs/en/agent-teams): agent teams, in-process teammates, and a teammate's terminal setup question.
- [Auto mode classifier billing](https://code.claude.com/docs/en/auto-mode-classifier-billing): classifier request charges.
- [Mods API](https://code.claude.com/docs/en/plugins/mods/api): mods.
- [Agent SDK user input](https://code.claude.com/docs/en/agent-sdk/user-input): the `canUseTool` callback.
- [Plugins overview](https://code.claude.com/docs/en/plugins/overview): plugins.
- [Goal](https://code.claude.com/docs/en/goal): `/goal`.
- [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings): server-managed settings.
- [Workflows](https://code.claude.com/docs/en/workflows): workflows.
- [Remote Control](https://code.claude.com/docs/en/remote-control): Remote Control and `claude remote-control`.
- [Worktrees](https://code.claude.com/docs/en/worktrees): worktree sessions and `.worktreeinclude`.
- [Model configuration](https://code.claude.com/docs/en/model-config): the auto-compact window, automatic model fallback and the fallback model chain, and `opusplan`.
- [Fast mode](https://code.claude.com/docs/en/fast-mode): fast mode.
- [LLM gateway](https://code.claude.com/docs/en/llm-gateway): LLM gateways.
- [MCP](https://code.claude.com/docs/en/mcp): MCP servers and their dialogs.
