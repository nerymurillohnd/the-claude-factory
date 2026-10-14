---
description: A vague request with no context. Hypothesis - with the plugin the reply asks a few questions about the situation and the outcome, none about model, effort or structure, and does not write the prompt yet; without it Claude either writes a generic prompt or asks technical questions.
tags: [core]
max_turns: 10
timeout_seconds: 180
allowed_tools: [Read]
model: sonnet
runs: 3
---
/prompt-writer:prompt-writer I want a prompt so Claude helps me deal with my suppliers better.
