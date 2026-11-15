---
name: <skill-name>
description: <what it does and when to use it>
hooks:
  <Event>:
    - matcher: "<matcher>"
      hooks:
        - type: command
          command: '"${CLAUDE_PROJECT_DIR}/<path>/<script>"'
          once: true
---
