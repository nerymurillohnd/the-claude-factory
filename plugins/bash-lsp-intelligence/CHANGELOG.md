# Changelog

All notable changes to **Bash LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-12

### Added

- Language server: connects Claude Code to bash-language-server for `.sh`, `.inc`, `.bash` and `.command` files, with diagnostics after each edit and restart on crash.
- `bash-lsp-intelligence` skill: navigates shell code with the language server; traces direct and transitive `source` chains before trusting same-named functions; respects the script's real dialect; fixes ShellCheck and shfmt findings without changing quoting, globbing or exit-status behavior; and reports each check's status, the scripts covered and what stayed unverified.
- Optional controls: a bundled runner checks ShellCheck and shfmt against known control files in a temporary folder, without running them or installing anything.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/bash-lsp-intelligence--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/bash-lsp-intelligence--v0.1.0
