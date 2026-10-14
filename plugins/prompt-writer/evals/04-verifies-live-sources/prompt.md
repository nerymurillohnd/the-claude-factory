---
description: The user's setup relies on settings that the target model rejects. Hypothesis - with the plugin the skill checks live official pages, tells the user what changed and writes a prompt without those settings; without it Claude writes the prompt around them or corrects them from memory without a source.
tags: [network]
max_turns: 30
timeout_seconds: 480
allowed_tools:
  - Read
  - "WebFetch(domain:platform.claude.com)"
  - "WebFetch(domain:docs.claude.com)"
  - "WebFetch(domain:code.claude.com)"
  - "WebFetch(domain:claude.com)"
  - "WebFetch(domain:support.claude.com)"
  - "WebFetch(domain:agentskills.io)"
model: sonnet
runs: 3
---
/prompt-writer:prompt-writer I call the API with Claude Opus 5.5 to extract invoice fields into JSON. My integration sets temperature to 0.2, prefills the assistant turn with "{" to force JSON, and sets thinking budget_tokens to 8000. Write the system prompt that goes with this setup. Check anything that may have changed before you write it. Everything else you need is above, so don't ask me anything.
