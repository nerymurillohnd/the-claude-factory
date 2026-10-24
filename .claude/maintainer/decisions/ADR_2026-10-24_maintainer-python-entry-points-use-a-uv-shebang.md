---
status: superseded
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-10-24_maintainer-python-shebang-follows-its-dependencies
---

# Maintainer Python entry points run through a PEP 723 uv shebang

## Scope

- In scope: every executable maintainer Python script under `scripts/`, its inline metadata, its executable bit, and how the gates and CI start it.
- Out of scope: plugin scripts, which keep `#!/usr/bin/env python3` and run on the user's `python3`; imported modules, test files, `conftest.py` and package initializers, which stay ordinary modules.

## Context and problem statement

Maintainer scripts ran as `python3 <script>`, on whatever `python3` came first on `PATH`. They run only on the maintainer's machine and in CI, on Python 3.15. How should they pick their interpreter and dependencies, without a root Python project?

## Decision drivers

- The maintainer's Python version, not the user's.
- Dependencies declared in the repository, environments outside it.
- A file beside the script must not shadow a standard module.

## Considered options

- **`#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script` with inline metadata**: chosen.
- **`#!/usr/bin/env -S uv run --script`, as uv's guide shows**: rejected because a `json.py` next to the script was imported in place of the standard module (measured).
- **`python3 -I <script>` from the gate**: rejected because it does not pick Python 3.15 or declare dependencies, and does not protect a script run by path.

## Decision outcome

Chosen option: **the uv shebang with `PYTHONSAFEPATH=1`**, because uv picks Python from `requires-python = "==3.15.*"` and builds the environment from `dependencies`, and `PYTHONSAFEPATH=1` keeps the script's folder off the import path.

- Each entry point declares `requires-python` and `dependencies` (empty for standard-library scripts), is `chmod +x` with the bit kept in Git, and runs by path.
- Python is installed explicitly with `uv python install 3.15`; uv uses only uv-managed interpreters and never downloads one (`UV_PYTHON_PREFERENCE=only-managed`, `UV_PYTHON_DOWNLOADS=manual`), locally and in CI.
- Existing entry points migrate when a task touches them.

### Consequences

- Good, because measured: with `PYTHONSAFEPATH=1` the script ran on Python 3.15.0 and imported `json` from the standard library despite a local `json.py`.
- Bad, because `PYTHONSAFEPATH=1` only keeps the script's folder off the import path; it is not a sandbox.
- Bad, because CI must install uv and Python 3.15 and set the same two uv variables before running a script.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| CI runs an entry point on Python 3.15 with the same uv policy | The `python` job of `validate.yml` | pending | When the first entry point joins a gate |

## More information

- Decided by Nery in the session of 2026-10-24. The first entry point is `scripts/check_plugin_names.py`.
- Related: ADR_2026-10-21_gates-run-installed-tools (CLI tools still run as installed, by bare name), ADR_2026-10-21_ci-installs-latest-tools.
