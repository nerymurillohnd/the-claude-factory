---
name: typescript7-lsp-intelligence
description: Navigates TypeScript and JavaScript by symbol through the native TypeScript 7 language server, finds the tsconfig program that owns each file, and checks changes with the pinned tsc using the project's own configuration. Use when editing, refactoring or diagnosing TypeScript or JavaScript on TypeScript 7, fixing a compiler error such as TS2322, finding every usage of an export, or explaining why the editor and tsc disagree.
---

# TypeScript and JavaScript code intelligence (TypeScript 7)

The TypeScript 7 server answers navigation requests but pushes no diagnostics after edits, so no `Found N new diagnostic issues` line ever appears for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` files: silence means unchecked, not clean. To check a whole program, or a caller in another file, run the plugin's compiler yourself: `node "${CLAUDE_PLUGIN_ROOT}/node_modules/typescript/bin/tsc" --noEmit -p <tsconfig.json>`.

Work with the language server first and the toolchain second. Nothing here mentions how the project is checked automatically; run every check yourself when the task calls for it.

## LSP and Grep are complementary

LSP owns questions about code structure; Grep owns questions about text. Route each question to its owner, and use both before changing or deleting code.

| Question | Owner | Operation |
| :-- | :-- | :-- |
| Where is X defined? | LSP | `goToDefinition` |
| Who uses or imports X? | LSP | `findReferences` |
| Type or signature of X? | LSP | `hover` |
| What does this file contain? | LSP | `documentSymbol`, before reading the whole file |
| Where is X, file unknown? | LSP | `workspaceSymbol`, always with `query` |
| Who calls X, what does X call? | LSP | `prepareCallHierarchy`, then `incomingCalls` / `outgoingCalls` |
| Implementations of an interface | LSP | `goToImplementation` |
| Where does a word appear as text (docs, comments, strings, config, scripts)? | Grep | — |
| Is it safe to delete or rename? | Both | LSP for code references, Grep for the blind spots below |

Every operation takes `filePath` (absolute), `line` (1-based) and `character` (1-based, UTF-16 code units: an emoji before the symbol counts 2). Raw LSP data in logs is 0-based: add 1 to both.

## Trusting a result

When a result is empty, shows only the definition, or will justify an edit or deletion, check all five before believing it:

1. **Position**: `hover` at the same spot shows the intended symbol. "No hover information" means a wrong position or no server, never "no usages".
2. **Warm-up**: a session's first workspace-wide query can be partial. Repeat until two consecutive results match (at most three).
3. **Scope**: only the session's working directory is indexed. Outside it, results are stable and incomplete: say so and use Grep plus reading.
4. **Freshness**: changes made outside Edit and Write (Bash, git, codegen, formatters) may never reach the index. Grep or Read those files instead of trusting counts.
5. **Blind spots**: Grep the name for the uses LSP cannot see (next section).

Only after all five does "no references" mean none. Never delete code on LSP evidence alone.

## Blind spots, every language

LSP sees static code references only. Grep the name in: strings and reflection (dynamic imports, `eval`, dispatch by name); entry points and config (package scripts, YAML, JSON, TOML, `.env`); framework injection (fixtures, decorators, registries, routes); shell scripts, CI, Makefiles, Dockerfiles; docs, comments, templates.

## Impact analysis (rename, signature change, deletion)

Copy this checklist into your working notes and tick each item:

- [ ] `findReferences` on the definition, with the five trust checks. The references are the must-change list.
- [ ] The language-specific steps in "Gotchas" below.
- [ ] Grep the blind spots. Textual mentions are listed as optional; any dynamic use blocks a deletion.
- [ ] After the change, run the checks in [toolchain.md](references/toolchain.md) and fix what they report.

## Gotchas (verified on fixtures)

- **The TypeScript 7 server reports no diagnostics after edits** (it serves pull diagnostics only). When you need the compiler's view of a change, run the command at the top of this skill on each program the change touches, not only on the edited file's.
- **Only loaded projects are searched.** Callers in another `tsconfig` project, or in a file no `tsconfig` includes, are missing and the result is stable across repeats, so the warm-up check passes. `hover` one file of each other project first, then re-run `findReferences`.
- **`.astro`, `.svelte`, `.vue` and `.mdx` are invisible** to the server. Grep them before any rename or deletion.
- **Aliases and barrels are followed** (`import { f as g } from "./index"` lists the calls to `g`), so the reference list is the TypeScript-side must-change set.
- **`tsc` checks a whole program.** An error in a file you did not edit is breakage your change caused; fix it too. A file absent from `tsc --listFilesOnly -p <tsconfig>` has not been checked at all.
- **`allowJs` admits JavaScript; only `checkJs` or `// @ts-check` type-checks it.** A listed JS file with checking off has not passed type checking.

## Checks

Run them yourself after a change:

- `tsc --noEmit -p <tsconfig.json>` for every program that includes a changed file or a caller; `tsc --listFilesOnly -p <tsconfig.json>` to confirm membership; `tsc --showConfig -p <tsconfig.json>` to read the effective options (neither of the last two type-checks).
- The project's own formatter and linter (Biome, Prettier, ESLint), exactly as its `package.json` scripts run them.
- The project's tests for the changed behavior.

Read [toolchain.md](references/toolchain.md) when configuring TypeScript, raising strictness, telling TypeScript 6 and 7 apart, or wiring CI or an IDE. Read [fixtures.md](references/fixtures.md) when a check passes code it should flag.
