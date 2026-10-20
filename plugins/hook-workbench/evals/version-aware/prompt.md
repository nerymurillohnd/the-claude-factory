---
description: "Freshness case. The user runs 2.1.293. The changelog fixes, in 2.1.294, prompt and agent hooks written as rules allowing what they should block; the docs page doesn't say so. With the plugin, Claude must check the changelog, not only the docs, warn that this version is affected, recommend upgrading, and state what it verified against."
tags: [freshness, prompt-hooks]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, WebFetch]
---

I'm on Claude Code 2.1.293. Write me a prompt hook that blocks any Bash command that deletes files. Just give me the settings JSON.
