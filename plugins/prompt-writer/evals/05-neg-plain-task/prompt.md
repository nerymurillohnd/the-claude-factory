---
description: Negative case. A plain task with no invocation. Hypothesis - the skill stays out and the user gets the summary they asked for, with no prompt-writing output.
tags: [core]
max_turns: 5
timeout_seconds: 60
allowed_tools: [Skill]
model: sonnet
runs: 3
---
Summarize this in two sentences: "The warehouse in San Pedro Sula moved to a new inventory system last month. Scanning each pallet at the dock cut loading errors by a third, but the first two weeks were slow because staff were still learning the handheld scanners. The manager expects the savings to cover the cost of the system within a year."
