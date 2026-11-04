---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# The PR lifecycle agents read GitHub through the MCP tools first, with gh as the fallback

## Scope

The Tools sections and wait steps of `plugins/github-operations/agents/pr-lifecycle/*.md`, and the gotcha in `skills/auto-pr-lifecycle/SKILL.md` (commits 7a8c81b, 7ef1024, 38e4c29, 455221e, e2db449).

## Context and problem statement

The agents named no tools, or used `gh` only. Nery noted that the GitHub MCP tools return the same data faster, and that an agent whose MCP call failed had no stated alternative and could give up. Which layer does each read use, and what happens when it fails?

## Decision drivers

- One MCP call per fact, instead of several turns.
- No dead end: every read has a second path.
- Plugin subagents inherit the session's MCP tools, which load on demand.

## Considered options

- **MCP first, `gh` as the fallback for every read and write, MCP tools loaded with `ToolSearch` before the first call**: chosen.
- **`gh` only**: rejected because it costs more turns and context.
- **MCP only**: rejected because a missing, failed or unauthorized server would leave the agent with nothing.

## Decision outcome

Chosen option: **MCP first, `gh` as the fallback**.

- Each Tools table pairs every MCP read and write with its `gh` command.
- A fact counts as out of reach only after both paths failed, and both errors are reported.
- `gh` alone covers what MCP cannot: the blocking wait for checks, required checks, the review decision and a check run's output.
- A thread author's type is taken from `author.__typename`, read through the GraphQL query when the MCP result lacks it.

### Consequences

- Good, because reads are faster and a failed server does not end the inspection.
- Bad, because tool names are given bare: the prefix depends on the server (`mcp__plugin_github-operations_github__` for this plugin's), which departs from the platform advice to use fully qualified names.

## More information

Directed by Nery on 2026-11-04. Tool shapes were checked against the loaded GitHub MCP schemas and live reads on PR #1 of this repository.
