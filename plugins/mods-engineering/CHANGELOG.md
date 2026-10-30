# Changelog

All notable changes to **Mods Engineering** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-10-30

### Changed

- The guidance on missing declarations, what a check proves and how to declare a mod's minimum version is now one instruction per line.

## [0.1.2] - 2026-10-30

### Changed

- The guidance now says which sessions write a mod's type declarations (an interactive `--plugin-dir` session, or a mod Claude writes), and that `-p`, SDK sessions, `claude plugin test` and `claude plugin validate` never do.
- A type check, validate and test now count as proof only for the Claude Code build they ran on; your README's minimum version is what speaks to other users.
- Distribution advice now has you declare the minimum Claude Code version in the README, recorded apart from the version you tested on, and treat everything committed under the plugin as shipped: keep `.claude-plugin/types/` and the generated root `tsconfig.json` out of git.
- The README states the Desktop floor (v2.1.286) beside the terminal's (v2.1.287) and the VS Code drawing minimums.

## [0.1.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.1.0] - 2026-10-22

### Added

- `cc-mods-guidance` skill: an engineering workflow for Claude Code mods that routes each question to the right official page, checks every interface against the declarations your build writes, and covers design, implementation within the engine's static-analysis rules, validation, tests, debugging, organization policy and sharing.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/mods-engineering--v0.1.3...HEAD
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/mods-engineering--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/mods-engineering--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/mods-engineering--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/mods-engineering--v0.1.0
