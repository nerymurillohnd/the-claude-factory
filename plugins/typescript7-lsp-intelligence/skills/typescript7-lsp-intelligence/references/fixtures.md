# Fixtures: prove the checks detect breakage

A clean result proves nothing until the same checks fail on code that is broken on purpose. Each file in `fixtures/` holds one known defect, or none (`clean_control`). The files end in `.fixture` so no tool treats them as code; copy one to a `.ts` name to use it. `tsconfig.json.fixture` is a strict, self-contained program.

Run the fixtures in a temporary folder **inside** the project you are checking, extending its `tsconfig.json` so the project's options apply, and delete the folder afterwards:

```bash
W=$(mktemp -d "<project root>/lsp-fixture-XXXXXX")
cp "<this skill>/references/fixtures/implicit_any.ts.fixture" "$W/implicit_any.ts"
printf '{ "extends": "../tsconfig.json", "include": ["*.ts"] }\n' > "$W/tsconfig.json"
tsc --noEmit -p "$W/tsconfig.json"
rm -rf "$W"
```

Outside any project, copy `tsconfig.json.fixture` as `tsconfig.json` instead of extending.

| Fixture | Command | Expected |
| :-- | :-- | :-- |
| `clean_control.ts.fixture` | `tsc --noEmit -p` | exit 0, no errors |
| `type_mismatch.ts.fixture` | `tsc --noEmit -p` | `TS2322` |
| `implicit_any.ts.fixture` | `tsc --noEmit -p` | `TS7006`, only when `noImplicitAny` (part of `strict`) is on |
| `possibly_undefined.ts.fixture` | `tsc --noEmit -p` | `TS18048`, only when `strictNullChecks` (part of `strict`) is on |
| `references.ts.fixture` | `findReferences` on `target` at line 2, character 17 | The definition and three calls |

## Reading the outcome

- A broken fixture without its expected code means the check is blind here: the project's options turn that check off (`strict: false`), the file is in no program, or the compiler is not the one you think. Say which, and do not call code clean on that check.
- A failing `clean_control` means the checks misfire in this project. Explain the errors before trusting any other result.
- An error about `rootDir` or the include pattern concerns where the temporary folder sits, not the fixture: create it inside the program's `rootDir`.
- Fewer than four references after two matching results means the index is cold or the file belongs to no loaded project; see "Trusting a result" in SKILL.md.
