---
status: accepted
date: 2026-11-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Maintainer scripts keep Python and Node instead of consolidating on one runtime

## Scope

The maintainer tooling under `scripts/`, `package.json`, `pyproject.toml` and the CI setup action. Plugins under `plugins/` are out of scope: they run on users' machines with their own declared prerequisites.

## Context and problem statement

The maintainer tooling runs on two runtimes: Python for its logic and Node as the npm entry point. The owner asked whether keeping both is worth it, or whether to migrate the maintainer scripts to one runtime.

## Decision drivers

- A consolidation should remove a runtime from the repository, not only move code between them.
- The repository must still lint, type-check and test the Python and the JavaScript and TypeScript that plugins ship.
- A rewrite must not change what the existing checks report.

## Considered options

- **Keep Python for the maintainer logic and Node as the npm entry point**: chosen.
- **Consolidate on Node**: rejected because it means rewriting about 4,580 source lines and 4,190 test lines (347 tests). Three skill-lint rules read Python code with `ast` and `tomllib`, which Node cannot parse, so `python3` would stay anyway, and Ruff and basedpyright stay for the plugins' Python.
- **Consolidate on Python**: rejected because it removes only `scripts/generators/plugin-icons.mjs`. Node, npm, Biome (which also lints Markdown, JSON and YAML) and tsc stay for the mods, the tailwind MCP server and `devEngines`.

## Decision outcome

Chosen option: **keep Python for the maintainer logic and Node as the npm entry point**, because neither consolidation removes a runtime from the repository: each would only add migration cost and risk.

### Consequences

- Good, because the 347 maintainer tests and every check keep their current behavior.
- Good, because npm stays the single entry point: every maintainer command is an npm script.
- Bad, because maintainers keep two toolchains configured: Biome and tsc beside Ruff and basedpyright.

## More information

The owner decided in the session that reorganized `scripts/` on branch `chore/scripts-hygiene`. The evidence came from read-only research of the scripts, the plugins' languages and the CI setup action. Related records: ADR_2026-11-22_maintainer-python-keeps-a-uv-project-for-ruamel-yaml and ADR_2026-11-22_scripts-is-one-package-run-with-python-m.
