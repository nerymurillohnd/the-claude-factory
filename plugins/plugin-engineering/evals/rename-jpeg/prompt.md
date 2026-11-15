---
description: "Unrelated shell task"
tags: [trigger, should-not-trigger, effort-low]
max_turns: 10
model: claude-sonnet-5-5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write me a bash one-liner that renames every .jpeg file in the current folder to .jpg.
