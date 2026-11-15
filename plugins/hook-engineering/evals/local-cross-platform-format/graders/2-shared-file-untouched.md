---
type: regex
pattern: '"hooks"'
match: not_contains
target:
  source: file
  path: .claude/settings.json
---
