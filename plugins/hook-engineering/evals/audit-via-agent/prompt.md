---
description: Delegate a hook audit to the hook-engineer agent; settings contain five event-level defects and one correct hook
tags: [audit, agent]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Have the hook-engineer agent audit these Claude Code hooks from our project's .claude/settings.json and tell me what's broken. The scripts behave as their comments say.

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "startup", "hooks": [ { "type": "prompt", "prompt": "Summarize open TODOs for the user: $ARGUMENTS" } ] }
    ],
    "Stop": [
      { "matcher": "Bash", "hooks": [ { "type": "command", "command": "./hooks/run-tests.sh" } ] }
    ],
    "FileChanged": [
      { "matcher": "^\\.env", "hooks": [ { "type": "command", "command": "./hooks/reload-env.sh" } ] }
    ],
    "PermissionRequest": [
      { "matcher": "Bash", "hooks": [ { "type": "command", "command": "./hooks/deny-publish.sh" } ] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [ { "type": "command", "command": "./hooks/block-secrets.sh" } ] }
    ],
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [ { "type": "command", "command": "./hooks/no-force-push.sh" } ] }
    ]
  }
}
```

- deny-publish.sh: if the command contains "npm publish", prints a message to stderr and exits 2.
- block-secrets.sh: if the written content contains "AKIA", exits 2 so the write with the secret doesn't happen.
- no-force-push.sh: if the command contains "git push --force", prints {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Force push is blocked"}} and exits 0.
