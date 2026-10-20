---
description: "A decision made in the conversation is written as an accepted ADR, with the Write tool and not the shell, under .claude/maintainer/decisions, with the chosen option, the rejected option and the user's reasons. Claude Code runs an eval session in dontAsk mode, where a write under .claude/ is denied, so the case grades what Claude attempts and what it tells the user."
tags: [records, adr]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

We decided to keep user sessions in Postgres and not move them to Redis. One store is enough at our current traffic, and it saves us from running and monitoring a second service. Please record it.
