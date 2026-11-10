---
description: "Trigger rate, audit after an edit: the user changed a skill's references and wants to know nothing broke, without naming an audit. skills-best-practices must be invoked."
tags: [trigger, audit, validation]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I just rewrote the references in ~/.claude/skills/sql-helper, can you make sure I didnt break anything?
