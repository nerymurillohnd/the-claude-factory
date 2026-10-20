# Debugging prompt, agent and background hooks

Read when one of these hooks does not fire, fires but has no effect, keeps blocking, loses its output, or is slow.

Every section carries a `Docs:` line: fetch that section with the method in the docs map before stating its facts as current. Checked against Claude Code 2.1.305 (2026-10-20).

## Contents

- Turn logging on
- Read the log
- Symptom → cause
- Version table

## Turn logging on

Docs: <https://code.claude.com/docs/en/hooks#debug-hooks> · <https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu> · <https://code.claude.com/docs/en/hooks-guide#check-what-a-hook-did>

| Way | Where the log goes |
| :-- | :-- |
| `claude --debug-file <path>` | `<path>`; follow it with `tail -f <path>` |
| `claude --debug` | `~/.claude/debug/<session-id>.txt` (nothing is printed to the terminal) |
| `/debug` mid-session | Turns logging on and shows the log path |
| `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` | Adds matcher counts and query-matching lines |

Also useful:

- `/hooks`: read-only list of every configured hook with its source (user, project, local, plugin, session). Select one to see what it runs and where it is defined. **All events** at the end of the list shows events with nothing configured.
- `Ctrl+O`: the transcript view, where block reasons, Stop hook feedback and hook error notices appear. It also turns on verbose mode, which shows async completion notices.

## Read the log

Docs: <https://code.claude.com/docs/en/hooks#debug-hooks> · <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> · <https://code.claude.com/docs/en/hooks-guide#fields-at-the-wrong-level> · <https://code.claude.com/docs/en/hooks-guide#shell-profile-output-before-the-json>

- A command hook on a tool event, `UserPromptSubmit`, `SessionStart`, `Stop` and several other events leaves a summary line when it finishes, whatever it printed (2.1.296 or later):
  `Hooks: <Event>:<matched value> [<command>] <plugin, if any> finished with status <n> (<ms>ms)`.
  Other endings: `timed out after <N>ms`, `cancelled`, `moved to the background`, `failed to start`. On `Notification`, `SessionEnd` and `PreCompact` the line reads `completed with status` with no duration.
- Plain-text stdout shows up as `Hook output does not start with {, treating as plain text`.
- Misplaced JSON fields show up as `Hook JSON output had unrecognized keys`.
- Async fields with the wrong type are named in a warning and dropped.
- A project subagent's skipped frontmatter hooks log an error with the trust key to set.
- A bare `$CLAUDE_PROJECT_DIR` in a PowerShell hook logs a warning.

The docs do not publish the log format for prompt and agent hook runs line by line. Search the log for the event name and the hook's `prompt` text, and say which lines you relied on. Do not invent a line format.

## Symptom → cause

Docs: <https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting> · <https://code.claude.com/docs/en/hooks-guide#hook-not-firing> · <https://code.claude.com/docs/en/hooks-guide#/hooks-shows-no-hooks-configured> · <https://code.claude.com/docs/en/hooks-guide#stop-hook-hits-the-block-cap> · <https://code.claude.com/docs/en/debug-your-config#check-hooks>

| Symptom | Check, in order |
| :-- | :-- |
| Prompt or agent hook never runs | 1. `/hooks` lists it under the right event. 2. The event accepts the type (agent hooks are skipped on `PermissionRequest`; `SessionStart`, `Setup` and most lifecycle events take neither). 3. `if` set on a non-tool event, where it never runs. 4. Matcher case: matchers are case-sensitive. 5. The source is trusted (settings file held back, project subagent frontmatter skipped). 6. `disableAllHooks` or `allowManagedHooksOnly` in effect |
| `/hooks` shows nothing after an edit | Invalid JSON (trailing comma, comments), wrong file location, a missed file-watcher reload (restart the session), or a plugin hook that needs `/reload-plugins` |
| Prompt hook ends the turn instead of letting Claude retry | `PreToolUse` or `PostToolUse` without `continueOnBlock: true` |
| `ok: false` changes nothing | Event is `PermissionRequest` or `PermissionDenied`, where it has no effect |
| Stop hook keeps Claude working, then a "blocked too many consecutive times" warning | The 8-block cap. The prompt ignores `stop_hook_active`, or the condition can never be met: add the `stop_hook_active` rule, let a prompt hook return `impossible: true`, or narrow the condition |
| Prompt or agent hook allows what its rule should block | Version before 2.1.294: upgrade |
| Prompt hook errors behind a gateway or on some providers | Structured outputs rejected: 2.1.288+ and `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` |
| Stop hook allows when it should block | The prompt asks the model about "the conversation" instead of `last_assistant_message` and the transcript fields it actually receives; or the default background model is too weak for the judgment (set `model`) |
| Agent hook ignores `model` | Version before 2.1.300 |
| Prompt or agent hook times out | `timeout` too low (30 s prompt, 60 s agent by default), or more than 12 prompt/agent hooks on one event so some wait (2.1.302+), or an agent prompt that sends it exploring; narrow the prompt |
| Verdicts flip between runs on the same input | Several rules in one prompt, a vague condition, or untrusted input steering the model; split the hook and tighten the prompt |
| Async result never reaches Claude | Session idle; `-p` teardown cancelled it; stdout had other text and the JSON was not on its own line; multi-line JSON before 2.1.295 |
| Async result partly missing | A field had the wrong type and was dropped (warning in the log) |
| Async hook runs forever | Expected: `timeout` is not enforced on `async`. Use `asyncRewake` with `timeout` when it must be bounded |
| Hook works in a terminal, not under `claude -p` | Async work cancelled at teardown, or a project subagent's frontmatter hook, which never runs under `-p` |
| PowerShell hook can't find its script | Bare `$CLAUDE_PROJECT_DIR`, or the placeholder inside single quotes |
| Script "command not found" | Relative path; use a placeholder, and `"args": []` for exec form |

After a fix, re-trigger the same event and quote the log line that changed.

## Version table

Docs: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md> · <https://code.claude.com/docs/en/changelog>

Behaviors this skill relies on that depend on the Claude Code version:

| Version | Change |
| :-- | :-- |
| 2.1.218 | Project subagent frontmatter hooks require that folder's trust; they never run under `-p` |
| 2.1.287 | `asyncRewake` with a missing script is reported once instead of waking Claude repeatedly |
| 2.1.288 | Prompt hooks work behind gateways that reject structured outputs; `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` added |
| 2.1.290 | Fixed an endless reply loop from a plugin's async Stop hook with an unquoted path containing a space |
| 2.1.294 | Prompt and agent hooks written as rules no longer allow what they should block; Stop and SubagentStop rule prompts judged better |
| 2.1.295 | Async hook JSON may span several lines when it is alone on stdout |
| 2.1.296 | `Hooks:` summary lines with outcome and duration in the debug log |
| 2.1.300 | Agent hooks honor `model`; an unavailable model falls back to the caller's |
| 2.1.302 | At most 12 prompt or agent hooks of one event run at a time |
| 2.1.304 | Skills from one source can register at most 1,024 hooks and 16,384 matcher characters per session |

Re-check the changelog for versions newer than 2.1.305 (no in-scope hook change in 2.1.305) before relying on this table.
