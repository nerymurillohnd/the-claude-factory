# Fixtures: prove the checks detect breakage

A clean result proves nothing until the same checks fail on code that is broken on purpose. Run these once per project, before the first time you report that project's checks clean. Each file in `fixtures/` holds one known defect, or none (`clean_control`). The files end in `.fixture` so no tool treats them as code; copy one to a `.ts` name to use it. `tsconfig.json.fixture` is a strict, self-contained program.

"Project" means one repository or workspace root. Once per session is enough; a new session that cannot tell whether it ran them runs them again. Without a shell (Chat, Cowork) they cannot run: say the checks were not proven.

The skill folder is the `${CLAUDE_SKILL_DIR}` path that SKILL.md gives; write its absolute value in place of `<skill folder>`. Create and delete only the `lsp-fixture-*` folders below; touch nothing else in the project.

Run each type-check fixture in its own temporary folder **inside** the project, extending the tsconfig that owns the code by absolute path (when that tsconfig is a solution-style root, use the referenced program that lists the code). Create the folder inside that program's `rootDir`, or beside the tsconfig when it sets none, or `tsc` reports a `rootDir` or include error about the folder, not the fixture:

```bash
OWNER="<absolute path of the owning tsconfig.json>"
for name in clean_control type_mismatch implicit_any possibly_undefined; do
  W=$(mktemp -d "<rootDir of that program>/lsp-fixture-XXXXXX")
  cp "<skill folder>/references/fixtures/$name.ts.fixture" "$W/$name.ts"
  printf '{ "extends": "%s", "files": [], "include": ["*.ts"] }\n' "$OWNER" > "$W/tsconfig.json"
  # the strict check from SKILL.md, with -p "$W/tsconfig.json"; compare with the table
  rm -rf "$W"
done
```

Outside any project, create `W=$(mktemp -d)` and copy `tsconfig.json.fixture` to `$W/tsconfig.json` instead of extending.

For `references.ts.fixture`, copy it to a `references.ts` in a temporary folder inside the project, `hover` it so the server loads the program, run the `findReferences` of the table on that absolute path, then delete the folder.

| Fixture | Command | Expected |
| :-- | :-- | :-- |
| `clean_control.ts.fixture` | the strict check | exit 0, no errors |
| `type_mismatch.ts.fixture` | the strict check | `TS2322` |
| `implicit_any.ts.fixture` | the strict check | `TS7006` |
| `possibly_undefined.ts.fixture` | the strict check | `TS18048` |
| `references.ts.fixture` | `findReferences` on `target` at line 2, character 17 | The definition and three calls |

## Reading the outcome

- A broken fixture without its expected code means the check is blind here: the file is in no program, the owning config could not be read, or the compiler is not the one you think. Say which, and do not call code clean on that check.
- A failing `clean_control` means the checks misfire in this project. Explain the errors before trusting any other result.
- Fewer than four references after two matching results means the index is cold or the file belongs to no loaded project; see "Trusting a result" in SKILL.md.
