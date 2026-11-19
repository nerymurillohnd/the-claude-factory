# Changelog

All notable changes to **Work Lifecycle** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-18

### Added

- `restructuring-documents` skill: reorganizes documentation, such as splitting a long guide by topic, moving sections between files or renaming files other documents point to, without losing a line. It freezes a copy of the original, maps every line to its destination in a ledger you approve, moves the content task by task, and checks after each task, with a bundled script, that no line was lost, duplicated or altered and that no pointer names a stale file.
- `migration-verifier` agent: a read-only reviewer that runs in the background for the whole restructure, checks each task against the original and the ledger, and reports PASS or each problem with its file, line and original text.

### Changed

- `planning-before-execution` now delegates its research, before writing the plan, to one or more `planning-researcher` subagents in parallel, sized to the breadth of the work, and briefs each subagent, `plan-verifier` included, with the research resources your session has for the task: docs servers, connectors, skills and plugins. It no longer imposes worktree isolation: Claude decides where a probe or a parallel task runs from what the session and your settings allow.
- `planning-researcher` and `plan-verifier` now use your session's documentation servers, skills and other MCP tools to check facts, instead of fetching web pages only, and say when to use them at the start of their descriptions. Both now run on your session's model and effort level with every tool your session has, MCP tools included, and are told to change nothing; `plan-verifier` lacks `Edit` and `Write`.
- `planning-researcher` now covers everything a change touches beyond what its brief names: callers, entry points, every variant that changes the answer, and the official docs of every counterpart in an integration. It reads the release notes for the installed version, the four releases before it and every release after it.
- Both agents list only the keys of `.env`, settings and MCP configuration files, and never read or quote their values.
- `planning-before-execution` counts work published to third parties, such as a public plugin or marketplace, as high-stakes, so it gets the independent review.
- `planning-before-execution` now says what happens when you correct a plan before approving it: Claude checks each point, proposes the changes, rewrites the whole plan once you approve them, reviews it again and asks you to approve the full plan. Only the full plan, approved as written, starts the work.
- `planning-before-execution` reuses research done earlier in the session only after checking it again against its source, or when its evidence is already quoted, and still delegates exploration beyond a few files to `planning-researcher`.

## [0.1.0] - 2026-11-15

### Added

- Initial release. Requires Claude Code 2.1.325 or later and python3 3.12 or later.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/work-lifecycle--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/work-lifecycle--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/work-lifecycle--v0.1.0
