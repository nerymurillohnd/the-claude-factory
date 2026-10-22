---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# CI checks the maintainer tooling and the plugins' structure; plugin behavior and plugin code analysis stay local

## Scope

- In scope: which gates of `scripts/gates.mjs` run in `.github/workflows/validate.yml` (groups `policy`, `python`, `claude`, `lint`) and which run only on the maintainer's machine (group `local`); the move of the plugins' Node tests into `scripts/tests/<plugin>/`; `claude plugin test` leaving CI.
- Out of scope: `evals.yml`, which keeps running the evals of the changed plugins that have them, and `release.yml`.

## Context and problem statement

CI ran a mix: some plugin behavior (the TypeScript and Bash hook tests, `claude plugin test` for mods), some plugin code analysis (ruff and mypy on `plugins/`), and none of the plugins' Python tests since ADR_2026-10-20_retire-cross-os-python-ci-job. A proposal to bring those tests back to CI raised the question of what CI should prove at all. A plugin's behavior depends on the interpreter, tools and versions of whoever installs it, which CI does not reproduce: the mod tests pass on the CI pin of Claude Code 2.1.304 and fail on 2.1.307. What should CI check?

## Decision drivers

- Nothing in CI may judge plugins by an environment their users do not have.
- What is ours (the scripts and their tests) and what no machine changes (manifests, policy, catalog, versions) must still be checked on every push, because `release.yml` publishes after `Validate` passes on `main` and nobody reviews in between.
- Plugin behavior is proven locally before the push, and by evals for the plugins that have them, which run isolated.

## Considered options

- **CI runs the maintainer tooling and the plugins' structure; behavior and plugin code analysis stay local**: chosen.
- **Bring the plugins' Python tests and `by_path.sh` back to CI on Linux**: rejected because one runner's interpreter proves nothing about the users' and the result is already proven locally.
- **CI runs nothing about plugins**: rejected because a push made without the local gates would then publish an invalid manifest or an unbumped version.

## Decision outcome

Chosen option: **maintainer tooling and plugin structure in CI**, because it keeps the release safety net and drops every check whose result depends on an environment users do not share.

| Where | What |
| --- | --- |
| CI and local | Node tests in `scripts/tests/*.test.mjs`, `check-repo.mjs`, the catalog, the version bump, `tsc` on `scripts/`, ShellCheck, shfmt, ruff, mypy and basedpyright on `scripts/`, `claude plugin validate --strict` on the marketplace and every plugin, Biome outside `plugins/`, markdownlint, actionlint |
| Local only | The tests in `scripts/tests/<plugin>/` (Node, Python, `by_path.sh`), `claude plugin test`, the mods' `tsc`, and Biome, ShellCheck, shfmt, ruff, mypy, basedpyright and `tsc` on `plugins/` |

The plugins' Node tests moved from `scripts/tests/` to `scripts/tests/<plugin>/`, the folder convention the Python tests already used, so where a test lives decides where it runs. The `.mjs` type check split into `scripts/tsconfig.json` and `scripts/tsconfig.plugins.json`; both include every JavaScript and TypeScript extension so files the repository does not have yet are checked too.

### Consequences

- Good, because CI no longer goes red or green on a tool version users may not have, and the policy job no longer installs a global TypeScript for hook tests.
- Good, because basedpyright now runs in CI, on the maintainer Python under `scripts/`.
- Bad, because a push made without `npm run gates` reaches `main` with the plugins' behavior unproven; the local gates and the evals are the only guarantee.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No plugin behavior gate runs in CI | `scripts/tests/gates.test.mjs` → "--ci keeps maintainer tooling and plugin structure" | Passed on 2026-10-21 | Each push |
| Each CI group passes | `npm run gates:ci -- --group <group>` for the four groups | Simulated locally on 2026-10-21 with `--ci`: `policy`, `python`, `claude` and `lint` exit 0, and `--group local` finds no gate (exit 1). CI run pending | First push |

## More information

- Nery set the principle on 2026-10-21: CI must not go against what is in the plugins, whose behavior varies with the user who installs them; that is proven locally and by evals.
- ADR_2026-10-20_retire-cross-os-python-ci-job stays in force; this record extends its reasoning to every plugin behavior gate.
