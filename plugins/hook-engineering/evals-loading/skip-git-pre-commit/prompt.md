---
description: "Must not load writing-hooks: a Git hook, which has nothing to do with Claude Code hooks."
tags: [loading, should-not-trigger, effort-low]
max_turns: 10
model: claude-sonnet-5-5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a Git pre-commit hook that runs the tests.
