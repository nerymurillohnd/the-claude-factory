# Fixtures: prove the checks detect breakage

A clean result proves nothing until the same checks fail on code that is broken on purpose. Each file in `fixtures/` holds one known defect, or none (`clean_control`). The files end in `.fixture` so no tool treats them as scripts; each starts with `# shellcheck shell=bash`, so a copy with a `.sh` name needs no shebang.

Run the fixtures in a temporary folder **inside** the project you are checking, so the project's `.editorconfig` and `.shellcheckrc` apply, and delete the folder afterwards:

```bash
W=$(mktemp -d "<project root>/lsp-fixture-XXXXXX")
cp "<this skill>/references/fixtures/unquoted_expansion.sh.fixture" "$W/unquoted_expansion.sh"
shellcheck "$W/unquoted_expansion.sh"
shfmt -d "$W/unquoted_expansion.sh"
rm -rf "$W"
```

| Fixture | Command | Expected |
| :-- | :-- | :-- |
| `clean_control.sh.fixture` | `shellcheck`, `shfmt -d` | No findings; exit 0 |
| `unquoted_expansion.sh.fixture` | `shellcheck` | `SC2086`; with `-o all` also `SC2250` |
| `optional_checks.sh.fixture` | `shellcheck -o all` | `SC2250`; exit 0 without `-o all`, which proves whether the optional checks are on |
| `unformatted.sh.fixture` | `shfmt -d` | exit 1 and a diff |
| `references.sh.fixture` | `findReferences` on `target` at line 2, character 1 | The definition and three calls |

## Reading the outcome

- A broken fixture without its expected code means the check is blind here: a `disable=` in an rc file, `SHELLCHECK_OPTS`, or a tool that is not the one you think. Say which, and do not call code clean on that check.
- A failing `clean_control` means the checks misfire in this project. Explain the findings before trusting any other result.
- Fewer than four references after two matching results means the index is cold or the file is outside the working directory; see "Trusting a result" in SKILL.md.
