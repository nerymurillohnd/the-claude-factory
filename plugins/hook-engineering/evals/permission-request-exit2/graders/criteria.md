---
type: llm
---

PASS if the answer says that exit code 2 is not honored (ignored) for the PermissionRequest event, and that the hook must instead print JSON with a hookSpecificOutput.decision object whose behavior is "deny" (optionally with a message), or alternatively move the check to a PreToolUse hook that denies.
FAIL if the answer claims exit code 2 should work on PermissionRequest and blames something else (matcher, permissions, executable bit) as the root cause, or if it proposes a top-level "decision": "block" for PermissionRequest.
