---
description: "A gate on a plugin's own MCP tool: PreToolUse with the mcp__plugin_ name, a deny that spares tmp_ tables, a block on unreadable input and onFailure block, verified on three inputs."
tags: [quality, location-plugin, mcp, gate, effort-high]
plugins: ["../..", "../_support/docs-mcp"]
max_turns: 100
model: claude-sonnet-5-5
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

Stop Claude from dropping tables through our warehouse server unless the table name starts with tmp_.
