---
name: verify
description: Runs every quality gate of The Claude Factory repository (script tests, policy checks, catalog sync, claude plugin validate --strict, markdownlint, actionlint) and reports raw results. Use before every commit, before a release, or when asked to verify, validate or check the repo.
allowed-tools:
  - "Bash(node *)"
  - "Bash(npx --yes markdownlint-cli2*)"
  - "Bash(.github/scripts/validate-claude.sh)"
  - "Bash(git diff*)"
  - "Bash(git status*)"
---

# Verify the repository

Run every gate from the repository root. Show the **raw output** of each command; never summarize a failure away.

## Steps

1. Script tests:

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

5. Markdown lint:

   ```bash
   npx --yes markdownlint-cli2@0.23.3
   ```

6. Workflow lint, only when `.github/workflows/` changed: run `actionlint` if installed; otherwise say CI will run it.

## Report

- A table: gate · result (✔/✖) · key line of output.
- For each failure: the root cause and the fix. Fix it at the source — never loosen a check, skip a gate or edit generated blocks by hand.
- Only declare "verified" when every gate shows ✔.
