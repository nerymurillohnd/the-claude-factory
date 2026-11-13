---
paths:
  - "scripts/**"
---

# Maintainer scripts

Scripts that check, generate and release the marketplace. No plugin calls them and none ships to users; a plugin's runtime files (hook handlers, skill scripts, MCP and LSP servers) stay inside that plugin.

## Where a new script goes
- Put a check that fails on a defect in a repository file (a schema, required files, agreement between manifests, catalog and READMEs) in `validators/`, as `skill-lint.py` and its `skill_lint/` package do.
- Put a check that looks beyond the file, such as whether a plugin name is free or a URL resolves, in `checkers/`.
- Put a script that writes repository files (catalog, marketplace, plugin scaffold, plugin icons) in `generators/`, with icon sources at `generators/plugin-icons/<plugin>.svg`.
- Put version bumps, the bump check, release notes and the post-release install check in `release/`. Write them for Python 3.12 and the standard library: `release.yml` runs them by path on the runner's `python3`, and `ruff.toml` targets 3.12 there.
- Put one JSON Schema per file shape in `schemas/`, for the validators to read.
- Put tests in `testers/`, mirroring the package under test (`testers/skill_lint/` tests `validators/skill_lint/`), in files named `test_*.py`.
- Put type stubs for a dependency without usable types in `typings/<package>/`.
- Keep `sync-labels.py`, `check-github-files.py` and `pyrightconfig.json` at the root of `scripts/`.
- Ask the owner before creating a subfolder this list does not name.

## Working here
- Look up a script in `.claude/architecture/refactor.md` before writing it, and rebuild a planned script to current official practice instead of copying it from `main`.
- Delete a subfolder's `.gitkeep` in the same commit as its first script.
- After each change, run `npm run lint:python`, `npm run typecheck:python` and `npm run test:scripts`, and fix each finding instead of suppressing it.
