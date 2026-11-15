---
description: "A team gate on a pinned Claude Code 2.1.290: no onFailure (added in 2.1.295), a script that fails closed by itself, the limit on timeouts stated, the team settings file, and the script run on real inputs."
tags: [quality, version, gate, effort-high]
plugins: ["../..", "../_support/docs-mcp"]
max_turns: 40
model: claude-sonnet-5-5
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

Add a hook for the whole team that blocks any Bash command that runs rm -rf on a path outside this project. If the hook itself breaks or times out, the command must be blocked too. If you can't write a file, show me its exact content.
