# Changelog

All notable changes to **Project Maintainer** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-19

### Added

- `write-records` skill that writes a project's important decisions as architecture decision records (ADRs) and keeps a pending and a resolved technical-debt ledger.
- Templates for the ADR (based on MADR 4.0, with a scope, a risks table, a confirmation table and an optional pros-and-cons section), the pending-debt ledger and the resolved-debt ledger.
- The first time records are created in a git repository, Claude asks once whether git should track them or ignore them, and adds `.claude/maintainer/` to `.gitignore` only if you choose to ignore it.
- Before it creates the first records folder of a kind, Claude looks for decisions, debt and pending lists the project already keeps elsewhere, asks whether to migrate them, and asks again before it replaces, deletes or keeps each original, so no record lives in two places.
- Records live in a fixed place inside the project's `.claude/` folder, `.claude/maintainer/decisions/` and `.claude/maintainer/technical-debt/`, written with the Write tool. The README explains the permission prompt that Claude Code shows for `.claude/`.
- `write-handoff` skill and a `SessionStart` hook, carried over from the Session Handoff plugin: the handoff saves what was done, decided, corrected, learned and left open in `.claude/session-handoff/`, and the next session reads it first and ends its reply with the open items.
- The handoff is reconciled with the records: every pending debt item is listed in its open items, debt resolved since the last handoff is closed with its evidence, and decisions recorded since then are added, so the next session does not read the ledger separately.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/project-maintainer--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/project-maintainer--v0.1.0
