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
- Run `basedpyright -p scripts <file>` under `scripts/`.

## Annotations

Write annotations that run unchanged on Python 3.12 through 3.15:

- Leave out `from __future__ import annotations`: Python 3.14 deprecated it, for removal after 3.13's end of life. The maintainer scripts under `scripts/` that still use it wait for their own migration, so keep the import when you edit one of them for another reason.
- Define a name before the annotations that use it, so they need no quotes.
- Quote a forward reference you can't avoid, such as a class naming itself in a field (`list["Node"]`): 3.12 and 3.13 evaluate annotations when the definition runs, so an unquoted forward name raises `NameError` there.
- Write type aliases with the `type` statement (`type Surface = Literal[...]`), whose value is evaluated only when used, not with `TypeAlias` or a plain assignment.
