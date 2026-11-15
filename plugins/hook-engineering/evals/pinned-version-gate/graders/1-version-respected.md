---
type: llm
focus: last_message
---

The team is pinned to Claude Code 2.1.290. The `onFailure` hook field was added in Claude Code 2.1.295, so it doesn't exist on 2.1.290.

PASS if the configuration the reply delivers doesn't set `onFailure`, or sets it only while saying plainly that it has no effect before 2.1.295, and the reply tells the user that blocking on a hook failure or timeout through `onFailure` needs 2.1.295 or later.
FAIL if the configuration relies on `onFailure` for the team's 2.1.290 without saying it doesn't exist there, or the reply never relates the design to the pinned version.
