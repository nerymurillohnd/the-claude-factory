# Changelog

All notable changes to **Project Maintainer** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-19

### Added

- `write-records` skill that writes a project's important decisions as architecture decision records (ADRs) and keeps a pending and a resolved technical-debt ledger.
- Templates for the ADR (based on MADR 4.0, with a scope, a risks table, a confirmation table and an optional pros-and-cons section), the pending-debt ledger and the resolved-debt ledger.
- The first time records are created in a git repository, Claude asks once whether git should track them or ignore them, and adds the two folders to `.gitignore` only if you choose to ignore them.
- Before it creates the first records folder of a kind, Claude looks for decisions, debt and pending lists the project already keeps elsewhere, asks whether to migrate them, and asks again before it replaces, deletes or keeps each original, so no record lives in two places.
- A new ADR takes the naming pattern of the ADRs already in the folder, so numbered folders stay numbered.
- Records go where the project already keeps them (`CLAUDE.md`, `AGENTS.md` or an existing folder) and default to `docs/decisions/` and `docs/technical-debt/`.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/project-maintainer--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/project-maintainer--v0.1.0
