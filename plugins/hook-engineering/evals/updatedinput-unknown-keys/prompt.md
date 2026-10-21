---
description: Changelog-only fact (v2.1.300) not yet in the docs; measures whether the plugin carries post-docs releases
tags: [freshness, skill]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I'm on Claude Code 2.1.305. My PreToolUse hook on Bash returns permissionDecision "allow" with updatedInput set to the original Bash input plus an extra key, "audit_tag": "ticket-812", so my PostToolUse hook can read tool_input.audit_tag later and log it. Will that work? Answer yes or no first, then explain.
