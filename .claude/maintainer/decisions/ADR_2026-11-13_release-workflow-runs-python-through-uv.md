---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# release.yml runs the release scripts through uv, not npm run

## Scope

- **In scope:**
  - `.github/workflows/release.yml`
  - the Python target that `ruff.toml` sets for `scripts/release/`
- **Out of scope:**
  - the missing `Validate` workflow
  - every other workflow

## Context and problem statement

`release.yml` called `scripts/release/release-notes.py` by path. Its runner had only `actions/setup-node`, so the script would have run on the runner's OS `python3`.

`ruff.toml` set `scripts/release/**/*.py` to `py312` for that runner. Its comment cited an ADR that does not exist on this branch: ADR_2026-10-27_python-version-is-set-per-scope.

Locally, maintainer Python runs on 3.15 through `uv run` (ADR_2026-11-13_python-3-15-default-and-pinned-in-cloud-setup). Two ways of running it in CI were possible:
- `npm run release:notes`
- `uv run python scripts/release/release-notes.py`

## Decision drivers

- The same Python and interpreter in CI as on the maintainer's machine.
- Each CI step must run on the runner as it is set up.
- Actions pinned by full commit SHA, with no cache in a job that publishes releases.

## Considered options

- **`astral-sh/setup-uv` and `uv run python scripts/release/release-notes.py`**: chosen.
- **`npm run --silent release:notes`**: rejected. `.nvmrc` pins Node 26.13.0, and the Node.js release index (nodejs.org/dist/index.json, read 2026-11-13) lists npm 11.20.0 for both 26.13.0 and 26.13.1. `devEngines` in `package.json` requires npm `^12.2.1` with `onFail: error`, so the step would fail on the runner's npm.
- **Run the script by path on the runner's `python3`**: rejected. That interpreter isn't the maintainer's 3.15, and it bypasses `uv run`.

## Decision outcome

Chosen option: **setup-uv and uv run**, because it runs the script on the project's own Python without depending on the npm that ships with Node.

The setup step:
- uses `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2`, which is v10.3.3
- has `enable-cache: false`
- was pinned from the action repository's tag on 2026-11-13. The commit is dated 2026-10-28, past the 14-day cooldown for a major version that `dependabot.yml` sets.

`ruff.toml` now targets 3.15 for `scripts/release/`.

### Consequences

- Good, because CI and local runs use the same script, on the same Python.
- Good, because `actionlint` and `zizmor --offline` report nothing on the changed workflow (2026-11-13).
- Bad, because the CI step doesn't go through the npm script, unlike every local maintainer command (ADR_2026-11-12_npm-scripts-are-the-single-entry-point).

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The workflow passes its linters | `npm run lint:workflows` | 2026-11-13: no findings | Every workflow change |
| The release step works on the runner | The first `workflow_dispatch` or `Validate`-triggered run of `release.yml` | pending | The first release after this change |
| npm still fails `devEngines` on the runner | The npm version in the `setup-node` log, compared with `devEngines` | pending | When `.nvmrc` or `devEngines` changes; switch to `npm run` once they agree |
