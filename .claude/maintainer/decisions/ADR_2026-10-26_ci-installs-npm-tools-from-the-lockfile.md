---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-21_ci-installs-latest-tools
superseded-by: none
---

# CI installs the npm tools from the lockfile and the other tools at their latest release

## Scope

- In scope: the tool installs of `.github/workflows/validate.yml` and the gates' note on where their tools come from in `scripts/gates.mjs`.
- Out of scope: the GitHub Actions themselves, pinned by commit SHA and updated by Dependabot; which npm tools the repository pins (ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies).

## Context and problem statement

ADR_2026-10-21_ci-installs-latest-tools had CI install every tool at its latest release, with TypeScript as the one pin (`TYPESCRIPT_VERSION`). Its own consequence was that a new release could turn CI red with no change in the repository, and `validate.yml` had since also pinned Biome by hand at 2.6.3. With Biome and TypeScript now exact devDependencies, where should CI get them?

## Decision drivers

- CI runs the same npm tool versions as the maintainer's `npm run` and git hooks.
- A new npm tool release reaches CI only through a reviewed Dependabot pull request.
- No version written by hand in the workflow.

## Considered options

- **The npm tools from `npm ci --ignore-scripts`, the others at their latest release**: chosen.
- **Every tool at its latest release** (ADR_2026-10-21_ci-installs-latest-tools): rejected because CI and the lockfile would drift, and a release could break CI with no change in the repository.

## Decision outcome

Chosen option: **the lockfile for the npm tools**, because `npm run gates:ci` puts `node_modules/.bin` first on PATH, so the gates run the pinned Biome and TypeScript.

- `validate.yml` drops `TYPESCRIPT_VERSION` and the global `typescript` and `@biomejs/biome` installs; the policy and lint jobs run `npm ci --ignore-scripts`.
- `HUSKY: "0"` in the workflow env keeps git hooks off the runners, as the Husky docs advise; `--ignore-scripts` already skips `prepare`.
- ruff, basedpyright, shfmt, ShellCheck, actionlint and Claude Code keep installing at their latest release.

### Consequences

- Good, because CI and local runs agree on Biome and TypeScript, and their updates are reviewed.
- Bad, because the tools outside npm can still turn CI red on a new release, as before.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No global npm tool install remains | `grep -n "install --global\|TYPESCRIPT_VERSION" .github/workflows/*.yml` | Passed on 2026-10-26: no match; `actionlint` clean | Each workflow change |
| CI's gates pass on the pinned tools | The Validate run after the next push | pending | The next push |

## More information

- Decided by Nery on 2026-10-26, together with ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies.
