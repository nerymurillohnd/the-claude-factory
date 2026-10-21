---
description: "Debug case. The async hook prints a progress line, then multi-line JSON. JSON must be alone on stdout (multi-line allowed on 2.1.295+) or on one line of its own, so Claude Code treats this output as plain text and nothing reaches Claude. With the plugin, Claude must name that cause and fix the output, not blame the version or the async flag."
tags: [debug, async]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

I'm on Claude Code 2.1.304. The async hook in this project runs after every edit (I can see npm test running), but Claude never says anything about the test results on the next turn. What's wrong and how do I fix it?
