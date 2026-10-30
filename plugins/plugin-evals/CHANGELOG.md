# Changelog

All notable changes to **Plugin Evals** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-10-30

### Changed

- The warnings that a committed suite and its recorded replays ship to users are now separate, single-action instructions.

## [0.1.3] - 2026-10-30

### Changed

- The skill now warns that a committed eval suite ships: the eval directory always sits below the plugin, so prompts, fixtures and recorded MCP replays reach every user's copy. Keep secrets and private data out of them.

## [0.1.2] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.1.1] - 2026-10-14

### Fixed

- The references no longer say the plugin evals docs page grades runs that ended on an API error: the page documents since v2.1.299 that such a run scores 0 without grading. The results reference now matches the page on other abnormal endings: some are still graded, so an error does not mean a score of 0.
- The references' snapshot was checked again against Claude Code v2.1.300, which brought no `plugin eval` changes.

## [0.1.0] - 2026-10-14

### Added

- Skill `plugin-evals`: loads whenever a task involves Claude Code plugin evals, and checks every time-sensitive fact against the installed `claude` CLI, the live docs and the changelog before using it.
- A method for suites whose score means something: cases that prove a difference, an outcome and a process grader per case, triggering measured as a rate, tools that match the graders, a one-run pilot, and a cost check before every paid run. CI commands always carry pinned agent and judge models, a cost ceiling, the threshold and trust inside the command.
- References for the case format and graders, fixtures and MCP mocks, running and CI (targets, options, tool grants and the OS sandbox, trust, credentials, exit codes), reading results and troubleshooting, and other eval formats (skill-creator's `evals.json`, `/claude-api build-eval`), written against Claude Code v2.1.299.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/plugin-evals--v0.1.4...HEAD
[0.1.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-evals--v0.1.4
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-evals--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-evals--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-evals--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-evals--v0.1.0
