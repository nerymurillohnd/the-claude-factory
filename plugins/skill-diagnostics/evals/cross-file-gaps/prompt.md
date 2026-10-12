---
description: "Difference: without the plugin, Claude misses subtle cross-file defects (a placeholder named differently where it is defined, a script flag the script rejects, a value used before the step that produces it); with it, at least two come back with file references and a failing verdict."
tags: [output, trigger]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Is the skill in skills/invoice-note ready to use? Could a model follow it without guessing anything?
