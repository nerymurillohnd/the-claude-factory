---
description: "Difference: a user about to upload a skill to claude.ai. Hypothesis: without the plugin, Claude misses upload rules that need current platform facts and the upload breaks; with it, the two problems that need those facts (`when_to_use` rejected by uploads, the `!` line replaced by a placeholder in Cowork) are reported before the upload. The pilot's earlier three-of-four rubric passed the baseline once, because two of the four need only general knowledge."
tags: [output, trigger]
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

I'm about to upload skills/claude-notes to claude.ai so I can use it in Cowork. Check it first and tell me everything that will break or misbehave there.
