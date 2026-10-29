---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The repo-auditor agent reads the audit references through the plugin root

## Scope

- `plugins/github-operations/agents/repo-auditor.md`, new in 0.5.0, and the files it reads: `skills/github/references/audit/intake-local.md`, `history.md`, `github.md`, `links.md`, and `skills/github/scripts/branch-states.sh`.
- Out of scope: `agents/pr-tracker.md`, which keeps its whole procedure in its body under ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker.

## Context and problem statement

The audit's collection (steps 0 to 2: intake, collection, classification) is the heaviest read in the plugin, and its output is consumed from files anyway. Running it in a subagent keeps the main context for the report and the two approval gates. The procedure it follows is about 30 KB of references that the main session's cleanup lifecycle also uses. ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker made `pr-tracker` work from its body alone, with no file reads at start. Should the new agent follow the same rule and inline the audit procedure?

## Decision drivers

- One copy of the audit procedure, so a fix reaches both the agent and the main session.
- Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` in plugin agent bodies ([manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference#where-each-variable-resolves)).
- The 2026-10-18 ADR's driver was one agent with one specific job and a thin wrapper body; it did not set a rule for every agent of the plugin.

## Considered options

- **The agent reads the four audit references and runs `branch-states.sh` through `${CLAUDE_PLUGIN_ROOT}`**: chosen.
- **Inline the audit procedure in the agent body, as `pr-tracker` does**: rejected, because about 30 KB would exist twice and drift.

## Decision outcome

Chosen option: **the agent reads the references by plugin path**, because the procedure stays in one place and the agent gets the same text the main session follows. ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker stays in force for `pr-tracker`; its scope is that agent only.

### Consequences

- Good, because a change to an audit reference reaches the agent with no mirrored copy.
- Bad, because the agent needs `Read` and depends on the plugin's file layout: moving an audit reference must update the agent body in the same change.
- Bad, because the plugin now has two agent patterns, one self-contained and one reading references.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The agent resolves and reads every path it names | One live launch on this repository, findings and coverage files written to the scratch folder | pending | Each move of an audit reference |

## More information

- Spec: `.claude/specs/2026-10-29-github-operations-0.5.0-design.md`, section "Agents". Decided by Nery in the 2026-10-29 design conversation.
