---
description: "Design case. A prompt hook on PreToolUse that blocks reading .env files, where the user wants Claude to get the reason and keep working. A prompt hook's ok:false on PreToolUse ends the turn unless continueOnBlock is true, so the handler must set it."
tags: [design, prompt-hooks]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

Make me a Claude Code hook where a single quick model check (not a full agent) decides whether a Bash command would read a .env file and blocks it if so. When it blocks, I don't want my turn to end: Claude should see why and try another way. Reply with the settings JSON only, no files.
