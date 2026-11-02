# Changelog

All notable changes to **Instruction Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-11-02

### Changed

- The plugin's keywords now name what it works on: `claude-md`, `rules`, `instructions`, `memory` and `audit`.
- The README states why Claude Code 2.1.271 is the minimum.

### Fixed

- The changelog describes what 0.1.0 shipped.

## [0.1.0] - 2026-10-28

### Added

- `instruction-engineering:claude-md-and-rules` skill: writes, edits, reviews, audits, debugs and refactors `CLAUDE.md`, `CLAUDE.local.md` and `.claude/rules` files at user and project scope against Claude Code's current loading rules. It checks every change against the whole instruction set, finds contradictions, duplicates, ambiguous and misplaced lines, and says when a line belongs in a path-scoped rule, a skill or a hook instead.
- A read-only checker, `check_instructions.py`, that the skill runs with `python3` 3.12 or later: it inventories the instruction files at project and user scope and reports frontmatter problems, path globs that match nothing, imports that do not resolve, duplicate lines and size limits. It never edits, runs or uploads anything.
- `instruction-engineering:reviewer` agent: an independent, read-only reviewer that audits a large instruction set, a refactor or proposed changes in its own context, without loading your `CLAUDE.md` files.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/instruction-engineering--v0.1.1...HEAD
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/instruction-engineering--v0.1.0
