---
type: llm
focus: trace
---

PASS if Claude's first AskUserQuestion call comes before any Write or Edit of a hook configuration or hook script, or Claude writes no hook file at all.
FAIL if a hook configuration or hook script is written before the first AskUserQuestion call, or AskUserQuestion is never called.
