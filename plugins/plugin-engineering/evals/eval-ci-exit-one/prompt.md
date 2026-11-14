---
description: "Test: a failing plugin eval CI step"
tags: [trigger, should-trigger]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Our GitHub Actions job runs `claude plugin eval --json --tag smoke plugins/ticket-triage` and exits 1 on every pull request, even though the cases score around 0.9 when I run them on my laptop. Why does it fail and what should the step look like?
