---
type: llm
focus: trace
---

Look at the questions in Claude's first AskUserQuestion call.

PASS if it asks one to four questions, and they ask about the user's goal and context: what quality means for this repository, what must block and what should only warn, who the hooks are for, or where they should apply.
FAIL if it asks more than four questions, or the questions ask the user to pick technical details such as hook events, matchers, exit codes or exec versus shell form.
