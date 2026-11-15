---
description: "Wrong-domain plugin error"
tags: [trigger, should-not-trigger, effort-low]
max_turns: 10
model: claude-sonnet-5-5
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

After upgrading to webpack 5 our custom webpack plugin throws `TypeError: Cannot read properties of undefined (reading 'tap')` in compiler.hooks. How do I fix the plugin?
