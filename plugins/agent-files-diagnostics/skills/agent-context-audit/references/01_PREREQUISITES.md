# Phase 1: Prerequisites (steps)

1. Confirm that the operating system is supported (macOS, Linux, or WSL).
2. Confirm that Claude Code is installed, is signed in, and is version 2.1.271 or later. That is the first version that supports `omitClaudeMd`, which all four agents set. Read the version with `claude --version`.
3. Confirm that the tools of the deterministic steps are available: `git` when the repository uses it, `perl`, `cp`, `mkdir`, `wc`, and `shasum` or `sha256sum`. Add every interpreter or CLI that the approved plan names, at the minimum version the plan states.
4. Detect whether Codex is installed and record its version with `codex --version`. Codex has no minimum version: the audit reads files and documentation and never runs Codex. If Codex is not installed, record `not installed`. Its sources are still inventoried and audited, their loading modes come from the documentation, and whatever only the installed program could settle is marked `applicability unverified` and listed in the limitations of the report.
5. Identify the repository root and the target directory.
6. Define the report folder (see Write boundary) and assign this run a unique, sortable identifier.
