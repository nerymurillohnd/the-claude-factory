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

## Run in this order after each write or edit

1. Run `ruff check --fix <file>` to lint it and apply the safe fixes.
2. Run `ruff format <file>` to format it.
3. Run `basedpyright -p scripts <file>` to type-check a file under `scripts/`, or `basedpyright <file>` for any other.
4. Fix every finding, then run steps 1 to 3 again until all pass.
5. Read the file again before the next edit.
