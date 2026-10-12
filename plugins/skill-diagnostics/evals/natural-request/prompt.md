---
description: "Cases 1, 3 and 4. A user asks in plain words, with no slash command, to check a ten-file skill whose output-deciding defect lives only in one script's argument list (render.py accepts en, fr and de; the country table, a template and SKILL.md treat es as supported). With the plugin, Claude must invoke the audit on its own, take the full inventory, send both lens agents every file with the instruction to read all of it and quote evidence, have the agents read every file in full plus their references, then verify the findings against live official sources. finds-defect is scored in both arms and measures what the plugin adds; the other graders check the plugin's own steps."
tags: [agents, verification]
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Can you check my skill in skills/invoice-pack before I share it with my team? I want to know if anything in it is broken.
