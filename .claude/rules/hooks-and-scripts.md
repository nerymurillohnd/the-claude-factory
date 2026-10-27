---
paths:
  - "scripts/**"
  - "**/scripts/**"
  - "**/hooks/**"
---

# Hooks and scripts

A `hooks/` or `scripts/` folder in this repository belongs to one of two scopes. Identify the scope before editing; scope-specific rules never apply to the other scope.

## Identify the scope

| Path | Scope | Execution environment | Required guidance |
| :-- | :-- | :-- | :-- |
| `plugins/<plugin>/hooks/`, `plugins/<plugin>/scripts/`, `plugins/<plugin>/skills/*/scripts/` | Plugin: every change goes through a pull request | The user's machine, with only what the plugin's `README.md` declares | Load `plugin-hooks-guidance` for a hook; load `building-mods` for a mod's hooks module |
| `scripts/`, `.claude/hooks/`, `.claude/skills/*/scripts/` | Maintainer | Nery's machine and CI | This file; no additional scope-specific guidance |

For every script, also load the skill for its language:

- Python: `python-lsp-intelligence:python-lsp-intelligence`.
- TypeScript or JavaScript: `typescript6-lsp-intelligence:ts-lifecycle`.
- Shell: `bash-lsp-intelligence:bash-lsp-intelligence`.

## Command-hook execution model

These are Claude Code capabilities, as the [hooks reference](https://code.claude.com/docs/en/hooks) describes them, not permission to override the scope-specific policies below. When the reference or the release notes change, they win over this section.

### Command-hook fields

In addition to the common hook fields, command hooks accept:

| Field | Required | Meaning |
| :-- | :-- | :-- |
| `command` | Yes | In shell form, the shell command to execute. In exec form, only the executable name or path. |
| `args` | No | Argument vector. When present, selects exec form: Claude Code spawns `command` directly without a shell. |
| `async` | No | When `true`, runs the hook in the background without blocking. |
| `asyncRewake` | No | When `true`, runs the hook in the background and wakes Claude on exit code `2`. Claude receives the hook's stderr, or stdout if stderr is empty, as a system reminder. |
| `shell` | No | Accepts `"bash"` or `"powershell"`. Defaults to `"bash"`, or `"powershell"` on Windows when Git Bash is unavailable. Ignored when `args` is present. Claude Code 2.1.176 already accepts it. |
| `onFailure` | No | Accepts `"continue"` or `"block"` to control whether the triggering action proceeds when the hook fails. Requires Claude Code v2.1.295 or later. Consult the hook failure documentation before relying on the behavior when this field is omitted. |

Do not add version-dependent fields without checking the plugin's or maintainer environment's supported Claude Code version. If a plugin relies on a version-dependent feature, document its minimum Claude Code version in its `README.md`.

### Exec form: `args` present

Claude Code resolves `command` as an executable and spawns it directly with `args` as the argument vector. No shell runs, and no shell tokenization occurs on any platform. Each `args` element is one argument exactly as written, with path placeholders substituted as plain strings. On Windows, `command` must be a real executable such as `node.exe`; `.cmd` and `.bat` shims cannot be spawned. Plugin hooks in this repository never use exec form (see Plugin scope).

### Shell form: `args` absent

Claude Code passes the `command` string to a shell:

- macOS and Linux: `sh -c`, per the hooks reference. Claude Code 2.1.176 describes `"shell": "bash"` as the user's `$SHELL` (bash, zsh or sh), so older releases can run the string in zsh.
- Windows: Git Bash, or PowerShell when Git Bash is unavailable.
- The `shell` field selects the hook's shell explicitly.

The shell tokenizes the command and interprets variable expansion, pipes, `&&`, redirects and globs. Quote path placeholders to keep paths containing spaces together.

Claude Code recommends exec form when referencing path placeholders because it avoids shell parsing. This repository deliberately requires shell form for plugin hooks to retain the Git Bash execution policy on supported Windows installations (ADR_2026-10-27_plugin-hooks-run-in-shell-form-through-bash).

### Placeholders, environment and plugin options

Both execution forms support these path placeholders and export the corresponding environment variables to the spawned process:

- `CLAUDE_PROJECT_DIR`.
- `CLAUDE_PLUGIN_ROOT`.
- `CLAUDE_PLUGIN_DATA`.

A script can read these variables directly, such as through `process.env.CLAUDE_PLUGIN_ROOT` in Node or `os.environ["CLAUDE_PLUGIN_ROOT"]` in Python.

Plugin option substitution differs by execution form:

- Exec form supports `${user_config.*}` in `command` and each `args` element. Values are substituted as plain strings without shell reparsing.
- Shell-form plugin commands containing `${user_config.*}` fail instead of running. Before Claude Code v2.1.207, these commands also performed option substitution; do not rely on that legacy behavior.
- In shell form, read plugin options inside the script through `CLAUDE_PLUGIN_OPTION_<KEY>`, such as `CLAUDE_PLUGIN_OPTION_WEBHOOK_URL` for `webhook_url`.

## Plugin scope

### Platforms and prerequisites

- Every plugin targets macOS and Linux, with POSIX-compatible interfaces.
- Windows is supported only through Git Bash, and only when the plugin's `README.md` says so. Do not add PowerShell, `cmd.exe` or native Windows execution paths.
- The `README.md` names the supported platforms and every program the hooks and scripts run, such as `python3`, `node`, `bash` and `jq`, with a command to check each prerequisite.

### Command hooks in `hooks/hooks.json`

Use shell form only. Omit `args`.

This is a repository portability policy: exec form bypasses Git Bash on Windows, and setting `"shell": "bash"` does not change that because `shell` is ignored when `args` is present.

- Set `"shell": "bash"` on every command hook so Windows never falls back to PowerShell. A plugin whose `README.md` declares a minimum Claude Code older than 2.1.176 confirms the field on that version first.
- Write the `command` string so `sh`, `bash` and `zsh` all read it the same: the interpreter, the quoted script path and plain arguments, with no pipes, `&&`, redirects, globs or shell-specific syntax. A script may use the interpreter explicitly named in the command, including Bash.
- Name the interpreter first, then the script. Never execute a script by its path alone, relying on its shebang and executable bit.
- Enclose every path containing `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PROJECT_DIR}` in double quotes.
- Never include `${user_config.*}` in `command`. Read `CLAUDE_PLUGIN_OPTION_<KEY>` inside the script.
- Keep persistent state in `CLAUDE_PLUGIN_DATA`, never in `CLAUDE_PLUGIN_ROOT`, which is replaced with each plugin version.
- Choose `async`, `asyncRewake` and `onFailure` deliberately according to the hook's intended blocking and failure behavior.

Interpreter patterns:

| Language | Command |
| :-- | :-- |
| Python | `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/check.py"` |
| Node | `node "${CLAUDE_PLUGIN_ROOT}/hooks/check.mjs"` |
| Bash | `bash "${CLAUDE_PLUGIN_ROOT}/hooks/check.sh"` |

Example command-hook entry:

```json
{
  "type": "command",
  "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/check.py\"",
  "shell": "bash"
}
```

Fix any hook that violates these rules in its plugin's next pull request.

### Scripts

- Python:
  - Use `#!/usr/bin/env python3`.
  - Use only the standard library.
  - Target Python 3.12 or later, the floor checked by `ruff.toml` and `pyrightconfig.json`.
  - State that minimum in the plugin's `README.md`.
  - Never require `uv run`, PEP 723 metadata or a virtual environment; the user may have none of them.
- Shell:
  - Use `#!/usr/bin/env bash` for Bash or `#!/bin/sh` for POSIX `sh`.
  - Use only tools shipped by both macOS and Linux unless the `README.md` declares the additional tool.
- Node:
  - Use only `node:` built-in modules unless the plugin ships its dependencies.
- Hook entry-point scripts:
  - Read hook input as JSON from stdin.
  - Write results to stdout.
  - Write diagnostics to stderr.
  - Read paths from `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` and `CLAUDE_PROJECT_DIR`, and plugin options from `CLAUDE_PLUGIN_OPTION_<KEY>`, never from arguments the command would have to expand.

## Maintainer scope

### Python

- Standard-library-only scripts:
  - Use `#!/usr/bin/env python3`.
  - Target Python 3.15, except for scripts in `.claude/skills/*/scripts/`.
  - Scripts in `.claude/skills/*/scripts/` target Python 3.12 because CI runs them with the `python3` provided by its `ubuntu-24.04` runner. `ruff.toml` and `.claude/skills/pyrightconfig.json` check that floor.
- Scripts with third-party dependencies:
  - Use `#!/usr/bin/env -S uv run --script`.
  - Declare `requires-python = "==3.15.*"` and all dependencies in PEP 723 inline metadata.
  - `scripts/gates.mjs` recognizes this shebang and runs the script in its own environment.
  - `scripts/basedpyright-maintainer.mjs` type-checks the script against that environment.

### Maintenance commands

Every maintenance command runs through an `npm run` script so local runs, Git hooks and CI use the pinned tools.
