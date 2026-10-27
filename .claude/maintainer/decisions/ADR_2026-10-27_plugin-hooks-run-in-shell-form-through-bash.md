---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Plugin command hooks run in shell form through Bash, with the interpreter named

## Scope

- Every `type: "command"` hook in a plugin's `hooks/hooks.json`, and the platforms every plugin targets.
- The rule that states it: `.claude/rules/hooks-and-scripts.md`.
- Out of scope: maintainer hooks and scripts (`.claude/hooks/`, `scripts/`, `.claude/skills/*/scripts/`), and a mod's hooks module.

## Context and problem statement

Claude Code runs a command hook in one of two forms (Hooks reference, code.claude.com, read on 2026-10-27):

- **Exec form**, when `args` is present: Claude Code resolves `command` on `PATH` and spawns it directly, with no shell. On Windows, `command` must be a real executable such as a `.exe`.
- **Shell form**, when `args` is absent: the command goes to `sh -c` on macOS and Linux, Git Bash on Windows, or PowerShell when Git Bash isn't installed. The `shell` field accepts `"bash"` or `"powershell"` and defaults to `"bash"`, or to `"powershell"` on Windows without Git Bash.

The reference says "Prefer exec form for any hook that references a path placeholder". `.claude/CLAUDE.md` says plugins target macOS and Linux, and Windows only through Git Bash when the README declares it. On 2026-10-27 all 11 command hooks of the 7 plugins that have them used shell form without `shell`. Two of them (`skill-diagnostics`, `project-maintainer`) ran a script by its path, relying on its shebang. Which form keeps Windows on Git Bash only?

## Decision drivers

- Windows runs only through Git Bash, never PowerShell or a native interpreter (Nery, 2026-10-27).
- A hook behaves the same on macOS, Linux and Git Bash.
- No hook depends on a script's executable bit or shebang to start.

## Considered options

- **Shell form, `"shell": "bash"`, interpreter named first, placeholders in double quotes**: chosen.
- **Exec form with the interpreter in `command` and the script in `args`**: rejected. It is the documented preference and removes quoting, but on Windows it spawns the program without Git Bash, from the Windows `PATH`, where `python3` may be missing or be the Microsoft Store alias.
- **Shell form without `shell`**: rejected, because Windows without Git Bash would fall back to PowerShell.

## Decision outcome

Chosen option: **shell form through Bash**. Every plugin command hook:

- sets `"shell": "bash"` and no `args`;
- names its interpreter, then the script: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/check.py"`, `node "…"`, `bash "…"`;
- wraps each placeholder in double quotes, and never references `${user_config.*}`, reading `$CLAUDE_PLUGIN_OPTION_<KEY>` instead.

Every plugin targets macOS and Linux; Windows only through Git Bash, when its `README.md` declares it. A hook that does not meet this is fixed in its plugin's next pull request.

### Consequences

- Good, because one form runs the same command on macOS, Linux and Git Bash, and Windows never runs a plugin hook in PowerShell.
- Good, because no hook depends on a script's shebang or executable bit.
- Bad, because the repository departs from the reference's preference for exec form; the reason is recorded here and in the rule.
- Bad, because shell form needs correct quoting, and on macOS and Linux runs through `sh -c`, so a command must use POSIX `sh` syntax only.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Every plugin command hook meets the contract | A validator over `plugins/*/hooks/hooks.json`, still to build | pending: 0 of 11 hooks meet it on 2026-10-27 | Each plugin pull request |
| With `"shell": "bash"`, Windows without Git Bash fails the hook instead of running PowerShell | A run on Windows without Git Bash | pending: inferred from the reference's description of the default, not tested | Before a plugin declares Windows support |
| Claude Code still runs shell-form hooks as described | The Hooks reference and release notes | 2026-10-27: as described | Each Claude Code release that changes hooks |

## More information

- Decided by Nery on 2026-10-27, after comparing exec and shell form against the Hooks reference.
- Rule: `.claude/rules/hooks-and-scripts.md`, which also holds the plugin script rules (standard library only, `#!/usr/bin/env python3`, no `uv`).
