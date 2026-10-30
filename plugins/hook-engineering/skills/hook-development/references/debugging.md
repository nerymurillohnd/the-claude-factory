# Debugging hooks

Read when a hook has no effect, has the wrong effect, shows an error notice, or you need to read the debug log. Source: <https://code.claude.com/docs/en/hooks#debug-hooks> and the input/output sections of the same page.

Also read when a prompt, agent or background hook does not fire, fires but has no effect, keeps blocking, loses its output, or is slow. Before you state a section's facts as current, fetch its `Docs:` section with the method in `docs-map.md`.

## Contents

- Collect evidence first
- Turn logging on
- Read the log
- A hook that never runs or does nothing
- Symptom → cause → check
- Prompt, agent and background hooks: symptom → cause
- Common mistakes
- Reproduce without Claude Code

## Collect evidence first

Docs: [debug hooks](https://code.claude.com/docs/en/hooks#debug-hooks) · [debug your config](https://code.claude.com/docs/en/debug-your-config)

1. The exact hook entry as configured: event, command (shell or exec form), `timeout`, `onFailure`, `async`.
2. A real input sample for that event. The most reliable source is a temporary hook that writes stdin to a file: `cat > "$CLAUDE_PROJECT_DIR/.claude/last-input.json"`. Remove it afterwards.
3. The installed version: `claude --version`.
4. The debug log: start with `claude --debug` (file at `~/.claude/debug/<session-id>.txt`) or `claude --debug-file <path>`. `--debug` prints nothing to the terminal. `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` adds matcher counts.
5. Run the probe with that input and command: the probe command in `SKILL.md` → Verify, with `--input sample.json -- <command>`.

Useful log lines:

- `Hook <Event>:<matcher> (<Event>) success:` followed by the stdout.

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
  Other endings: `timed out after <N>ms`, `cancelled`, `moved to the background`, `failed to start`. On `Notification`, `SessionEnd` and `PreCompact` the line reads `completed with status` with no duration. Use the duration to find slow hooks.
- Plain-text stdout shows up as `Hook output does not start with {, treating as plain text`.
- Misplaced JSON fields show up as `Hook JSON output had unrecognized keys`.
- Async fields with the wrong type are named in a warning and dropped.
- A project subagent's skipped frontmatter hooks log an error with the trust key to set.
- A bare `$CLAUDE_PROJECT_DIR` in a PowerShell hook logs a warning.

The docs do not publish the log format for prompt and agent hook runs line by line. Search the log for the event name and the hook's `prompt` text, and say which lines you relied on. Do not invent a line format.

## A hook that never runs or does nothing

Docs: [hook not firing](https://code.claude.com/docs/en/hooks-guide#hook-not-firing) · [hook JSON has no effect](https://code.claude.com/docs/en/hooks-guide#hook-json-has-no-effect)

A hook that "never runs" is usually: wrong event, matcher on the wrong field or an exact string where a regex was meant, `if` on a non-tool event, a handler outside a `hooks` array, a script path the shell can't find, a plugin not reloaded, or a policy (`disableAllHooks`, `allowManagedHooksOnly`) turning it off.

A hook that "does nothing" is usually one of: stdout not a lone JSON object, wrong `hookEventName`, a field this event ignores, exit 1 meant as a block, a timeout without `onFailure`, or a script path that never ran. The table below maps each symptom to its check.

A mod in the same session can also be the cause: one that answers `tool.call` without calling `next` keeps non-managed settings `PreToolUse` hooks from running (managed ones run before mods), and one whose `tool.check` approves a call can get past a `PreToolUse` block. Check `/plugin` for `N mod active` and read `mods-and-hooks.md`.

## Symptom → cause → check

Docs: [hook input and output](https://code.claude.com/docs/en/hooks#hook-input-and-output) · [limitations and troubleshooting](https://code.claude.com/docs/en/hooks-guide#limitations-and-troubleshooting)

| Symptom | Likely cause | Check or fix |
| :-- | :-- | :-- |
| JSON decision ignored, no error | Other text on stdout (profile banner, `echo`, a tool's output) made it plain text | Probe shows `stdout: plain`. Print only the object; send everything else to stderr or `/dev/null` |
| `hook error` notice with a parse or validation message | Unparseable JSON, unknown keys, wrong types, or several JSON lines where one sets a field | Build JSON with `jq -n`/`json.dumps`; compare field names with the event's entry in its `events-*.md` file |
| Fields ignored, valid JSON | `hookEventName` missing or not the exact event name; a field the event doesn't honor; a field the event discards | Probe `check:` lines; the event's `events-*.md` entry |
| Tool works in your terminal but `command not found` inside the hook | Hooks run in non-interactive shells; a version manager that sets `PATH` from the profile may not have run (inference: the docs only say the shell is non-interactive) | Log `command -v <tool>` and `$PATH` to stderr and read the debug log; resolve the tool in the script or use an absolute path (`security-and-trust.md` → Guards) |
| A guard lets a call through when its input is odd | It swallowed a parse error or a missing `jq` and exited 0 | Probe it with garbage and with input missing the field: it must exit 2 or deny (`security-and-trust.md` → Guards) |
| "Block" doesn't block | Exit 1 instead of 2; or exit 2 on an event that can't block (PermissionRequest, PostToolUse, SessionStart…) | Use exit 2 or the event's decision field |
| Deny works but Claude retries blindly | `permissionDecisionReason` only says what was refused | Say what to do instead |
| `allow` ignored for AskUserQuestion or ExitPlanMode | `allow` without `updatedInput` holding the answer | Return both |
| `allow` still prompts or is denied | A deny or ask rule matched; the action is one no mode auto-approves; `updatedInput` with unknown keys or rejected input (v2.1.300+) | Permission rules win; fix the rewritten input |
| Hook "passes everything" | It times out or can't start, and onFailure isn't `block` | Notice says `Failed with non-blocking status code` or nothing; set `onFailure: "block"` (v2.1.295+) |
| Notice carries `No such file or directory` | Script path in the config is wrong; the hook never ran | Fix the path; quote `${CLAUDE_PLUGIN_ROOT}`/`${CLAUDE_PROJECT_DIR}` |
| Deny printed but call went ahead | The decision was printed by a background child after the hook exited | Print the decision before starting background work; redirect its output |
| Call blocked with `refusing to honor the suspect capture` | Hook printed an allow and left a background process holding stdout | Redirect the background process: `>/dev/null 2>&1 &` |
| Context never reaches Claude | Plain stdout on an event that logs it; stderr on exit 0; output over 10,000 chars (Claude gets a path) | Use `additionalContext`; keep it under the cap |
| Context reaches the user instead of being used | Text written as system commands tripped prompt-injection defenses | Rewrite as factual statements |
| Stop hook loops or stops after 8 rounds | `stop_hook_active` not checked; the 8-continuation cap | Return early when `stop_hook_active` is true |
| Stale values after resume | `additionalContext` is replayed from the transcript | Refresh in SessionStart (`source: "resume"`) |
| Windows: `blocking because Git Bash wasn't found` | Shell-form hook ran in PowerShell | See `exit-codes.md` → Windows without Git Bash |
| ElicitationResult turns declines into accepts | Hook returns `accept` without checking input `action` | Return `accept` only when input `action` is `accept` |
| `updatedToolOutput` ignored | Value doesn't match the built-in tool's output shape | Match the shape (Bash: `stdout`, `stderr`, `interrupted`, `isImage`) |
| `PreToolUse` hook listed in `/hooks` never runs, no error | A mod answered `tool.call` without calling `next` (not for a managed hook, which runs before mods) | `/plugin` mod line; `claude plugin validate <mod dir>` lists its `tool.call` hook; `mods-and-hooks.md` |
| A `PreToolUse` block or deny did not hold, no hook error | A mod's `tool.check` approved the call (no managed settings or Team/Enterprise `/login`) | `/plugin` mod line; `mods-and-hooks.md` → Mods and hook decisions |

## Prompt, agent and background hooks: symptom → cause

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

## Common mistakes

Docs: [hook events](https://code.claude.com/docs/en/hooks#hook-events)

| Mistake | Fix |
|---|---|
| Matching `Edit\|Write` to catch every change to a file | Bash and outside processes bypass it; use `FileChanged` (can't block) or match `*` + `git status --porcelain` |
| Expecting `PreToolUse` to fire for `@file` mentions | `@` contents are inlined without a tool call; add a `Read` deny rule or set `CLAUDE_CODE_DISABLE_FILE_MENTIONS=1` (v2.1.299+) |
| Shell hook matcher only `Bash` | On Windows PowerShell may be the only shell; match `Bash\|PowerShell` |
| Path checks with `/src/` on Windows | `file_path` arrives with backslashes; normalize separators first |
| `Stop` hook that always blocks | Check `stop_hook_active`; Claude Code overrides after 8 consecutive continuations (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) |
| `FileChanged` matcher `^\.env` or `*` | Matcher segments are literal filenames for the watch list |
| `updatedInput` with only changed fields, or extra keys | It replaces the whole input object; include unchanged fields. Unknown keys are dropped and invalid input denies the call *(changelog v2.1.300)* |
| `UserPromptSubmit` slow hook | Default timeout is 30 s and timeout discards its context; `SessionEnd` default is 1.5 s |
| `defer` in an interactive session or a multi-tool turn | Honored only with `-p` and a single tool call in the turn |

## Reproduce without Claude Code

```bash
# exit code and raw streams
./hook.sh < sample.json > out.txt 2> err.txt; echo "exit=$?"
# is stdout one JSON object?
jq -e 'type == "object"' out.txt
```

Then run the probe for the event-aware prediction. Reproduce in a clean environment too (`env -i HOME="$(mktemp -d)" PATH=/usr/bin:/bin ./hook.sh < sample.json`): a hook inherits the environment of the process that started Claude Code, which may not be your terminal's (for example the desktop app), so a tool your terminal finds can be missing.
