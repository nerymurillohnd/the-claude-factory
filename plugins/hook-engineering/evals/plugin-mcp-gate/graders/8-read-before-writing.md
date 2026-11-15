---
type: tool_order
before:
  tool: Read
  input_match: '\.mcp\.json|plugin\.json'
after:
  tool: Write
  input_match: 'hooks\.json'
---
