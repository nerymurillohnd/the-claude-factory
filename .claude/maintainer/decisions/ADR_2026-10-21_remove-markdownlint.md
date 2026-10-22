---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The repository has no Markdown linter: markdownlint-cli2 is removed

## Scope

- In scope: `.markdownlint-cli2.jsonc`, the `markdownlint` gate of `scripts/gates.mjs`, the `MARKDOWNLINT_CLI2_VERSION` pin in `.github/workflows/validate.yml`, the name of its `lint` job, the allow rule in `.claude/settings.json`, `.claude/CLAUDE.md` and the `plugin-consistency` skill.
- Out of scope: the other gates of the `lint` group (Biome outside `plugins/`, actionlint).

## Context and problem statement

The `markdownlint` gate ran markdownlint-cli2 with the `**/*.md` glob of `.markdownlint-cli2.jsonc`, in CI and locally. That glob covers every plugin `README.md` and `CHANGELOG.md`, so CI linted plugin files, against the rule that CI checks only the maintainer tooling and the plugins' structure (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure), and plugins are tested only through evals. Should Markdown keep a linter, and where?

## Decision drivers

- Nothing of a plugin is tested, formatted or linted in CI; a plugin is tested through its evals.
- Every gate must earn its cost: markdownlint was also one of the `npx` gates that stalled for about 300 s on a cold npm cache.

## Considered options

- **Remove markdownlint from the project**: chosen.
- **Keep it in CI with `plugins/` excluded, and lint plugin Markdown locally**: not chosen: Nery ordered the removal instead on 2026-10-21.

## Decision outcome

Chosen option: **remove markdownlint**, by Nery's decision on 2026-10-21. Its configuration, gate, pin and permission are gone, and the CI job is named "Workflow & JSON lint". Broken links and anchors, which it reported as MD051, are now checked by reading in the `plugin-consistency` skill, step 4.

This replaces the markdownlint entries in ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure (its "CI and local" row) and ADR_2026-10-21_maintainer-only-root-package-json (the CLIs on `npx`); the rest of both records stands.

### Consequences

- Good, because CI no longer reads any plugin file beyond the structural checks.
- Good, because one `npx` download fewer per run.
- Bad, because Markdown style and broken anchors are no longer checked by a tool; the `plugin-consistency` review is the only check.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No markdownlint reference remains outside settled records | `git grep -n -i markdownlint` | Only this record, the two settled ADRs and the `.claude/CLAUDE.md` pointer to it, on 2026-10-21 | Each push |
| The gates and CI run without it | `node --test scripts/tests/gates.test.mjs`, `npm run gates:ci -- --group lint`, actionlint | See the commit that removed it | First push |

## More information

Nery ordered the removal on 2026-10-21, after the CI split showed markdownlint reading plugin files.
