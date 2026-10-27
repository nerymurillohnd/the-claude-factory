---
paths:
  - "scripts/**"
  - "**/scripts/**"
  - "**/hooks/**"
---

# Hooks and scripts

A `hooks/` or `scripts/` folder in this repository belongs to one of two scopes, and each scope has its own rules. Identify the scope before you edit; a rule of one scope never applies to the other.

## Which scope this is

| Path | Scope | Runs on | Load |
| :-- | :-- | :-- | :-- |
| `plugins/<plugin>/hooks/`, `plugins/<plugin>/scripts/`, `plugins/<plugin>/skills/*/scripts/` | Plugin: every change goes through a pull request | The user's machine, with only what the plugin's `README.md` declares | `plugin-hooks-guidance` for a hook; `building-mods` for a mod's hooks module |
| `scripts/`, `.claude/hooks/`, `.claude/skills/*/scripts/` | Maintainer | Nery's machine and CI | Nothing more than this file |

For every file, also load the skill of its language: `python-lsp-intelligence:python-lsp-intelligence`, `typescript6-lsp-intelligence:ts-lifecycle` or `bash-lsp-intelligence:bash-lsp-intelligence`.

## Plugin scope

### Platforms

- Every plugin targets macOS and Linux, with POSIX-compatible interfaces.
- Windows is supported only through Git Bash, and only when the plugin's `README.md` says so. Never PowerShell, `cmd.exe` or a native Windows interpreter.
- The `README.md` names the platforms and every program the hooks and scripts run (`python3`, `node`, `bash`, `jq` and so on), with how to check each one.

### Command hooks in `hooks/hooks.json`

Shell form, never exec form: exec form (`args`) starts the program without a shell, so on Windows it bypasses Git Bash.

- Set `"shell": "bash"` on every command hook, so Windows never falls back to PowerShell. On macOS and Linux, shell form runs through `sh -c`, so the `command` string itself uses POSIX `sh` syntax only; the script it runs may use the interpreter it names, Bash included.
- Name the interpreter first, then the script: `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/check.py"`, `node "${CLAUDE_PLUGIN_ROOT}/hooks/check.mjs"`, `bash "${CLAUDE_PLUGIN_ROOT}/hooks/check.sh"`. Never run a script by its path alone, relying on its shebang and executable bit.
- Wrap every placeholder (`${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}`) in double quotes.
- Never put `${user_config.*}` in a command: Claude Code refuses it in shell form. Read `$CLAUDE_PLUGIN_OPTION_<KEY>` inside the script instead.
- Keep state in `${CLAUDE_PLUGIN_DATA}`, never in `${CLAUDE_PLUGIN_ROOT}`, which each plugin version replaces.

A hook that does not meet these rules is fixed in its plugin's next pull request.

### Scripts

- Python: `#!/usr/bin/env python3`, standard library only, written for any `python3` a user may have. Declare a minimum version in the `README.md` only when a feature requires it. Never `uv run`, PEP 723 metadata or a virtual environment: the user may have none of them.
- Shell: `#!/usr/bin/env bash` for Bash, `#!/bin/sh` for POSIX `sh`, and only tools macOS and Linux both ship, unless the `README.md` declares the tool.
- Node: only `node:` built-in modules, unless the plugin ships its dependencies.
- A script reads hook input as JSON from stdin, writes its result to stdout, and writes diagnostics to stderr.

## Maintainer scope

- Python with only the standard library: `#!/usr/bin/env python3`.
- Python with third-party dependencies: `#!/usr/bin/env -S uv run --script`, with `requires-python = "==3.15.*"` and its `dependencies` in PEP 723 inline metadata. `scripts/gates.mjs` recognises this shebang to run the script in its own environment, and `scripts/basedpyright-maintainer.mjs` type-checks it against that environment.
- Every maintenance command runs through an `npm run` script, so local runs, the git hooks and CI use the pinned tools.
