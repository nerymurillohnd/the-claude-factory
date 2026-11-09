---
description: "Trigger rate, near miss: the user asks to run a skill's evals and report pass rates, which the description excludes (running evals or benchmarks). skills-best-practices must not be invoked, in either arm."
tags: [trigger, negative, validation]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Run the evals in skills/pdf-forms/evals and tell me the pass rate with and without the skill.
