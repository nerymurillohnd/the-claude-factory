---
name: verify
description: Runs every quality gate of The Claude Factory repository (script tests, policy checks, catalog sync, claude plugin validate --strict, Biome, shellcheck, shfmt, plugin Python tests and lint, markdownlint, actionlint) and reports raw results. Use before every commit, before a release, or when asked to verify, validate or check the repo.
allowed-tools:
  - "Bash(node *)"
  - "Bash(npx --yes markdownlint-cli2*)"
  - "Bash(npx --yes @biomejs/biome@2.5.15 check --error-on-warnings .)"
  - "Bash(git ls-files -z *)"
  - "Bash(.github/scripts/validate-claude.sh)"
  - "Bash(git diff*)"
  - "Bash(git status*)"
  - "Bash(python3 -m unittest discover *)"
  - "Bash(uvx ruff@0.17.0 *)"
---

# Verify the repository

Run every gate from the repository root. Show the **raw output** of each command; never summarize a failure away.

## Steps

1. Script tests (the LSP hook tests need `shfmt`, `shellcheck`, `ruff`, `basedpyright` on `PATH` and, once, `npm ci --ignore-scripts --prefix plugins/typescript6-lsp-intelligence` and the same for `typescript7-lsp-intelligence`; a missing tool skips its cases, so read the `skipped` count):

   ```bash
   node --test ".github/scripts/tests/*.test.mjs"
   ```

2. Repository policy and catalog:

   ```bash
   node .github/scripts/check-repo.mjs
   node .github/scripts/catalog.mjs --check
   ```

3. Official validator (needs the `claude` CLI):

   ```bash
   .github/scripts/validate-claude.sh
   ```

4. Version bumps against the last pushed state (skip if there is no `origin/main` yet):

   ```bash
   node .github/scripts/check-version-bump.mjs origin/main
   ```

5. JavaScript and JSON format, lint and imports (config in `biome.json`; fix with `--write`, never by loosening the config):

   ```bash
   npx --yes @biomejs/biome@2.5.15 check --error-on-warnings .
   ```

6. Shell scripts, with the shell style in `.editorconfig` and shellcheck's optional checks:

   ```bash
   git ls-files -z '*.sh' | xargs -0 shellcheck -o all -S style -x -a -P SCRIPTDIR
   git ls-files -z '*.sh' | xargs -0 shfmt -d
   ```

7. Plugin Python (the versions CI pins in `validate.yml`; CI also runs these on Linux, macOS and Windows with Python 3.9 and 3.13):

   ```bash
   python3 -m unittest discover -s .github/scripts/tests/skill-diagnostics
   .github/scripts/tests/skill-diagnostics/by_path.sh
   python3 -m unittest discover -s .github/scripts/tests/python-lsp-intelligence
   .github/scripts/tests/python-lsp-intelligence/by_path.sh
   uvx ruff@0.17.0 check plugins .github/scripts
   uvx ruff@0.17.0 format --check plugins .github/scripts
   git ls-files -z 'plugins/*.py' '.github/scripts/tests/*.py' | xargs -0 uvx --from mypy==1.20.2 mypy --python-version 3.9 --strict
   ```

   Repeat the first two lines for every plugin folder under `.github/scripts/tests/`.

8. Markdown lint:

   ```bash
   npx --yes markdownlint-cli2@0.23.3
   ```

9. Workflow lint, only when `.github/workflows/` changed: run `SHELLCHECK_OPTS='-o all -S style -x -a -P SCRIPTDIR' actionlint` if installed; otherwise say CI will run it.

## Report

- A table: gate · result (✔/✖) · key line of output.
- For each failure: the root cause and the fix. Fix it at the source — never loosen a check, skip a gate or edit generated blocks by hand.
- Only declare "verified" when every gate shows ✔.
