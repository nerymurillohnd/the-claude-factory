---
status: accepted
date: 2026-11-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Maintainer Python keeps a uv project for its one dependency, ruamel.yaml

## Scope

`pyproject.toml`'s `dev` dependency group, `uv.lock`, `.venv`, the `setup:python` npm script and the `typings/ruamel/yaml/` stubs. The uv tools (ruff, basedpyright, zizmor, check-jsonschema) are out of scope: they are pinned in the `tools:<tool>` npm scripts and need no project environment.

## Context and problem statement

The owner pointed out that ruff and basedpyright run as global uv tools, so the repository does not need a project environment for them. The uv project exists for one dependency of the maintainer scripts, `ruamel.yaml`, plus the Python version in `.python-version`. Is that one dependency worth a lockfile, a `.venv` and a `uv sync` step?

## Decision drivers

- `scripts/checks/frontmatter_lint/` checks how a value is written, such as its quote style, through `CommentedMap` and `DoubleQuotedScalarString`, not only what it holds.
- `.claude/rules/code-quality/python.md` forbids turning off a basedpyright rule to make a check pass.
- The dependency should stay pinned by hash and visible to Dependabot.

## Considered options

- **Keep the uv project with `ruamel.yaml` in the `dev` group**: chosen.
- **Declare `ruamel.yaml` inline in each script (PEP 723) and drop `uv.lock` and `.venv`**: rejected because basedpyright can't see a script's uv environment, and the lockfile's hash pin and Dependabot updates would be lost.
- **Drop `ruamel.yaml` for the standard library**: rejected because no standard-library parser keeps quote styles and comments, so `frontmatter_lint` would lose the checks it exists for.

## Decision outcome

Chosen option: **keep the uv project with `ruamel.yaml` in the `dev` group**, because without the `.venv`, basedpyright run on the three files that import ruamel reports 9 `reportMissingModuleSource` errors even with the stubs, and silencing them is forbidden.

### Consequences

- Good, because `ruamel.yaml` stays pinned by hash in `uv.lock` and Dependabot proposes its upgrades.
- Good, because basedpyright type-checks the scripts against the installed package.
- Bad, because a fresh setup still runs `uv sync --locked` and keeps a `.venv` for one package.

## More information

The owner decided in the session that reorganized `scripts/` on branch `chore/scripts-hygiene`. The 9-error probe ran `basedpyright --pythonpath ~/.local/bin/python3 --outputjson` on `scripts/check-github-files.py`, `scripts/validators/frontmatter_lint/checks.py` and `scripts/validators/skill_lint/frontmatter.py`, the paths those files had before the reorganization. With the `.venv`, the same files report 0 errors. Related record: ADR_2026-11-22_maintainer-scripts-keep-python-and-node.
