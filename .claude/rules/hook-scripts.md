---
paths:
  - "plugins/*/hooks/**"
  - "plugins/*/.claude-plugin/plugin.json"
  - ".claude/hooks/**"
  - ".claude/settings.json"
  - ".claude/agents/**"
---
# Hook scripts

Applies to every script a Claude Code `command` hook runs, in a plugin or in this project.

## Pick the language

- Write a hook in Bash when it is direct: read a field or two from the input JSON, run one tool, print a message and exit.
- Write it in Python when it parses or branches on the input, keeps state, or covers many cases.
- Write it in JavaScript, as an ES module named `.mjs`, when it needs Node or sits beside the plugin's other JavaScript; never as `.ts`, which `node` does not run on every Node version a user may have.
- Leave out the files a mod's `hooks/hooks.json` names under `"modules"` and the files they import: Claude Code loads them in its own process, so they get no shebang and keep mode 100644.

## Start every script the same way

- Make the first line `#!/usr/bin/env bash`, `#!/usr/bin/env python3` or `#!/usr/bin/env node`, matching the language.
- Give every script mode 100755: `chmod +x <script>`, then `git add`, and confirm the index with `git ls-files -s <script>`.

## Bash

- Put `set -euo pipefail` on the line after the shebang.
- Drop `-e` only when the script sets its exit code on every path itself, such as a guard that may exit only 0 or 2 or a hook that must always exit 0; then check each command's status, and say why in a comment on the `set` line.
- On an event that can block, remember that under `-e` a command failing with status 2 makes the hook exit 2 and block the action: map unexpected failures to exit 1 with the `trap` from "Keep transient failures retryable in a shell hook" (code.claude.com/docs/en/self-hosted-environments-configuration), and exit 2 only on purpose.
- Read an environment variable that may be unset, such as `CLAUDE_ENV_FILE`, as `${VAR:-}` under `-u`.
- Under `pipefail`, end a pipeline that may stop early, such as one into `head` or `grep -q`, with `|| true`, or write it without the pipe.
- Check Bash hooks with `npm run lint:shell`.

## Python

- In a plugin, import only the standard library: no PEP 723 block and no package installs. Keep the syntax valid on Python 3.12, which ruff (`per-file-target-version` `py312`) and basedpyright already check for `plugins/`.
- In `.claude/hooks/`, follow the Maintainer tooling section of `.claude/CLAUDE.md`.
- Check Python hooks with `npm run lint:python` and `npm run typecheck:python`.

## Wire the hook

- Choose the form for each hook. Use exec form (`"args"` set) when the command holds `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` or `${user_config.*}`, since exec form passes each path as one argument and is the only form that substitutes `${user_config.*}`.
- Use shell form only when the command needs pipes, `&&` or redirects, and wrap each placeholder in double quotes.
- Test a hook by piping a sample input into it and printing the exit code: `echo '<input JSON>' | ./<script>; echo $?`.
