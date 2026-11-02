---
status: accepted
date: 2026-11-01
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-28_instruction-engineering-joins-the-marketplace
superseded-by: none
---

# instruction-engineering stays in the marketplace with no eval suite, kept nowhere

## Scope

Applies to the `instruction-engineering` plugin: its identity, category, components and evals. How other plugins keep their evals is out of scope.

## Context and problem statement

ADR_2026-10-28_instruction-engineering-joins-the-marketplace published the plugin without its evals. It said the 594 eval files were kept at `~/Claude/ideas-and-brainstorm/instruction-engineering/evals/`. On 2026-11-01 that folder did not exist. The evals survived only in `~/Downloads/instruction-engineering.plugin` and in two unreachable checkpoint commits (bf5f2dc and 1490d3b), which a `git gc` would prune. `.claude/CLAUDE.md` says a plugin's eval suite stays in the plugin's directory, the only place `claude plugin eval` finds it.

## Decision drivers

- A record must not point at a copy that does not exist.
- Nery already ran and accepted the evals before the plugin joined.

## Considered options

- **Keep no eval suite for the plugin**: chosen.
- **Restore the evals into `plugins/instruction-engineering/evals/`**: rejected by Nery.
- **Restore the evals to `~/Claude/ideas-and-brainstorm/instruction-engineering/evals/`**: rejected by Nery.

## Decision outcome

Chosen option: **no eval suite**. The plugin keeps the rest of the earlier decision: `instruction-engineering` 0.1.0, category `documentation`, for Claude Code and the Claude app, with the skill `claude-md-and-rules` and the agent `reviewer`.

### Consequences

- Good, because no record or rule points at evals that do not exist.
- Bad, because a change to the skill or the agent has no suite to check it against, and DEBT-043's eval CI has nothing to run for this plugin.

## More information

Nery decided on 2026-11-01, from the consolidated audit of 2026-11-01 (finding N-01). The archive in `~/Downloads` and the unreachable commits were left as they are.
