# Maintainer Tooling Rules

## Python and uv
- Use Python 3.15 for validation scripts; never add compatibility code for older versions.
- Use uv to manage Python, and install Ruff and Basedpyright through `uv tool`.
- Prefer the Python standard library and avoid unnecessary dependencies.
- Install Python explicitly with `uv python install 3.15`; uv uses only uv-managed interpreters and never downloads one on its own (`UV_PYTHON_PREFERENCE=only-managed`, `UV_PYTHON_DOWNLOADS=manual`), locally and in CI.
- Keep maintainer code and its tests in `scripts/` at the root, never under `.github/`: Basedpyright and other tools skip folders whose name starts with a dot (ADR_2026-10-21_maintainer-scripts-at-root).

## Executable entry points
- Start an executable maintainer Python entry point that needs only the standard library with `#!/usr/bin/env python3`, and run it with the `python3` on `PATH`: the maintainer's machine and CI run uv-managed Python. This applies to maintainer scripts only; plugin scripts follow `plugin-tooling.md`.
- Start an entry point with third-party dependencies with `#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script` on a single line, and declare `requires-python = "==3.15.*"` and its `dependencies` in its inline metadata.
- Mark executable entry points with `chmod +x`, preserve their executable bits in Git, and run them by path.
- Declare script dependencies in PEP 723 inline metadata; never use per-invocation `--with` or a root Python project.
- Let uv manage script environments outside the repository; never create a manually maintained root virtual environment.
- Keep imported modules, test files, `conftest.py`, and package initializers as ordinary Python modules; do not give them independent execution metadata unless they are also standalone entry points.
- Do not restore broad import paths to bypass `PYTHONSAFEPATH=1`.

## Validators
- Inspect plugin metadata and files without importing or executing plugin code, hooks, or subprocesses.
- Reject placeholder-only function bodies using `...`, `pass`, or `raise NotImplementedError` in executable maintainer implementations.
- Allow placeholder declarations only in `.pyi` stubs, `Protocol` classes, `@overload` signatures, and `@abstractmethod` methods.
- Run validators separately against actual marketplace data in read-only mode; exit nonzero on validation failures.

## Type checking
- Do not add a second type checker without an ADR; classify its diagnostics using the diagnostic classes defined in `CLAUDE.md` → Tooling.
- Configure Basedpyright for maintainer code with `typeCheckingMode = "all"` and `failOnWarnings = true`; scope that configuration to maintainer paths.
- Run `uv sync --script <file>` before `uv python find --script <file>`.
- Pass the resolved interpreter to Basedpyright through `--pythonpath`; analyze tests importing pytest against the test runner's environment.
- When the editor or a hook disagrees with the CLI gate, fix the interpreter selection there; never suppress the diagnostic.

## Linting and tests
- Use Ruff for linting and formatting; run `ruff check` and `ruff format --check` as non-mutating gates.
- Use pytest through a PEP 723 runner that declares pytest and the dependencies required by its test suite.
- Test validators, metadata contracts, and structural rules with valid, invalid, and boundary cases.
- Fail the test run when tests or modules are skipped; cover collection-time and execution-time skips.

## CI
- Install the latest release of each tool in CI, except where an ADR pins one.
