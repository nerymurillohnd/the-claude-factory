# Changelog

All notable changes to **Work Lifecycle** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-18

### Changed

- `planning-researcher` and `plan-verifier` now use your session's documentation servers, skills and other MCP tools to check facts, instead of fetching web pages only, and say when to use them at the start of their descriptions. Both now run on your session's model with every tool your session has, MCP tools included, except `Edit` and `Write`, and are told to change nothing; `planning-researcher` also runs at your session's effort level.
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
