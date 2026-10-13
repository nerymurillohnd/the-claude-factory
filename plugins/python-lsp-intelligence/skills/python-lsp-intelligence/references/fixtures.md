# Fixtures: prove the checks detect breakage

A clean result proves nothing until the same checks fail on code that is broken on purpose. Each file in `fixtures/` holds one known defect, or none (`clean_control`). The files end in `.fixture` so no tool treats them as code; copy one to a `.py` name to use it.

Run the fixtures in a temporary folder **inside** the project you are checking, so the project's configuration applies, and delete the folder afterwards:

```bash
W=$(mktemp -d "<project root>/lsp-fixture-XXXXXX")
cp "<this skill>/references/fixtures/undefined_name.py.fixture" "$W/undefined_name.py"
ruff check "$W/undefined_name.py"
basedpyright "$W/undefined_name.py"
rm -rf "$W"
```

| Fixture | Command | Expected |
| :-- | :-- | :-- |
| `clean_control.py.fixture` | `ruff check`, `ruff format --check`, `basedpyright` | No findings; every exit 0 |
| `undefined_name.py.fixture` | `ruff check`, `basedpyright` | `F821`; `reportUndefinedVariable` |
| `return_type.py.fixture` | `basedpyright` | `reportReturnType` |
| `unformatted.py.fixture` | `ruff format --check` | exit 1, the file would be reformatted |
| `references.py.fixture` | `findReferences` on `target` at line 2, character 5 | The definition and three calls |

## Reading the outcome

- A broken fixture without its expected code means the check is blind here: the project's configuration disables that rule, the tool is not the one you think, or it runs in another environment. Say which, and do not call code clean on that check.
- A failing `clean_control` means the checks misfire in this project. Explain the findings before trusting any other result.
- Fewer than four references after two matching results means the index is cold or the file is outside the working directory; see "Trusting a result" in SKILL.md.
