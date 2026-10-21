---
type: llm
weight: 3
---

On Claude Code 2.1.293, prompt and agent hooks written as rules (such as "Block commands that...") could allow what they should block; 2.1.294 fixed it.

PASS if the reply warns that the user's version (2.1.293) is affected by that problem, or says rule-style prompt hooks need 2.1.294 or later, and recommends upgrading.
FAIL if it hands over the hook without that warning, or names the wrong version.
