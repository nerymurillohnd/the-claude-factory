---
description: "Trigger rate, near miss: shares words with the skill's scope but asks for something its description excludes. skills-best-practices must not be invoked, in either arm. Packaging or publishing a plugin is excluded by the description; before-publishing is the matching positive (review the skills first)."
tags: [trigger, negative]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Package this plugin and set up a marketplace.json so my team can install it with /plugin install. Don't change the skill.
