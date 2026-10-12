---
description: "Difference: a multi-file skill whose output-deciding defect lives only in one script's argument list: render.py accepts en, fr and de, while the country table, a template and SKILL.md treat es as supported, so every invoice for Spain or Mexico fails. Hypothesis: a plain review skims the files and trusts the visible signals (the table, the es template); the plugin's full read of every file finds it."
tags: [output, coverage]
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Can you review my skill in skills/invoice-pack before I share it with my team?
