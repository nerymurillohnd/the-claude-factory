---
type: regex
target: trace
match: not_contains
pattern: "changed and wasn't audited after the change"
---

The Stop hook never gave up: its loop-guard warning (systemMessage) is absent, so the verdict cleared the gate before the turn ended.
