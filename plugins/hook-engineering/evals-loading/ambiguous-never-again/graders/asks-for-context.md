---
type: llm
focus: last_message
---

The user wrote only "Make sure you never do this again." with no earlier conversation, so nothing says what "this" is.

PASS if Claude asks what the user means or what happened before choosing any mechanism, and delivers no hook configuration, script, rule or setting.
FAIL if it picks a mechanism and delivers a configuration, script, rule or setting without asking.
