---
status: accepted
date: 2026-10-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Fold the pr-diagnostics skill into the pr-tracker agent

## Scope

The `github-operations` plugin: `agents/pr-tracker.md`, the removed `skills/pr-diagnostics/`, the references to that skill in `auto-pr-lifecycle` and `references/github-read-tasks.md`, and the README component table. The general pattern of preloading skills into agents in other plugins is out of scope.

## Context and problem statement

The `pr-tracker` agent preloaded the `pr-diagnostics` skill through `skills:`. The skill held the inspection procedure, the diagnosis rules and the report format. It was `user-invocable: false`, and its only consumer was this agent.

The agent's own body was a thin wrapper. It told the agent to read the skill file and `references/github-read-tasks.md` if the skill was not in context.

Nery judged the skill unnecessary. The agent has one specific job, and its markdown body is its system prompt, so the instructions belong there.

## Decision drivers

- The agent's system prompt should hold everything it needs, without depending on preloading or file reads at start.
- Fewer components to version, document and keep in sync.
- Least privilege: an agent that reads no local files needs no `Read`, `Grep` or `Glob`.

## Considered options

- **Agent body holds the procedure, the status rule, the report format and the read-only MCP tool for each task**: chosen.
- **Keep the preloaded skill**: rejected. It was a second component for one consumer, and it carried a fallback file read to cover the case where preloading failed.

## Decision outcome

Chosen option: **fold the skill into the agent body**. It keeps the agent's whole job in its system prompt and removes a component that users never invoke.

### Consequences

- Good, because the agent works without reading plugin files, and its tools shrink to `ToolSearch` plus the read-only GitHub MCP tools.
- Good, because the procedure and the MCP parameters are in one file. The parameters were checked against the live tool schemas on 2026-10-18.
- Bad, because the read-only task list now exists in two places: the agent body, with MCP forms only, and `references/github-read-tasks.md`, with MCP and `gh` forms for the main session. A change to one must be mirrored in the other.
- Bad, because removing a listed skill is breaking. It ships as 0.3.0 under ADR_2026-10-18_breaking-changes-bump-minor-in-0x.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The agent reports correctly from its body alone | A/B run on the PR #20 expired-token failure (run 39138684403, attempt 1) | pending | Before PR #20 merges |
| No file still references `pr-diagnostics` | `rg -n pr-diagnostics plugins docs README.md`, excluding changelogs | pending | Before PR #20 merges |

## More information

- PR #20 in `nerymurillohnd/the-claude-factory`.
- The 2026-10-18 handoff listed this fold as an open item, blocked on the 0.x versioning decision.
