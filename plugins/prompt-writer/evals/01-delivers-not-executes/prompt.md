---
description: A user invokes the skill with a task Claude could simply do. Hypothesis - with the plugin the reply is a prompt for another session; without it Claude does the task.
tags: [core]
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read]
model: sonnet
runs: 3
---
/prompt-writer:prompt-writer Translate this to Spanish for a customer email, formal tone: "The shipment leaves Puerto Cortés on Monday and arrives in Rotterdam 18 days later." Everything you need is above, so don't ask me anything.
