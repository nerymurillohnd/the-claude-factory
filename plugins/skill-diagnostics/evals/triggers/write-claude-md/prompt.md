---
description: "Trigger rate, near miss: shares words with the skill's scope but asks for something its description excludes. skills-best-practices must not be invoked, in either arm. Writing a CLAUDE.md is excluded by the description."
tags: [trigger, negative, smoke]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write a CLAUDE.md for this repo telling Claude to run npm test before every commit and to never edit files under dist/.
