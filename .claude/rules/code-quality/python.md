---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python code quality

Use ruff and basedpyright only, never black, flake8, mypy or pyright.

## After editing a Python file

- Format it: `ruff format <file>`.
- Lint it and apply the safe fixes: `ruff check --fix <file>`.
- Type-check a file under `scripts/`: `basedpyright -p scripts <file>`.
- Type-check any other Python file: `basedpyright <file>`.
- Read the file again before the next edit: `ruff format` and `ruff check --fix` rewrite it.

## Before a commit

- Check every Python file: `npm run lint:python`.
- Type-check every Python file: `npm run typecheck:python`.

## Findings

- Fix each finding at its cause, never with `# noqa`, `# type: ignore` or `cast()`.
- When a finding is a false positive, show the evidence and ask the owner before suppressing it.

## LSP

- Load the `python-lsp-intelligence:python-lsp-intelligence` skill before refactoring, renaming or deleting Python code.
