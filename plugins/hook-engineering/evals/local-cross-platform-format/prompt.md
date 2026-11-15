---
description: "A personal formatter hook: .claude/settings.local.json, the shared file untouched, PostToolUse on the file tools, a form that runs on Windows, the file kept out of git, and how to confirm it fires."
tags: [quality, location-local, windows, effort-high]
plugins: ["../..", "../_support/docs-mcp"]
max_turns: 100
model: claude-sonnet-5-5
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

Only for me, without touching what the team shares: format every file you edit with Prettier. If you can't write a file, show me its exact content.
