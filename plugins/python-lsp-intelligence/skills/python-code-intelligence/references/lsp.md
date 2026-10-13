# Python (basedpyright)

Server: `basedpyright-langserver --stdio` from the `basedpyright-lsp` plugin, for `.py`, `.pyi`, `.pyw`.
Binary installed with `uv tool install basedpyright`. Behaviour below verified 2026-09-29 with
basedpyright 1.40.1 on a fixture project.

## Observed behaviour

| Situation | What the server returns | Meaning |
|---|---|---|
| First `findReferences` of a session | Definition only (`Found 1 reference`) | Warm-up; the repeat returned the full set |
| `character` inside the `def` keyword or on whitespace | `No references found` | Wrong position, not "unused" |
| Aliased import `from m import f as g` | `findReferences` on `f` lists the import line, **not** the uses of `g` | A rename changes the import line only; to find alias uses, run `findReferences` on `g` |
| File changed by Bash/codegen while the server runs | Old counts, even after re-query | Stale index; Grep/Read the changed file |
| Target outside the session working directory | Definition only, stable across repeats | Scope limit, not "unused" |

## Python blind spots (static references LSP never reports)

Verified: each case below returned only the definition.

- **pytest fixtures** requested by parameter name (`def test_x(sample_prices)`) — Grep the fixture name in `tests/` and `conftest.py`
- **Dynamic lookup**: `getattr(module, "name")`, `importlib.import_module("pkg.mod")`, string-based registries
- **Entry points**: `[project.scripts]` / `[project.entry-points]` in `pyproject.toml`, `setup.cfg` console scripts

Also treat as blind spots (by the same mechanism): `__all__` string lists, Django/Flask string references
(`INSTALLED_APPS`, `urls.py` string views, `settings` dotted paths), Celery task names, `mock.patch("pkg.mod.name")` targets,
and names built with f-strings.

Before declaring a Python symbol unused, Grep its bare name across `*.py`, `*.toml`, `*.cfg`, `*.ini`, `*.yaml`, `*.yml`,
`*.json`, and `*.md`.

## Diagnostics caveat

For PEP 723 scripts run with `uv run`, dependencies live in an ephemeral env the server does not see, so
`reportMissingImports` and cascading `reportUnknown*` warnings in the LSP can be false positives. The
`basedpyright-lsp` quality gate (`ruff-basedpyright.sh`) resolves the script env (`uv sync --script` + `--pythonpath`) and is authoritative.
