---
name: plugin-hooks-guidance
description: Use when creating, editing or reviewing a plugin hook: hooks.json, hook scripts, matchers or README hook claims.
---

# Plugin hooks guidance

A hook runs on every user's machine, on every matching event, without anyone watching. When it is wrong it either blocks work it should not or silently lets through what it should stop, and neither shows up in a test that only checks the happy path. This skill covers a plugin hook from the decision to write it to the README that states what it does not reach. It runs inside `plugin-development` whenever the component is a hook.

## Role

Act as a hook engineer who assumes the hook will meet hostile input, a missing interpreter and an unusual shell. You write the smallest hook that does the job, you make it fail loudly, and you claim in the README only what you tested.

## Rules

- A hook is a barrier for Claude, not a security boundary: it never sees what a person types in their own terminal. A hard allow or deny belongs to permissions; say so in the README.
- Never put `if` on a hook that enforces a policy: the filter is best-effort. Filter inside the script, on the words after lexing, never on the raw text.
- A hook that enforces a policy sets `"onFailure": "block"`, so a broken hook never passes in silence. A hook that only advises or observes does not: on `UserPromptSubmit` a failure with `block` blocks the prompt itself, so a reminder that crashes would stop every prompt. Leave it at `"continue"`.
- A guard that cannot read or parse its own input denies the call and says why. A raw-text test is acceptable only to decide to deny when the interpreter is missing, never to let a call pass.
- Claim coverage in the README only after step 6 has tested it.
- Do not propose or build a hook that reminds Claude to invoke an LSP intelligence skill before the first edit until Nery reports skipped skills: recall memory `deferred-pretooluse-skill-reminder`. That memory covers only that reminder; other advisory hooks are not held back by it.

## Gotchas

- `timeout` defaults to 600 seconds for `command`, `http` and `mcp_tool` hooks, but to 30 on `UserPromptSubmit`, `PreModelSwitch` and `PostModelSwitch`, 10 on `MessageDisplay`, 30 for `prompt` hooks and 60 for `agent` hooks. `SessionEnd` hooks share a 1.5-second budget that a plugin hook's `timeout` does not raise. Set `timeout` on every handler.
- `"onFailure": "block"` works on `command` and `http` hooks only. It has no effect on `Stop`, `SubagentStop`, `TaskCompleted` or `TeammateIdle`, or on background hooks (`async`, `asyncRewake`). Declaring it makes Claude Code 2.1.295 the plugin's minimum.
- A matcher made only of letters, digits, `_`, `-`, spaces, `,` and `|` is an exact tool-name match, so `Bash` does not cover `PowerShell`. A matcher for MCP tools needs `.*` (`mcp__<server>__.*`), and a plugin-bundled server's tools are named `mcp__plugin_<plugin>_<server>__<tool>`.
- `if` holds exactly one permission rule; `|`, `&&` and lists never match. Leading `VAR=value` assignments are stripped; treat `sudo`, `env`, `xargs`, `watch` and `bash -c` as not stripped until a test shows otherwise. When Claude Code cannot tell what a Bash command runs, it runs the hook anyway.
- Hooks that match one event run in parallel, and the strictest decision wins: `deny`, then `defer`, `ask`, `allow`.
- Plugin hooks run inside subagents, and the input then carries `agent_id` and `agent_type`.
- A hook in `settings.json` loads on save; a plugin hook needs `/reload-plugins`.
- Plugin hooks and LSP servers get no shell profile, so `node`, `tsc` and other tools from a version manager are not on `PATH` unless the hook resolves them.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| Another skill invoked you (`plugin-development`, `plugin-consistency`) | Nothing: hand back to it. `plugin-development` runs `plugin-consistency` once at its end |
| You loaded this skill alone | `plugin-consistency`, when step 7 is done |
| The hook matches an MCP tool of this plugin | `plugin-mcp-guidance`, for the scoped tool name |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.

## Workflow

Tick each step as you finish it, in order. A later step assumes the earlier ones are settled.

Progress:
- [ ] 1. **Intent**: enforce, advise or observe, and on which event.
- [ ] 2. **Declare**: `hooks/hooks.json`, command, timeout.
- [ ] 3. **Filter**: matcher and in-script filtering.
- [ ] 4. **Decide**: the output that blocks or passes.
- [ ] 5. **Fail**: what happens when the hook breaks.
- [ ] 6. **Test**: adverse conditions before any claim.
- [ ] 7. **Document**: Limitations in the README.

## Step details

### 1. Intent

Decide what the hook is for before you write it: to enforce a policy (deny a call), to advise (add context for Claude) or to observe (log or react). The answer sets the event, whether `onFailure` is `block`, and what the README may promise. Read `/en/hooks` and `/en/hooks-guide` first; the event list, input fields and exit-code behavior per event change between releases.

### 2. Declare

- Declare the hook in `hooks/hooks.json`, with the three levels: event, matcher group, handler. The input arrives as JSON on stdin; never write a `"hook"` object and never read `$TOOL_INPUT`.
- Write the command in shell form with the placeholder in double quotes: the variable `CLAUDE_PLUGIN_ROOT`, wrapped as `${…}`, followed by `/hooks/<script>`, inside escaped quotes in the JSON string. Exec form (`args`) needs a real `.exe` on Windows, and Windows runs only through Git Bash here.
- Set `timeout` on every handler.
- Start the script with `#!/usr/bin/env <interpreter>`, as `plugin-development` says. Resolve `node` and `tsc` across every Node manager inside the script.

### 3. Filter

- Pick the narrowest matcher that is still exact, and add one handler per tool when you cover Bash and PowerShell.
- Do the real filtering inside the script, on the words after lexing. The shell joins quotes, so `g"i"t commit --no-verify` runs git and contains no `git` substring. Parsing costs far less than starting an interpreter.
- Where `if` is allowed because nothing is enforced, write one permission rule per field.

### 4. Decide

- To block, print one JSON object on stdout and exit 0, with `permissionDecisionReason` telling Claude what to do instead. Exit 2 with a reason on stderr also blocks. Exit 1 never blocks.
- Print nothing else on stdout: a second line turns the output into plain text or a parse failure.
- To pass a call, print nothing and exit 0. Silence leaves the decision to the permission flow; it never approves.

Example, a PreToolUse deny:

```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Run the commit without --no-verify so the repo's hooks run."}}
```

### 5. Fail

- A hook that runs an interpreter starts from a launcher script that checks the interpreter and its minimum version first. When either is missing, the launcher prints `systemMessage` and `additionalContext` and exits 0, because with `"onFailure": "block"` a missing interpreter would block every call, not only the guarded ones.
- A guard whose job is to deny is the exception: when its tool is missing it denies the commands it guards and says what to install.
- Past those checks, a crash, a timeout or an exit code other than 0 or 2 blocks. That is the intent.

### 6. Test

1. Run the script by hand with a minimal environment, once per interpreter manager the hook depends on: `env -i HOME= PATH=/usr/bin:/bin ./hooks/<script> < input.json`, with `input.json` built from a quoted heredoc.
2. Test one call made from a subagent before the README says the hook covers them.
3. Test in `default` and in `bypassPermissions` mode before the README states what the hook blocks: the docs do not say it runs in both. Start the session in each mode as `/en/permission-modes` describes.
4. Run `claude plugin validate --strict plugins/<name>` and the plugin's tests, which live in `scripts/tests/<plugin>/`: `node --test` for `*.test.mjs`, and `python3 -m unittest discover` plus `by_path.sh` for a Python script, as `.claude/CLAUDE.md` → Commands lists them. Break the rule on purpose once and confirm a test fails.
5. Reload with `/reload-plugins` after each edit and test again.

### 7. Document

Under Limitations in the README, name what the hook does not reach:

- a tool the matcher leaves out, such as the PowerShell tool when `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` turns it on;
- the policies that turn hooks off, `allowManagedHooksOnly` and `disableAllHooks`;
- the surfaces where it does not run, per `docs/compatibility.md`.

Add the barrier-not-boundary statement from the Rules, with the matching permission rule for users who need a hard block. Then hand off as the table above says.
