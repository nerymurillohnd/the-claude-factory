---
description: "Guardrail: the executability lens must catch subtle cross-file defects (a placeholder named differently where it is defined, a script flag the script rejects, a value used before the step that produces it). The pilot showed Sonnet catches them unaided too (delta 0), so this guards the lens rather than proving a difference."
tags: [guardrail]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

Is the skill in skills/invoice-note ready to use? Could a model follow it without guessing anything?
