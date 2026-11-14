---
paths:
  - "plugins/*/hooks/**"
  - "plugins/*/.claude-plugin/plugin.json"
  - ".claude/hooks/**"
  - ".claude/settings.json"
  - ".claude/agents/**"
---

# Hook scripts

- Write a hook in Bash when it reads a field or two and runs one tool, in Python when it parses, branches or keeps state, and in JavaScript as an `.mjs` module when it needs Node; never in `.ts`.
- Give no shebang to a mod's `"modules"` files or what they import, and keep them at mode 100644.
- Start every other hook script with `#!/usr/bin/env bash`, `#!/usr/bin/env python3` or `#!/usr/bin/env node`, and give it mode 100755 with `chmod +x <script>` before `git add`.
- Put `set -euo pipefail` on the line after a Bash shebang; drop `-e` only when the script sets its exit code on every path, and say why in a comment on that line.
- Map unexpected failures to exit 1 in a hook on a blocking event, with the `trap` from the official "Keep transient failures retryable in a shell hook" guide; exit 2 only on purpose.
- Read a variable that may be unset as `${VAR:-}`.
- End a pipeline that may stop early, such as one into `head` or `grep -q`, with `|| true`.
- Import only the standard library in a plugin's Python hook, and keep it valid on Python 3.12.
- Use exec form (`"args"`) when the command holds `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` or `${user_config.*}`; use shell form only for pipes, `&&` or redirects, with every placeholder in double quotes.
