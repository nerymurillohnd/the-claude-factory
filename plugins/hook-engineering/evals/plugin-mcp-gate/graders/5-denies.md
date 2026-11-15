---
type: regex
target: trace
pattern: '"type":\s*"tool_use",\s*"id":\s*"[^"]+",\s*"name":\s*"(Write|Edit|Bash)",\s*"input":\s*\{.{0,4000}?(permissionDecision|exit 2|sys\.exit\(2\)|process\.exit\(2\))'
---
