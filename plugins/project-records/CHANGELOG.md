# Changelog

All notable changes to **Project Records** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-19

### Added

- `record-decisions-and-debt` skill that writes a project's important decisions as architecture decision records (ADRs) and keeps a pending and a resolved technical-debt ledger.
- Templates for the ADR (based on MADR 4.0, with a scope, a risks table and a confirmation table), the pending-debt ledger and the resolved-debt ledger.
- Records go where the project already keeps them (`CLAUDE.md`, `AGENTS.md` or an existing folder) and default to `docs/decisions/` and `docs/technical-debt/`.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/project-records--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/project-records--v0.1.0
