---
type: llm
---

The skill is valid for Claude Code. These are all supported there: the missing `name` field (it defaults to the folder name); the `when_to_use`, `argument-hint`, `arguments` and `effort` fields; `allowed-tools` written as a space-separated string; the `$file` placeholder; and the `` !`date +%F` `` line, which injects the command's output.

PASS if the reply does not tell the user that any of those items is invalid, unrecognized, ignored, an error, or must be changed for Claude Code. Saying an item would not work on another surface (a claude.ai upload or the API) is fine, and so is an optional, low-priority suggestion to add `name` for portability, as long as it is not called required or an error in Claude Code. Other suggestions are fine.
FAIL if it says any of those items is invalid, unrecognized, ignored, an error, or must be changed for Claude Code.
