---
type: tool_order
before: { tool: Write, input_match: 'greet/SKILL\.md' }
after: { tool: Skill, input_match: '"skill"\s*:\s*"(?:[\w-]+:)?skills-best-practices"' }
arm: both
---
