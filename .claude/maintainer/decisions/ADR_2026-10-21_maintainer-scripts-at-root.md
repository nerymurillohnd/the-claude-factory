---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The maintainer scripts and their tests live in `scripts/` at the root, not under `.github/`

## Scope

- In scope: every file that was under `.github/scripts/` (the Node scripts, `categories.json`, `evals-config.json`, `tsconfig.json`, `validate-claude.sh`, `run-evals.sh` and `tests/`), now under `scripts/`, and every live reference to them: the workflows, `.pre-commit-config.yaml`, `biome.json`, `.claude/settings.json`, `.claude/hooks/version-bump-gate.sh`, `.claude/CLAUDE.md`, `.claude/rules/WORKFLOW.md`, the project skills, the templates and the PR template.
- Out of scope: settled ADRs, specs and session handoffs, which keep the path they had when written; `.github/` keeps what belongs to GitHub (workflows, issue and PR templates, Dependabot, labels, CODEOWNERS).

## Context and problem statement

basedpyright never type-checked the Python tests under `.github/scripts/tests/`. Its documented default excludes `**/.*`, every folder whose name starts with a dot; an `exclude` setting adds to those patterns instead of replacing them, and they win over `include` (docs.basedpyright.com, Configuration → config files). Measured on 2026-10-21 with basedpyright 1.40.2: the repository root reports 4 source files, the `plugins/` ones; the test files passed on the command line report "No source files found"; a root `pyrightconfig.json` with `include` and `exclude` still reports 4. The next action that DEBT-003 recorded (pass the file list) cannot work. A copy of the repository with the folder moved to `scripts/` reports 7 source files and findings no gate had seen (4 errors and 28 warnings without a config). Where should the maintainer scripts live so every tool checks them?

## Decision drivers

- Every quality tool must see the maintainer code without a per-tool workaround.
- `.github/` is GitHub's configuration; the maintainer scripts are not GitHub-specific.
- The repository root should say at a glance what ships (`plugins/`) and what only maintainers use (`scripts/`).
- History of each file must survive the move.

## Considered options

- **Move `.github/scripts/` to `scripts/` with `git mv`**: chosen.
- **Configure basedpyright to reach `.github/`**: rejected because its default exclusion of dot folders cannot be overridden; measured above.
- **Leave the tests to mypy only (close DEBT-003 that way)**: rejected because basedpyright is the maintainer's Python type checker and dropping it for part of the code is a regression.

## Decision outcome

Chosen option: **move the folder to `scripts/`**, because it fixes the cause (a hidden folder) for basedpyright and for any tool that skips dot folders, with no configuration, and keeps each file's history (`git mv`).

The relative paths that depended on the depth moved one level: `ROOT` in `scripts/lib.mjs`, the root the Node tests, the Python tests (`parents[3]`) and the `by_path.sh` scripts compute, and the `extends` and `include` of `scripts/tsconfig.json`.

### Consequences

- Good, because `basedpyright --warnings` at the root checks every tracked Python file with no list and no config, which lets DEBT-003 close.
- Good, because GitHub's folder holds only GitHub's files.
- Bad, because every command, permission rule and doc that named `.github/scripts/` had to change in one commit, and older records keep the old path.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Nothing broke with the move | `node --test "scripts/tests/*.test.mjs"`, the unittest folders, every `by_path.sh`, `check-repo.mjs`, `catalog.mjs --check`, `tsc -p scripts/tsconfig.json` | All passed on 2026-10-21 (126 of 126 Node tests, 0 skipped) | Each push |
| No live file still names the old path | `rg '\.github/scripts'` outside `.claude/maintainer/`, `.claude/specs/`, `.claude/session-handoff/` and `.claude/plans/` | No match on 2026-10-21 | After any rename |
| basedpyright sees every Python file | `basedpyright --warnings --verbose` prints `Found 7 source files` | Pending: the findings it reports are fixed in the next commit | After the fix |

## More information

- Nery decided this on 2026-10-21 ("¿y si los scripts de mantenimiento pasan a raíz? scripts/"), after the dot-folder exclusion was measured and confirmed in the basedpyright docs.
- Related: DEBT-003, ADR_2026-10-21_maintainer-only-root-package-json.
