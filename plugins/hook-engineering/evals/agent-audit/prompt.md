---
description: "Audit case through the agent. Three seeded defects: an agent hook on PermissionRequest (Claude Code skips it), a prompt hook on SessionStart (prompt hooks are not supported there) and async on a prompt hook (async exists only on command hooks). With the plugin, Claude must delegate to hook-engineer, report all three and change no files."
tags: [audit, agents]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, WebFetch]
---

Use the hook-engineer agent to audit the hooks in this project's .claude/settings.json. Don't change anything, just tell me what's wrong.
