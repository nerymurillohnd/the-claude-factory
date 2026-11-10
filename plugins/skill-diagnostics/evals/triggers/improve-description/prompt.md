---
description: "Trigger rate, improve: a plain-words request to improve an existing skill's triggering, with no slash command and no skill name. The description names improving a skill, its description or its triggering, so skills-best-practices must be invoked: the audit says what to fix."
tags: [trigger, improve, train]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

claude never picks up my pr-summary skill (skills/pr-summary) on its own when i ask for a PR summary. can you rewrite its description so it actually triggers?
