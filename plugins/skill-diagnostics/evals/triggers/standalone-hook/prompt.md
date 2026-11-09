---
description: "Trigger rate, near miss: shares words with the skill's scope but asks for something its description excludes. skills-best-practices must not be invoked, in either arm. A hook that is not part of a skill is excluded by the description."
tags: [trigger, negative, train]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a PostToolUse hook to .claude/settings.json that runs prettier on every file Claude writes or edits.
