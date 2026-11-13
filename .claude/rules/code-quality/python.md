---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python code quality

Use ruff and basedpyright only, never black, flake8, mypy or pyright.

## Order of work on a Python file

1. Before changing a symbol's name, signature or existence, find every use with the LSP tool, as `lsp.md` sets.
2. Edit the file, then fix the LSP diagnostics Claude Code reports for it.
3. Apply the safe lint fixes: `ruff check --fix <file>`. Run it before formatting, because its fixes can leave code that needs reformatting.
4. Format: `ruff format <file>`. It adds no new lint findings, because `ruff.toml` turns off the rules that conflict with the formatter.
5. Fix by hand any finding step 3 could not fix, then repeat steps 3 and 4.
6. Type-check last, on the final code: `basedpyright -p scripts <file>` for a file under `scripts/`, `basedpyright <file>` for any other.
7. Read the file again before the next edit: steps 3 and 4 rewrite it.

## Before a commit

- Check every Python file: `npm run lint:python`.
- Type-check every Python file: `npm run typecheck:python`.

## Findings

- Fix each finding at its cause, never with `# noqa`, `# type: ignore` or `cast()`.
- When a finding is a false positive, show the evidence and ask the owner before suppressing it.

## LSP

- Load the `python-lsp-intelligence:python-lsp-intelligence` skill before refactoring, renaming or deleting Python code.
