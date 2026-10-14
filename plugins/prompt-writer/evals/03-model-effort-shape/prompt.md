---
description: All the context is given, so the skill proceeds. Hypothesis - with the plugin it reads its references and chooses model, effort, session mode and a single-prompt shape with reasons that match the documented guidance; without it the choice is generic or unreasoned.
tags: [core]
max_turns: 20
timeout_seconds: 300
allowed_tools: [Read]
model: sonnet
runs: 3
---
/prompt-writer:prompt-writer I run the support inbox of an online store. Every ticket is classified the moment it arrives: my backend sends the ticket text to Claude in one API call and needs the answer back in about a second. The answer must be a single JSON object with a category (billing, shipping, product or other) and an urgency from 1 to 5; a person only reviews urgency 4 and 5 the next morning. There is no conversation and no follow-up call. Everything you need is above, so don't ask me anything: write the prompt.
