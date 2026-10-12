---
type: regex
target: trace
arm: with-only
pattern: '^(?=[\s\S]*?"input":\{"file_path":"[^"]*skills/audit/references/conformance\.md"\}[^\n]*"parent_tool_use_id":"toolu_)(?=[\s\S]*?"input":\{"file_path":"[^"]*skills/audit/references/fields\.md"\}[^\n]*"parent_tool_use_id":"toolu_)(?=[\s\S]*?"input":\{"file_path":"[^"]*skills/audit/references/surfaces\.md"\}[^\n]*"parent_tool_use_id":"toolu_)(?=[\s\S]*?"input":\{"file_path":"[^"]*skills/audit/references/executability\.md"\}[^\n]*"parent_tool_use_id":"toolu_)'
---

The lens agents read the skill's own references in full: conformance.md, fields.md and surfaces.md for conformance, executability.md for executability.
