# Changelog

All notable changes to **Python LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-12

### Added

- Language server: connects Claude Code to basedpyright for `.py`, `.pyi` and `.pyw` files, with diagnostics after each edit and restart on crash.
- `python-lsp-intelligence` skill: navigates Python code with the language server; checks aliases, re-exports, entry points and dynamic consumers before a rename or deletion; fixes basedpyright and Ruff findings by validating untrusted data instead of casting, suppressing or weakening rules; and reports each check's status, the files covered and what stayed unverified.
- Optional controls: a bundled runner checks basedpyright and Ruff against known control files in a temporary folder, without running them or installing anything.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/python-lsp-intelligence--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.1.0
