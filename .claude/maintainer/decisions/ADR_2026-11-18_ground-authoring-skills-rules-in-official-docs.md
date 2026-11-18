---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Every rule authoring-skills teaches rests on an official source or the owner's approval

## Scope

The rules in `plugins/skills-engineering/skills/authoring-skills/` and how new ones are added.

## Context and problem statement

The owner asked what backed two description rules the skill taught: no summary of the workflow, and no claims of quality. Neither came from the official docs: one came from superpowers' `writing-skills`, the other from no source at all. A source check of every rule then found other rules with no official source, and one narrower than the official guidance on giving reasons.

## Decision drivers

- The official documentation outranks other sources and Claude's own judgment.
- A rule Claude follows on every run must be one the owner can trace.

## Considered options

- **Keep a rule only with an official source, or with the owner's approval as a project default**: chosen.
- **Keep the rules as written**: rejected, because some had no source and one contradicted the official guidance.

## Decision outcome

Chosen option: **official source or owner approval**, because the owner asked to work from the official documentation.

### Consequences

- Good, because the description rules now follow agentskills.io's guide: start with "Use when", the user's intent rather than the mechanics, insistent about its cases, within the limits.
- Good, because reasons go with judgment steps, as agentskills.io advises, and fixed steps say what to do without narration, as the Claude Code docs ask.
- Good, because "a subagent-run skill can't ask the user" now cites the sub-agents docs, which remove the question tool from every subagent.
- Bad, because rules without a source were dropped: lists over tables, the flowchart criterion, a parallel Claude Code copy and the task-tool caution.

## More information

Commits 9961a86, b708209 and 7983b5a. The source of each rule was listed for the owner on 2026-11-18, outside the repository.
