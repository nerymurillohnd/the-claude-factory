---
description: "Trigger rate, audit: a plain-words request to check a skill, with no slash command and no skill name. skills-best-practices must be invoked."
tags: [trigger, audit, train]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Check skills/changelog-writer/SKILL.md against the official skill best practices.
