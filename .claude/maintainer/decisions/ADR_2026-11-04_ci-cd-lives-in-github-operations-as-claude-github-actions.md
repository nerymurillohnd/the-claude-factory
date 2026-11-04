---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# CI/CD work lives in github-operations as the claude-github-actions skill

## Scope

`plugins/github-operations/skills/claude-github-actions/` and the CI/CD Engineering blueprint (rev 13.1) that Nery shared on 2026-11-04. Out of scope: authoring workflows from scratch (DEBT-045).

## Context and problem statement

The blueprint proposed a standalone plugin, `ci-cd-engineering`, with a skill `claude-github-actions`. It argued that the action releases often, and that github-operations required a token and shipped Python hooks. Nery chose to keep CI/CD inside github-operations. What goes in, and under which name?

## Decision drivers

- One plugin for GitHub work, with no overlap between its skills.
- A name close to the original: "Para evitar confusiones y no separarse tanto del original".
- Rescue only what no skill already covers, verified against the current action source.

## Considered options

- **A skill named `claude-github-actions` inside github-operations, with only the blueprint parts no skill covered**: chosen.
- **The blueprint's standalone `ci-cd-engineering` plugin**: rejected by Nery.
- **The name `ci-cd-actions`**: rejected by Nery, to stay close to the original name.

## Decision outcome

Chosen option: **`claude-github-actions` inside github-operations**. It got:

- the claude-code-action contract;
- the sharp-edge catalog SE-01 to SE-14;
- the trust-boundary and authentication references;
- a workflow-file audit with a patch per finding;
- Claude-step diagnosis;
- the existing default-branch CI repair.

Every fact was re-verified at `anthropics/claude-code-action@c0949c5`; the blueprint used `6d5ae52`. Its packaging, identity, offline pins file and list-only style were not taken.

### Consequences

- Good, because one skill owns every workflow-definition or Claude-step failure, and the other skills hand those to it.
- Bad, because the platform reserves `claude` in skill names uploaded through the API or to claude.ai. Claude Code accepts the name, and the plugin is distributed for Claude Code only.
- Bad, because the action's facts drift between releases with nothing watching them (DEBT-046).

## More information

The overlap analysis, three audits verified one by one, is in the approved plan of 2026-11-04. Built in commits d7d9912 to bbfe56b.
