---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python code quality

## Formatting and linting

- Format and lint Python with ruff, never black or flake8.
- After editing a Python file, run `ruff format <file>` and `ruff check <file>`, then read the file again before the next edit.
- Before a commit, run `npm run lint:python`.

## Type checking

- Type-check with basedpyright, never mypy or pyright.
- Before a commit, run `npm run typecheck:python`, which checks the root and `scripts/` with their own configurations.

## Findings

- Fix each finding at its cause, never with `# noqa`, `# type: ignore` or `cast()`.
- When a finding is a false positive, show the evidence and ask the owner before suppressing it.

## LSP

- Load the `python-lsp-intelligence:python-lsp-intelligence` skill before refactoring, renaming or deleting Python code.
