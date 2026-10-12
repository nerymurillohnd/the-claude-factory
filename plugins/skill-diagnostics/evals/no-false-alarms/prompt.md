---
description: "Difference: a valid Claude Code skill that uses current fields (no `name`, `when_to_use`, `arguments`, `effort`, space-separated `allowed-tools`, an injected command). Hypothesis: without the plugin, Claude applies generic or outdated skill rules and tells the user to fix things that are valid; with it, it doesn't. A user who follows false alarms breaks a working skill."
tags: [output, trust]
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent]
---

The skill in skills/doc-digest is a project skill I only use in Claude Code. Before I commit it, is everything in it valid? Tell me what I must fix.
