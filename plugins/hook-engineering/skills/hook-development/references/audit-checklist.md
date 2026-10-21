# Audit checklist

Read when auditing any hook: its configuration, its input and output, its event, prompt, agent and background hooks, the security posture, and the mods in the same session. Write the result with the [report template](../assets/report.md).

Mark every item **pass**, **fail** or **n/a**, with the file and line (or the doc section) as evidence. Severity for a failure: **blocker** (wrong behavior or a security exposure), **risk** (breaks under a stated condition), **improvement**.

Give each finding an impact label too, and rank findings by it:

| Impact label | Class | Severity |
| :-- | :-- | :-- |
| `never runs`, `ignored field`, `ignored output` | broken (never runs or never takes effect) | blocker |
| `runs on the wrong calls`, `blocks wrongly` | broken when it hits a real call; fragile when it needs an unlikely input | blocker or risk |
| `fails open` | unsafe (enforcement that can be bypassed or fails open) | blocker |
| (none of the above; works now, breaks on a likely input) | fragile | risk |
| `style` | cleanup | improvement |

## Contents

- A. Every hook in scope
- B. Prompt and agent hooks
- C. Background hooks
- D. Scripts and security
- E. PowerShell
- F. Evidence of behavior
- G. Configuration
- H. Input and output
- I. Events and wiring
- J. Mods

## A. Every hook in scope

Docs: <https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents> · <https://code.claude.com/docs/en/hooks#common-fields> · <https://code.claude.com/docs/en/hooks#workspace-trust> · <https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields>

1. Its source is known: settings file and scope, plugin `hooks/hooks.json`, skill frontmatter or subagent frontmatter.
2. The source runs where the user expects, given workspace trust and the session type (interactive, `-p`, SDK).
3. No field that belongs to another hook type sits on it (`async`, `asyncRewake` or `shell` on a prompt or agent hook; `continueOnBlock` on an agent hook).
4. `timeout` is set explicitly and fits the work.
5. `if`, when present, sits only on a tool event; elsewhere the hook never runs.
6. `once` appears only in skill frontmatter.
7. Not declared in a plugin subagent's frontmatter, where `hooks` is ignored.
8. `"onFailure": "block"` only on hooks that enforce a policy. An advisory hook (a reminder on `UserPromptSubmit`) keeps `continue`, or one failure blocks every prompt.

## B. Prompt and agent hooks

Docs: <https://code.claude.com/docs/en/hooks#prompt-based-hooks> · <https://code.claude.com/docs/en/hooks#response-schema> · <https://code.claude.com/docs/en/hooks#agent-based-hooks> · <https://code.claude.com/docs/en/hooks#stop-input>

1. The event accepts the type (agent hooks: not `PermissionRequest`; neither on `SessionStart`, `Setup` or the lifecycle-only events).
2. The prompt states one rule or one condition.
3. `$ARGUMENTS` is placed deliberately; literal dollars are escaped (`\$`).
4. The prompt names the input fields it relies on and asks for `{"ok": ...}` with an actionable `reason`.
5. The configured `ok: false` behavior is what the author intends for that event (turn ends vs. continues; `continueOnBlock`).
6. `Stop` / `SubagentStop`: the prompt handles `stop_hook_active`; a prompt hook uses `impossible` when the condition can be unreachable.
7. `model` is set when the default background model is not enough, and left unset otherwise.
8. Cost: on a frequent event, a matcher (and `if` on tool events) limits how often it runs; no more than 12 prompt/agent hooks pile onto one event without reason.
9. Agent hook: the author accepts that it is experimental; any dependence on running commands is verified on the user's version.
10. The hook is not the only guard for something that must never happen; enforcement lives in permissions.

## C. Background hooks

Docs: <https://code.claude.com/docs/en/hooks#run-hooks-in-the-background> · <https://code.claude.com/docs/en/hooks#how-async-hooks-execute> · <https://code.claude.com/docs/en/hooks#limitations>

1. `async` / `asyncRewake` sit on a `type: "command"` hook.
2. Nothing downstream expects the hook to block or decide.
3. The script prints its JSON alone on stdout or on one line of its own, built with an encoder.
4. Delivered fields have the right types (`additionalContext` inside `hookSpecificOutput` with `hookEventName`; `systemMessage` a string).
5. Multi-line JSON only when the user runs 2.1.295 or later.
6. Unbounded work: `asyncRewake` with a `timeout`, or a documented reason it may run long.
7. `-p` use: no result that must survive teardown, or a detached process for work that must outlive the session.
8. Concurrent runs are safe.

## D. Scripts and security

Docs: <https://code.claude.com/docs/en/hooks#security-best-practices> · <https://code.claude.com/docs/en/hooks#workspace-trust> · <https://code.claude.com/docs/en/hooks#reference-scripts-by-path>

1. Input is parsed as data and validated; nothing from input is evaluated or interpolated into a command.
2. Every variable and substitution is quoted.
3. Paths from input are checked for `..` and confined to the intended root.
4. Scripts are referenced through a path placeholder; shell form quotes it, exec form uses `args`.
5. No sensitive file (`.env`, `.git/`, keys) is read, printed or forwarded into Claude's context.
6. Repository-supplied hooks under `-p`: a stated mitigation (`--bare`, `--settings '{"disableAllHooks": true}'`, `--setting-sources user`, or a review).
7. Scripts that must act where Claude works read `cwd` from input, not `${CLAUDE_PROJECT_DIR}`.
8. A guard that cannot read or parse its input blocks and says why (exit 2 or a deny), and still does when `jq` is missing. Probe it with garbage and with a missing field.
9. A command filter compares parsed words (`shlex`), not raw text: `g"i"t commit` must not slip past.
10. Every tool the script calls resolves in a non-interactive shell; nothing depends on `~/.zshrc`.

## E. PowerShell

Docs: <https://code.claude.com/docs/en/hooks#windows-powershell-tool>

1. `shell: "powershell"` is not combined with `args` (where it is ignored).
2. Placeholders use `${CLAUDE_PROJECT_DIR}` or `$env:CLAUDE_PROJECT_DIR`, never bare `$CLAUDE_PROJECT_DIR`.
3. No placeholder sits inside single quotes.

## F. Evidence of behavior

Docs: <https://code.claude.com/docs/en/hooks#debug-hooks> · changelog: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>

1. Each claim about what a hook does at run time cites a debug-log line or a reproducible trigger, or is labeled untested.
2. Version-gated behavior is matched to the user's `claude --version`.

## G. Configuration

Docs: <https://code.claude.com/docs/en/hooks#configuration> · <https://code.claude.com/docs/en/hooks#hook-locations> · <https://code.claude.com/docs/en/hooks#matcher-patterns> · <https://code.claude.com/docs/en/hooks#hook-handler-fields>

1. Every hooks source in play is read: user, project and local settings, `hooks/hooks.json`, skill and agent frontmatter, and managed settings if present.
2. Run the linter on every hooks file in play, then confirm in `/hooks` that the hook is registered where you expect. Frontmatter hooks are YAML: check those by hand against the same rules.
3. The policies that can turn hooks off are checked (`disableAllHooks`, `allowManagedHooksOnly`).

## H. Input and output

Docs: <https://code.claude.com/docs/en/hooks#hook-input-and-output> · <https://code.claude.com/docs/en/hooks#exit-code-output> · <https://code.claude.com/docs/en/hooks#json-output>

1. Every hook script is read with the event it serves, and checked against the skill: stdout discipline, exit codes, field names and placement, fields the event ignores or discards, timeouts, background processes, failure handling, caps, Windows behavior if the hook can run there.
2. Run the probe on the hook as configured: the same command, the same sample event.

## I. Events and wiring

Docs: <https://code.claude.com/docs/en/hooks#hook-events> · <https://code.claude.com/docs/en/hooks#matcher-patterns>

For each hook, check against the skill:

- Event exists and is spelled correctly; matcher values exist for that event; matcher set on an event without matcher support (silently ignored); regex vs exact-match pitfalls (`Edit.*` hits `NotebookEdit`, unanchored plugin agent names, `FileChanged` literal filenames).
- Handler type is supported by the event (e.g. `prompt` on `SessionStart` never runs; `agent` on `PermissionRequest` is skipped; plugin agent frontmatter `hooks` is ignored).
- Output uses the field that event actually reads (deprecated `PreToolUse` top-level `decision`, exit 2 on `PermissionRequest`, `additionalContext` on events that discard it, `updatedInput` missing unchanged fields).
- Timeouts that will bite (`UserPromptSubmit` 30 s, `SessionEnd` 1.5 s, `MessageDisplay` 10 s, `PreModelSwitch` timeout blocks).
- No hook relies on the order of other hooks on the same event; merge precedence is documented only for PreToolUse, PreModelSwitch and Elicitation (`lifecycle.md`).
- Loops, fail-open vs fail-closed behavior, and hooks relied on for enforcement that a path bypasses (`@` mentions vs `PreToolUse` on `Read`, Bash writes vs `PostToolUse` on `Edit|Write`, `PowerShell` vs `Bash`).
- Deprecated or removed values (`bypass_permissions_disabled`, `team_name`) and version-gated fields the installed version may lack.

## J. Mods

Docs: <https://code.claude.com/docs/en/plugins/mods/events#where-settings-hooks-run-in-the-order> · <https://code.claude.com/docs/en/permissions#precedence-among-rules-hooks-and-mods>

1. The mods the session loads are known (`/plugin` shows `N mod active · <names>`), and which of them hook `tool.call`, `tool.check` or `classic.*` (`claude plugin validate <dir>` lists their `hooks:`).
2. A hook relied on for enforcement is not undone by a mod: a mod that answers `tool.call` without `next` keeps non-managed settings `PreToolUse` hooks from running, and without managed settings or a Team or Enterprise `/login` a mod's `tool.check` approval gets past a `PreToolUse` block (`mods-and-hooks.md`).
