---
type: llm
weight: 3
---

The settings file has three defects:
1. An agent-type hook on PermissionRequest: Claude Code skips agent hooks on that event (and ok:false from a prompt hook there has no effect either).
2. A prompt-type hook on SessionStart: prompt hooks are not supported on SessionStart.
3. "async": true on a prompt-type hook: async exists only on command hooks, so it is not a valid field there (ignored or invalid; either wording is correct).

PASS if the final reply identifies all three, each with the correct reason.
FAIL if any of the three is missing or explained wrongly, or if the reply says it changed the settings file.
