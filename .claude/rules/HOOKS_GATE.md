---
paths:
  - "plugins/*/hooks/**"
---

# Hooks Gate

- Source: <https://code.claude.com/docs/en/hooks>. Re-read the sections named below before changing a rule: the page moves.
- This file adds to the hook bullets in `.claude/CLAUDE.md` (Plugin Development). It never repeats them.

## Declare

- Use the three levels of `hooks/hooks.json`: event, matcher group, handler. The contract is JSON on stdin. Never write a `"hook"` object or read `$TOOL_INPUT`.
- Write the command in shell form with the placeholder in double quotes: `"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/<script>\""`. Exec form (`args`) needs a real `.exe` on Windows, and Windows runs only through Git Bash here.
- Set `timeout` on every handler. A command hook defaults to 600 seconds.
- A matcher of letters, digits, `_`, `-` and `|` is an exact tool-name match. `Bash` does not cover `PowerShell`.

## Decide

- Block with one JSON object on stdout and exit 0: `hookSpecificOutput.hookEventName` `"PreToolUse"`, `permissionDecision` `"deny"`, and a `permissionDecisionReason` that tells Claude what to do instead. Exit 2 with a reason on stderr blocks too. Exit 1 never blocks.
- Print nothing else on stdout. A second line turns the output into plain text or a parse failure.
- To pass a call, print nothing and exit 0. Silence leaves the decision to the permission flow; it never approves.
- A guard that cannot read or parse its own input denies the call and says why.

## Filter

- Never put `if` on a hook that enforces a policy. The page calls the filter best-effort: it strips leading `VAR=` assignments, and the permissions page strips only `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin` and `noglob`. Treat `sudo`, `env`, `xargs`, `watch` and `bash -c` as not stripped until a test shows otherwise, so `if: "Bash(git *)"` would skip `sudo git commit --no-verify`.
- Filter inside the script instead: exit early on a cheap, case-insensitive check of the command text, before any parsing.

## Fail

- Declaring `onFailure` makes Claude Code 2.1.295 the plugin's minimum. Older versions let a hook that cannot start pass the call.
- A hook that runs an interpreter starts from a launcher script. The launcher checks the interpreter and its minimum version first. When either is missing it prints `systemMessage` and `additionalContext` and exits 0, because with `"onFailure": "block"` a missing interpreter would block every call, not only the guarded ones.
- Past that check, a crash, a timeout or an exit code other than 0 or 2 blocks. That is the intent.

## Cover

- Plugin hooks also run inside subagents. The input carries `agent_id` and `agent_type`. Test one call made from a subagent before the README says the hook covers them.
- Test the hook in `default` and in `bypassPermissions` mode before the README states what it blocks. The page does not say the hook runs in both.
- Hooks that match one event run in parallel, and the strictest decision wins: `deny`, then `defer`, `ask`, `allow`.

## Document

- Under Limitations in the README, name what the hook does not reach:
  - a tool the matcher leaves out, such as the PowerShell tool when `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` turns it on;
  - the policies that turn hooks off, `allowManagedHooksOnly` and `disableAllHooks`;
  - the surfaces where it does not run, per [compatibility](../../docs/compatibility.md).
- State that a hook is a barrier for Claude, not a security boundary, and that it never sees what a person types in their own terminal. The page says to enforce a hard allow or deny through permissions.
