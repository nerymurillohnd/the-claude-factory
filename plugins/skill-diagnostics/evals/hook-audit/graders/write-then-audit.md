---
type: tool_order
before: { tool: Write, input_match: 'invoice-pack/SKILL\.md' }
after: { tool: Skill, input_match: '"skill"\s*:\s*"(?:[\w-]+:)?audit"' }
arm: both
---
