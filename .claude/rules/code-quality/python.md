---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python

- Load the `python-lsp-intelligence:python-lsp-intelligence` skill.
- Use only ruff and basedpyright; never black, flake8, mypy or pyright.
- Fix every finding before moving on; never leave one as debt.
- Add `# noqa`, `# type: ignore` or `cast()` only for a proven false positive, with its reason and the owner's approval.

## After each write or edit, run in order

1. Lint and apply the safe fixes: `ruff check --fix <file>`.
2. Format: `ruff format <file>`.
3. Type-check: `basedpyright -p scripts <file>` for a file under `scripts/`; `basedpyright <file>` for any other.
4. Fix every finding, then repeat steps 1 to 3 until all pass.
5. Read the file again before the next edit.
