---
description: "Trigger rate, near miss: the user asks for a subagent that is not part of a skill, which the description excludes. skills-best-practices must not be invoked, in either arm."
tags: [trigger, negative, validation]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a subagent in .claude/agents that reviews my SQL migrations before I merge them.
