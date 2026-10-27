---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-24_workflow-is-a-stage-map
superseded-by: none
---

# The workflow contract lives in CLAUDE.md

## Scope

- In scope: the Workflow section of `.claude/CLAUDE.md`, the deleted `.claude/rules/workflow.md`, and the references to it in `.claude/skills/building-plugins/SKILL.md` and `.claude/skills/building-plugins/references/versioning-and-release.md`.
- Out of scope: the procedures inside the project skills, the path-scoped rules that stay in `.claude/rules/` (`readme-md.md`, `plugins/`, `schemas/`), and plugins.

## Context and problem statement

ADR_2026-10-24_workflow-is-a-stage-map kept the order of work apart from `.claude/CLAUDE.md` on purpose: a map of stages that named the skill or rule for each one and restated no rule. The map later moved to `.claude/rules/workflow.md` (commit `e081941`) and became a contract of stages, skills and key jobs (commit `88a7dfc`). By 2026-10-26 it no longer held only an order of work: the scope rules, the maintainer and plugin tooling, and the working-file locations governed every stage, and they lived in `.claude/CLAUDE.md` while the stages that depend on them lived in the rule file. Keeping two files that state permanent rules about the same work lets them drift apart. Where should the contract live?

## Decision drivers

- The contract now holds permanent rules (the two scopes, their tooling, where specs and plans live and which files stay out of git), not only an order of work.
- One source of truth, so the stages and the rules they apply cannot contradict each other.
- The contract must load in every session, as the map did.

## Considered options

- **Move the contract into `.claude/CLAUDE.md` as its Workflow section and delete `.claude/rules/workflow.md`**: chosen.
- **Keep the stage map apart from `.claude/CLAUDE.md`** (ADR_2026-10-24_workflow-is-a-stage-map): rejected because the map now carries permanent rules, and two files holding them can drift apart.

## Decision outcome

Chosen option: **the Workflow section of `.claude/CLAUDE.md`**, because the scope, tooling and working-file rules and the stages that apply them then live in one place.

- `## Workflow` holds, as level-three sections: Maintainer and Plugin Scopes (with Maintainer Tooling and Plugin Tooling), Working Files, Management, Maintenance and Quality Gates, and Marketplace Plugins.
- Change Control stays its own `##` section after the Workflow: it governs the work, it is not a stage.
- The procedure of each stage still lives in its skill; the Workflow names the skill and the key jobs only.
- Skills refer to "the Workflow in `.claude/CLAUDE.md`". Dated ADRs and specs keep their mentions of `.claude/rules/workflow.md`.

### Consequences

- Good, because the scope and tooling rules and the stages that apply them cannot drift apart.
- Good, because Working Files now lists `.claude/plans/` as git-ignored, matching `.gitignore`, which settles a contradiction between the two.
- Bad, because `.claude/CLAUDE.md` grows by the contract, about 100 lines, and loads it in every session; the rule file loaded in every session too, so the context cost does not change.
- Neutral, because ADR_2026-10-24_workflow-is-a-stage-map's split of procedures into skills still holds; only where the map lives changes.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `.claude/rules/workflow.md` no longer exists | `ls .claude/rules/` and `git ls-files` | Passed on 2026-10-26: only `readme-md.md`, `plugins/` and `schemas/` remain | When `.claude/rules/` changes |
| No live file points to `.claude/rules/workflow.md` | `rg -uu "workflow.md"`, ADRs, specs, handoffs and git logs excluded as history | Passed on 2026-10-26 | When a skill or CLAUDE.md section is renamed |

## More information

- Decided by Nery on 2026-10-26: he replaced the scope and working-file sections of `.claude/CLAUDE.md` with the contract and ordered `.claude/rules/workflow.md` deleted (commit `47401ae`), then approved nesting its parts under `## Workflow` and returning Change Control to its own section (commit `7d1cfd6`).
- Related: ADR_2026-10-25_plugin-tooling-rule-folds-into-claude-md (the same move of a rule file into `.claude/CLAUDE.md`).
