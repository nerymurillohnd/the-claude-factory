---
paths:
  - "plugins/*/scripts/**"
  - "plugins/*/hooks/**"
  - "plugins/*/skills/*/scripts/**"
---

# Plugin Scripts

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

## Hooks

- Choose `async`, `asyncRewake` and `onFailure` deliberately, by the hook's intended blocking and failure behavior.
