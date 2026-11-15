---
type: regex
target: trace
pattern: '"type":"tool_use","id":"[^"]+","name":"(Write|Edit|Bash)","input":\{.{0,4000}?(permissionDecision|exit 2|sys\.exit\(2\)|process\.exit\(2\))'
---
