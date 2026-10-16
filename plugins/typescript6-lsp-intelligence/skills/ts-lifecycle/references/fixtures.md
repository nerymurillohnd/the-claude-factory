# Fixtures: prove the checks detect breakage

A clean result proves nothing until the same check fails on code that is broken on purpose. Run the fixtures once per program the change touches, before the first time you report that program's checks clean; a new session that cannot tell whether it ran them runs them again. Without the Bash tool they cannot run: say the checks were not proven. In `research` mode, run only `--outside`, and only when a conclusion rests on the compiler's sensitivity (SKILL.md); otherwise skip the fixtures and report them as not run.

The fixtures prove that this compiler and this tsconfig chain see the program's files and report strict errors. They do not prove the project's own check command: a framework checker (`vue-tsc`, `svelte-check`, `astro check`), a package script or a lax `tsconfig.json` checked without the strict profile needs its own sensitivity probe. They also do not prove which files a program contains: check that with `tsc --listFilesOnly -p <tsconfig.json>`.

Each file in the skill's `assets/` folder holds one known defect, or none (`clean_control`). The files end in `.fixture` so no tool treats them as code. `tsconfig.json.fixture` is a strict, self-contained program.

## Run the type-check fixtures

The owning tsconfig is the program that contains the changed files: `tsc --listFilesOnly -p <tsconfig.json>` lists them. When that tsconfig is a solution-style root (`files: []` with `references`), use the referenced program that lists them. Changed files have no type-check layer when no `tsconfig.json` or `jsconfig.json` program contains them, or when they are JavaScript that neither `checkJs` nor a `// @ts-check` line covers: report the layer as not present instead of running the fixtures.

- `implementation` mode: `bash <skill folder>/scripts/run-fixtures.sh <owning tsconfig.json>`. The script creates one `lsp-fixture-*` folder at a time in the program's `rootDir` (or beside the tsconfig), extends the owning tsconfig by absolute path with its `files` reset, runs the strict check below, and deletes the folder.
- `research` mode, only when a conclusion rests on the compiler's sensitivity: `bash <skill folder>/scripts/run-fixtures.sh --outside`. It uses `tsconfig.json.fixture` in a temporary folder outside the project, which proves the compiler but not the project's config.

`<skill folder>` is the `${CLAUDE_SKILL_DIR}` that SKILL.md gives. The script uses the project's `node_modules/.bin/tsc`, walking up from the tsconfig, then a `tsc` on `PATH`; pass a compiler path as the last argument to override it. It never uses `npx tsc`, which fetches the deprecated npm package named `tsc` when no local TypeScript exists. It always exits 0 and prints one line per fixture, `expected` against `observed`, then a verdict.

## The strict check

The script runs each fixture through this command, from the fixture's folder:

```bash
tsc -p <tsconfig.json> --pretty false --noEmit true --tsBuildInfoFile <file in a temporary folder> --skipLibCheck true --allowJs true --checkJs true --strict true --noImplicitAny true --strictNullChecks true --strictFunctionTypes true --strictBindCallApply true --strictPropertyInitialization true --strictBuiltinIteratorReturn true --noImplicitThis true --useUnknownInCatchVariables true --alwaysStrict true --exactOptionalPropertyTypes true --noUncheckedIndexedAccess true --noPropertyAccessFromIndexSignature true --noImplicitReturns true --noImplicitOverride true --noFallthroughCasesInSwitch true --noUnusedLocals true --noUnusedParameters true --allowUnusedLabels false --allowUnreachableCode false
```

The fixtures are `.ts` files, so `--allowJs` and `--checkJs` change nothing for them; they are there because the strict profile is the plugin hook's, which checks edited JavaScript too. Each option has an explicit value because `--strict` alone does not override an explicit `"strictNullChecks": false` in the config; the project's `paths`, module resolution and `types` still apply. `--tsBuildInfoFile` keeps an `incremental` or `composite` config from writing its build-info file into the project. A compiler that rejects an option (TS5023) predates it: say which option, and do not call the fixtures passed.

## Run the references fixture

Skip it in `research` mode, without an `LSP` tool, and without the Bash tool, which the cleanup needs: report reference coverage as not proven. Otherwise:

1. Create `lsp-fixture-references/references.ts` at the root of the session's working directory with the Write tool, with the content of `assets/references.ts.fixture`. Write reaches the language server; a file copied from the shell may not. If that folder already exists, stop: it is not yours to overwrite.
2. `hover` `target` at line 2, character 17, so the server loads the program.
3. Run `findReferences` at the same position.
4. Delete the folder from Bash with `rm -rf <working directory>/lsp-fixture-references`, even when a step failed. Write cannot delete.

| Fixture | Command | Expected |
| :-- | :-- | :-- |
| `clean_control.ts.fixture` | the strict check | no errors |
| `type_mismatch.ts.fixture` | the strict check | `TS2322` |
| `implicit_any.ts.fixture` | the strict check | `TS7006` |
| `possibly_undefined.ts.fixture` | the strict check | `TS18048` |
| `missing_member.ts.fixture` | the strict check | `TS2551`, the error an incomplete rename leaves |
| `references.ts.fixture` | `findReferences` on `target` at line 2, character 17 | The definition and three calls |

## Reading the outcome

- A broken fixture without its expected code means the check is blind here: the owning config could not be read, or the compiler is not the one you think. Say which, and do not call code clean on that check.
- A failing `clean_control` means the checks misfire in this program. Explain the errors before trusting any other result.
- Fewer than four references after two matching results means the index is cold, the file is not synchronized with the server, or it belongs to no loaded project; see "Trusting a result" in SKILL.md.
