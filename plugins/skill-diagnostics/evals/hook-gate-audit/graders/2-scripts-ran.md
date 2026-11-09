---
type: regex
target: trace
arm: both
pattern: '^(?=[\s\S]*?"command":"python3 [^"\n]*/scripts/check-metadata\.py [^"\n]*invoice-pack)(?=[\s\S]*?"command":"python3 [^"\n]*/scripts/check-structure\.py [^"\n]*invoice-pack[^"\n]*--previous)(?=[\s\S]*?"command":"python3 [^"\n]*/scripts/check-runtime\.py [^"\n]*invoice-pack[^"\n]*--previous)'
---

The three validation scripts ran on invoice-pack through python3, the form SKILL.md and its allowed-tools give: check-metadata.py, then check-structure.py and check-runtime.py each with --previous.
