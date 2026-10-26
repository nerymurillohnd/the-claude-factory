---
status: superseded
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-10-25_plugin-readme-rules-live-in-building-plugins
---

# The marketplace's user docs have their own skill

## Scope

The documentation users read about the marketplace itself: the root `README.md` outside its generated blocks, `docs/`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and the root `LICENSE`. The files a plugin ships, the plugin templates, the root `CHANGELOG.md`, and issues, issue forms and labels are out of scope.

## Context and problem statement

These files had no procedure of their own. Their rules were spread over `.claude/rules/user-docs.md`, which mixed general style with plugin README rules; `.claude/templates/root-readme.md`, a blueprint stored as a template; and two rows of the `plugin-consistency` skill. Nothing covered `CODE_OF_CONDUCT.md`, the root `LICENSE` or the links in these files, and Biome ignores Markdown here (`biome check README.md` reports the path as ignored). Where should the procedure for keeping them correct live?

## Decision drivers

- What these files say reaches users nobody reviews them for, so a stale command or minimum version must be caught before it ships.
- Maintainer documentation stays separate from the files a plugin is scaffolded with, which a later stage covers.
- GitHub operations (issues, forms, labels) get their own skill later.
- An older file loses only what the new skill covers; what it does not cover stays.

## Considered options

- **A `maintaining-user-docs` skill, with `user-docs.md` narrowed to plugin READMEs and their templates**: chosen.
- **Keep `user-docs.md` as the only source for every user doc**: rejected, because a style rule gives no procedure, sources or cross-file checks, and it left files uncovered.
- **Delete `user-docs.md` and move its plugin README rules into the future plugin-creation skill now**: rejected, because that skill does not exist yet and plugin READMEs would lose their style rules in between; `.claude/CLAUDE.md` holds only their structural rules.

## Decision outcome

Chosen option: **a `maintaining-user-docs` skill**, because it gives these files a scope, an official source per file, the facts that must agree across files, a workflow and a freshness sweep.

- `.claude/skills/maintaining-user-docs/` holds the skill, and `references/root-readme.md` holds the blueprint moved from `.claude/templates/`.
- `.claude/rules/user-docs.md` keeps only plugin READMEs and the plugin templates.
- `plugin-consistency` drops its root README and `docs/` checks and keeps every plugin check.
- `.claude/rules/workflow.md` → User documentation names the skill.

### Consequences

- Good, because every file users read about the marketplace now has a procedure and a source to check it against.
- Good, because no rule was lost: what the skill does not cover stays in the older files.
- Bad, because the plugin README style lives in two places, this skill and `user-docs.md`, until the plugin-creation stage settles where it goes.

## More information

Decided by Nery on 2026-10-25, after reviewing the proposal and the plan in this session. Revisit when the plugin-creation stage or the GitHub operations skill is built, since each takes over files this one only reads.
