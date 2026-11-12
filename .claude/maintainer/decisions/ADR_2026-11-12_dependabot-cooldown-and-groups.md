---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Delay Dependabot updates by a cooldown and group them

## Scope

`.github/dependabot.yml`: the `github-actions` and `npm` entries.

## Context and problem statement

Dependabot proposed every release as soon as it appeared, one pull request per dependency. zizmor 1.32.0's `dependabot-cooldown` audit flags a cooldown under 7 days. GitHub applies a 3-day default cooldown even when none is set.

## Decision drivers

- Give a broken or compromised release time to be pulled before it is proposed.
- Fewer update pull requests.

## Considered options

- **A 7-day cooldown (14 for an npm major), one group for all actions, one group for npm minor and patch updates**: chosen.
- **GitHub's 3-day default**: rejected because it is below zizmor's recommended minimum.

## Decision outcome

Chosen option: **a 7-day cooldown with grouped updates**.

### Consequences

- Good, because `check-jsonschema` 0.39.0 validates the file against Dependabot's schema.
- Bad, because fixes also arrive 7 days later, and security updates are not delayed by cooldown, which applies to version updates only.

## More information

- Sources: GitHub docs, Dependabot options reference (`cooldown`, `groups`); `zizmorcore/zizmor` docs at v1.32.0 (`dependabot-cooldown`).
- Pending: a `uv` entry once the maintainer lock is in use (see ADR_2026-11-12_uv-project-pins-maintainer-python-tools).
- Commit: d6700c2.
