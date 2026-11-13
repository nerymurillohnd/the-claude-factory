---
paths:
  - "scripts/**"
---

# Maintainer scripts (`scripts/`)

The maintainer scripts that check, generate and release the marketplace. No plugin calls them and none ships to users: a plugin's runtime files (hook handlers, skill scripts, MCP and LSP servers) stay inside that plugin.

## Where each script goes
- `validators/`: checks that fail on a defect in a repository file, such as a schema, required files, or consistency between manifests, catalog and READMEs. Holds `skill-lint.py` (entry point) and the `skill_lint/` package.
- `checkers/`: checks that look beyond the file itself, such as `check-plugin-name`, `markdown-urls`, `reference-pages` and `fetch-github-mod` (all pending).
- `generators/`: scripts that write repository files, such as `catalog`, `marketplace`, `scaffold-plugin` and `plugin-icons`. Icon sources go in `generators/plugin-icons/<plugin>.svg`.
- `release/`: version bumps, the bump check, release notes and the post-release install check. `.github/workflows/release.yml` runs these by path on the runner's `python3`, so ruff targets Python 3.12 here (`ruff.toml`, `per-file-target-version`); keep their code within 3.12 and the standard library.
- `schemas/`: one JSON Schema per file shape, read by the validators.
- `testers/`: the `unittest` tests. Mirror the package under test (`testers/skill_lint/` tests `validators/skill_lint/`) and name files `test_*.py`.
- `typings/`: local type stubs for basedpyright (`ruamel/`); add a stub here when a dependency ships no usable types.
- Root: `sync-labels.py` (`npm run labels:sync`), `check-github-files.py` (`npm run lint:github`) and `pyrightconfig.json`, which type-checks `scripts/` at Python 3.15 from `.venv`.

## Working here
- Before adding a script, find its entry and status in `.claude/architecture/refactor.md`. A pending script is rebuilt to current official practice, never copied from `main`.
- When the right subfolder is unclear, ask the owner instead of creating a new one.
- An empty subfolder keeps its `.gitkeep`; delete the `.gitkeep` with the first script that lands there.
- Run `npm run lint:python`, `npm run typecheck:python` and `npm run test:scripts` after each change, and fix every finding without suppressing it.
