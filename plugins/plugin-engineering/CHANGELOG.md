# Changelog

All notable changes to **Plugin Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-07

### Added

- `plugin-commands` skill: the complete Claude Code plugin CLI reference, so Claude runs the right `claude plugin` and `claude plugin marketplace` command, `/plugin` form, `/reload-plugins` or `--plugin-dir`/`--plugin-url` flag, with exact flags, defaults, aliases, messages, `--json` fields, exit codes, scopes and minimum versions, checked against Claude Code 2.1.319.
- Gotchas Claude keeps in view, such as `/plugin install` with a path installing nothing, `marketplace remove` uninstalling that marketplace's plugins, and reloads that change MCP tools needing `--force`.
- Before relying on a version-gated flag, Claude checks `--help` on your Claude Code version and the live docs, and tells you what differs.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/plugin-engineering--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/plugin-engineering--v0.1.0
