---
type: llm
focus: last_message
---

PASS if the reply puts the hook in the project's shared `.claude/settings.json`, written or edited there, or shown as that file's exact content.
FAIL if the hook goes in `.claude/settings.local.json`, the user's `~/.claude/settings.json` or anywhere else the team doesn't share.
