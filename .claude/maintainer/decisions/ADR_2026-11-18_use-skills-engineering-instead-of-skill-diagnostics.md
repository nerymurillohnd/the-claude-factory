---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# This project uses skills-engineering, not skill-diagnostics

## Scope

`enabledPlugins` in `.claude/settings.json`, and which plugin this project's sessions use to write and audit skills.

## Context and problem statement

`.claude/CLAUDE.md` routes skill writing to `skills-engineering:authoring-skills` and skill audits to `skills-engineering:auditing-skills`. But the project's settings never enabled `skills-engineering`, so no session could load those skills, while `skill-diagnostics` stayed enabled. The catalog describes `skill-diagnostics`' gate as having "Claude audit every skill it creates or changes before it finishes", against the rule to audit only when the owner asks. The owner asked to uninstall `skill-diagnostics`, and, if that failed, to set it to `false` in the project settings.

## Decision drivers

- Sessions must be able to load the skills CLAUDE.md names.
- Audits run only when the owner asks.

## Considered options

- **Enable skills-engineering and set skill-diagnostics to false**: chosen. `claude plugin uninstall` found nothing to remove under the default, user, project or local scope.
- **Keep both enabled**: rejected by the owner, because the two overlap and the gate forces audits.

## Decision outcome

Chosen option: **skills-engineering on, skill-diagnostics off**, because it makes CLAUDE.md's routing real and stops the forced audits.

### Consequences

- Good, because the project uses one plugin for skills, the one its instructions name.
- Bad, because the project's sessions load `skills-engineering` from the marketplace only after it reaches `main`.

## More information

Commit dea4a2c.
