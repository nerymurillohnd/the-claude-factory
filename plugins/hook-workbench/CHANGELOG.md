# Changelog

All notable changes to **Hook Workbench** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-20

### Added

- `hook-design` skill: designs, writes, audits and debugs prompt hooks, agent hooks and background (`async`, `asyncRewake`) hooks, with per-event `ok: false` behavior, Stop-loop handling, workspace-trust and safe-script review, PowerShell placeholders, a debug-log symptom table and a version table checked against Claude Code 2.1.305.
- Docs map (`references/docs-map.md`): every section the plugin relies on, with its exact source header, its URL and anchor, and how the anchor was verified; how to fetch a section's raw text and the changelog entries newer than the user's version. Every reference section carries a `Docs:` line, and every answer states what it was verified against.
- `hook-engineer` agent: runs a design, write, audit or debug task in its own context with the skill preloaded, and reports changed files, checks run and anything out of scope.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/hook-workbench--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-workbench--v0.1.0
