# Fixtures: prove the TypeScript checks detect breakage

A clean result proves nothing until the same checks fail on code that is broken on purpose. Each fixture in `fixtures/` holds one known defect, or none (`clean_control`). The files end in `.fixture` so no compiler, linter or hook treats them as code; copy one to a `.ts` name to use it. `tsconfig.json.fixture` is a strict, self-contained program for level 1.

Set `FIXTURES` to the fixtures directory named in SKILL.md.

## Expected results

| Fixture                         | Expected                                                                 | Proves                                                  |
| ------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------- |
| `clean_control.ts.fixture`      | `tsc` exits 0                                                            | The checks do not report false positives here           |
| `type_mismatch.ts.fixture`      | `TS2322`                                                                 | tsc runs and type-checks                                |
| `implicit_any.ts.fixture`       | `TS7006`, only when `noImplicitAny` (part of `strict`) is on             | Strictness is in effect. If this file passes, it is off |
| `possibly_undefined.ts.fixture` | `TS18048`, only when `strictNullChecks` (part of `strict`) is on         | Null checking is in effect                              |
| `references.ts.fixture`         | No errors; `findReferences` on `target` (line 2, character 17) returns 4 | The language server indexes and answers                 |

Verified on TypeScript 6.0.3, where a failing `tsc` exits 2. Rely on "non-zero" and on the TS codes, not on the exact number.

## Level 1: the tools, outside any project

```bash
W=$(mktemp -d)
cp "$FIXTURES/tsconfig.json.fixture" "$W/tsconfig.json"
cp "$FIXTURES/implicit_any.ts.fixture" "$W/implicit_any.ts"
cd "$W" && tsc --noEmit -p tsconfig.json
cd "$W" && tsc --listFilesOnly -p tsconfig.json | grep implicit_any.ts
cd / && rm -rf "$W" && test ! -e "$W"
```

Use the same `tsc` the quality check uses (the project's `node_modules/.bin/tsc` when present). Repeat for every fixture in the table and compare with the expected column.

## Level 2: the project's configuration

Apply the project's compiler options to the fixtures by extending its tsconfig from a temporary directory inside the project:

```bash
W=$(mktemp -d "<project root>/lsp-fixture-XXXXXX")
cp "$FIXTURES/implicit_any.ts.fixture" "$W/implicit_any.ts"
printf '{ "extends": "../<the program tsconfig>", "include": ["*.ts"] }\n' > "$W/tsconfig.json"
cd "$W" && tsc --noEmit -p tsconfig.json
rm -rf "$W" && test ! -e "$W"
```

A fixture that fails at level 1 but passes at level 2 means the project's options turn that check off, for example `strict: false`. Tell the user. Do not change their configuration, and do not call code clean on that check. An error about `rootDir` or the include pattern concerns where the probe directory sits, not the fixture: create it inside the program's `rootDir`.

Quality-gate hooks of the session may report the copied fixture. That is expected: remove the directory before the turn ends.

## Level 3: the language server

Copy `references.ts.fixture` to a `.ts` name in a temporary directory inside the session's working directory, then:

1. `hover` at line 2, character 17 shows `function target(value: number): number`. "No hover information" means the server is not serving the file: stop here.
2. `findReferences` at the same position returns 4 (the definition and 3 calls). Repeat until two results match.
3. Fewer than 4 after two matching results: the index is cold or the file belongs to no loaded project. See "Cold index and wrong root" in SKILL.md.

Remove the directory afterwards and confirm it is gone.

## Reading the outcome

- A broken fixture without its expected code is a silent failure. Report which check is blind and the likely cause (tool missing, configuration, wrong `tsc`), and do not report any code as clean on that check.
- A failing `clean_control` means the checks misfire in this environment. Explain the errors before trusting any other result.
