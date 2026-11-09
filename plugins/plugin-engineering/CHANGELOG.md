# Changelog

All notable changes to **Plugin Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2026-11-09

### Changed

- `public-marketplace-dev` now tells Claude to declare `options` on a `userConfig` field that a plugin hook reads as one of a few fixed values, instead of leaving it free text.

## [0.2.1] - 2026-11-09

### Changed

- `public-marketplace-dev` now loads the `cli-commands-guide` skill before Claude runs, writes or explains a plugin command, including the `claude plugin validate --strict` run after a change, so its exact flags, gotchas and exit codes apply. Answers that use no plugin command don't load it.

## [0.2.0] - 2026-11-08

### Added

- `public-marketplace-dev` skill: the official Claude Code, Claude plugin, Claude Platform and Help Center pages, pruned to what a public GitHub marketplace and the people who install its plugins need and rewritten for Claude, so Claude designs, builds, validates, releases and maintains plugins and marketplaces from the documented behavior instead of memory. It holds 65 references in seven areas (plugins and marketplaces, mods, feature references such as hooks, skills, subagents and MCP servers, settings, CLI and diagnostics, the Agent SDK, and other surfaces), 29 images of the official pages and 3 example manifests.
- Before relying on a version-sensitive fact, Claude checks the Claude Code release notes published after the references were checked (Claude Code 2.1.319) and the live page, and tells you what differs. After it changes plugin or marketplace files, it runs `claude plugin validate --strict` and fixes what the validator reports.

### Changed

- **Breaking:** the `plugin-commands` skill is now `cli-commands-guide`, so its name says what it covers next to the new skill. If you call it by name, use `/plugin-engineering:cli-commands-guide`; its content is unchanged.

## [0.1.0] - 2026-11-07

### Added

- `plugin-commands` skill: the complete Claude Code plugin CLI reference, so Claude runs the right `claude plugin` and `claude plugin marketplace` command, `/plugin` form, `/reload-plugins` or `--plugin-dir`/`--plugin-url` flag, with exact flags, defaults, aliases, messages, `--json` fields, exit codes, scopes and minimum versions, checked against Claude Code 2.1.319.
- Gotchas Claude keeps in view, such as `/plugin install` with a path installing nothing, `marketplace remove` uninstalling that marketplace's plugins, and reloads that change MCP tools needing `--force`.
- Before relying on a version-gated flag, Claude checks `--help` on your Claude Code version and the live docs, and tells you what differs.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/plugin-engineering--v0.2.2...HEAD
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.1.0
