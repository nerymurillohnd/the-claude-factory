# Changelog

All notable changes to **Project Maintainer** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-22

### Changed

- **Breaking:** requires Claude Code v2.1.307 or later. The guardrails now ask for your approval with the `{ decision: 'ask', reason }` answer, and drop the `decider` field that Claude Code v2.1.307 no longer reads. From that version, Claude Code puts every guardrail prompt to you and no classifier can answer it. On v2.1.304 to v2.1.306, auto mode's classifier could approve the edit for you, so update Claude Code first.
- The README's "What's inside" table now says what each piece does for you and what it prevents, with the four parts of the guardrails listed one by one, and where the hook and the mod run.

## [0.1.0] - 2026-10-19

### Added

- `write-records` skill that writes a project's important decisions as architecture decision records (ADRs) and keeps a pending and a closed technical-debt ledger. One ADR per decision, so each can be replaced on its own.
- Templates for the ADR (based on MADR 4.0, with a scope, a risks table, a confirmation table and an optional pros-and-cons section), the pending-debt ledger and the closed-debt ledger.
- A debt item closes with an outcome and the evidence it needs: *resolved* (the fix works and the old failure is gone), *obsolete* (the code or the architecture changed and the problem no longer exists) or *accepted* (you decided to keep it, recorded in an ADR).
- The first time records are created in a git repository, Claude asks once whether git should track them or ignore them, and adds `.claude/maintainer/` to `.gitignore` only if you choose to ignore it.
- Before it creates the first records folder of a kind, Claude looks for decisions, debt and pending lists the project already keeps elsewhere, asks whether to migrate them, and asks again before it replaces, deletes or keeps each original, so no record lives in two places.
- Records live in a fixed place inside the project's `.claude/` folder, `.claude/maintainer/decisions/` and `.claude/maintainer/technical-debt/`, written with the Write tool. The README explains the permission prompt that Claude Code shows for `.claude/`.
- `write-handoff` skill and a `SessionStart` hook, carried over from the Session Handoff plugin, which this plugin replaces (the marketplace renames an existing install): the handoff saves what was done, decided, corrected, learned and left open in `.claude/session-handoff/`, and the next session reads it first and ends its reply with the open items.
- The handoff is reconciled with the records: every pending debt item is listed in its open items, debt closed since the last handoff is closed there too, and decisions recorded since then are added, so the next session does not read the ledger separately.
- The start-of-session hook tells the next session when the records changed after the handoff was written: a pending item the handoff does not mention, a closed item it still lists as open, or a newer ADR. It finds the handoff in a git worktree too.
- Guardrails, a Claude Code mod: a malformed ADR or debt ledger is refused with the reason; Claude Code asks you before a settled ADR, a closed debt entry or a pending item without a closed entry is changed, and before a shell command rewrites the records. No classifier can approve those prompts for you, and where nobody can answer the edit is refused.
- Before a compaction, the summary is told to keep decisions, open items and record IDs. After a commit that looks like a decision, such as one that changes dependencies, a schema, CI or infrastructure, Claude gets one reminder to record it. The reminder can be turned off in the plugin's settings.
- **Requires Claude Code v2.1.304 or later.**

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/project-maintainer--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/project-maintainer--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/project-maintainer--v0.1.0
