# Changelog

All notable changes to **TypeScript 6 LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.3.0] - 2026-10-22

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

## [0.2.1] - 2026-10-20

### Changed

- Post-edit hook: every message Claude receives (type errors, files left unchecked because no compiler was found, a missing policy file) now ends with one line telling it to use `typescript6-lsp-intelligence:ts-lifecycle` and apply all its knowledge when working on TypeScript and JavaScript files. What the hook checks, when it runs and how it exits are unchanged.

## [0.2.0] - 2026-10-16

### Changed

- **Breaking:** the skill is now `ts-lifecycle` (`/typescript6-lsp-intelligence:ts-lifecycle`), replacing `typescript6-lsp-intelligence`. It researches a change from official docs and release notes before editing, works in `research` or `implementation` mode, navigates with the language server and confirms with Grep, and proves its checks with fixtures run through the same strict check the hook applies, using the bundled `scripts/run-fixtures.sh`, with a fixture for the error an incomplete rename leaves. It also says what to do without a language server, without network or without a project toolchain, and ends with a short report. It treats a `findReferences` result as never the full list (it misses `.svelte`, `.vue` and `.astro` callers from a `.ts` file, mocks, string references and files changed from the shell) and confirms it with Grep before a deletion or signature change, loads the `LSP` tool through `ToolSearch` when it is deferred, sends the session's first `LSP` call alone, and says diagnostics arrive on a later turn after an edit, so their absence right after it is not a clean result. In `research` mode it runs only commands and project scripts that write nothing in your project, takes diagnostics from `tsc` instead of the server, and runs the fixtures outside the project only when a conclusion needs them. It applies a change you asked for even when no check can run, and says it is not verified. It type-checks JavaScript only where `checkJs` or `// @ts-check` applies, asks before renaming a symbol other packages can import from your published `package.json` entry points, and follows your own rename scope when you say "everywhere". It retries a language-server call only on a transient failure, never repeats an invalid one, and applies every fallback row that matches when several tools are missing. `scripts/run-fixtures.sh` is the single source of the fixtures' strict options and expected codes.
- The plugin no longer ships TypeScript or typescript-language-server. The language server is your global `typescript-language-server`, and the hook checks with your project's `tsc`, or a global one. Install them with `npm install -g typescript-language-server typescript@6`; Node.js 22.22.2 or later is the language server's minimum. It starts one TypeScript server process instead of two (`useSyntaxServer: "never"`), which uses less memory.
- Post-edit hook rewritten in Bash (`hooks/tsc-check.sh`): it runs on macOS, Linux and Windows through Git Bash, needs no Node.js for its own logic, and finds Node.js 14.17 or later and `tsc` through nvm, fnm, Volta, asdf, mise, n, Homebrew, pnpm, Bun or a custom npm prefix, even when Claude Code starts without your shell profile. It writes nothing into your project: no compiled output and no `.tsbuildinfo` file, even for an emitting, `incremental` or `composite` config.
- Strictest policy: the edited files must pass every option of `hooks/tsconfig.strictest.json`, passed on the command line so it overrides your project's config, an explicit `false` included. The environment (path aliases, module resolution, `types`, `include`) stays your project's. Errors in other files count only when your own config finds them too, and errors in your config are always reported. A file outside every program is checked alone on top of the nearest config, with its `types`; a file with no config above it is checked with the strictest config. The policy includes `checkJs`, so an edited JavaScript file is type-checked in its program even when the project sets only `allowJs`, or neither.
- Requires Claude Code v2.1.295 or later: the hook sets `onFailure: "block"`, so a hook that cannot run, times out or prints invalid output reaches Claude instead of passing in silence.
- Hook hardening from an external audit, each case reproduced with a real `tsc` and covered by a new test suite: a compiler that crashes or exits non-zero without a TypeScript error is reported as not checked instead of passing; a project's `noCheck` no longer switches the check off (the policy passes `noCheck false`); the policy is read as JSON tokens, so its formatting cannot drop flags, and the hook stops when `noEmit` or `noCheck` is missing; event paths come from `tool_input`, with every JSON escape decoded (`\u` and surrogate pairs included); an event without `tool_name` fails instead of passing; a file checked alone on top of a `composite` or `outDir` config no longer fails on `rootDir`; each file uses the compiler of its own package, and the success line names the compiler version and counts strictest-only errors in other files instead of hiding them; on `PostToolUseFailure` the findings reach Claude through `additionalContext`, the only output that event takes; PowerShell calls are checked like Bash, staged files are found without a diff, and an incomplete or skipped `bashEditDiff` list adds the recent changes; an edited file that is gone or in a dependency folder is reported as not checked; a mise shim can no longer install a tool while the hook runs. Compiler output with Windows line endings no longer breaks the hook's JSON. File names with non-ASCII characters, quotes or tabs from `git` are no longer skipped.

### Added

- Without a usable compiler the hook no longer blocks: you get one message per session listing every place it searched and everything it skipped, such as a Node.js below the minimum, and Claude is told the file was not checked.

### Removed

- `package.json`, `package-lock.json` and `hooks/check.mjs`. Claude Code no longer runs `npm` when it caches the plugin.

## [0.1.0] - 2026-10-13

### Added

- Language server: typescript-language-server 6.0.2 with TypeScript 6.0.3, both pinned in the plugin and installed by Claude Code when it caches it, for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files, with diagnostics after each edit. The server uses the project's own TypeScript when the project has one, else the pinned 6.0.3.
- Post-edit hook: after each Edit, Write or Bash call, the pinned `tsc --noEmit` checks the `tsconfig.json` program of every TypeScript or JavaScript file it changed; errors in the edited file first, breakage elsewhere in the program after, a file outside every program reported, compiler defaults when no `tsconfig.json` exists.
- `typescript6-lsp-intelligence` skill: LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, server gotchas verified on fixtures, and a `toolchain.md` reference for the pinned compiler, TypeScript 6 vs 7, configuration, a strict profile, CI and IDE.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/typescript6-lsp-intelligence--v0.3.1...HEAD
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.3.0
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript6-lsp-intelligence--v0.1.0
