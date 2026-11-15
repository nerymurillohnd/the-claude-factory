---
description: "A decision made in the conversation is drafted as an accepted ADR at .claude/maintainer/decisions/ADR_<date>_<slug>.md with the Write tool, not the shell, holding the chosen option, the rejected option and the user's reasons, and the reply names the path and says the save was refused, with the draft. .claude/ is a protected path (code.claude.com/docs/en/permission-modes#protected-paths) and an eval run never stops to ask for permission, so the write is refused without a prompt even with Write, Edit and Bash granted; the case grades the Write and Edit attempts, their input, and the reply."
tags: [records, adr]
max_turns: 25
model: claude-sonnet-5-5
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

We decided to keep user sessions in Postgres and not move them to Redis. One store is enough at our current traffic, and it saves us from running and monitoring a second service. Please record it.
