---
description: "Debug: a plugin that loads after being turned off"
tags: [trigger, should-trigger, effort-low]
max_turns: 10
model: claude-sonnet-5-5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I set the review plugin to false in my own settings because I don't want it, but it still loads in every session in this repo and the plugin list says it still loads. How do I turn it off just for me without changing it for my teammates?
