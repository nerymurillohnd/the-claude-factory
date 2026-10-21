---
type: llm
---

PASS if the answer says no, because updatedInput is validated like Claude's own tool input and unknown keys such as audit_tag are dropped (a change from Claude Code v2.1.300), and suggests another way to carry the tag (for example a file or other state keyed by tool_use_id or session_id).
FAIL if it says the extra key will be passed through to PostToolUse, or says no only for an unrelated reason without mentioning that unknown keys are dropped.
