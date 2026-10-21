---
description: Debug a SessionEnd hook that gets cut off
tags: [debug, skill]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

My Claude Code SessionEnd hook uploads the session log to S3. It works when I run the script by hand (takes about 4 seconds), but when I exit Claude Code the upload almost never finishes. It's configured in ~/.claude/settings.json without a timeout field. What's going on and how do I fix it?
