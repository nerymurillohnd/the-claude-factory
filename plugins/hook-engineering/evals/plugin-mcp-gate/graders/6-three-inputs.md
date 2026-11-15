---
type: llm
focus: last_message
---

The task was a hook that stops dropping warehouse tables unless the name starts with tmp_.

PASS if the reply reports running the hook script itself on at least three inputs, with the outcome each one actually produced: a table name without tmp_ that is denied, a tmp_ name that is allowed, and an input the script cannot read (malformed or missing fields) that is blocked.
FAIL if it reports fewer than these three, describes only expected outcomes without having run the script, or reports an unreadable input that is allowed through.
