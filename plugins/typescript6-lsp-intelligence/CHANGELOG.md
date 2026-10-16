# Changelog

All notable changes to **TypeScript 6 LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-16

### Changed

- **Breaking:** the skill is now `ts-lifecycle` (`/typescript6-lsp-intelligence:ts-lifecycle`), replacing `typescript6-lsp-intelligence`. It researches a change from official docs and release notes before editing, works in `research` or `implementation` mode, navigates with the language server and confirms with Grep, and proves its checks with fixtures run through the same strict check the hook applies. It treats a `findReferences` result as never the full list (it misses `.svelte`, `.vue` and `.astro` callers from a `.ts` file, mocks, string references and files changed from the shell) and confirms it with Grep before a deletion or signature change, loads the `LSP` tool through `ToolSearch` when it is deferred, sends the session's first `LSP` call alone, and says diagnostics arrive on a later turn after an edit, so their absence right after it is not a clean result.
- The plugin no longer ships TypeScript or typescript-language-server. The language server is your global `typescript-language-server`, and the hook checks with your project's `tsc`, or a global one. Install them with `npm install -g typescript-language-server typescript@6`; Node.js 22.22.2 or later is the language server's minimum. It starts one TypeScript server process instead of two (`useSyntaxServer: "never"`), which uses less memory.
- Post-edit hook rewritten in Bash (`hooks/tsc-check.sh`): it runs on macOS, Linux and Windows through Git Bash, needs no Node.js for its own logic, and finds Node.js 14.17 or later and `tsc` through nvm, fnm, Volta, asdf, mise, n, Homebrew, pnpm, Bun or a custom npm prefix, even when Claude Code starts without your shell profile. It writes nothing into your project: no compiled output and no `.tsbuildinfo` file, even for an emitting, `incremental` or `composite` config.
- Strictest policy: the edited files must pass every option of `hooks/tsconfig.strictest.json`, passed on the command line so it overrides your project's config, an explicit `false` included. The environment (path aliases, module resolution, `types`, `include`) stays your project's. Errors in other files count only when your own config finds them too, and errors in your config are always reported. A file outside every program is checked alone on top of the nearest config, with its `types`; a file with no config above it is checked with the strictest config. The policy includes `checkJs`, so an edited JavaScript file is type-checked in its program even when the project sets only `allowJs`, or neither.
- Requires Claude Code v2.1.295 or later: the hook sets `onFailure: "block"`, so a hook that cannot run, times out or prints invalid output reaches Claude instead of passing in silence.

### Added

- Without a usable compiler the hook no longer blocks: you get one message per session listing every place it searched and everything it skipped, such as a Node.js below the minimum, and Claude is told the file was not checked.

### Removed

- `package.json`, `package-lock.json` and `hooks/check.mjs`. Claude Code no longer runs `npm` when it caches the plugin.

## [0.1.0] - 2026-10-13

### Added

- Language server: typescript-language-server 6.0.2 with TypeScript 6.0.3, both pinned in the plugin and installed by Claude Code when it caches it, for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files, with diagnostics after each edit. The server uses the project's own TypeScript when the project has one, else the pinned 6.0.3.
- Post-edit hook: after each Edit, Write or Bash call, the pinned `tsc --noEmit` checks the `tsconfig.json` program of every TypeScript or JavaScript file it changed; errors in the edited file first, breakage elsewhere in the program after, a file outside every program reported, compiler defaults when no `tsconfig.json` exists.
- `typescript6-lsp-intelligence` skill: LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, server gotchas verified on fixtures, and a `toolchain.md` reference for the pinned compiler, TypeScript 6 vs 7, configuration, a strict profile, CI and IDE.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/typescript6-lsp-intelligence--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.1.0
