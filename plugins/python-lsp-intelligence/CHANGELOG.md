# Changelog

All notable changes to **Python LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-13

### Added

- Post-edit hook: after each Edit, Write, NotebookEdit or Bash call, the Python files it changed go through `ruff check --fix`, `ruff format` and `basedpyright` with your own configuration (the plugin's strict defaults only when you have none). Findings reach Claude as an error to fix; a clean run confirms with one line.

### Changed

- `python-lsp-intelligence` skill rewritten: LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, basedpyright gotchas verified on fixtures, and a `toolchain.md` reference for configuration, strictness, environments, CI and IDE.

### Removed

- The control runner (`verify-fixtures.sh`) and `fixtures.json`; the fixtures now come with `fixtures.md`, which says how to run each one with the project's configuration.

## [0.1.0] - 2026-10-12

### Added

- Language server: connects Claude Code to basedpyright for `.py`, `.pyi` and `.pyw` files, with diagnostics after each edit and restart on crash.
- `python-lsp-intelligence` skill: navigates Python code with the language server; checks aliases, re-exports, entry points and dynamic consumers before a rename or deletion; fixes basedpyright and Ruff findings by validating untrusted data instead of casting, suppressing or weakening rules; and reports each check's status, the files covered and what stayed unverified.
- Optional controls: a bundled runner checks basedpyright and Ruff against known control files in a temporary folder, without running them or installing anything.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/python-lsp-intelligence--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.1.0
