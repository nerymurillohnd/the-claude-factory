---
type: regex
target: trace
arm: both
pattern: '^(?=[\s\S]*?"subagent_type":"skill-diagnostics:description-reviewer")(?=[\s\S]*?"subagent_type":"skill-diagnostics:instructions-reviewer")(?=[\s\S]*?"subagent_type":"skill-diagnostics:scripts-runtime-reviewer")(?=[\s\S]*?"subagent_type":"skill-diagnostics:security-reviewer")(?=[\s\S]*?"subagent_type":"skill-diagnostics:cold-executor")(?=[\s\S]*?"subagent_type":"skill-diagnostics:adversarial-verifier")'
---

All six plugin agents were launched: the four reviewers, the cold executor and the adversarial verifier.
