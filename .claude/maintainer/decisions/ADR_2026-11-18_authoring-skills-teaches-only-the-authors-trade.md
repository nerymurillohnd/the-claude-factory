---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills teaches only what writing a skill needs

## Scope

`plugins/skills-engineering/skills/authoring-skills/`: its `SKILL.md` and references. The platform and configuration knowledge `auditing-skills` uses is out of scope.

## Context and problem statement

The first full version of `authoring-skills` held about 1,600 lines in 12 files, most of them platform and configuration facts: cloud vendors, Managed Agents counts, sync timing, precedence rules, reserved names, hook limits, settings and permission internals. The owner asked whether such facts change how a skill is written, and they don't: they serve an auditor checking a configuration, not an author writing a skill. A comparison read in full on 2026-11-18 showed that neither `skill-creator` nor superpowers' `writing-skills` carries such a catalog.

## Decision drivers

- What the skill teaches must change what Claude writes or where it puts it.
- Every line costs context in every run.
- The auditor's knowledge already lives in `auditing-skills`.

## Considered options

- **The author's test**: a line stays only if it changes what the author writes or where the author puts it; otherwise it becomes one pointer to the official page, or it goes. Chosen.
- **Full platform references**: references covering every location, surface, field limit and setting. Rejected, because nearly none of it changes a writing decision, and it buries the writing logic.

## Decision outcome

Chosen option: **the author's test**, because it keeps the skill on its purpose, writing skills, and leaves verification of a configuration to the auditor.

### Consequences

- Good, because the skill fell to 841 lines in 7 files, with `SKILL.md` near 4,900 tokens on invoke.
- Good, because the same test is taught in the skill, for the platform facts in the skills Claude writes.
- Bad, because a rare platform case now needs a lookup in the official docs instead of a ready answer.

## More information

Rewrite in commit 823ca5a; the test appears in phase 4 of `SKILL.md`. Related: ADR_2026-11-18_authoring-skills-body-holds-every-run-decision.
