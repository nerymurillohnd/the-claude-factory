# Changelog

All notable changes to **TypeScript 7 LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-10-16

### Changed

- Skill: the check command passes the strict profile's options on the command line, listed in full in `toolchain.md`, so a lax `tsconfig.json` no longer hides errors that the strictest policy reports.
- The plugin no longer ships TypeScript. The language server is the `tsc --lsp --stdio` of your global TypeScript 7, and the hook checks with your project's TypeScript 7, or a global one. Install it with `npm install -g typescript@7`.
- Post-edit hook rewritten in Bash (`hooks/tsc-check.sh`): it runs the native compiler binary of your `typescript` package directly, with no Node.js, on macOS, Linux and Windows through Git Bash. It finds `tsc` through nvm, fnm, Volta, asdf, mise, n, Homebrew, pnpm, Bun or a custom npm prefix, even when Claude Code starts without your shell profile.
- Strictest policy: the edited files must pass every option of `hooks/tsconfig.strictest.json`, passed on the command line so it overrides your project's config, an explicit `false` included. The environment (path aliases, module resolution, `types`, `include`) stays your project's. Errors in other files count only when your own config finds them too, and errors in your config are always reported. A file outside every program is checked alone on top of the nearest config, with its `types`; a file with no config above it is checked with the strictest config. The policy includes `checkJs`, so an edited JavaScript file is type-checked in its program even when the project sets only `allowJs`, or neither.
- Requires Claude Code v2.1.295 or later: the hook sets `onFailure: "block"`, so a hook that cannot run, times out or prints invalid output reaches Claude instead of passing in silence.

### Added

- Without a usable compiler the hook no longer blocks: you get one message per session listing every place it searched and everything it skipped, such as a Node.js below the minimum, and Claude is told the file was not checked.

### Removed

- `package.json`, `package-lock.json` and `hooks/check.mjs`. Claude Code no longer runs `npm` when it caches the plugin.

## [0.2.0] - 2026-10-13

### Added

- The TypeScript 7.0.2 compiler and language server are pinned in the plugin and installed by Claude Code when it caches it; nothing to install, and your project's `tsc` is never used or changed.
- Post-edit hook: after each Edit, Write or Bash call, the pinned `tsc --noEmit` checks the `tsconfig.json` program of every TypeScript or JavaScript file it changed; errors in the edited file first, breakage elsewhere in the program after, a file outside every program reported, compiler defaults when no `tsconfig.json` exists. The native server pushes no diagnostics after edits, so this is where type errors come from.

### Changed

- The language server starts from the plugin's own TypeScript (`node …/node_modules/typescript/bin/tsc --lsp --stdio`) instead of a global `tsc`.
- `typescript7-lsp-intelligence` skill rewritten: it opens by saying the native server pushes no diagnostics and how to run `tsc --noEmit` on a program or a caller when needed, then LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, server gotchas verified on fixtures, and a `toolchain.md` reference for the pinned compiler, TypeScript 6 vs 7, configuration, a strict profile, CI and IDE.

### Removed

- The control runner (`verify-fixtures.sh`) and `fixtures.json`; the fixtures now come with `fixtures.md`, which says how to run each one with the project's configuration.

## [0.1.0] - 2026-10-12

### Added

- Language server: connects Claude Code to the native TypeScript 7 server (`tsc --lsp --stdio`) for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files, with diagnostics after each edit and restart on crash.
- `typescript7-lsp-intelligence` skill: navigates TypeScript and JavaScript with the language server; checks program membership and effective configuration before trusting a diagnostic; tells TypeScript 6 `tsserver` tooling apart from the TypeScript 7 native server; fixes compiler findings by narrowing `unknown` instead of using assertions, `any` or suppressions; and reports each check's status, the programs covered and what stayed unverified.
- Optional controls: a bundled runner compiles known control files with the compiler you choose, in a temporary folder, without running them or installing anything.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/typescript7-lsp-intelligence--v0.3.0...HEAD
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.3.0
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.1.0
