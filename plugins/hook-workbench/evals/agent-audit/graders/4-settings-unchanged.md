---
type: regex
pattern: 'Check the written file has no secrets\. \$ARGUMENTS",\s*"async": true'
target: { source: file, path: .claude/settings.json }
arm: both
---
