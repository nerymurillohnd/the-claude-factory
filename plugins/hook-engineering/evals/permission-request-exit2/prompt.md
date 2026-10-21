---
description: Debug a PermissionRequest hook that relies on exit code 2 to deny
tags: [debug, skill]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I have a Claude Code hook on PermissionRequest with matcher "Bash". The script checks if the command contains "npm publish" and if so prints "publishing is not allowed" to stderr and exits 2. But when Claude tries npm publish I still get the normal permission prompt and nothing gets denied. Why, and what should the script output instead?
