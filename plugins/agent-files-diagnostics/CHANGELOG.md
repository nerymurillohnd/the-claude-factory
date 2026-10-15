# Changelog

All notable changes to **Agent Files Diagnostics** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-15

### Added

- `agent-files-diagnostics:agent-context-audit` skill, started only with `/agent-files-diagnostics:agent-context-audit`: a read-only audit of every Markdown file Claude Code and Codex load as instructions and memory (`CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `AGENTS.override.md`, rules, auto memory, subagent definitions, output styles, `loop.md`, Codex memories, and every Markdown file they import), agreed with you first and ending in one evidence-backed report. `latest` shows the newest report.
- Two dynamic workflows, `audit-domains` and `review-and-verify`, that run the four read-only agents the skill relies on: `domain-auditor` (one per package, reads every assigned line), `cross-domain-reviewer` (compares meaning across files and settles the challenge round), `finding-verifier` (re-reads every finding) and `claim-researcher` (checks claims about tools and versions against official sources).
- A bundled Python script that inventories the sources with their loading mode, consumption, availability and applicability, makes redacted working copies, runs the mechanical checks (broken imports and links, dead rules, truncation, exact duplicates), proves from the agents' transcripts that every line was read, validates every finding against the copies, records your own inspection of each finding, checks that nothing changed, and writes `report.md`, `report.json` and `status.json` with a run history.
- Eleven finding categories: false, wrong, obsolete, dead, ambiguous, duplicated, overlapping, misplaced, contradictory, redundant-with-defaults and non-conformant, each with exact lines, the excerpt, what it conflicts with, a disposition, and its verification status.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/agent-files-diagnostics--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/agent-files-diagnostics--v0.1.0
