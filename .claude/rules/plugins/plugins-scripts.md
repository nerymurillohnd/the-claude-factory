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

- Run `chmod +x` on every plugin script, unless the command that runs it names its interpreter.

## Paths and state

- Enclose every path containing `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PROJECT_DIR}` in double quotes.
- Never include `${user_config.*}` in `command`; read `CLAUDE_PLUGIN_OPTION_<KEY>` inside the script.
- Keep persistent state in `CLAUDE_PLUGIN_DATA`, never in `CLAUDE_PLUGIN_ROOT`, which is replaced with each plugin version.

## Platforms and prerequisites

- Target macOS and Linux with POSIX-compatible interfaces.
- Support Windows only through Git Bash, and only when the README says so; never add PowerShell, `cmd.exe` or native Windows paths.
- Name in the README the supported platforms and every program the hooks and scripts run, each with a command to check it.
- Shell scripts use only tools both macOS and Linux ship, unless the README declares more.
- Node scripts use only `node:` built-in modules, unless the plugin ships its dependencies.
- Python scripts with the `python3` shebang use only the standard library.

## Hook commands in `hooks/hooks.json`

These follow ADR_2026-10-27_plugin-hooks-run-in-shell-form-through-bash.

- Load `plugin-hooks-guidance` before writing or reviewing a hook.
- Use shell form: omit `args`, because exec form bypasses Git Bash on Windows and ignores `shell`.
- Set `"shell": "bash"` on every command hook.
- Write `command` as the interpreter, the quoted script path and plain arguments: no pipes, `&&`, redirects, globs or shell-specific syntax.
- Name the interpreter first (`python3`, `node`, `bash`, or `uv run --script` for a PEP 723 script); never run a script by its path alone.
- Check every version-dependent hook field against the minimum Claude Code version the README states.
- Choose `async`, `asyncRewake` and `onFailure` deliberately, by the hook's intended blocking and failure behavior.

## Hook entry-point scripts

- Read the hook input as JSON from stdin.
- Write results to stdout and diagnostics to stderr.
- Read paths from `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` and `CLAUDE_PROJECT_DIR`, and options from `CLAUDE_PLUGIN_OPTION_<KEY>`, never from arguments the command would expand.
