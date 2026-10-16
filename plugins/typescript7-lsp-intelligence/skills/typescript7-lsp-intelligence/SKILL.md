---
name: typescript7-lsp-intelligence
description: Navigates TypeScript and JavaScript by symbol through the native TypeScript 7 language server (tsc --lsp), finds the tsconfig program that owns each file, and checks changes with the project's own tsc under a strict profile. Use when editing, refactoring or diagnosing TypeScript or JavaScript on TypeScript 7, fixing a compiler error such as TS2322, finding every usage of an export, configuring tsconfig or strictness or CI, or explaining why the editor and tsc disagree.
---

# TypeScript and JavaScript code intelligence (TypeScript 7)

The TypeScript 7 server answers navigation requests but pushes no diagnostics after edits, so no `Found N new diagnostic issues` line ever appears for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` files: silence means unchecked, not clean. Run the strict check under "Checks" yourself after every change to such a file.

Work with the language server first and the toolchain second. Without an LSP tool (Chat and Cowork load this skill but ignore language servers, and the server may be off in Claude Code), answer structure questions with Grep and Read, say the result is textual only, and run the strict check when a shell is available.

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
2. **Warm-up**: a session's first workspace-wide query can be partial. Repeat until two consecutive results match (at most three runs). If three runs never match, treat the result as incomplete and use Grep.
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
- [ ] Grep the blind spots. Textual mentions are listed as optional; any dynamic use blocks a deletion and must be updated by hand in a rename or signature change.
- [ ] Before the change, take the baseline of the strict check (see "Checks").
- [ ] After the change, run the strict check and the other checks, fix what they report, and run them again until the strict check reports 0 errors in the edited files and 0 new errors elsewhere.

## Gotchas (verified on fixtures)

- **Run the strict check on each program the change touches**, not only on the edited file's.
- **Only loaded projects are searched.** Callers in another `tsconfig` project, or in a file no `tsconfig` includes, are missing and the result is stable across repeats, so the warm-up check passes. List the other projects with Glob `**/tsconfig.json` (skip `node_modules`), `hover` one file of each, then re-run `findReferences`. For files outside every program (`tsc --listFilesOnly` does not list them), Grep the name.
- **`.astro`, `.svelte`, `.vue` and `.mdx` are invisible** to the server. Grep them before any rename or deletion.
- **Aliases and barrels are followed** (`import { f as g } from "./index"` lists the calls to `g`), so the reference list is the TypeScript-side must-change set.
- **`tsc` checks a whole program.** An error in a file you did not edit is yours when the baseline did not have it; see "Checks". A file absent from `tsc --listFilesOnly -p <tsconfig>` has not been checked at all.
- **`allowJs` admits JavaScript; only `checkJs` or `// @ts-check` type-checks it.** A listed JS file with checking off has not passed type checking.

## Checks

After every change to a TypeScript or JavaScript file, and before you report it clean, run these yourself. They are not optional.

**The compiler** is the project's `node_modules/.bin/tsc`, found walking up from the program's folder; use a global `tsc` only when the project has none. Never `npx tsc`: without a local install it fetches the deprecated npm package named `tsc`. Check `--version` first (see [toolchain.md](references/toolchain.md)). If the compiler is missing, rejects an option as unknown (an old TypeScript) or fails with no `error TS` line, the check did not run: say so and never call the code clean.

**The strict check** is the only command whose result decides "clean". It holds the code to the same profile as this plugin's post-edit hook, whatever the project's config says. Run it from the folder that holds the program's `tsconfig.json`, once per program that includes a changed file or a caller:

```bash
tsc -p <tsconfig.json> --pretty false --noEmit true --skipLibCheck true --allowJs true --checkJs true --strict true --noImplicitAny true --strictNullChecks true --strictFunctionTypes true --strictBindCallApply true --strictPropertyInitialization true --strictBuiltinIteratorReturn true --noImplicitThis true --useUnknownInCatchVariables true --alwaysStrict true --exactOptionalPropertyTypes true --noUncheckedIndexedAccess true --noPropertyAccessFromIndexSignature true --noImplicitReturns true --noImplicitOverride true --noFallthroughCasesInSwitch true --noUnusedLocals true --noUnusedParameters true --allowUnusedLabels false --allowUnreachableCode false
```

Read the results this way:

1. **Baseline**: run the strict check on each program before you edit, and keep the error list.
2. **Edited files**: fix every error, new or old.
3. **Other files**: an error missing from the baseline is yours; fix it. An error already in the baseline is existing strictness debt: do not fix it, and tell the user. Compare by file, code and message, since line numbers shift.
4. Run it again until the edited files report 0 errors and no new error appears elsewhere.

`tsc -p <tsconfig.json> --listFilesOnly` confirms a file is in the program and `--showConfig` shows the effective options; neither type-checks.

**Also run**, on the changed files:

- The project's formatter and linter (Biome, Prettier, ESLint) in their check-only form: `biome check` without `--write`, `prettier --check`, `eslint` without `--fix`, even when `package.json` scripts write. If they report, apply the fix to the changed files only.
- The project's tests for the changed behavior, with the command from its `package.json` scripts or README.

Read [toolchain.md](references/toolchain.md) when configuring TypeScript, raising strictness, telling TypeScript 6 and 7 apart, wiring CI or an IDE, or when the editor and `tsc` disagree. Run [fixtures.md](references/fixtures.md) once per project, before the first time you report that project's checks clean. This skill's folder is `${CLAUDE_SKILL_DIR}`; the fixtures are in its `references/fixtures/` folder.
