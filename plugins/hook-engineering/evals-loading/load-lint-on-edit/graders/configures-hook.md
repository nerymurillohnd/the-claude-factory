---
type: llm
focus: last_message
---

The user asked for the linter to run automatically every time Claude edits a file. That calls for a Claude Code hook, not a Git hook or an instruction in CLAUDE.md.

PASS if the reply configures a Claude Code hook, a PostToolUse hook whose matcher covers Edit and Write (or an equivalent such as Edit|MultiEdit|Write) and whose command runs a linter, or shows that exact hook configuration and the settings file it belongs in.
FAIL if the reply offers only a Git hook, a CLAUDE.md or memory instruction, an editor setting or a promise to run the linter, or if it shows no hook configuration.
