---
description: "A broad request: Claude asks about the user's goal and context with AskUserQuestion before writing any hook, with one to four non-technical questions."
tags: [quality, clarify, effort-medium]
max_turns: 30
model: claude-sonnet-5-5
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

Set up hooks so the code quality of this repo doesn't slip.
