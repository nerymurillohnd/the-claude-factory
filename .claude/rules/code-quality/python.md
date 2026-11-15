---
paths:
  - "**/*.py"
  - "/ruff.toml"
  - "/pyrightconfig.json"
  - "scripts/pyrightconfig.json"
---

# Python

- Fix every finding at its cause, never its symptom. Never lower, relax, bypass or route around a gate, test, check or script to make it pass, and never add a suppression: no `# noqa`, `# type: ignore`, `cast()`, `Any` or loosened setting in `ruff.toml` or `pyrightconfig.json`.
- Fix every finding the `python-lsp-intelligence` plugin's post-edit hook reports after an edit before the next edit; the hook runs `ruff check --fix`, `ruff format` and `basedpyright`, in that order.
- Read the file again after each edit, because the hook rewrites it.
- When no hook message follows an edit, run `ruff check --fix <file>`, `ruff format <file>` and `basedpyright <file>` yourself, in that order; under `scripts/`, run `basedpyright -p scripts <file>`.
