---
paths:
  - "plugins/*/scripts/**"
  - "plugins/*/hooks/hooks.json"
  - "plugins/*/hooks/**/*.{sh,bash,py,mjs,cjs,js}"
  - "plugins/*/skills/*/scripts/**"
---

# Plugin Scripts

<!-- plugins/*/scripts/** matches no file today; it is where building-plugins puts a plugin's executables. -->

These rules apply to every script that ships inside a public marketplace plugin. The platforms and the Python floor are set in `.claude/CLAUDE.md` → Plugin Tooling.

A mod's hooks module (the file `hooks/hooks.json` names under `modules`) and the files it imports are not scripts, and none of these rules applies to them. Claude Code loads them directly: no shebang, no `chmod +x`, no Node prerequisite, imports only from the plugin by relative path plus `claude-code`, options from `register(on, options)`. Load `building-mods` for them.

## Shebang

- Python with complex logic: `#!/usr/bin/env python3`; never hard-code a version above the floor.
- Python with third-party dependencies: `#!/usr/bin/env -S uv run --script`, with the dependencies in PEP 723 inline metadata and `uv` declared in the plugin's README.
- Simple, direct logic: `#!/usr/bin/env bash`, followed by `set -euo pipefail`.
- Omit `-e`, and `-u` with it, only where the script must keep running after a failing command or an unset variable (collecting results, a hook that must fail closed); say in a comment which flag is omitted and why.
- Never leave `set -x` in a script.
- Quote `"$@"` and `"${arr[@]}"` instead of changing `IFS`.
- Support bash 3.2 (macOS default): guard empty arrays under `set -u` with `${arr[@]+"${arr[@]}"}`.
- A blocking hook exits `2` on every failure path, or sets `onFailure: "block"`; an `-e` exit is `1` and lets the action through.
- Node scripts the plugin runs as commands: `#!/usr/bin/env node`.

## Executability

- Run `chmod +x` on every hook script, and on every other plugin script unless the command that runs it names its interpreter.

## Paths and state

- In a shell script or a shell-form `command`, enclose every path containing `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PROJECT_DIR}` in double quotes. In exec form, write each such path as one bare `args` element: there is no shell, so quotes would become part of the path.
- In a shell-form hook, read options from `CLAUDE_PLUGIN_OPTION_<KEY>` inside the script: Claude Code rejects `${user_config.*}` in a shell-form `command`.
- Keep persistent state in `CLAUDE_PLUGIN_DATA`, never in `CLAUDE_PLUGIN_ROOT`, which is replaced with each plugin version.

## Platforms and prerequisites

- Name in the README the supported platforms and every program the hooks and scripts run, each with a command to check it.
- Shell scripts use only tools both macOS and Linux ship, unless the README declares more.
- Node scripts use only `node:` built-in modules, unless the plugin ships its dependencies.
- Python scripts with the `python3` shebang use only the standard library.

## Hook commands in `hooks/hooks.json`

- Load `plugin-hooks-guidance` before writing or reviewing a hook.
- Use exec form (`args`, v2.1.139+) for every command hook, as `/en/hooks` → Exec form and shell form recommends whenever a command references a path placeholder: `"command": "bash", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/check.sh"]`.
- Keep `command` to one executable name and put every argument in `args`; exec form has no shell, so no pipes, `&&`, redirects or globs.
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
