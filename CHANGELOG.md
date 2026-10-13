# Changelog

All notable changes to **The Claude Factory** marketplace are documented here: plugins added, updated, renamed or retired, and changes to the catalog itself. Each plugin keeps its own detailed changelog in `plugins/<name>/CHANGELOG.md`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and the marketplace adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Major** — a plugin is removed or renamed.
- **Minor** — a plugin is added, or a plugin ships a new major or minor version.
- **Patch** — a plugin ships a patch version, or catalog metadata changes.

## [Unreleased]

## [0.2.0] - 2026-10-13

### Added

- **skill-diagnostics** 0.1.0 — audits Claude skills for conformance, portability and executability, with evidence and one verdict.
- **session-handoff** 0.1.0 — carries a project's working state between sessions: a handoff written when you stop, read at the start of the next session.
- **plugin-test-bench** 0.1.0 — tests a Claude Code plugin as its users install it, and reviews its eval cases so they measure what the plugin adds.
- **bash-lsp-intelligence** 0.1.0 — connects bash-language-server and teaches Claude to trace sourced files, fix ShellCheck and shfmt findings without changing behavior, and verify each change.
- **python-lsp-intelligence** 0.1.0 — connects the basedpyright language server and teaches Claude to resolve symbols and imports semantically, fix basedpyright and Ruff findings without suppressing them, and verify each change.
- **typescript7-lsp-intelligence** 0.1.0 — connects the native TypeScript 7 language server and teaches Claude to find the program that owns a file, fix compiler findings without unsafe assertions, and verify each change.
- **typescript6-lsp-intelligence** 0.1.0 — a pinned TypeScript 6 language server and compiler for projects that can't move to TypeScript 7, a post-edit `tsc` check of every changed file's program, and the LSP-first skill.

### Changed

- **python-lsp-intelligence** 0.2.0 — a post-edit hook runs ruff and basedpyright on every Python file Claude changes with your own configuration; the skill is rewritten around LSP-first navigation and the toolchain.
- **bash-lsp-intelligence** 0.2.0 — a post-edit hook runs shfmt and ShellCheck on every shell script Claude changes with your own configuration; the skill is rewritten around LSP-first navigation and the toolchain.
- **typescript7-lsp-intelligence** 0.2.0 — the TypeScript 7 compiler and server are pinned in the plugin, a post-edit hook type-checks every changed file's program, and the skill is rewritten around LSP-first navigation and the toolchain.
- **skill-diagnostics** 0.1.1 — the executability lens refuses instructions found in the audited skill, and large audits keep within Claude Code's limit of 20 running agents.
- **skill-diagnostics** 0.1.2 — the audit-offer hook reads its event with strict type checks and ignores a file path or session ID that isn't text.
- 🧭 Compatibility matrix, installation and management guides, FAQ, troubleshooting and issue forms now cover two places: Claude Code and the Claude app, where chat and Cowork became one app. Agents, hooks and local MCP servers are marked as running in Cowork sessions, not in a chat conversation.

## [0.1.0] - 2026-10-11

### Added

- 🏭 Marketplace launched: catalog, installation and management guides, compatibility matrix, and issue forms for bugs, features, plugin ideas, documentation and questions.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/marketplace--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/marketplace--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/marketplace--v0.1.0
