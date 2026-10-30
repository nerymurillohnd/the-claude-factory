# Changelog

All notable changes to **Hook Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2026-10-30

### Changed

- The Setup hook note on `additionalContext` is now a short check you run on your own Claude Code build, instead of a dated observation from one older version.
- The event references no longer carry the date and version they were last read at; check facts against your installed Claude Code.
- Every reference now points to the baseline in `sources.md` instead of repeating its date and version.

## [0.2.2] - 2026-10-30

### Fixed

- A note on `additionalContext` in Setup hooks now names the declarations file Claude Code writes into a mod's `.claude-plugin/types/`, instead of a path from an older layout.

## [0.2.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.2.0] - 2026-10-22

### Removed

- **Breaking:** the plugin no longer bundles the `claude-code-docs` MCP server. Add it yourself once: in Claude Code, `claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp`, then check it with `claude mcp list`; in the Claude app, add `https://code.claude.com/docs/mcp` as a custom connector with **No sign in**. Without it, the plugin tells you the command once and reads the raw docs pages.

### Changed

- The `hook-engineer` agent now inherits your session's tools instead of a fixed list, so it can use the docs server under any name, a Claude app connector included.
- When `python3`, `curl` or `awk` is missing, the skill names the tool, says which check could not run and marks what that check would have proved as unverified.

## [0.1.0] - 2026-10-21

### Added

- `hook-development` skill: workflows to design, write, audit and debug Claude Code hooks, with condensed references for every hook event, handler type, matcher, exit code and JSON output field, for prompt, agent and background hooks, for workspace trust and security, and for mods that overrule hooks. Facts are checked against the Claude Code docs and changelog through v2.1.305.
- `hook-engineer` agent: a hooks specialist that works in design, write, audit or debug mode and reports what it changed, checked and could not verify.
- Helper scripts: a linter for hooks configuration files, a probe that predicts how Claude Code reads a command hook's result, and a changelog script that lists the hook-related entries newer than your installed version.
- The `claude-code-docs` MCP server (`https://code.claude.com/docs/mcp`), so Claude reads the official hooks pages instead of recalling them.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/hook-engineering--v0.2.3...HEAD
[0.2.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.3
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.1.0
