---
description: "Must load writing-hooks without being named, ahead of update-config, for a behavior that must run on every edit."
tags: [loading, should-trigger, effort-low]
max_turns: 4
model: claude-sonnet-5-5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Set it up so the linter runs automatically every time you edit a file.
