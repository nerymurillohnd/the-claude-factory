---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Check workflows with actionlint for correctness and zizmor for security

## Scope

The `lint:workflows` script, `.github/zizmor.yml` and the four workflows in `.github/workflows/`.

## Context and problem statement

The owner asked whether actionlint is the right tool or whether something stronger exists. actionlint 1.7.12 reported nothing on the four workflows. It checks syntax, expression types, runner labels, action inputs and shell, but its docs say it "focuses on catching mistakes": it does not check least privilege, SHA pinning, dangerous triggers or persisted credentials.

## Decision drivers

- Catch both workflow mistakes and workflow security problems.
- Run locally and in CI from npm, with a pinned version.

## Considered options

- **actionlint plus zizmor 1.32.0 (pinned in the uv lock), with accepted findings recorded in `.github/zizmor.yml`**: chosen.
- **actionlint alone**: rejected because it misses the security classes above.
- **poutine or octoscan**: rejected because they overlap zizmor and target organization-wide or offensive scanning; octoscan is GPL-3.0 and pre-1.0.

## Decision outcome

Chosen option: **actionlint and zizmor together**. `.github/zizmor.yml` accepts two findings with their reasons: `artipacked`, because the owner keeps `actions/checkout`'s default `persist-credentials: true` and claude-code-action replaces that token with its own; and `dangerous-triggers`, because `claude.yml` needs comment triggers to answer `@claude` and `release.yml`'s `workflow_run` runs only after Validate succeeds on a push to `main`.

### Consequences

- Good, because `npm run lint:workflows` passes and any new security finding fails it.
- Bad, because zizmor runs `--offline`, so its online audits (impostor commits, known-vulnerable actions) do not run locally.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No unaccepted finding | `npm run lint:workflows` | Passed on 2026-11-12 ("No findings to report… 9 ignored") | Each workflow change |
| CodeQL default setup for Actions is on | Repository settings | Pending: recommended, not yet decided | When CI is rebuilt |

## More information

- Sources: `rhysd/actionlint` `docs/checks.md`; `zizmorcore/zizmor` at v1.32.0, `docs/audits.md` and `docs/configuration.md`; `actions/checkout` README (persist-credentials, v6 storage under `$RUNNER_TEMP`).
- Commits: 359f9d9, a3e35ec.
