---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-24_maintainer-tests-run-pytest-from-a-pep723-runner
superseded-by: none
---

# Maintainer Python tests run on unittest through a PEP 723 runner

## Scope

- In scope: the maintainer Python suites that need third-party packages (`scripts/testers/schemas/`, `scripts/testers/validators/`), their runner `scripts/testers/run_unittest.py`, the `unittest-maintainer` gate, and the environment Basedpyright reads for those suites (`scripts/basedpyright-maintainer.mjs`).
- Out of scope: the plugin-script suites under `scripts/testers/<plugin>/`, which already run on unittest through `unittestGate` with the first `python3` on PATH; Node tests; mod tests; plugin evals; plugin files that mention pytest because they describe users' projects.

## Context and problem statement

Nery wants pytest gone from the project and every Python test on unittest. pytest was used only by the two maintainer suites above and their runner `run_pytest.py`; the other seven Python suites in `scripts/testers/` already used unittest. The schema suite needs `jsonschema` and `referencing`, which the bare `python3` that `unittestGate` runs does not have, so those suites still need a runner that declares their dependencies. How do they run on unittest without losing the guarantees the pytest runner gave?

## Decision drivers

- One Python test framework in the repository, from the standard library.
- Keep the pytest runner's guarantees: warnings are errors, and a skip, an expected failure or an unexpected success fails the run.
- unittest passes an empty run, so an empty discovery or an empty parameter list must not pass silently.
- Basedpyright in `all` mode must still resolve the suites' imports from a declared environment.
- No root `pyproject.toml` or virtual environment.

## Considered options

- **unittest through a PEP 723 runner that declares the suites' dependencies**: chosen.
- **The bare-`python3` `unittestGate`**: rejected because it has no `jsonschema` or `referencing`, so the schema suite cannot import.
- **Keep pytest**: rejected by Nery.

## Decision outcome

Chosen option: **unittest through a PEP 723 runner**, because it removes pytest while the dependencies stay declared in the repository, uv keeps their environment outside it, and Basedpyright reads that environment as before.

- The runner discovers each directory with a fresh `TestLoader` and that directory as its top level, runs everything in one suite with warnings as errors (set before discovery and in `TextTestRunner`), and exits non-zero on a failure, a skip, an expected failure, an unexpected success, a directory with no tests or an empty run.
- Each former `pytest.mark.parametrize` is a loop over `subTest`, preceded by an assert that its input list is not empty.

### Consequences

- Good, because pytest leaves the repository's test tooling, and every Python suite uses one framework.
- Good, because every check survives: pytest collected 210 tests; unittest runs 14 tests holding 200 subtests, which is again 210 outcomes, with the same count per former parametrized test (74, 44, 41, 41).
- Bad, because a test directory is put on `sys.path` as its own top level, so test module names must differ across the runner's directories.
- Bad, because the suites carry no PEP 723 header, so a per-file editor or hook check that does not use the runner's environment reports their third-party imports as missing; `scripts/basedpyright-maintainer.mjs` is the authority and resolves them.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A clean suite passes | Scratch suite with one passing test | passed on 2026-10-29: exit 0 | When the runner changes |
| A skip fails the run, including a skipped subtest | Scratch suites with `@unittest.skip` and with `skipTest` inside `subTest` | passed on 2026-10-29: exit 1 for both, ids listed | When the runner changes |
| An expected failure (xfail) fails the run | Scratch suite with `@expectedFailure` that fails | passed on 2026-10-29: exit 1 | When the runner changes |
| An unexpected success (xpass) fails the run | Scratch suite with `@expectedFailure` that passes | passed on 2026-10-29: exit 1 | When the runner changes |
| No tests fails the run | An empty directory, alone and next to a clean one | passed on 2026-10-29: exit 1 for both | When the runner changes |
| A warning fails the run | Scratch test raising `DeprecationWarning` | passed on 2026-10-29: exit 1, the warning raised as an error | When the runner changes |
| An unraisable exception fails the run, as pytest's unraisable-exception check did under `-W error` | Scratch test that leaves a file open | failed on 2026-10-29 (exit 0) in the final review; passed after the runner's `sys.unraisablehook`: exit 1 | When the runner changes |
| A file named like a test that discovery skips fails the run | Scratch `test*.py` in a subfolder without `__init__.py`, and a `*_test.py` file | failed on 2026-10-29 (exit 0) in the final review; passed after the runner compares those files with the loaded modules: exit 1 for both | When the runner changes |
| No arguments is a usage error | The runner with no arguments | passed on 2026-10-29: exit 2 | When the runner changes |
| The converted suites keep their coverage | Subtest count against `run_pytest.py --collect-only` | passed on 2026-10-29: 210 before and after | When a suite changes shape |
| A broken recorded case fails | One case in `cases.json` flipped, then restored | passed on 2026-10-29: exit 1 | When the schema suite changes |
| Basedpyright resolves the suites' imports | `node scripts/basedpyright-maintainer.mjs` | passed on 2026-10-29: 0 errors, 0 warnings in the `run_unittest.py` group | When a suite's dependencies change |

## More information

- Decided by Nery before the session of 2026-10-29, through the plan that this change implements.
- The `unittest` behavior relied on was checked against the Python 3.15 documentation: `discover(start_dir, pattern, top_level_dir)`, whose top level "is only stored for the duration of discover call" since 3.13, `TextTestRunner(warnings=...)`, and `wasSuccessful()`, which "Returns False if there were any unexpectedSuccesses" since 3.4. What's New in Python 3.15 lists no unittest removals.
- Related: ADR_2026-10-24_maintainer-python-entry-points-use-a-uv-shebang, ADR_2026-10-27_maintainer-uv-shebang-drops-pythonsafepath.
