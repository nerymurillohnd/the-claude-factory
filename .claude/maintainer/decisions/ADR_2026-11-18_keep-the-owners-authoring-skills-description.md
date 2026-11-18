---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Keep the owner's description for authoring-skills

## Scope

The `description` in the frontmatter of `plugins/skills-engineering/skills/authoring-skills/SKILL.md`.

## Context and problem statement

The owner wrote the original description and had tested that it triggers well. A shorter rewrite lost its proactive trigger, its location words and what sets it apart. A later review called the original defective for opening with "Use every time..." and for summarizing the workflow. A check of the official sources showed those objections don't hold: agentskills.io recommends the imperative "Use this skill when...", and no official doc forbids describing the method.

## Decision drivers

- The description is what makes the skill load.
- The owner's text was tested.
- The official guidance is the measure, not third-party rules.

## Considered options

- **The owner's original, plus one clause for requests that never say "skill"**: chosen. The clause is "such as making a prompt or procedure reusable across sessions", for 1,023 characters.
- **A rewrite that opens with the capability**: rejected, because it lost trigger words and rested on rules without an official source.

## Decision outcome

Chosen option: **the owner's description with one clause**, because it follows the official guidance and keeps what made it trigger.

### Consequences

- Good, because the description keeps its locations, its proactive trigger and its boundary with auditing.
- Bad, because it sits one character under the 1,024 limit for uploads, so any addition must replace words.

## More information

Commit 823ca5a.
