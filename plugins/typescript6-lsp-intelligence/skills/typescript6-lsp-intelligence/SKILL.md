---
name: typescript6-lsp-intelligence
description: Navigates TypeScript and JavaScript by symbol through the TypeScript 6 language server, finds the tsconfig program that owns each file, and checks changes with the project's own tsc and configuration. Use when editing, refactoring or diagnosing TypeScript or JavaScript on TypeScript 6, fixing a compiler error such as TS2322, finding every usage of an export, or explaining why the editor and tsc disagree.
---

# TypeScript and JavaScript code intelligence (TypeScript 6)

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
| Is it safe to delete, rename or change a signature? | Both | LSP for code references, then Grep to confirm them and find the blind spots below |

When Grep finds several symbols with the same name, search for the name together with the module it is imported from, and read the import lines to tell them apart. Without `hover`, read the type's declaration (the `.d.ts` under `node_modules` for a library) or ask `tsc`.

Every operation takes `filePath` (absolute), `line` (1-based) and `character` (1-based, UTF-16 code units: an emoji before the symbol counts 2). Raw LSP data in logs is 0-based: add 1 to both.

If the `LSP` tool is not loaded, load it first with `ToolSearch` and the query `select:LSP`. Send `LSP` calls in their own message, never in parallel with another tool; several `LSP` calls may share a message. The session's first `LSP` call goes alone: its answer can come from a server still loading the project, so pass the warm-up check below before grouping calls.

## Trusting a result

When a result is empty, shows only the definition, or will justify an edit or deletion, check all five before believing it:

1. **Position**: `hover` at the same spot shows the intended symbol. "No hover information" means a wrong position or no server, never "no usages".
2. **Warm-up**: a session's first `LSP` calls can be partial or wrong, `goToDefinition` included (it may point at the import line). Repeat until two consecutive results match (at most three).
3. **Scope**: only the session's working directory is indexed. Outside it, results are stable and incomplete: say so and use Grep plus reading.
4. **Freshness**: changes made outside Edit and Write (Bash, git, codegen, formatters) may never reach the index. Grep or Read those files instead of trusting counts.
5. **Blind spots**: Grep the name for the uses LSP cannot see (next section).

Only after all five does "no references" mean none. Never delete code on LSP evidence alone.

## Blind spots, every language

LSP sees static code references only. Grep the name in: strings and reflection (dynamic imports, `eval`, dispatch by name); test mocks and stubs (`vi.mock`, `jest.mock` and other module paths in strings); entry points and config (package scripts, YAML, JSON, TOML, `.env`); framework injection (fixtures, decorators, registries, routes); shell scripts, CI, Makefiles, Dockerfiles; docs, comments, templates.

## Impact analysis (rename, signature change, deletion)

Copy this checklist into your working notes and tick each item:

- [ ] `findReferences` on the definition, with the five trust checks. The references start the must-change list; they are never all of it.
- [ ] The language-specific steps in "Gotchas" below.
- [ ] Before deleting or changing a signature, Grep the name to confirm the references and add every caller they missed. Textual mentions are listed as optional; any dynamic use or mock blocks a deletion.
- [ ] After the change, run the checks in [toolchain.md](references/toolchain.md) and fix what they report.

## Gotchas (verified on fixtures)

- **`findReferences` is never the full list.** It misses callers in `.svelte`, `.vue` and `.astro` files when run from a `.ts` file, mocks and other string references, and files changed from the shell. Confirm with Grep before deleting a symbol or changing a signature: compare the two counts and explain each difference. It returns only file, line and column; read each hit's line in Grep's output instead of opening every file.
- **Diagnostics arrive on a later turn after an edit, not immediately, and cover the edited file only.** No diagnostics straight after an edit does not mean the edit is clean; run the type check before reporting done. To check a whole program, or a caller in another file, run the compiler yourself on that program: `node_modules/.bin/tsc --noEmit -p <tsconfig.json>` from the project, or the global `tsc` when the project has none.
- **`prepareCallHierarchy` then `incomingCalls` works here**; module-level calls appear as the module.
- **Only loaded projects are searched.** Callers in another `tsconfig` project, or in a file no `tsconfig` includes, are missing and the result is stable across repeats, so the warm-up check passes. `hover` one file of each other project first, then re-run `findReferences`.
- **`.astro`, `.svelte`, `.vue` and `.mdx` are invisible** to the server, so `findReferences` run from a `.ts` file misses their callers. Grep them before any rename, signature change or deletion.
- **Aliases and barrels are followed** (`import { f as g } from "./index"` lists the calls to `g`), so the reference list covers the TypeScript-side callers; Grep still finds the rest.
- **`tsc` checks a whole program.** An error in a file you did not edit is breakage your change caused; fix it too. A file absent from `tsc --listFilesOnly -p <tsconfig>` has not been checked at all.
- **`allowJs` admits JavaScript; only `checkJs` or `// @ts-check` type-checks it.** A listed JS file with checking off has not passed type checking.

## Checks

Run them yourself after a change, before reporting it done:

- `tsc --noEmit -p <tsconfig.json>` for every program that includes a changed file or a caller, with the strict profile's options from [toolchain.md](references/toolchain.md) on the command line so a lax config does not hide errors in the changed files; `tsc --listFilesOnly -p <tsconfig.json>` to confirm membership; `tsc --showConfig -p <tsconfig.json>` to read the effective options (neither of the last two type-checks).
- The project's own formatter and linter (Biome, Prettier, ESLint), exactly as its `package.json` scripts run them.
- The project's tests for the changed behavior.

Read [toolchain.md](references/toolchain.md) when configuring TypeScript, raising strictness, telling TypeScript 6 and 7 apart, or wiring CI or an IDE. Read [fixtures.md](references/fixtures.md) when a check passes code it should flag.
