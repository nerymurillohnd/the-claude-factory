---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: ADR_2026-11-12_uv-project-pins-maintainer-python-tools
superseded-by: none
---

# Install the maintainer Python tools as pinned uv tools and run maintainer scripts with the .venv Python

## Scope

The npm scripts in the root `package.json`, the `dev` group of `pyproject.toml`, `uv.lock`, `scripts/*.py` and `scripts/pyrightconfig.json`. Maintainer scope. Plugin scripts are out of scope.

## Context and problem statement

ADR_2026-11-12_uv-project-pins-maintainer-python-tools put ruff, basedpyright and zizmor in the uv `dev` group and ran them with `uv run --locked`. The owner runs these tools as uv tools on PATH and wants maintainer commands to call them bare. The new maintainer scripts need Python 3.15 and one package, ruamel.yaml, because the standard library has no YAML parser. In this cloud session, bare `python3` is 3.13.18, not 3.15.

## Decision drivers

- Call tools by their bare name, as the owner does in the terminal.
- One place that states each tool's version.
- Maintainer scripts run on Python 3.15 whatever `python3` points to.

## Considered options

- **ruff 0.17.4, basedpyright 1.40.2, zizmor 1.32.0 and check-jsonschema 0.39.0 installed with `uv tool install`, pinned in the `tools:install` npm script and called bare; the `dev` group keeps only `ruamel.yaml==0.19.1`; npm scripts run `scripts/*.py` with `.venv/bin/python`; `basedpyright -p scripts` checks them at Python 3.15**: chosen.
- **Keep the tools in the `dev` group with `uv run --locked`**: rejected by the owner, who prefers bare commands.
- **Run maintainer scripts with bare `python3`**: rejected because `python3` is not 3.15 on every machine (3.13.18 in this cloud session).

## Decision outcome

Chosen option: **pinned uv tools called bare, and the .venv Python for maintainer scripts**, because commands match how the owner works, and the scripts get the right Python and their one dependency from the lock.

### Consequences

- Good, because `npm run lint:python`, `lint:workflows`, `lint:github` and `typecheck:python` passed with the bare tools on 2026-11-12.
- Bad, because Dependabot does not read `tools:install`, so the four tool versions are bumped by hand.
- Bad, because only ruff guards against a different installed version (`required-version` in `ruff.toml`); for the others, `tools:install` states the expected version.
- Bad, because CI must run `npm run tools:install` and `uv sync --locked` before the checks.

## More information

- This record also replaces the clause "Python tools run with `uv run --locked`" of ADR_2026-11-12_npm-scripts-are-the-single-entry-point, whose decision, npm scripts as the single entry point, still holds.
- Dependabot's `uv` entry now keeps `uv.lock` current, under ADR_2026-11-12_dependabot-cooldown-and-groups.
- Sources: uv docs, "Tools" (`uv tool install`); basedpyright docs, configuration (`extends`, `venvPath`, `venv`); PyPI release data for each pinned version, read on 2026-11-12.
- The owner decided this in this session, on 2026-11-12.
