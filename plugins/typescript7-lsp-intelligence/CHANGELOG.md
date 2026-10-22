# Changelog

All notable changes to **TypeScript 7 LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-10-22

### Changed

- **Breaking:** Post-edit hook: the strictest policy is now a set of defaults, and your config wins. Each strict option goes to `tsc` only when your `tsconfig.json` or `jsconfig.json`, or a config it extends, leaves it unset; an option you set yourself, `false` included, is yours. Setting `strict` keeps the whole strict family yours, and an option `tsc` would reject next to your choice (`exactOptionalPropertyTypes` or `strictPropertyInitialization` with `strictNullChecks` off, `checkJs` with `allowJs` off, `allowJs` with `isolatedDeclarations`) is left out instead of turning into a config error. Before, every option was forced on the command line and overrode your explicit `false`. `noEmit` and `noCheck false` still always apply. The skill's `run-fixtures.sh` applies your config the same way, so a lax config shows as a fixture `MISMATCH`.
- Post-edit hook: the strictest policy now lives in the hook itself, and `hooks/tsconfig.strictest.json` is gone. The policy holds only checks that apply to any project, and nothing of your environment: a file with no `tsconfig.json` or `jsconfig.json` above it is now checked with your compiler's own defaults for `target` and `module` (with TypeScript 6, `es2025` and `esnext`; with TypeScript 5, ES5 and CommonJS), instead of a fixed `es2022` and `nodenext` that made such a file CommonJS and rejected top-level `await`.
- Post-edit hook: each strict option goes only to a `tsc` that knows it. With an older project compiler, such as TypeScript 5.4, `strictBuiltinIteratorReturn` (TypeScript 5.6) is left out instead of every check failing on an unknown option, and Claude is told which options were not applied. `run-fixtures.sh` names any option it leaves out the same way.
- Post-edit hook: a config that uses an option deprecated in TypeScript 6, such as `baseUrl`, is reported as such, and the edit is still blocked: the option stops working in TypeScript 7. An `ignoreDeprecations` you set yourself is respected.
- Post-edit hook: the message Claude gets for type errors states the facts (`tsc found TypeScript errors after this edit…`) instead of giving orders, as the hooks documentation advises.

### Fixed

- Post-edit hook: a file that only a `tsconfig.<name>.json` or `jsconfig.<name>.json` lists, beside the nearest `tsconfig.json` and not referenced by it (such as the `tsconfig.node.json` or `tsconfig.app.json` many templates create), is now checked with that config's program. Before, it was checked alone and reported as not part of any program. The hook tries the `tsconfig.<name>.json` files and then the `jsconfig.<name>.json` files after the nearest config's references, in name order, and skips one `tsc` cannot read and one the nearest config extends (a `tsconfig.base.json` is a base, not a program), so a program you reference still wins.
- Post-edit hook: files a Bash or PowerShell command changes are now looked for in the folder Claude works in, the `cwd` of the event, instead of the folder the session started in. In a worktree, or after a `cd`, they were missed and left unchecked.
- Post-edit hook: a TypeScript development build whose version has a patch number starting with 0, such as `5.6.0-dev.20240819`, no longer has options wrongly left out as unknown.

## [0.3.1] - 2026-10-20

### Changed

- Post-edit hook: every message Claude receives (type errors, files left unchecked because no compiler was found, a missing policy file) now ends with one line telling it to use `typescript7-lsp-intelligence:ts-lifecycle` and apply all its knowledge when working on TypeScript and JavaScript files. What the hook checks, when it runs and how it exits are unchanged.

## [0.3.0] - 2026-10-16

### Changed

- **Breaking:** the skill is now `ts-lifecycle` (`/typescript7-lsp-intelligence:ts-lifecycle`), the same skill as the TypeScript 6 plugin, replacing `typescript7-lsp-intelligence`. It says the TypeScript 7 server pushes no diagnostics, so silence after an edit means unchecked; researches a change from official docs and release notes before editing; works in `research` or `implementation` mode; navigates with the language server and confirms `findReferences` with Grep before a deletion or signature change; loads the `LSP` tool through `ToolSearch` when it is deferred and sends the session's first `LSP` call alone; says what to do without a language server, network or project toolchain; proves its checks with fixtures through the hook's strict check, using the bundled `scripts/run-fixtures.sh`, with a fixture for the error an incomplete rename leaves; and ends with a short report.
- The plugin no longer ships TypeScript. The language server is the `tsc --lsp --stdio` of your global TypeScript 7, and the hook checks with your project's TypeScript 7, or a global one. Install it with `npm install -g typescript@7`.
- Post-edit hook rewritten in Bash (`hooks/tsc-check.sh`): it runs the native compiler binary of your `typescript` package directly, with no Node.js, on macOS, Linux and Windows through Git Bash. It finds `tsc` through nvm, fnm, Volta, asdf, mise, n, Homebrew, pnpm, Bun or a custom npm prefix, even when Claude Code starts without your shell profile. It writes nothing into your project: no compiled output and no `.tsbuildinfo` file, even for an emitting, `incremental` or `composite` config.
- Strictest policy: the edited files must pass every option of `hooks/tsconfig.strictest.json`, passed on the command line so it overrides your project's config, an explicit `false` included. The environment (path aliases, module resolution, `types`, `include`) stays your project's. Errors in other files count only when your own config finds them too, and errors in your config are always reported. A file outside every program is checked alone on top of the nearest config, with its `types`; a file with no config above it is checked with the strictest config. The policy includes `checkJs`, so an edited JavaScript file is type-checked in its program even when the project sets only `allowJs`, or neither.
- Requires Claude Code v2.1.295 or later: the hook sets `onFailure: "block"`, so a hook that cannot run, times out or prints invalid output reaches Claude instead of passing in silence.
- Hook hardening from an external audit, each case reproduced with a real `tsc` and covered by a new test suite: a compiler that crashes or exits non-zero without a TypeScript error is reported as not checked instead of passing; a project's `noCheck` no longer switches the check off (the policy passes `noCheck false`); the policy is read as JSON tokens, so its formatting cannot drop flags, and the hook stops when `noEmit` or `noCheck` is missing; event paths come from `tool_input`, with every JSON escape decoded (`\u` and surrogate pairs included); an event without `tool_name` fails instead of passing; a file checked alone on top of a `composite` or `outDir` config no longer fails on `rootDir`; each file uses the compiler of its own package, and the success line names the compiler version and counts strictest-only errors in other files instead of hiding them; on `PostToolUseFailure` the findings reach Claude through `additionalContext`, the only output that event takes; PowerShell calls are checked like Bash, staged files are found without a diff, and an incomplete or skipped `bashEditDiff` list adds the recent changes; an edited file that is gone or in a dependency folder is reported as not checked; a mise shim can no longer install a tool while the hook runs. Compiler output with Windows line endings no longer breaks the hook's JSON. File names with non-ASCII characters, quotes or tabs from `git` are no longer skipped.

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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/typescript7-lsp-intelligence--v0.4.0...HEAD
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.0
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.3.0
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.1.0
