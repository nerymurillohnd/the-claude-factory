# Background hooks: `async` and `asyncRewake`

Read when a command hook should run without blocking Claude, or when a background hook's result never arrives.

Every section carries a `Docs:` line: fetch that section with the method in the docs map before stating its facts as current. Checked against Claude Code 2.1.305 (2026-10-20).

## Contents

- The two flags
- What a background hook can and cannot do
- Output rules
- Timeouts and session end
- Visibility
- Worked example
- Common mistakes

## The two flags

Docs: <https://code.claude.com/docs/en/hooks#command-hook-fields> · <https://code.claude.com/docs/en/hooks#configure-an-async-hook>

| Field | Behavior |
| :-- | :-- |
| `async: true` | Starts the command and continues at once. When the process exits, its `additionalContext` and `systemMessage` reach Claude on the next conversation turn |
| `asyncRewake: true` | Runs in the background too. Exit code 2 wakes Claude, even when the session is idle, and shows the hook's stderr (or stdout when stderr is empty) to Claude as a system reminder |

Both exist only on `type: "command"` hooks. On a prompt, agent, HTTP or MCP tool hook they are not valid fields; flag them.

## What a background hook can and cannot do

Docs: <https://code.claude.com/docs/en/hooks#run-hooks-in-the-background> · <https://code.claude.com/docs/en/hooks#limitations>

- It cannot block or steer. `decision`, `permissionDecision` and `continue` have no effect, because the action already completed.
- It receives the same JSON input on stdin as a synchronous hook.
- Each execution is a separate process. A hook on a frequent event (every `Write`) can stack several runs; make the script safe to run concurrently, or debounce inside it.
- If the result must gate the next action, a background hook is the wrong tool. Say so and keep the part that fits.

## Output rules

Docs: <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> · changelog 2.1.295: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>

Claude Code delivers two fields from the hook's JSON response: `additionalContext` (inside `hookSpecificOutput`, with `hookEventName`) and `systemMessage`.

- Neither field is shown to the user, unlike a synchronous hook's `systemMessage`.
- Print the JSON either alone on stdout or on one line of its own:
  - **Alone on stdout**: may span several lines, such as pretty-printed `jq` output. Requires Claude Code 2.1.295 or later; earlier versions ignored multi-line output.
  - **On a line of its own**: other text may surround it if the JSON fits on one line, such as `jq -c` output.
- The response is validated against the same output schema as synchronous hooks. A field with the wrong type, such as a non-string `systemMessage`, is dropped, not delivered. `--debug` logs a warning naming each dropped field.
- Build the JSON with an encoder (`jq -n --arg`, `json.dumps`, `JSON.stringify`), never by string concatenation: test output full of quotes breaks hand-built JSON.

## Timeouts and session end

Docs: <https://code.claude.com/docs/en/hooks#configure-an-async-hook> · <https://code.claude.com/docs/en/hooks#common-fields> · <https://code.claude.com/docs/en/hooks#limitations>

- `timeout` is not enforced on an `async` hook once it runs in the background. It is enforced on `asyncRewake`.
- Results are delivered only while the session runs. If the session is idle, an `async` result waits for the next user interaction; only an `asyncRewake` exit 2 wakes Claude.
- In `claude -p`, any background hook still running at teardown is killed and finalized as `cancelled`. Work that must outlive a `-p` run has to start a fully detached process from the hook.

## Visibility

Docs: <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> · <https://code.claude.com/docs/en/hooks#debug-hooks>

- Completion notifications for async hooks are hidden by default. Turn on verbose mode with `Ctrl+O`, or start with `--verbose`.
- In the debug log a background run can end as `moved to the background`; see `debugging.md` → Read the log.

## Worked example

Docs: <https://code.claude.com/docs/en/hooks#run-tests-after-file-changes> · <https://code.claude.com/docs/en/hooks#exec-form-and-shell-form>

Runs tests after a source file is written and tells Claude the result on the next turn. Script at `.claude/hooks/run-tests-async.sh`, executable:

```bash
#!/usr/bin/env bash
input=$(cat)
file_path=$(printf '%s' "${input}" | jq -r '.tool_input.file_path // empty')

case "${file_path}" in
  *.ts | *.js) ;;
  *) exit 0 ;;
esac

if result=$(npm test 2>&1); then
  msg="Tests passed after editing ${file_path}"
else
  msg="Tests failed after editing ${file_path}: ${result}"
fi
jq -nc --arg msg "${msg}" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $msg}}'
```

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/run-tests-async.sh",
            "args": [],
            "async": true
          }
        ]
      }
    ]
  }
}
```

`"args": []` selects exec form, so the path placeholder needs no quoting. To be woken on failure instead of waiting for the next turn, switch to `asyncRewake: true`, print the failure to stderr and exit 2; set a `timeout`, since it is enforced there.

## Common mistakes

Docs: <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> · <https://code.claude.com/docs/en/errors#hook-needs-quotes-around-a-path-with-a-space> · changelog 2.1.287, 2.1.290, 2.1.295: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>

| Symptom | Cause |
| :-- | :-- |
| Claude never mentions the result | Session idle (use `asyncRewake`), `-p` teardown cancelled it, or the JSON was not alone on stdout or on its own line |
| Result ignored on an older version | Multi-line JSON before 2.1.295 |
| One field arrives, another does not | Wrong type; the debug log names the dropped field |
| Hook "blocks" nothing | Expected: background hooks never decide |
| `asyncRewake` wakes Claude again and again when its script is missing | Fixed in 2.1.287, which reports the broken hook once; fix the script path |
| A slow async hook never times out | Expected for `async`; only `asyncRewake` enforces `timeout` |
| Endless replies from a plugin's async Stop hook under a path with a space (such as `Application Support`) | Unquoted path in shell form; fixed in Claude Code 2.1.290, and quoting or exec form avoids it on any version |
| "Hook needs quotes around a path with a space" notice | An `asyncRewake` shell-form hook runs an interpreter followed by an unquoted path placeholder that resolves to a path with a space; wrap the path in double quotes |
