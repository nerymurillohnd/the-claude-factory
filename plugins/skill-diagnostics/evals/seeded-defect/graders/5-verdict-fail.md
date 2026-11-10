---
type: tool_used
tool: Bash
input_match: '"command":"(?:[^"\\]|\\.)*record-verdict\.py(?:[^"\\]|\\.)*invoice-pack(?:[^"\\]|\\.)*\sfail(?![\w-])'
arm: both
---

The audit ended by recording the verdict for invoice-pack with record-verdict.py, and the verdict is fail: the seeded defect is high (it breaks execution for two countries the reference table supports).
