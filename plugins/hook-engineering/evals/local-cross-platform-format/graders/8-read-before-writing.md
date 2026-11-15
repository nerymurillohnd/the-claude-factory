---
type: tool_order
before:
  tool: Read
  input_match: 'README\.md|\.claude/settings\.json'
after:
  tool: Write
  input_match: 'settings\.local\.json'
---
