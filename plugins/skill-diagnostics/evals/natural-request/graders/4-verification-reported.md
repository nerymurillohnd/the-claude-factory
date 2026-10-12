---
type: regex
pattern: 'Verification:[\s\S]{0,400}?(?<![\w-])[1-9]\d* (?:\w+ )?verified'
flags: i
arm: both
---

The report's Verification line, or the list nested under it, gives a non-zero count of verified findings.
