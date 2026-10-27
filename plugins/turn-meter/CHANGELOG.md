# Changelog

All notable changes to **Turn Meter** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-10-27

### Changed

- Internal code cleanup from a stricter lint rule; the band shows the same figures.
- Validated and tested on Claude Code v2.1.311.

## [0.1.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.1.0] - 2026-10-22

### Added

- A band above the prompt that shows how long the last turn took, its tool calls split between the main thread and subagents, and its tokens, with how it ended when it was interrupted, failed or refused.
- A long-turn alert, as a toast or a native notification, after a number of seconds you choose.
- The `/turn-meter` command and a **Hide** button to hide or show the band.
- Tested with Claude Code v2.1.308; requires v2.1.295 or later.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/turn-meter--v0.1.2...HEAD
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/turn-meter--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/turn-meter--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/turn-meter--v0.1.0
