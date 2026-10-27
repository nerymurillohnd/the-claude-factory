---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Every README.md gets one path-scoped rule that names its kind, owner and template

## Scope

`.claude/rules/readme-md.md`, which loads when a session reads or edits any `README.md` in this repository: the root one, each plugin's, the older plugin template, and the maintainer notes under `scripts/tests/`.

## Context and problem statement

The repository holds four kinds of README, each with its own owner skill, template, review path and checks:
- the marketplace's front page;
- each plugin's user guide;
- the plugin template;
- maintainer notes.

Nothing told a session which kind it was editing, so the rules of one kind could be applied to another. How does a session learn, at the moment it touches a README, which rules apply?

## Decision drivers

- Instructions load only where they apply.
- A session editing a README must know its owner skill and template before it writes.
- The criteria the skills do not state, such as which README is which, whether it needs a pull request, and what the checks do and do not read, need a home.

## Considered options

- **A path-scoped rule on `README.md` and `**/README.md`**: chosen. The rule names the kind, the skill to load, the template, whether a pull request is needed, the checks, and the rules every README shares.
- **Put the same text in CLAUDE.md**: rejected, because it would load in every session, including those that touch no README.

## Decision outcome

Chosen option: **a path-scoped rule**, because it loads when a README is read or edited, and only then.

- `.claude/rules/readme-md.md` was added (commit 426e317). It was later aligned with the `building-plugins` template and the frozen older template (commits 9ceffb3, 76df125).

### Consequences

- Good, because a session that opens a README learns its kind, owner skill and template before it writes.
- Bad, because the rule repeats some facts the skills also state, such as the template's location, and has to change when they change.

## Confirmation

- 2026-10-27, Claude Code 2.1.311: confirmed. In session `f5bdd77c-541a-4187-8bf3-85461bccdf16`, a `Read` of `plugins/tailwind-development/README.md` was followed at 16:09:36Z by a `nested_memory` attachment with the path `.claude/rules/readme-md.md`. The rule loaded on the README read, not at launch. A later `Edit` of the same README in that session also delivered the rule's contents.

## More information

Decided by Nery on 2026-10-25 in this session. Whether the rule loads on a README read is **pending**: it has not been confirmed in a fresh session the way ADR_2026-10-24_workflow-is-a-stage-map confirmed its rules.
