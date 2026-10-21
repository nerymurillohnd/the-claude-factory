---
description: "Design case. A user wants an LLM-judged Stop hook. With the plugin, Claude must use the hook-development skill and hand back a complete prompt-type Stop handler that injects the input with $ARGUMENTS, handles stop_hook_active so it cannot loop, and sets an explicit timeout."
tags: [design, prompt-hooks]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

I want Claude Code to stop ending its turn while things I asked for are still unfinished. Give me a hook for my settings.json that uses a model to judge that, and paste the JSON in your reply. Don't write any files.
