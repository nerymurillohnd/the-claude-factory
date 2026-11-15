---
type: llm
focus:
  source: file
  path: hooks/hooks.json
---

The file is a Claude Code plugin's hooks/hooks.json. A command hook runs in shell form when it has no "args" field and in exec form when it has one.

PASS if every "command" that contains ${CLAUDE_PLUGIN_ROOT} either has an "args" field (exec form), or, without "args" (shell form), keeps the placeholder inside double quotes that are escaped in the JSON, such as "\"${CLAUDE_PLUGIN_ROOT}/scripts/tunnel.sh\" open".
FAIL if a shell-form command leaves ${CLAUDE_PLUGIN_ROOT} unquoted, or the file is missing or not valid JSON.
