# Changelog

All notable changes to **Tool Ledger** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.1.0] - 2026-10-22

### Added

- A live panel, opened with `/tool-ledger`, that lists each tool call of the session with its status (`runs`, `done`, `error` or `denied`), its tool, what it acted on and its duration, with subagents' calls grouped under their type and task.
- `denied` for calls another mod, a settings `PreToolUse` hook or the permission check refuses.
- An **Errors only** filter, and the `autoOpen`, `showTargets` and `maxRows` options.
- A ledger that fails never touches the call: it still runs once and returns its own result.
- Tested with Claude Code v2.1.308; requires v2.1.295 or later.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/tool-ledger--v0.1.1...HEAD
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tool-ledger--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/tool-ledger--v0.1.0
