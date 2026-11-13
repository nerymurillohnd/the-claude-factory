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
- Put version bumps, the bump check, release notes and the post-release install check in `release/`. Their Python runs on the maintainer Python through `uv run`, in `release.yml` too (ADR_2026-11-13_release-workflow-runs-python-through-uv).
- Put one JSON Schema per file shape in `schemas/`, for the validators to read.
- Put tests in `testers/`, mirroring the package under test (`testers/skill_lint/` tests `validators/skill_lint/`), in files named `test_*.py`.
- Put type stubs for a dependency without usable types in `typings/<package>/`.
- Keep `sync-labels.py`, `check-github-files.py` and `pyrightconfig.json` at the root of `scripts/`.
- Ask the owner before creating a subfolder this list does not name.

## Working here
- Look up a script in `.claude/architecture/refactor.md` before writing it, and rebuild a planned script to current official practice instead of copying it from `main`.
- Delete a subfolder's `.gitkeep` in the same commit as its first script.
- After each change, run `npm run lint:python`, `npm run typecheck:python` and `npm run test:scripts`, and fix each finding instead of suppressing it.
- Start every new `.py` file under `validators/` and `testers/` with `#!/usr/bin/env python3` and give it mode 100755 (`chmod +x`, then `git add`), as every existing one has; ruff's EXE rules fail a file whose shebang and mode disagree.
- Import package modules absolutely (`from validators.skill_lint.model import Finding`): `ruff.toml` bans relative imports, and a bare `import skill_lint` fails at runtime.
- Type ruamel.yaml through the local stubs in `typings/ruamel/yaml/`: add each new ruamel member a script uses to them, and check them against the installed version when `uv.lock` bumps ruamel.yaml.
- Write the failing test first, then the code, and confirm the test fails without the change.
