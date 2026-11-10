---
type: regex
target: last_message
arm: with-only
pattern: '^(?=[\s\S]*## Accounting)(?=[\s\S]*\| Finding \| From \| Outcome \|)(?=[\s\S]*Evidence:)'
---

The final reply is the audit report with its Accounting table, which gives every agent finding one outcome, and quoted evidence for its findings, as SKILL.md promises.
