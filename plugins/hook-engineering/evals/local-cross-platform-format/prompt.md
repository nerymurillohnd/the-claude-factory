---
description: "A personal formatter hook: .claude/settings.local.json, the shared file untouched, PostToolUse on the file tools, a form that runs on Windows, the file kept out of git, and how to confirm it fires."
tags: [quality, location-local, windows, effort-high]
max_turns: 40
model: claude-sonnet-5-5
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

Only for me, without touching what the team shares: format every file you edit with Prettier. If you can't write a file, show me its exact content.
