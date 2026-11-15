---
description: "A plugin agent's start and stop hooks: hooks/hooks.json, not the agent's frontmatter, on SubagentStart and SubagentStop with the anchored scoped name, scripts through the plugin root, verified with real inputs."
tags: [quality, location-plugin, subagent-events, effort-high]
max_turns: 40
model: claude-sonnet-5-5
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, AskUserQuestion, TodoWrite]
---

When db-agent starts, open the database tunnel with scripts/tunnel.sh open, and close it with scripts/tunnel.sh close when the agent finishes.
