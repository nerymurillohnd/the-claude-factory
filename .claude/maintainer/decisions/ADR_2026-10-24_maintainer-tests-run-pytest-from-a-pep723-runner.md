---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Maintainer Python tests run on pytest through a PEP 723 runner

## Scope

- In scope: the Python tests of maintainer code and of plugin scripts under `scripts/tests/`, the runner script that declares pytest, and the way Basedpyright resolves `import pytest`.
- Out of scope: Node tests (`node --test`), mod tests (`claude plugin test`), plugin evals, and the plugins' own runtime, which never depends on pytest.

## Context and problem statement

Python tests used `unittest`. Validators need many valid, invalid and boundary cases, which pytest expresses with less code. pytest is not in the standard library, and the repository has no root `pyproject.toml` or virtual environment. How do the tests get pytest, and how does Basedpyright see its types?

## Decision drivers

- Valid, invalid and boundary cases for every validator and structural rule.
- No root Python project or manually maintained virtual environment.
- Basedpyright in `all` mode must resolve `import pytest`; a missing import is never suppressed.
- A skipped test fails the run.

## Considered options

- **pytest declared in a PEP 723 runner script**: chosen.
- **unittest**: rejected because cases need more code; it stays for unmigrated tests until they are touched.
- **pytest as a `uv tool`**: rejected because the tool's environment is isolated, so Basedpyright reports `import pytest` as `reportMissingImports` (measured).
- **pytest per invocation with `uv run --with pytest`**: rejected because the dependency is not declared in the repository.
- **A root `pyproject.toml` or virtual environment**: rejected because maintainer dependencies stay out of the repository root.

## Decision outcome

Chosen option: **a PEP 723 runner**, because the dependency is declared in the repository, uv manages its environment outside it, and Basedpyright reads that environment.

- Run `uv sync --script <runner>`, then pass `uv python find --script <runner>` to Basedpyright as `--pythonpath`. Before the sync, the find returns the base interpreter, without pytest (measured).
- The runner fails the run on any skip, at collection or at execution.

### Consequences

- Good, because measured: with the runner's interpreter, Basedpyright in `all` mode resolves `import pytest` and types `pytest.raises`.
- Bad, because the first run of the runner resolves pytest from the network; later runs use uv's cache.
- Bad, because the editor and hooks need the same interpreter selection as the CLI gate; the gate is the authority.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The runner fails on a skipped test | A test skipped on purpose | passed on 2026-10-24: `scripts/tests/run_pytest.py` exits 1 with "1 passed, 1 skipped" and 0 with no skip | When the runner changes |
| Basedpyright resolves pytest in the gate | `basedpyright --pythonpath "$(uv python find --script <runner>)" scripts/tests` | partly: on 2026-10-24 the runner itself checks with 0 errors in all mode; no gate runs it and `scripts/tests/schemas/` is broken (DEBT-007) | When a pytest suite joins a gate |

## More information

- Decided by Nery in the session of 2026-10-24. The runner is not written yet; the first one ships with `scripts/check_plugin_names.py`.
- Related: ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang, ADR_2026-10-24_basedpyright-is-the-only-python-type-checker.
