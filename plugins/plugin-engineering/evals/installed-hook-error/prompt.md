---
description: "Troubleshoot: a plugin hook error that appears only after a marketplace install"
tags: [trigger, should-trigger]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I installed our team's formatter plugin from the company marketplace and now every edit shows `PostToolUse hook error: Failed with non-blocking status code: Error: Cannot find module '../../../shared/style-config.js'`. It worked fine when I ran it from my own checkout. What's going on and how do I fix it?
