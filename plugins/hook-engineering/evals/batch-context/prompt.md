---
description: Pick the event that runs once after parallel tool calls
tags: [design, skill]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

When Claude reads several files from our ledger/ folder in parallel, I want a Claude Code hook to inject one reminder ("run pytest before marking done") a single time after that whole group of reads finishes, not once per file. Which hook event should I use, and what JSON should the hook print?
