# Fixtures: prove the shell checks detect breakage

A clean result proves nothing until the same checks fail on code that is broken on purpose. Each fixture in `fixtures/` holds one known defect, or none (`clean_control`). The files end in `.fixture` so no linter, formatter or hook treats them as scripts; each starts with `# shellcheck shell=bash`, so a copy with a `.sh` name needs no shebang.

Set `FIXTURES` to the fixtures directory named in SKILL.md.

## Expected results

| Fixture                         | Expected                                                                  | Proves                                                                  |
| ------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `clean_control.sh.fixture`      | shellcheck and `shfmt -d` exit 0                                          | The checks do not report false positives here                           |
| `unquoted_expansion.sh.fixture` | `SC2086`; with `-o all` also `SC2250`                                     | shellcheck runs and reports default checks                              |
| `optional_checks.sh.fixture`    | `SC2250` and `SC2312` with `-o all`; exit 0 without it                    | `-o all` is in effect. If this file passes, the optional checks are off |
| `unformatted.sh.fixture`        | `shfmt -d` exits non-zero and prints a diff                               | shfmt runs                                                              |
| `references.sh.fixture`         | No findings; `findReferences` on `target` (line 3, character 1) returns 4 | The language server indexes and answers                                 |

shellcheck also reads the `SHELLCHECK_OPTS` environment variable and `.shellcheckrc` or `shellcheckrc` files. Either can add or remove checks without anything in the command line showing it: a machine with `SHELLCHECK_OPTS="-o all"` reports the optional checks even when the check chain drops `-o all`.

## Level 1: the tools, outside any project

Run each fixture in a fresh temporary directory, with the environment and rc files neutralized:

```bash
W=$(mktemp -d)
cp "$FIXTURES/optional_checks.sh.fixture" "$W/optional_checks.sh"
cd "$W" && env -u SHELLCHECK_OPTS shellcheck --norc -o all -S style -x -a -f gcc optional_checks.sh
cd "$W" && env -u SHELLCHECK_OPTS shellcheck --norc -S style -x -a -f gcc optional_checks.sh
cd "$W" && shfmt -d -s -i 2 -ci -sr -bn optional_checks.sh
cd / && rm -rf "$W" && test ! -e "$W"
```

Repeat for every fixture in the table and compare with the expected column.

## Level 2: the project's configuration

Create the temporary directory next to the file you are checking, so the project's `.shellcheckrc` and `.editorconfig` apply, and run the check chain exactly as for real code (with the session's environment):

```bash
W=$(mktemp -d "<directory of the changed file>/lsp-fixture-XXXXXX")
cp "$FIXTURES/unquoted_expansion.sh.fixture" "$W/unquoted_expansion.sh"
shellcheck -o all -S style -x -a "$W/unquoted_expansion.sh"
rm -rf "$W" && test ! -e "$W"
```

A fixture that fails at level 1 but passes at level 2 means the project or the environment turns that check off (`disable=` in an rc file, or `SHELLCHECK_OPTS`). Tell the user which one. Do not change their configuration, and do not call code clean on that check.

Quality-gate hooks of the session may report the copied fixture. That is expected: remove the directory before the turn ends.

## Level 3: the language server

Copy `references.sh.fixture` to a `.sh` name in a temporary directory inside the session's working directory (not a hidden directory: the server skips most of those), then:

1. `findReferences` at line 3, character 1 returns 4 (the definition and 3 calls). Repeat until two results match.
2. Fewer than 4 after two matching results: the index is cold or the file is outside what the server discovers. See "Cold index and wrong root" in SKILL.md.

Remove the directory afterwards and confirm it is gone.

## Reading the outcome

- A broken fixture without its expected code is a silent failure. Report which check is blind and the likely cause (tool missing, configuration, environment), and do not report any code as clean on that check.
- A failing `clean_control` means the checks misfire in this environment. Explain the findings before trusting any other result.
- Rely on "non-zero" and on the SC codes, not on a specific exit status.
