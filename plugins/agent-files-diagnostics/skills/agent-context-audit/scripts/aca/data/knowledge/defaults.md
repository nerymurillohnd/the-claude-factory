# Documented defaults catalog (evidence ladder level b)

A finding of category `redundant-with-defaults` at ladder level `b` must cite one of these IDs in `conflicts_with` (kind `default`). Each entry is a behavior the official docs describe as native or default. All were checked on 2026-10-14. When an instruction only restates one of these, it costs context without changing behavior; when it narrows or changes the default, it is not redundant.

| ID | Default behavior | Source |
| :-- | :-- | :-- |
| DEF-CC-CLAUDEMD-LOADS | Claude Code reads CLAUDE.md files at the start of every session (no instruction is needed to make it read them). | <https://code.claude.com/docs/en/memory> |
| DEF-CC-AGENTSMD-FALLBACK | Without a CLAUDE.md, Claude Code reads AGENTS.md as project instructions (2.1.277+). | <https://code.claude.com/docs/en/memory#agents-md> |
| DEF-CC-AUTO-MEMORY | Claude saves corrections and preferences to auto memory on its own; a "remember what I correct" instruction adds nothing. | <https://code.claude.com/docs/en/memory#auto-memory> |
| DEF-CC-READ-BEFORE-OVERWRITE | Claude Code requires a read before editing or overwriting a file in the cases that need one; the Edit tool enforces it. | <https://code.claude.com/docs/en/tools-reference#edit-tool-behavior> |
| DEF-CC-EDIT-PROMPTS | File edits and non-read-only shell commands ask for permission by default (Manual mode). | <https://code.claude.com/docs/en/permissions> |
| DEF-CC-READONLY-COMMANDS | Built-in read-only commands such as ls, cat, grep, find and read-only git run without a prompt. | <https://code.claude.com/docs/en/permissions#read-only-commands> |
| DEF-CC-PROTECTED-PATHS | Writes to protected paths (.git, .claude and shell profile files, among others) are never pre-approved by allow rules: they prompt, go to the auto-mode classifier, or are denied, except in bypassPermissions mode. | <https://code.claude.com/docs/en/permission-modes> |
| DEF-CC-GIT-INSTRUCTIONS | Claude's context includes built-in commit and pull request instructions unless includeGitInstructions is false. | <https://code.claude.com/docs/en/settings-reference#includegitinstructions> |
| DEF-CC-ATTRIBUTION | Claude Code adds attribution to commits and pull requests by default; the attribution setting changes or hides it. | <https://code.claude.com/docs/en/settings-reference#attribution> |
| DEF-CC-CHECKPOINTS | Claude Code snapshots files before edits so /rewind can restore them. | <https://code.claude.com/docs/en/settings-reference#filecheckpointingenabled> |
| DEF-CC-SUBAGENT-CONTEXT | A subagent starts fresh: no conversation history and no main auto memory, only its prompt, the delegation message and the CLAUDE.md hierarchy. | <https://code.claude.com/docs/en/sub-agents#what-loads-at-startup> |
| DEF-CC-RULES-PATHS | A rule with paths frontmatter loads only when Claude touches a matching file; restating "apply this only to X files" in prose adds nothing. | <https://code.claude.com/docs/en/memory#path-specific-rules> |
| DEF-CODEX-AGENTSMD-LOADS | Codex reads AGENTS.md files before doing any work, concatenated from the project root down. | <https://developers.openai.com/codex/guides/agents-md> |
| DEF-CODEX-NO-CACHE | Codex rebuilds the instruction chain on every run; there is nothing to refresh by hand. | <https://developers.openai.com/codex/guides/agents-md> |
| DEF-CODEX-SIZE-LIMIT | Codex reads at most project_doc_max_bytes (32 KiB by default) of project instructions. | <https://developers.openai.com/codex/guides/agents-md> |
