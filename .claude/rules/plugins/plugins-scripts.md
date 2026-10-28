---
paths:
  - "plugins/*/scripts/**"
  - "plugins/*/hooks/**"
  - "plugins/*/skills/*/scripts/**"
---

# Plugin Scripts

<!-- plugins/*/scripts/** matches no file today; it is where building-plugins puts a plugin's executables. -->

These rules apply to every script that ships inside a public marketplace plugin. The scripts must be portable across macOS and Linux; never assume Nery's machine.

## Shebang

- Python with complex logic: `#!/usr/bin/env python3`, with Python 3.12 as the floor; never hard-code a higher version.
- Python with third-party dependencies: `#!/usr/bin/env -S uv run --script`, with the dependencies in PEP 723 inline metadata and `uv` declared in the plugin's README.
- Simple, direct logic: `#!/usr/bin/env bash`, followed by `set -euo pipefail`.
- Omit `-e` only where the script must keep running after a failing command (collecting results, a hook that must fail closed); say why in a comment.
- Never leave `set -x` in a script.
- Quote `"$@"` and `"${arr[@]}"` instead of changing `IFS`.
- Support bash 3.2 (macOS default): guard empty arrays under `set -u` with `${arr[@]+"${arr[@]}"}`.
- A blocking hook exits `2` on every failure path, or sets `onFailure: "block"`; an `-e` exit is `1` and lets the action through.
- Mods, or when the plugin integration requires Node: `#!/usr/bin/env node`.

## Executability

- Run `chmod +x` on every hook script, and on every other plugin script unless the command that runs it names its interpreter.

## Paths and state

- Enclose every path containing `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PROJECT_DIR}` in double quotes.
- In a shell-form hook, read options from `CLAUDE_PLUGIN_OPTION_<KEY>` inside the script: Claude Code rejects `${user_config.*}` in a shell-form `command`.
- Keep persistent state in `CLAUDE_PLUGIN_DATA`, never in `CLAUDE_PLUGIN_ROOT`, which is replaced with each plugin version.

## Platforms and prerequisites

- Target macOS and Linux with POSIX-compatible interfaces.
- Support Windows only through Git Bash, and only when the README says so; never add PowerShell, `cmd.exe` or native Windows paths.
- Name in the README the supported platforms and every program the hooks and scripts run, each with a command to check it.
- Shell scripts use only tools both macOS and Linux ship, unless the README declares more.
- Node scripts use only `node:` built-in modules, unless the plugin ships its dependencies.
- Python scripts with the `python3` shebang use only the standard library.

## Hook commands in `hooks/hooks.json`

- Load `plugin-hooks-guidance` before writing or reviewing a hook.
- Choose shell form or exec form (`args`) for each hook from what that plugin runs and the platforms its README declares, against `/en/hooks` → Exec form and shell form; no form is the default here.
- Keep `command` free of pipes, `&&`, redirects, globs and shell-specific syntax.
- Check every version-dependent hook field against the minimum Claude Code version the README states.
- Choose `async`, `asyncRewake` and `onFailure` deliberately, by the hook's intended blocking and failure behavior.

## Hook entry-point scripts

- Simple, direct logic: Bash.
- Logic beyond that: Python, with the `python3` shebang.
- Python that needs third-party dependencies: the `uv run --script` shebang with them in PEP 723 inline metadata, or the `python3` shebang with them passed in the hook's `command` (`uv run --with <package> <script>`).
- When a hook runs `uv` in either form, declare `uv` in the README as a prerequisite, with its install command.
- Read the hook input as JSON from stdin.
- Write results to stdout and diagnostics to stderr.
- Read paths from `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` and `CLAUDE_PROJECT_DIR`, and options from `CLAUDE_PLUGIN_OPTION_<KEY>`, never from arguments the command would expand.
