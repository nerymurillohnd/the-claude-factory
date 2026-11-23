# Changelog

All notable changes to **Hook Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `writing-hooks` now sends a hook's tests and evals to `plugin-engineering:test-and-evals` and plugin debugging to `plugin-engineering:troubleshoot-and-debug`, which replace `plugin-testing-and-debugging`.

## [0.3.3] - 2026-11-23

### Fixed

- `writing-hooks` now tells Claude that on Windows a file path in the hook input arrives with backslashes, even under Git Bash, and has it convert them to forward slashes before the hook compares the path. Before, a hook it wrote could miss every Windows path and let through a call it was meant to block.

## [0.3.2] - 2026-11-19

### Changed

- The `hook-engineer` agent's instructions now open with its role, its expertise and a goal that sums up its existing rules, and mark each section with a plain label instead of a Markdown heading. Its instructions keep everything they said.

## [0.3.1] - 2026-11-18

### Changed

- `hook-development` now loads when you audit, review or debug a hook, or ask how hooks behave, and no longer competes with `writing-hooks` when you ask for a new hook. The `hook-engineer` agent says it audits, debugs or writes a hook from a complete task message and reports back, and that writing a hook with you is `writing-hooks`' job. Nothing else changes in how the plugin works.

## [0.3.0] - 2026-11-15

### Added

- A new `writing-hooks` skill writes a new hook of any type (command, HTTP, MCP tool, prompt or agent) in any place a hook can live: a plugin, your user, project, local or managed settings, a skill or a subagent. It reads what you ask and your project first, asks you only about your goal when something is unclear, reads the current official hooks docs and changelog for your Claude Code version, and tests the hook with real inputs before it hands it over.

## [0.2.6] - 2026-11-15

### Changed

- `hook-development` now warns that `set -e` makes a Bash hook exit with the failing command's own code. `grep` and `jq` can exit 2, which blocks on events such as `PreToolUse` and `Stop`. The skill shows how to map every unexpected failure to the exit code the hook means.

## [0.2.5] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.2.4] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.2.3] - 2026-10-30

### Changed

- The configuration rules in the skill are now one instruction per line: how to nest handlers, write matchers, use `if`, `once` and `onFailure`, and reach plugin options.
- The Setup hook note on `additionalContext` is now a short check you run on your own Claude Code build.
- The references no longer repeat the date and version they were last read at; the skill keeps one baseline in `sources.md`, which its changelog check uses.

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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/hook-engineering--v0.3.3...HEAD
[0.3.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.3.3
[0.3.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.3.2
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.3.0
[0.2.6]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.6
[0.2.5]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.5
[0.2.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.4
[0.2.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.3
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/hook-engineering--v0.1.0
