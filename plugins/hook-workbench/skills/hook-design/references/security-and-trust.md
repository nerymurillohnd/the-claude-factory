# Security, workspace trust and PowerShell

Read when a hook runs a script, ships inside a repository, plugin, skill or subagent, runs under `claude -p` or the SDK, or targets Windows PowerShell.

Every section carries a `Docs:` line: fetch that section with the method in the docs map before stating its facts as current. Checked against Claude Code 2.1.305 (2026-10-20).

## Contents

- What a hook can do to the machine
- Workspace trust, by where the hook lives
- Running over a repository you did not write
- Safe-script practice
- Prompt and agent hooks are not a security boundary
- Windows PowerShell

## What a hook can do to the machine

Docs: <https://code.claude.com/docs/en/hooks#disclaimer>

Command hooks run shell commands with the user's full permissions: they can read, change or delete anything the account can. Review and test every hook before adding it, including hooks that arrive with a repository or a plugin.

## Workspace trust, by where the hook lives

Docs: <https://code.claude.com/docs/en/hooks#workspace-trust> · <https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents> · <https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder> · <https://code.claude.com/docs/en/sub-agents#hooks-in-subagent-frontmatter>

| Where the hook is defined | Interactive session | `claude -p` or SDK |
| :-- | :-- | :-- |
| Any settings file, including `~/.claude/settings.json` | Held back until the user accepts the trust dialog for the folder, or for a parent whose trust extends to it | Runs: these sessions never show the dialog and treat the folder as trusted |
| Project skill frontmatter | Same rule as settings files; registered when the skill is invoked | Registered when invoked, even in a folder never trusted |
| Project subagent frontmatter (`.claude/agents/`) | Runs only after the trust dialog is accepted for the folder that holds the agent file; a parent's trust is not enough | Never runs: `-p` does not count as accepting trust |
| User subagents (`~/.claude/agents/`) and `--agents` definitions | Run without the trust step | Run |
| Subagent from an `--add-dir` folder outside the trusted repository | Needs that folder trusted separately | Never runs |
| Plugin subagent frontmatter | `hooks` is ignored; plugin hooks belong in `hooks/hooks.json` | Same |

- A skipped subagent hook leaves a debug-log error that names how to trust the folder, including the `~/.claude.json` key `projects["<path>"].hasTrustDialogAccepted`.
- Subagent frontmatter hooks could run from untrusted folders before Claude Code 2.1.218. On older versions, treat every project subagent's hooks as untrusted code.

## Running over a repository you did not write

Docs: <https://code.claude.com/docs/en/hooks#workspace-trust> · <https://code.claude.com/docs/en/hooks#disable-or-remove-hooks> · <https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder> · <https://code.claude.com/docs/en/headless#start-faster-with-bare-mode>

Before scripting `claude -p` over a repository you did not write, pick at least one:

- Review its `.claude/` settings files, skills and agents first.
- `--bare`: reads no hooks, skills, commands, subagents, plugins or `.mcp.json` servers from the project. The project's `env` block and helpers such as `awsAuthRefresh` still apply.
- `--settings '{"disableAllHooks": true}'`: turns hooks off for that run and takes precedence over project and local settings. Setting `disableAllHooks` only in user settings is not enough, because a project's `"disableAllHooks": false` overrides it.
- `--setting-sources user`: reads neither the project's settings files nor its `.mcp.json`.

There is no switch for a single hook: remove its entry, or disable all hooks. Managed policy settings (`allowManagedHooksOnly`, managed `disableAllHooks`) can override all of this; audit them when hooks appear or vanish unexpectedly.

## Safe-script practice

Docs: <https://code.claude.com/docs/en/hooks#security-best-practices> · <https://code.claude.com/docs/en/hooks#reference-scripts-by-path> · <https://code.claude.com/docs/en/hooks#exec-form-and-shell-form>

| Practice | What to check |
| :-- | :-- |
| Validate input | Read stdin as data. Check types and required fields before use; never `eval` or interpolate input into a command |
| Quote variables | `"$var"`, never `$var`; quote command substitutions too |
| Block path traversal | Reject `..` in any path taken from input; resolve it and confirm it stays inside the intended root |
| Absolute paths | Reference scripts through `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_DATA}`. Exec form (`args` set, even `[]`) needs no quoting; in shell form, wrap the placeholder in double quotes |
| Skip sensitive files | Never read, print or send `.env`, `.git/`, keys or credentials, and never echo them into `additionalContext` |
| Output | Build JSON with an encoder; a background hook's output reaches Claude's context |
| Worktrees | `${CLAUDE_PROJECT_DIR}` stays at the session's starting root; the input's `cwd` follows Claude into a worktree. A script that must act where Claude works reads `cwd` |

Exec form on Windows needs `command` to be a real executable such as `node.exe`; `.cmd` and `.bat` shims from `node_modules/.bin` need shell form or `node <script>` in exec form.

## Prompt and agent hooks are not a security boundary

Docs: <https://code.claude.com/docs/en/hooks#bash-if-matching> · <https://code.claude.com/docs/en/hooks#response-schema> · <https://code.claude.com/docs/en/hooks-guide#hooks-and-permission-modes>

- Their verdict is a model judgment over input that can contain text from files, web pages, tool output or the user. Our position (not a documented behavior): treat that input as able to steer the verdict, and never rely on a prompt or agent hook as the only guard.
- The docs send hard allow or deny to the permission system when discussing the best-effort `if` filter. We apply the same position to model verdicts: recommend permission rules for enforcement and keep the prompt hook as an advisory layer. Designing those rules is out of scope.
- A `PermissionRequest` prompt hook cannot deny anything: `ok: false` has no effect there.
- An agent hook can read the repository. Keep its prompt from asking it to print secrets into `reason`, which Claude reads.

## Windows PowerShell

Docs: <https://code.claude.com/docs/en/hooks#windows-powershell-tool> · <https://code.claude.com/docs/en/hooks#command-hook-fields>

- `"shell": "powershell"` on a command hook runs it via PowerShell on Windows. Claude Code picks `pwsh.exe` (PowerShell 7+) and falls back to `powershell.exe` (5.1). It does not need `CLAUDE_CODE_USE_POWERSHELL_TOOL`. `shell` is ignored when `args` is set.
- Default shell when `shell` is unset: Bash, or PowerShell on Windows when Git Bash isn't installed.
- In a PowerShell shell-form command, write `${CLAUDE_PROJECT_DIR}` or `$env:CLAUDE_PROJECT_DIR`. Claude Code rewrites `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` to `${env:NAME}` in settings, plugin and skill hooks.
- The rewritten placeholder expands inside double quotes, never inside single quotes.
- Never write bare `$CLAUDE_PROJECT_DIR`: PowerShell reads it as an undefined local variable (`$null`), so the path loses its root. Claude Code does not rewrite it and only logs a warning in the debug log.

```json
{
  "type": "command",
  "shell": "powershell",
  "command": "& \"$env:CLAUDE_PROJECT_DIR\\.claude\\hooks\\check.ps1\""
}
```
