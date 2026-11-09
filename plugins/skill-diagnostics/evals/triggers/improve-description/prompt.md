---
description: "Trigger rate, authoring: a plain-words request to write or improve a skill, with no slash command and no skill name. Authoring is in the skill's scope since 0.3.0, so skills-best-practices must be invoked."
tags: [trigger, authoring]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

claude never picks up my pr-summary skill (skills/pr-summary) on its own when i ask for a PR summary. can you rewrite its description so it actually triggers?
