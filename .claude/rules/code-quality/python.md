---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python

- Fix every finding the `python-lsp-intelligence` plugin's post-edit hook reports after an edit before the next edit; the hook runs `ruff check --fix`, `ruff format` and `basedpyright`, in that order.
- Read the file again after each edit, because the hook rewrites it.
- Add `# noqa`, `# type: ignore` or `cast()` only with the owner's approval, and write the reason beside it.
- When no hook message follows an edit, run `ruff check --fix <file>`, `ruff format <file>` and `basedpyright <file>` yourself, in that order; under `scripts/`, run `basedpyright -p scripts <file>`.
