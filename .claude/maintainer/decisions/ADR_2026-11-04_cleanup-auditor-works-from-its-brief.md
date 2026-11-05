---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: ADR_2026-10-29_repo-auditor-reads-skill-references
superseded-by: none
---

# The cleanup auditor works from its brief, not from the skill's references

## Scope

`plugins/github-operations/agents/repo-hygiene/health-diagnostics.md` and the `cleanup-and-debug` skill that briefs it. The `repo-auditor` agent, which read the legacy skill's audit references by plugin path, was removed in commit b4109a2.

## Context and problem statement

`repo-auditor` read `skills/github/references/audit/*` through `${CLAUDE_PLUGIN_ROOT}`, so it depended on the legacy skill's files. The redesigned cleanup audits in phases, and a large repository needs several auditors at once, each on part of the work. How does the auditor learn its scope?

## Decision drivers

- One auditor that can be reused for any phase, and run several times in parallel.
- No dependency on another skill's files.

## Considered options

- **A reusable auditor scoped by the brief the skill writes**: chosen.
- **Keep an auditor that reads the skill's references by plugin path**: rejected because it ties the agent to a skill's file layout and to one fixed scope.

## Decision outcome

Chosen option: **the brief carries the scope**. `cleanup-and-debug` reads the phase's reference and copies the sections the auditor must collect, with their "Done when" list, into the brief. `health-diagnostics` never reads the skill or its references.

### Consequences

- Good, because one agent serves every audit phase, and the skill decides how many run at once from the repository's size.
- Bad, because each brief must carry the phase's sections in full, which the skill must verify before relying on a report.

## More information

Built in commit 1a43ab2 ("make health-diagnostics the reusable auditor of cleanup-and-debug").
