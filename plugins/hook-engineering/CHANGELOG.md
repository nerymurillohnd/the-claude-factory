# Changelog

All notable changes to **Hook Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-20

### Added

- `hook-development` skill: workflows to design, write, audit and debug Claude Code hooks, with condensed references for every hook event, handler type, matcher, exit code and JSON output field, for prompt, agent and background hooks, for workspace trust and security, and for mods that overrule hooks. Facts are checked against the Claude Code docs and changelog through v2.1.305.
- `hook-engineer` agent: a hooks specialist that works in design, write, audit or debug mode and reports what it changed, checked and could not verify.
- Helper scripts: a linter for hooks configuration files, a probe that predicts how Claude Code reads a command hook's result, and a changelog script that lists the hook-related entries newer than your installed version.
- The `claude-code-docs` MCP server (`https://code.claude.com/docs/mcp`), so Claude reads the official hooks pages instead of recalling them.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/hook-engineering--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.1.0
