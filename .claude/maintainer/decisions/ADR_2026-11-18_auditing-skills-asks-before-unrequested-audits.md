---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# auditing-skills asks before an audit nobody requested

## Scope

The description and the "When no one asked for an audit" section of `plugins/skills-engineering/skills/auditing-skills/SKILL.md`.

## Context and problem statement

The description of `auditing-skills` said to use it "right after a skill or any of its files is created or edited", and its body launched the reviewers at once. Every edit could start nine reviewer agents nobody asked for, which the audit of `authoring-skills` reported as a High finding. The owner asked that the skill instead ask the user whether to run the audit, right after a skill is created or edited.

## Decision drivers

- Each reviewer runs as its own agent and spends usage.
- The project runs audits only when the owner asks.

## Considered options

- **Load after a create or edit, then ask before running, offering all or some reviewers**: chosen.
- **Run the full audit after every create or edit**: rejected, because it spends usage nobody approved.
- **Drop the trigger after edits**: not chosen, because the owner wants the offer at that moment.

## Decision outcome

Chosen option: **ask before running**, because it keeps the offer where it helps and the spend under the user's control.

### Consequences

- Good, because the skill names the skill to audit, says each reviewer runs as its own agent, and runs only on a yes.
- Bad, because the user answers one more question after each skill change.

## More information

Commit da95633; the CHANGELOG line says so.
