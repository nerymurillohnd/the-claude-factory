---
type: llm
---

PASS if the answer identifies that SessionEnd hooks have a short default timeout (1.5 seconds) and gives at least one correct fix: setting a per-hook "timeout" on that hook in a settings file (which raises the overall budget, up to 60 seconds), or setting the CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS environment variable in milliseconds.
FAIL if it attributes the problem mainly to credentials, networking or the script itself, or states a default timeout of 60 or 600 seconds for SessionEnd.
