---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# testing-plugins owns the live MCP checks

## Scope

The live checks of a plugin's MCP servers and of hooks that match or call MCP tools: loading the plugin with an option unset and set, connecting the server, calling its tools from the main conversation and from an agent, the Claude app Connectors steps, and the runtime cases of `mcp_tool` hooks. The skills involved are `.claude/skills/building-plugins/` and `.claude/skills/testing-plugins/`, and the routing in `.claude/rules/workflow.md`. Out of scope: the static checks of a plugin build, evals, and unit tests, type checks, linters and `claude plugin validate` runs.

## Context and problem statement

`building-plugins` declares testing out of its scope, yet its `references/mcp-servers.md` loaded the plugin in its Declare step and carried a four-point Test step, and `references/mcp-hooks-and-lifecycle.md` a list of runtime cases. `testing-plugins` excluded every test other than evals. So a comprehensibility review found that no skill owned the live MCP checks while one skill ran them against its own scope. Which skill owns them?

## Decision drivers

- Each skill runs only what its scope governs, with no gray area about who does what.
- Building a plugin never starts its servers or calls real tools; live checks wait until Nery says the plugin is ready.
- Testing work lives with the skill named for testing plugins.

## Considered options

- **testing-plugins owns them**: chosen.
- **building-plugins keeps them as a gated step**: rejected because it keeps testing inside the skill whose scope excludes testing.

## Decision outcome

Chosen option: **testing-plugins owns them**, because it is the testing skill and its exclusion of "tests other than evals" was aimed at unit tests, type checks, linters and validate runs, not at live load checks.

### Consequences

- Good, because `building-plugins` now runs static checks only and says so, and hands the live checks to `testing-plugins` in its "Other skills" table.
- Good, because `testing-plugins/references/mcp-live-checks.md` holds every live MCP check in one place, run only on Nery's word that the plugin is ready.
- Bad, because `testing-plugins` grows a third job beside evals and troubleshooting, so its scope line and description change.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No `building-plugins` reference loads the plugin or runs a live test | A comprehensibility review of the skill | pending | After each change to the skill's MCP references |

## More information

Nery chose this on 2026-10-25, answering a question raised by a comprehensibility review of `building-plugins`. Commit `d9875ba` moved the checks.
