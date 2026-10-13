---
name: typescript7-lsp-intelligence
description: Navigates TypeScript and JavaScript through the native TypeScript language server, finds the tsconfig program that owns each file, repairs compiler findings without unsafe assertions or suppressions, and verifies each change with the compiler. Use when navigating, editing, refactoring or diagnosing TypeScript or JavaScript, resolving imports, types or program membership, explaining why the editor and tsc disagree, or verifying a change.
---

# TypeScript and JavaScript Code Intelligence

Understand the symbol and the program that owns it, preserve runtime and public API contracts, and verify the affected behavior. Fix the actionable diagnostics before beginning unrelated changes: those are the findings in the code the task changes, including any the change introduces. Report pre-existing findings in code the task does not touch; fix them only when the user asks.

**Authorized** means what the request covers explicitly or necessarily implies, such as editing the code it asks to change and running read-only checks. Installing or switching compilers, changing dependencies, and changing `tsconfig`, lint or format policy always need an explicit request.

## Choose the right tool

**Claude must prefer the LSP over Grep, Glob, and Bash for code navigation and semantic relationships.** Use source reading to understand implementation and text search for metadata, dynamic names, and source formats outside semantic coverage. Use the compiler and other command-line tools for explicit verification.

| Operation | Purpose | Use before |
|---|---|---|
| `goToDefinition` | Identify a symbol's declaration | Modifying unfamiliar code |
| `findReferences` | Discover static consumers | Refactoring or renaming |
| `goToImplementation` | Find interface/abstract implementations | Changing polymorphic behavior |
| `hover` | Inspect inferred types, signatures, and documentation | Understanding APIs or validating position |
| `documentSymbol` | Obtain a file outline | Exploring a large file |
| `workspaceSymbol` | Search named symbols | Locating related source |
| `prepareCallHierarchy` | Identify the callable hierarchy item | Analyzing call relationships |
| `incomingCalls` | Discover callers | Impact analysis |
| `outgoingCalls` | Discover callees | Dependency tracing |

For the Claude `LSP` tool, provide the common parameters for every operation:

- `filePath`: the absolute source path.
- `line`: a 1-based line number.
- `character`: a 1-based UTF-16 column at the symbol name.

Supply additional fields only when the actual tool schema exposes them. Read [operations.md](references/operations.md) for capability checks, workspace symbol search, and import actions.

## Change an exported symbol

1. Identify the declaration with `goToDefinition` or `hover`.
2. Find the program that owns the file (see "Verify what changed") and query `findReferences` from a source file in each implicated program. For a short or empty result, check path, position, synchronization, and loaded projects, then retry at most twice after the initial request.
3. Inspect what references miss: re-exports, local import aliases, package `exports` and entry points, declaration files, dynamically named consumers, and framework files a TS-only server can't read.
4. Edit the confirmed consumers; list unresolved ones separately.
5. Verify with the compiler on every affected program. The change is done when those checks pass, the diagnostics Claude Code reports after each edit show no new findings, and the unresolved consumers are reported.

Read [typescript-navigation.md](references/typescript-navigation.md) for project scope, moved files, and call analysis. When semantic tooling is unavailable, report the boundary once and use source reading and text search; do not install a server merely to answer a lookup.

## Diagnose the actual program

Preserve the diagnostic's source, file, location, code, message, snapshot, and relevant configuration. The LSP findings are the diagnostics Claude Code reports automatically after each edit; compare them with a CLI run on the same source and program before deciding why they disagree.

For external or unknown values, validate runtime shape and narrow `unknown` into the required contract. Preserve rejection behavior, module side effects, and affected callers. Do not use unsafe assertions, non-null assertions, broader `any`, suppressions, invented defaults, or weaker checking merely to make diagnostics disappear. Reread source changed by a formatter or code action before the next edit.

Read [diagnostics-and-repair.md](references/diagnostics-and-repair.md) before selecting a correction or changing configuration.

## Verify what changed

1. Find the owning `tsconfig.json`: the nearest one above the file. Confirm with `tsc --listFilesOnly -p <tsconfig>` that the file is listed; if it isn't, follow that config's `references`, or the solution-style root that lists it, until you find the program that includes it.
2. Compile with the project's own compiler, `tsc --noEmit -p <tsconfig>`, run through the project's package manager (for example `npx tsc`). A compiler the user or the project declares replaces this default.
3. Run the project's declared lint, format, and test commands for the changed files.
4. After each fix, rerun the same checks; [verification.md](references/verification.md) sets when to stop.

Preserve every process status and full stdout/stderr. Report the change or diagnosis, the compiler and version used, the programs checked, and remaining uncertainty.

## Pitfalls

- `--showConfig` and `--listFilesOnly` inspect configuration and membership; neither type-checks.
- A config without `files` or `include` still defines a program: the defaults include source files.
- `allowJs` brings JavaScript into the program; only `checkJs` or a file's `// @ts-check` type-checks it.
- A moved file absent from the compiler's program has not been validated by that compiler; a passing CLI run cannot dismiss its LSP diagnostic.
- A failed `tsc` with no `error TS` line is still a failure; a successful final filter does not establish compiler success.
- `--noEmit` stops program output, not incremental or build metadata writes.
- The legacy generation exposes `tsserver` (`lib/tsserver.js`), which wrappers such as typescript-language-server need; the native generation exposes `tsc --lsp --stdio` and no `tsserver.js`. Do not point a `tsserver` wrapper at a native-only package.
- Raw LSP protocol positions are 0-based; convert once.

## Control tests

Run the control tests only when the user asks to test tool coverage, or when a check passes code it should flag. They are not a step of ordinary coding tasks. Read [controls.md](references/controls.md) first, then run the bundled runner by path:

```bash
"${CLAUDE_SKILL_DIR}/scripts/verify-fixtures.sh"
"${CLAUDE_SKILL_DIR}/scripts/verify-fixtures.sh" --tool tsc=/absolute/path/to/declared/tsc
```

The first form uses `tsc` from `PATH`; pass `--tool tsc=/absolute/path` for the compiler the task declares, and run once per compiler generation you need to check. The runner needs `bash` and `jq` 1.6 or later, installs nothing, and never executes the controls.

- **Exit 0**: the JSON report printed. `allExpectedOutcomesMatched` is the overall result; each entry in `results` carries its own `expectedOutcomeMatched`.
- **Exit 2**: setup failed and no report printed; stderr names the failed step and what to do next.

## Reference map

- [operations.md](references/operations.md): capability checks, workspace symbol search, and import actions.
- [typescript-navigation.md](references/typescript-navigation.md): symbol identity and consumer coverage.
- [diagnostics-and-repair.md](references/diagnostics-and-repair.md): program context, compiler generations, and safe repairs.
- [verification.md](references/verification.md): what each check establishes, Biome, and the repeat-after-fix loop.
- [controls.md](references/controls.md): the control tests and their expected results.
- [sources.md](references/sources.md): read when an installed tool behaves differently from this skill, before revising an assumption.
