---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills researches the skill's domain in primary sources, in any field

## Scope

Standard 1, Phase 2 step 1 and `references/phase-2-domain-research.md` of `plugins/skills-engineering/skills/authoring-skills/`.

## Context and problem statement

The skill required official sources only for how to write a skill, never for the domain the skill works in, so Claude could write a database or marketing skill from memory. The owner called this a large gap on 2026-11-19. He asked that the research cover every field a skill can serve, not only software, and use the project, live sources, official documentation, repositories, changelogs, release notes and each tool's own commands.

## Decision drivers

- A skill must meet its goal with facts true at the version its users run.
- Skills serve any field: code, data, design, marketing, documentation, science, operations and productivity.

## Considered options

- **A domain research reference, with standard 1 naming the concrete sources**: chosen.
- **Extend the environment file's project-material section**: rejected, because it breaks the one-topic-per-file standard.
- **A separate thirteenth standard**: rejected, because it would repeat standard 1.

## Decision outcome

Chosen option: **a domain research reference, with the sources named in standard 1**.

- It maps the discipline's knowledge, the technologies with their versions, the platforms and their rules, and the user's material.
- It reviews what the skill acts on.
- It reads primary sources first, then expert sources checked against them.
- It stops when two reads add nothing new.
- It records each source for the design.

### Consequences

- Good, because the design template and the Phase 5 checklist require the sources.
- Bad, because research takes longer, which parallel subagents can shorten where available.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19.
