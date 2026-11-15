---
description: "Changing an accepted decision writes a new ADR that supersedes the old one, marks the old one superseded, and never rewrites the old reasoning. A write under .claude/ is denied in an eval session (dontAsk mode), so the case grades what Claude attempts."
tags: [records, adr, effort-medium]
max_turns: 25
model: claude-sonnet-5-5
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

We changed our mind about sessions: they move to Redis, because Postgres latency under load was worse than we expected. Update the decision record.
