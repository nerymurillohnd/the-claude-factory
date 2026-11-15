---
name: <agent-name>
description: <when to delegate to it>
hooks:
  PreToolUse:
    - matcher: "<tool>"
      hooks:
        - type: command
          command: '"${CLAUDE_PROJECT_DIR}/.claude/hooks/<script>"'
  Stop:
    - hooks:
        - type: command
          command: '"${CLAUDE_PROJECT_DIR}/.claude/hooks/<script>"'
---
