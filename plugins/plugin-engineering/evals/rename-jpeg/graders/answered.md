---
type: llm
focus: last_message
---

PASS if the reply gives a bash one-liner that renames every `.jpeg` file in the current folder to `.jpg`, such as `for f in *.jpeg; do mv -- "$f" "${f%.jpeg}.jpg"; done`.
FAIL if the reply refuses, asks for unrelated setup, talks about Claude Code plugins, or gives a command that would not rename the files.
