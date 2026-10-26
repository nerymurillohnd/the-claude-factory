---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# building-plugins is this repository's procedure

## Scope

`.claude/skills/building-plugins/`: what it is, what it governs, where it ends and which skill it hands off to. Out of scope: the content of the other skills.

## Context and problem statement

The skill called itself "the general case" that project rules and skills displace, while it already carried this repository's scaffold and checks; its steps covered choosing a repo layout and marketplace name that are fixed here, and repeated versioning and publishing, which belong to another stage. Is it a general skill or this repository's procedure?

## Decision drivers

- `.claude/CLAUDE.md` defines `.claude/skills/` as "the procedures for work on this repository".
- Nery's standard on conflicts: his instructions win over any skill, the more specific rule wins, official docs and release notes win over project files, and new validated work outranks older work.
- A loaded skill must leave no gray area about what to do, when, and which skill comes next.

## Considered options

- **This repository's procedure**: chosen. It governs creating and changing a plugin of this repository, its manifest and components, the README, LICENSE and NOTICE, and the static checks of what it wrote; versioning, release, renames, testing, evals and marketplace docs go to the skills `.claude/rules/workflow.md` names, listed in an "Other skills" table; CI has no skill and goes to Nery.
- **General, with a repository section**: rejected because the repository's own definition of project skills makes it a repository procedure.

## Decision outcome

Chosen option: **This repository's procedure**, because the repository defines its skills that way, and the general facts stay in the references as the reasons behind its rules.

### Consequences

- Good, because every step applies here, and each situation outside its scope names the skill to load and when.
- Bad, because a reader who wants the general guidance for another repository finds it mixed with this repository's rules.

## More information

Decided on 2026-10-25 through Nery's standard ("ante conflictos, cual es mi standard?") and his confirmation of the scope analysis ("SI! ES LA MANERA CORRECTA"). Commits `091dd16`, `b53ee44`, `6431362`, `5997d48`.
