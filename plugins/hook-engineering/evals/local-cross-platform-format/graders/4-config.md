---
type: llm
focus: last_message
---

The team works on macOS and Windows, so the hook command must run on both. In a Claude Code hook, exec form ("args" set) needs "command" to be a real executable on Windows, so a .sh or .py path there fails; shell form (no "args") runs through Git Bash on Windows and needs each path placeholder in double quotes.

PASS if the reply shows a .claude/settings.local.json hook on PostToolUse whose matcher covers both Edit and Write, and whose command either runs a script in shell form with "${CLAUDE_PROJECT_DIR}" inside double quotes, runs Prettier directly in shell form, or uses exec form with "command" set to node.
FAIL if the hook is in .claude/settings.json, is not on PostToolUse, misses Edit or Write, or uses exec form with a .sh or .py path as "command".
