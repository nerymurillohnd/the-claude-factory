---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang
superseded-by: none
---

# Maintainer Python shebang follows the script's dependencies

## Scope

- In scope: every executable maintainer Python script under `scripts/`, its shebang, its inline metadata and its executable bit.
- Out of scope: plugin scripts, which keep `#!/usr/bin/env python3` and run on the user's `python3` (`.claude/rules/plugin-tooling.md`); imported modules, test files, `conftest.py` and package initializers, which stay ordinary modules.

## Context and problem statement

ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang gave every maintainer entry point the uv shebang, standard-library scripts included, with an empty `dependencies` list. On the maintainer's machine the `python3` on `PATH` is already uv-managed Python 3.15, and the repository is not a Python environment: no `pyproject.toml` and no virtual environment. For a script with no dependencies, uv has nothing to resolve. Which shebang should a maintainer script carry?

## Decision drivers

- A standard-library script needs no environment to resolve, and the `python3` on `PATH` is already the maintainer's 3.15.
- A script with third-party dependencies must state them, and must run and type-check on its own.
- The repository has no Python project to hold dependencies.

## Considered options

- **`#!/usr/bin/env python3` by default; `#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script` with PEP 723 inline metadata only for a script that needs third-party dependencies**: chosen.
- **The uv shebang for every entry point** (ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang): rejected because it adds a uv layer and an empty metadata block to scripts that need neither.
- **`#!/usr/bin/env python3` for every script, with the gate runner supplying dependencies through `uv run --no-project --with …`**: rejected because a script with dependencies would no longer run on its own (`./script.py` fails with `ModuleNotFoundError`), and its dependency contract would live outside the file. Basedpyright works this way: `sys.executable` inside `uv run --with` gave an interpreter with the dependencies, and `lsp-json-schema.py` and `plugin-json-schema.py` checked with `0 errors`.

## Decision outcome

Chosen option: **the shebang follows the dependencies**, because a standard-library script runs directly on the uv-managed `python3`, and a script with dependencies carries its own contract and runs alone by path.

- A standard-library entry point starts with `#!/usr/bin/env python3`, has no inline metadata, is `chmod +x` with the bit kept in Git, and runs by path.
- An entry point with third-party dependencies keeps the uv shebang with `PYTHONSAFEPATH=1`, declares `requires-python = "==3.15.*"` and its `dependencies` in inline metadata, and is type-checked with `uv sync --script` and `uv python find --script`.
- The same rule is recorded for every project on this machine in `~/.claude/ENVIRONMENT.md`.

### Consequences

- Good, because the four standard-library validators (`plugin-names-consistency.py`, `readme-catalog-consistency.py`, `plugin-required-files.py`, `plugin-versions-consistency.py`) run as `./script.py` on Python 3.15.0 and pass ruff and basedpyright.
- Good, because the four schema validators declare only what they use (`jsonschema`, `referencing`, `rfc3986-validator`) and pass ruff and basedpyright in all mode against `uv python find --script`.
- Bad, because a standard-library script loses `PYTHONSAFEPATH=1`: a file named like a standard module beside it can shadow that module.
- Bad, because a standard-library script now depends on the first `python3` on `PATH` being 3.15; nothing in the file bounds the version.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| CI runs a standard-library entry point on Python 3.15 | The `python` job of `validate.yml` once a validator joins a gate | pending | When the first validator joins a gate |

## More information

- Decided by Nery in the session of 2026-10-24.
- Rules updated in the same session: `.claude/rules/maintainer-tooling.md` → Executable entry points, and `.claude/CLAUDE.md` → Migration.
