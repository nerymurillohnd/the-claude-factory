---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-12_actionlint-and-zizmor-check-workflows
superseded-by: none
---

# actionlint and zizmor check the workflows, and zizmor accepts three findings with their reasons

## Scope

`npm run lint:workflows` and `.github/zizmor.yml`.

## Context and problem statement

ADR_2026-11-12_actionlint-and-zizmor-check-workflows chose actionlint and zizmor together and accepted two findings: `artipacked` and `dangerous-triggers` on `release.yml`'s `workflow_run`. The new workflows:
- check out with `persist-credentials: false`;
- dropped `workflow_run`;
- call a local composite action and a reusable workflow;
- install npm 12 by version;
- answer comment triggers in `claude.yml`.

## Decision drivers

- Keep both tools, since they check different things.
- Accept a finding only with a reason that holds for this repository.

## Considered options

- **Keep both tools, and accept `self-repository` (validate.yml, evals.yml), `adhoc-packages` (the setup action) and `dangerous-triggers` (claude.yml)**: chosen.
- **The `$/` self-repository syntax zizmor recommends**: rejected, because actionlint 1.7.12, the latest, rejects it as an invalid reference.

## Decision outcome

Chosen option: **both tools, with three accepted findings**:
- **`self-repository`:** actionlint rejects `$/`.
- **`adhoc-packages`:** `devEngines` requires npm ^12.2.1 and no lockfile can hold the npm that installs the lockfile.
- **`dangerous-triggers` on `claude.yml`:** mentions arrive only as comment events, the job checks out the default branch, and the action refuses bots and users without write access.

Each reason is in `.github/zizmor.yml`. The `artipacked` and `dangerous-triggers` exceptions on `release.yml` are gone.

### Consequences

- Good, because `zizmor --persona auditor` reports nothing beyond the three recorded findings.
- Bad, because the `self-repository` exception waits on actionlint (DEBT-007).

## More information

- Related: DEBT-007.
