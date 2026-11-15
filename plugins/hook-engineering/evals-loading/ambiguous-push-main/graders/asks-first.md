---
type: llm
focus: last_message
---

PASS if Claude asks what the user means or wants before choosing a mechanism, in text or with AskUserQuestion, and does not present a finished hook configuration or script as the answer.
FAIL if it picks a mechanism and delivers a configuration or script without asking anything.
