---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# A plugin runs only the programs its README declares, even when another one is installed

## Scope

Every plugin under `plugins/`. It was applied first to `plugins/github-operations/skills/claude-github-actions/` (commit 22cc2db). Maintainer tooling outside `plugins/` is out of scope.

## Context and problem statement

The Actions skill's validation loop ran `actionlint`, `zizmor` and `shellcheck` "when they are already on PATH". None of them is in the README's prerequisites. Can a public plugin run an undeclared program when the user happens to have it?

## Decision drivers

- The plugin runs on strangers' machines, from its README declarations only (`.claude/CLAUDE.md`, Purpose).
- Every command a plugin runs must be disclosed.
- Results must not change with what each user has installed.
- `zizmor`'s online audits can call the GitHub API: an undeclared network call.

## Considered options

- **Run only declared programs; validate with what the plugin ships**: chosen.
- **Run optional tools when present**: rejected by Nery: "Esto es plugin público!!!"

## Decision outcome

Chosen option: **only declared programs**. `claude-github-actions` runs `git`, `gh` and the GitHub MCP tools only. Its patch validation checks each patched file against `references/workflow-audit.md`, a checklist the skill ships. A third-party tool a plugin truly needs goes into its README prerequisites, with Nery's approval first.

### Consequences

- Good, because what a plugin runs is exactly what its README says.
- Bad, because the audit has no linter's precision; the checklist must stay complete.

## More information

Decided on 2026-11-04 after Nery rejected the linter loop.
