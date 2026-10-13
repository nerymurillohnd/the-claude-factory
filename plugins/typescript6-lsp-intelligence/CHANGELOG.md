# Changelog

All notable changes to **TypeScript 6 LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-13

### Added

- Language server: typescript-language-server 6.0.2 with TypeScript 6.0.3, both pinned in the plugin and installed by Claude Code when it caches it, for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files, with diagnostics after each edit. The server uses the project's own TypeScript when the project has one, else the pinned 6.0.3.
- Post-edit hook: after each Edit, Write or Bash call, the pinned `tsc --noEmit` checks the `tsconfig.json` program of every TypeScript or JavaScript file it changed; errors in the edited file first, breakage elsewhere in the program after, a file outside every program reported, compiler defaults when no `tsconfig.json` exists.
- `typescript6-lsp-intelligence` skill: LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, server gotchas verified on fixtures, and a `toolchain.md` reference for the pinned compiler, TypeScript 6 vs 7, configuration, a strict profile, CI and IDE.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/typescript6-lsp-intelligence--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.1.0
