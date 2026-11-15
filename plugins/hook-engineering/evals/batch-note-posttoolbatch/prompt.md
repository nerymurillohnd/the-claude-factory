---
description: "The optimal event: PostToolBatch with no matcher and hookSpecificOutput built from tool_calls, not PostToolUse, with the version check done and the alternative named."
tags: [quality, event-choice, effort-high]
plugins: ["../..", "../_support/docs-mcp"]
max_turns: 100
model: claude-sonnet-5-5
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

After you read several files at once, give yourself one short note listing which files you just read, not one note per file. Put it in this project's settings. If you can't write a file, show me its exact content.
