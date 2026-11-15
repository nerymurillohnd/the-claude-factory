---
type: llm
focus: last_message
---

In Claude Code, PostToolBatch fires once after a batch of parallel tool calls resolves, takes no matcher, receives tool_calls in its input, and adds context through hookSpecificOutput with hookEventName "PostToolBatch" and additionalContext. PostToolUse fires once per tool call.

PASS if the reply's configuration uses PostToolBatch with no matcher, and its script builds the note from tool_calls and prints hookSpecificOutput with hookEventName "PostToolBatch" and additionalContext.
FAIL if it uses PostToolUse or another per-call event for the note, sets a matcher on PostToolBatch, or prints the context in another shape.
