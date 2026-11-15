---
description: "Changing an accepted decision drafts a new ADR that supersedes the old one, edits the old one only to mark it superseded by the new ID, and never touches the old reasoning. .claude/ is a protected path (code.claude.com/docs/en/permission-modes#protected-paths) and an eval run never stops to ask for permission, so the write is refused without a prompt even with Write, Edit and Bash granted; the case grades the Write and Edit attempts, their input, and the reply."
tags: [records, adr]
max_turns: 25
model: claude-sonnet-5-5
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

We changed our mind about sessions: they move to Redis, because Postgres latency under load was worse than we expected. Update the decision record.
