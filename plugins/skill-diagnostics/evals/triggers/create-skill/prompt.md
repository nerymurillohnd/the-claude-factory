---
description: "Trigger rate, near miss: a plain-words request to write a new skill. The plugin only audits and its description excludes writing a skill from scratch, so skills-best-practices must not be invoked, in either arm."
tags: [trigger, negative, smoke]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Create a new skill in skills/csv-to-markdown that converts CSV files into Markdown tables.
