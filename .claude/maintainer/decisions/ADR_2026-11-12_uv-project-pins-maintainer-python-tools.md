---
status: superseded
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: ADR_2026-11-12_maintainer-tools-as-pinned-uv-tools
---

# Pin the maintainer Python tools with a non-package uv project

## Scope

Root `pyproject.toml`, `uv.lock` and `.python-version`, maintainer scope only. Plugin scripts keep their PEP 723 inline metadata and are out of scope.

## Context and problem statement

Ruff and basedpyright were installed as loose global binaries, so nothing fixed their versions across machines or CI; `required-version` in `ruff.toml` only set a floor. The repository had no `pyproject.toml` or `uv.lock`, so `uv sync --locked` failed. The owner asked whether a uv lock would let plugin scripts drop their PEP 723 dependencies.

## Decision drivers

- Exact, reproducible tool versions locally and in CI.
- Keep the maintainer scope and the plugin scope separate.
- npm stays the entry point; uv runs the Python tools.

## Considered options

- **A `pyproject.toml` with no build system, `tool.uv.package = false`, a `dev` dependency group pinning ruff 0.17.4, basedpyright 1.40.2 and zizmor 1.32.0, a committed `uv.lock`, and `uv run --locked`**: chosen.
- **Keep global binaries**: rejected because versions drift.
- **Drop PEP 723 from plugin scripts and rely on the repository lock**: rejected because plugin scripts run on users' machines, where this lock does not exist. uv ignores the surrounding project when it runs a script with inline metadata.

## Decision outcome

Chosen option: **a non-package uv project with a locked dev group**, because it pins the tools exactly and leaves the plugins' own metadata untouched.

### Consequences

- Good, because `uv sync --locked` and `uv lock --check` pass, and `--locked` fails on a stale lock instead of rewriting it.
- Good, because Dependabot supports the `uv` ecosystem, so the lock can be kept current.
- Bad, because `uv run` does not sync on its own in every case; scripts pass `--locked` explicitly.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The lock matches pyproject.toml | `uv lock --check` | Passed on 2026-11-12 | Each tool bump |
| Dependabot updates uv.lock | A `uv` entry in `.github/dependabot.yml` | Added on 2026-11-12; `check-jsonschema --builtin-schema vendor.dependabot` passed | First Dependabot run |

## More information

- Sources: docs.astral.sh/uv, "Configuring projects", "Managing dependencies", "Locking and syncing" and "Running scripts"; GitHub docs, Dependabot supported ecosystems (`uv`).
- Commit: a3e35ec.
