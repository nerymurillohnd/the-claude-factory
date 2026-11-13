---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python

- Load the `python-lsp-intelligence:python-lsp-intelligence` skill whenever you write, edit or review Python.
- Fix every issue a check reports before the next step or task; never leave it as debt.

## Gotchas

- Run `ruff check --fix` before `ruff format`: its fixes can leave code that needs reformatting.
- Type-check files under `scripts/` with `-p scripts`: that configuration points basedpyright at `.venv`.
- Use only ruff and basedpyright, never black, flake8, mypy or pyright, even when they are installed.
- Add `# noqa`, `# type: ignore` or `cast()` only for a proven false positive, with its reason and the owner's approval.

## After writing or editing a Python file, in this order

1. Run `ruff check --fix <file>` to apply the safe lint fixes; fix the rest by hand.
2. Run `ruff format <file>` to format it.
3. Run `basedpyright <file>`, or `basedpyright -p scripts <file>` under `scripts/`, to type-check the final code.
4. Read the file again before the next edit, because steps 1 and 2 rewrite it.

## Before a commit

1. Run `npm run lint:python` to check every Python file.
2. Run `npm run typecheck:python` to type-check every Python file.
