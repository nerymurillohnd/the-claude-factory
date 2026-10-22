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

The script runs each fixture through `tsc -p <tsconfig.json>` from the fixture's folder, with `--pretty false --noEmit true`, every option of its `STRICT_POLICY` that the compiler knows and the program's config chain leaves unset (read with `--showConfig`), and `--tsBuildInfoFile` in a temporary folder. `STRICT_POLICY` is the post-edit hook's own policy, so the fixtures prove the check the hook applies. `scripts/run-fixtures.sh` is the only source of the options and of the expected codes (its `expected_for`): read them there, never from a copy, and do not run the fixtures by hand.

The fixtures are `.ts` files, so `--allowJs` and `--checkJs` change nothing for them; they are there because the strict profile is the plugin hook's, which checks edited JavaScript too. An option the config sets itself, `false` included, stays the project's, as in the hook, and setting `strict` keeps the whole strict family the project's; the project's `paths`, module resolution and `types` still apply. A lax config therefore makes a fixture report MISMATCH: that is what the hook really checks in this program, not a broken fixture. `--tsBuildInfoFile` keeps an `incremental` or `composite` config from writing its build-info file into the project. An option newer than the compiler is left out, and the output names it on a `Not applied` line: report those options as not proven, since that compiler cannot check them.

## Run the references fixture

Skip it in `research` mode, without an `LSP` tool, and without the Bash tool, which the cleanup needs: report reference coverage as not proven. Otherwise:

1. Create `lsp-fixture-references/references.ts` at the root of the session's working directory with the Write tool, with the content of `assets/references.ts.fixture`. Write reaches the language server; a file copied from the shell may not. If that folder already exists, stop: it is not yours to overwrite.
2. `hover` `target` at line 2, character 17, so the server loads the program.
3. Run `findReferences` at the same position until two consecutive results match, at most three calls: the warm-up check under "Trusting a result" in SKILL.md.
4. Delete the folder from Bash with `rm -rf <working directory>/lsp-fixture-references`, even when a step failed. Write cannot delete.

The table below explains the codes the script prints; when it differs from the script, the script wins and the table is the bug to report.

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
- Fewer than four references in the two matching results means the index is cold, the file is not synchronized with the server, or it belongs to no loaded project; see "Trusting a result" in SKILL.md.
