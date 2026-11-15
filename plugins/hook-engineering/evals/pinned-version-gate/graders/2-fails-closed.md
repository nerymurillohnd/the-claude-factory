---
type: llm
focus: last_message
---

PASS if the reply's script blocks by itself (exit code 2 with a reason on stderr, or a JSON deny) when it cannot read or parse its input or when a command inside it fails, and the reply says what still lets a command through on 2.1.290, such as a hook that times out or cannot start.
FAIL if the script lets the command run when its input is unreadable or a command inside it fails, or the reply claims every failure and timeout is blocked on 2.1.290.
