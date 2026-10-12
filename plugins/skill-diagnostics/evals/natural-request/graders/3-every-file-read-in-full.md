---
type: regex
target: trace
arm: with-only
pattern: '^(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/SKILL\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/assets/invoice-de\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/assets/invoice-en\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/assets/invoice-es\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/assets/invoice-fr\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/references/countries\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/references/currency\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/references/tax-rules\.md"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/scripts/check_totals\.py"\}[^\n]*"parent_tool_use_id":"toolu_){2})(?=(?:[\s\S]*?"input":\{"file_path":"[^"]*invoice-pack/scripts/render\.py"\}[^\n]*"parent_tool_use_id":"toolu_){2})'
---

Each of the ten inventory files has at least two full reads (no offset or limit) made inside subagents: one per lens agent.
