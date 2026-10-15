# Changelog

All notable changes to **Agent Files Diagnostics** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-14

### Added

- `agent-files-diagnostics:agent-context-audit` skill, started only with `/agent-files-diagnostics:agent-context-audit`: a 14-phase, read-only audit of every Markdown file Claude Code and Codex load as instructions (`CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `AGENTS.override.md`, rules, memory, subagent definitions, output styles, `loop.md`, and every Markdown file they point to), planned first and run only after your approval, ending in one evidence-backed report.
- Four read-only agents the skill launches: `evidence-collector` (inventory and repository facts), `docs-researcher` (current official documentation and external claim checks), `instruction-reviewer` (one per package, reads every assigned line) and `audit-verifier` (checks coverage, every finding and the finished run).
- Eleven finding categories: false, wrong, obsolete, dead, ambiguous, duplicated, overlapping, misplaced, contradictory, redundant-with-defaults and non-conformant, each backed by exact lines and the evidence it conflicts with.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/agent-files-diagnostics--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/agent-files-diagnostics--v0.1.0
