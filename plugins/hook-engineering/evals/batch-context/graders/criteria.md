---
type: llm
---

PASS if the answer recommends the PostToolBatch event, explains that it fires once after all tool calls in a batch resolve (unlike PostToolUse, which fires per tool), and shows output with hookSpecificOutput.hookEventName "PostToolBatch" and an additionalContext string. It is fine if it notes that PostToolBatch has no matcher, so the script filters the tool_calls array itself.
FAIL if it recommends PostToolUse with deduplication as the primary answer, or puts a matcher on PostToolBatch as if it filtered tool names.
