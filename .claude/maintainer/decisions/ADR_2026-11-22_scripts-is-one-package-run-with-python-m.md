---
status: accepted
date: 2026-11-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# scripts/ is one Python package, run with python -m from the repository root

## Scope

The layout of `scripts/` (`checks/`, `release/`, `generators/`, `tests/`), how `package.json`, the Git pre-commit gate and the Release workflow start maintainer Python, and `pyproject.toml`'s basedpyright environment for `scripts/`.

## Context and problem statement

Each maintainer CLI had a shim file that put `scripts/` on `sys.path` and ran its module through `runpy`. Each needed a Ruff N999 exception, and each module counted parent folders to find the repository root. How should npm start maintainer Python?

## Decision drivers

- One way to run every maintainer module, with no per-tool shim.
- Absolute imports, as Ruff's `ban-relative-imports = "all"` requires.
- No build step: nothing here is installed or shipped.

## Considered options

- **Make `scripts/` one package and run modules with `uv run python -m scripts.<folder>.<module>` from the root**: chosen.
- **Keep one shim file per CLI**: rejected because the shims, their `sys.path` and `runpy` setup and the N999 ignores are boilerplate the package removes.
- **Install the project as a package with `[project.scripts]` entry points**: rejected because it adds a build backend and an editable install for a repository that ships nothing. uv's build backend also supports several root modules only as a structure it does not recommend.

## Decision outcome

Chosen option: **one package run with `python -m` from the root**, because npm, CI and the pre-commit gate already run from the repository root, where `scripts` imports as a package.

### Consequences

- Good, because seven shim files and their Ruff exceptions are gone, and `scripts.REPO_ROOT` replaces each module's own count of parent folders.
- Good, because tests run with `unittest discover -s scripts/tests -t .` and import the package absolutely.
- Bad, because basedpyright needs `extraPaths = ["."]` in the `scripts` execution environment, which otherwise resolves imports from `scripts/`.
- Bad, because a caller outside the root must set `PYTHONPATH` to the tree's root and use `python -P`, as `scripts/checks/pre-commit-gate.sh` and `scripts/release/publish-releases.sh` do.

## More information

The owner approved this layout in the session that reorganized `scripts/` on branch `chore/scripts-hygiene`. A probe in a throwaway worktree confirmed it before the move: the module started, unittest discovery passed, and basedpyright reported 0 errors on 159 files once `extraPaths = ["."]` was set. `.claude/rules/architecture/scripts.md` and `.claude/rules/npm-and-uv.md` hold the resulting rules. Related record: ADR_2026-11-22_maintainer-scripts-keep-python-and-node.
