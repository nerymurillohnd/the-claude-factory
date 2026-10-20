---
type: llm
weight: 3
---

The hook script prints a line ("Running tests for ...") on stdout before its pretty-printed JSON. On Claude Code 2.1.304 an async hook's JSON must be alone on stdout (several lines allowed) or fit on one line of its own, so this output is not read as JSON and nothing reaches Claude.

PASS if the reply identifies the extra stdout line before the JSON as the cause and fixes it, either by sending that line to stderr or removing it, or by printing the JSON on one line (for example `jq -c` / `jq -nc`).
FAIL if it blames something else as the main cause (the async flag itself, the matcher, the Claude Code version, the session being idle) or gives no concrete fix.
