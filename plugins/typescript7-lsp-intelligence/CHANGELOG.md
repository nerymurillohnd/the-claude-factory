# Changelog

All notable changes to **TypeScript 7 LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2026-11-26

### Changed

- Failures the project's checks already had before a change are no longer only listed under Gaps: Claude gives each one its cause and fix, fixes it in its own change when you or your project's instructions ask for every failure fixed, and offers the fix otherwise.

## [0.7.0] - 2026-11-23

### Changed

- **Breaking:** the plugin now needs Node.js 24 or later to start the TypeScript 7 language server, up from Node.js 16.20.0. Node.js 24 is the oldest Node.js this marketplace supports for code that runs on your machine. If `node --version` shows an older version, update Node.js before you update the plugin. The hook still runs the native compiler without Node.js, so an older Node.js on your `PATH` doesn't change its result or appear in its pass messages. When it has to start a `tsc` through Node.js, it skips a Node.js older than 24, the support floor, and its notice says so and lists each Node.js it skipped. When a TypeScript 7 package lacks its native compiler, the notice names the missing `@typescript/typescript-<os>-<arch>` package instead of blaming Node.js.

### Fixed

- When `tsc` crashed or stopped with a long output and no TypeScript error, the post-edit check could end with "the hook failed" instead of telling Claude that the files were not checked and showing the first lines of that output. It happened whenever the output was larger than about 64 KB, such as a long crash trace. Claude now always gets the notice and the first 20 lines.

## [0.6.0] - 2026-11-20

### Added

- With each prompt you send, the plugin now tells Claude to call the `typescript7-lsp-intelligence:ts-7-writing-and-navigation` skill with the Skill tool and apply it end to end, including its LSP and Grep steps, before it creates, writes or edits a TypeScript or JavaScript file, with any tool or command. A new `UserPromptSubmit` hook adds this short instruction to Claude's context; it sends nothing and writes nothing.

### Changed

- **Breaking:** the skill is now `typescript7-lsp-intelligence:ts-7-writing-and-navigation`, instead of `typescript7-lsp-intelligence:ts-lifecycle`, a name that says what it does and which TypeScript version it is for. If you type the skill's command, use `/typescript7-lsp-intelligence:ts-7-writing-and-navigation` from now on; Claude finds it on its own as before.

### Removed

- **Breaking:** the first TypeScript or JavaScript edit of a session no longer waits for the skill. The `PreToolUse` hook that denied the first Edit or Write call until Claude loaded `typescript7-lsp-intelligence:ts-7-writing-and-navigation` is gone, together with the entries that only tracked it (`PostToolUse` on the Skill tool, `UserPromptExpansion` and `PostCompact`). Claude now gets the instructions above with each prompt instead of a denied edit. Nothing for you to do: the marker files it left in the plugin's data folder, under `skill-loads/`, are no longer read, and you can delete them.

## [0.5.0] - 2026-11-19

### Added

- **Breaking:** the first TypeScript or JavaScript edit of a session now waits until Claude has loaded the `typescript7-lsp-intelligence:ts-lifecycle` skill. A new `PreToolUse` hook denies that one Edit or Write call, once, with a message that tells Claude to load the skill and retry; every later edit goes through, so a session that can't load skills is never locked out. A subagent counts on its own, and after compaction the next edit asks for the skill again. The hook keeps its markers in the plugin's data folder and does nothing where Claude Code gives it none.
- The skill now opens with a step that runs before the first TypeScript or JavaScript file of the task: it checks that the language server is installed and that the `LSP` tool is available, starts the server with a first call, and switches to Grep and reading, reported as such, when either is missing, as in cloud sessions.

### Changed

- The `ts-lifecycle` description now opens with the work it serves and the file types it covers, even for a small change, and says it is for projects on the native TypeScript 7 compiler and not for TypeScript 6, so Claude loads it for everyday edits and tells it apart from the TypeScript 6 plugin's skill of the same name.
- The skill now trusts an `LSP` result only after three consecutive identical answers to the same call, at most six calls, instead of two out of three, and records a result as unstable when no three match.

### Fixed

- The `ts-lifecycle` skill and its references now carry the corrections the TypeScript 6 plugin already had. Among them, `allowJs` alone no longer reads as type-checking JavaScript (only `checkJs` or `// @ts-check` does), research mode runs a project script only after confirming it writes nothing, and the public API, rename scope and tool-boundary rules are spelled out.

## [0.4.6] - 2026-11-14

### Fixed

- After a Bash command in a folder that isn't a Git repository, the hook no longer type-checks the files of a repository you cloned, a branch you checked out or a pull, which could run until the hook's time limit and stop Claude with an error. Inside a Git repository below your project, it checks only the files Git lists as modified, untracked or staged.
- When a Bash command leaves more than 20 TypeScript or JavaScript files outside any Git repository, such as an extracted archive, the hook checks none of them and tells Claude.
- After a Bash command, the hook no longer type-checks the files that command wrote into a place Git ignores, such as a build folder.
- Where Claude Code gives the plugin no data folder, the hook no longer keeps its once-per-session "no compiler" marker in your system's temporary directory, which other users of the machine can write to; it creates nothing there, and the message repeats instead.

## [0.4.5] - 2026-11-06

### Fixed

- In a project that installs TypeScript 7 under the `@typescript/native` alias, as the TypeScript 7 announcement recommends next to TypeScript 6, the hook now runs the native compiler directly instead of starting it through Node.js on every check (#88).
- When a Bash command changes more files than the 200 that Claude Code lists, the hook now also checks the ones past that limit instead of skipping them without a word (#88).

### Changed

- The README explains the TypeScript 6 and 7 side-by-side setup: this plugin fits it, the language server still needs a global TypeScript 7, and only one global `tsc` can be on your `PATH` (#88).

## [0.4.4] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.4.3] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.4.2] - 2026-11-02

### Changed

- The `ts-lifecycle` skill no longer pre-approves its fixture script: Claude Code asks you before it runs `run-fixtures.sh`, and **Yes, and don't ask again** lets it run without asking.
- The README now says what the plugin runs and sends, gives TypeScript 7's own defaults, and says the native server pushes diagnostics only for `tsconfig.json`, never for your source files.

### Fixed

- The notice shown when no compiler is found links to the README's Prerequisites section instead of the top of the page.
- A config option that TypeScript 7 removed, such as `baseUrl` or `target: es5`, is now reported as a removed option instead of as a generic config error.

## [0.4.1] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/typescript7-lsp-intelligence--v0.8.0...HEAD
[0.8.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.8.0
[0.7.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.7.0
[0.6.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.6.0
[0.5.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.5.0
[0.4.6]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.6
[0.4.5]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.5
[0.4.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.4
[0.4.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.3
[0.4.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.2
[0.4.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.1
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.4.0
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.3.0
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/typescript7-lsp-intelligence--v0.1.0
