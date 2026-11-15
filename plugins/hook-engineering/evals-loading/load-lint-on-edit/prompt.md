---
description: "Must load writing-hooks without being named."
tags: [loading, should-trigger, effort-low]
max_turns: 4
model: claude-sonnet-5-5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Whenever you edit a file, run the linter on it.
