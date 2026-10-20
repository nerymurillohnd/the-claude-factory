# Quality Gate

## No Progress With Open Issues

- Do not advance to the next step, file or task while a detected issue is open.
- Fix every issue the moment it appears: gate finding, failing test, error or warning in any output.
- Fix issues that predate your change too. Do not defer, park or work around them.
- Never accumulate technical debt: no TODO, no "fix later", no "known issue" left behind.
- Fix the root cause. Never silence the symptom.
- Report an issue as open only when it is blocked on a decision or a spend only Nery can make. Stop and ask.

## After Editing a File

- Run the gates for every `.py`, `.mjs` and `.sh` file you edit, write or create.
- Run them right after the edit, before the next task.
- Run in this order: formatter, linter, type checker, tests.
- Fix every finding at its source. Re-run until the output is clean.
- Never loosen a config, add an ignore comment, cast unsafely or edit a test to silence a finding.
- Quote each command and its output. Never report a gate as passing unless you ran it in this session.

### Python

- `uvx ruff@0.17.1 format <file>` - Run first, after every `.py` edit.
- `uvx ruff@0.17.1 check <file>` - Run after the formatter.
- `uvx --from mypy==1.20.2 mypy --strict <file>` - Run after ruff.
- `basedpyright --warnings <file>` - Run after mypy.
- `python3 -m unittest discover -s .github/scripts/tests/<plugin>` - Run when the file belongs to a plugin with Python tests.
- `.github/scripts/tests/<plugin>/by_path.sh` - Run when that plugin folder ships one.

### JavaScript Modules

- `npx --yes @biomejs/biome@2.5.15 check --write --error-on-warnings <file>` - Run first, after every `.mjs` edit.
- `npx --yes --package typescript@6.0.3 tsc -p plugins/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Run when the file is under `plugins/`.
- `npx --yes --package typescript@6.0.3 tsc -p .github/scripts/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Run when the file is under `.github/scripts/`.
- `node --test ".github/scripts/tests/*.test.mjs"` - Run after the type check. Read the `skipped` count.
- `node .github/scripts/check-repo.mjs` - Run after the tests.

`tsc` checks the whole project.

- Fix every error it reports, in the files you touched and in the others.

### Mods

A plugin that ships a mod keeps its code in `hooks/*.ts` and its tests in `tests/*.test.ts`.

- `npx --yes @biomejs/biome@2.5.15 check --write --error-on-warnings <file>` - Run first, after every `.ts` edit.
- `npx --yes --package typescript@6.0.3 tsc -p plugins/<plugin>/tsconfig.json --noEmit` - Run after Biome. The config extends the declarations the engine writes into `plugins/<plugin>/.claude-plugin/types/` when it loads the mod. Git ignores that folder, so after a fresh clone load the plugin once in an interactive session from a trusted folder (`claude --plugin-dir plugins/<plugin>`, then `/exit`) to write it. CI cannot run this gate for that reason.
- `claude plugin validate --strict plugins/<plugin>` - Run after tsc. It reads the mod the way the engine will. Pass `$` only inside `register.ts`: validation fails when `$` goes to a function imported from another file.
- `claude plugin test plugins/<plugin>` - Run last. Break the rule under test on purpose once and confirm its tests fail.

### Shell

- `shfmt -w <file>` - Run first, after every `.sh` edit.
- `shellcheck -o all -S style -x -a -P SCRIPTDIR <file>` - Run after shfmt.
- `.github/scripts/tests/<plugin>/by_path.sh` - Run when the script belongs to a plugin that ships one.

## Before Every Push

- Run the steps in order.
- Stop at the first failure. Fix the cause, then restart from step 1.
- Report the gates as a table: gate, result and key output line.
- Call the work verified only when every gate passes.
- The gates run pinned versions. CI pins the ones it runs in the `env` block of `.github/workflows/validate.yml`.
- No git hook runs `.pre-commit-config.yaml`, and CI does not run `basedpyright`. CI installs `tsc` only so the TypeScript hook tests run; it does not type-check the `.mjs` files.

1. `git branch --show-current` - Confirm it is the intended branch, not a stale or merged one.
2. `git status --short` - Confirm no path is staged that you did not change.
3. `git log --format='%h %G? %s' origin/main..HEAD` - Confirm every commit shows `G`.
4. `node --test ".github/scripts/tests/*.test.mjs"` - Runs the script tests and the LSP hook tests. They need `shfmt`, `shellcheck`, `ruff` and `basedpyright` on `PATH`. Read the `skipped` count: a missing tool skips its cases.
5. `node .github/scripts/check-repo.mjs` - Checks the repository policy: manifests, required plugin files and sections, changelog entries, and the root `README.md` and `CHANGELOG.md`.
6. `node .github/scripts/catalog.mjs --check` - Fails when the generated blocks of the root `README.md` are out of date.
7. `.github/scripts/validate-claude.sh` - Runs `claude plugin validate --strict` on the marketplace, on `.claude/` and on every plugin, and `claude plugin test` on every plugin that ships mod tests.
8. `node .github/scripts/check-version-bump.mjs origin/main` - Fails when a plugin changed since `origin/main` without a version bump and a changelog entry. Skip it when `origin/main` does not exist.
9. `npx --yes @biomejs/biome@2.5.15 check --error-on-warnings .` - Checks the format, lint and imports of the JavaScript and JSON files.
10. `git ls-files -z '*.sh' | xargs -0 shellcheck -o all -S style -x -a -P SCRIPTDIR` - Lints every tracked shell script.
11. `git ls-files -z '*.sh' | xargs -0 shfmt -d` - Shows the formatting drift of every tracked shell script.
12. `python3 -m unittest discover -s .github/scripts/tests/<plugin>` - Runs the Python tests of one plugin. Repeat for each test folder with `test_*.py` files.
13. `.github/scripts/tests/<plugin>/by_path.sh` - Runs the plugin scripts by path, as Claude Code does. Repeat for each plugin folder that ships one.
14. `uvx ruff@0.17.1 check plugins .github/scripts` - Lints the Python files.
15. `uvx ruff@0.17.1 format --check plugins .github/scripts` - Checks the formatting of the Python files.
16. `git ls-files -z 'plugins/*.py' '.github/scripts/tests/*.py' | xargs -0 uvx --from mypy==1.20.2 mypy --strict` - Type-checks the Python files.
17. `basedpyright --warnings` - Type-checks the whole project.
18. `npx --yes --package typescript@6.0.3 tsc -p plugins/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Type-checks the `.mjs` files under `plugins/`.
19. `npx --yes --package typescript@6.0.3 tsc -p .github/scripts/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Type-checks the `.mjs` files under `.github/scripts/`.
20. `npx --yes --package typescript@6.0.3 tsc -p plugins/<plugin>/tsconfig.json --noEmit` - Type-checks the mod of each plugin that ships one. Run it locally: it needs the declarations the engine writes, which CI does not have.
21. `npx --yes markdownlint-cli2@0.23.3` - Lints the Markdown that people read.
22. `SHELLCHECK_OPTS='-o all -S style -x -a -P SCRIPTDIR' actionlint` - Lints the workflows. Run it only when `.github/workflows/` changed.
23. `git push origin <branch>` - Never run a bare `git push`.
