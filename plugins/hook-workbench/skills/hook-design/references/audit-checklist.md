# Audit checklist

Read when auditing prompt hooks, agent hooks, background hooks, or the security posture of any hook. Write the result with the [report template](../assets/report.md).

Mark every item **pass**, **fail** or **n/a**, with the file and line (or the doc section) as evidence. Severity for a failure: **blocker** (wrong behavior or a security exposure), **risk** (breaks under a stated condition), **improvement**.

## A. Every hook in scope

Docs: <https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents> · <https://code.claude.com/docs/en/hooks#common-fields> · <https://code.claude.com/docs/en/hooks#workspace-trust> · <https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields>

1. Its source is known: settings file and scope, plugin `hooks/hooks.json`, skill frontmatter or subagent frontmatter.
2. The source runs where the user expects, given workspace trust and the session type (interactive, `-p`, SDK).
3. No field that belongs to another hook type sits on it (`async`, `asyncRewake` or `shell` on a prompt or agent hook; `continueOnBlock` on an agent hook).
4. `timeout` is set explicitly and fits the work.
5. `if`, when present, sits only on a tool event; elsewhere the hook never runs.
6. `once` appears only in skill frontmatter.
7. Not declared in a plugin subagent's frontmatter, where `hooks` is ignored.

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

## E. PowerShell

Docs: <https://code.claude.com/docs/en/hooks#windows-powershell-tool>

1. `shell: "powershell"` is not combined with `args` (where it is ignored).
2. Placeholders use `${CLAUDE_PROJECT_DIR}` or `$env:CLAUDE_PROJECT_DIR`, never bare `$CLAUDE_PROJECT_DIR`.
3. No placeholder sits inside single quotes.

## F. Evidence of behavior

Docs: <https://code.claude.com/docs/en/hooks#debug-hooks> · changelog: <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>

1. Each claim about what a hook does at run time cites a debug-log line or a reproducible trigger, or is labeled untested.
2. Version-gated behavior is matched to the user's `claude --version`.
