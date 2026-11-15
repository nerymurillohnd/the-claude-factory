---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_writing-hooks-evals-give-the-docs-mcp-only-to-the-skill-arm
superseded-by: none
---

# Eval overlays add files to the with-plugin arm only, on a staged copy of the plugin

## Scope

`.github/workflows/evals.yml`, `plugins/<plugin>/evals/_overlay/` (first used by hook-engineering for the docs MCP server), hook-engineering's grants in `.github/evals.json`, and `.claude/rules/plugins/evals.md`. The rest of ADR_2026-11-15_writing-hooks-evals-give-the-docs-mcp-only-to-the-skill-arm (the five cases, their mapping to the owner's failure points, one effort group) still holds.

## Context and problem statement

The superseded ADR gave the with-skill arm the docs MCP through a support plugin listed in each case's `plugins`. Its pending Confirmation row failed on Claude Code 2.1.325, observed in three probe runs on 2026-11-15:

- Listing hook-engineering itself (`plugins: ["../..", ...]`) is refused before any run: "a plugins entry names the case directory, its graders or mocks, or a directory covering them — a plugin shipped with a case must sit in its own subdirectory".
- Listing only the support plugin replaces the plugin under test: the with-arm had the docs tools but no `writing-hooks`, and its plugin list held only the support plugin.

The docs say to "ship any skills, agents, hooks, or MCP servers a case depends on in the plugin under test", and the owner decided hook-engineering doesn't bundle the docs server for its users.

## Decision drivers

- The with-skill arm needs hook-engineering and the docs MCP together; the baseline needs neither.
- Users must keep receiving hook-engineering without a bundled docs server.
- Only what `claude plugin eval` supports, with no change to the CLI's arms.

## Considered options

- **An `evals/_overlay/` folder copied over a temporary copy of the plugin, and the suite run on that copy**: chosen.
- **A support plugin in each case's `plugins`**: rejected, because the CLI refuses the plugin under test there and otherwise replaces it.
- **Bundle the docs server in hook-engineering**: rejected by the owner's decision.
- **A combined copy of the skill inside the eval folder**: rejected, because it would evaluate a duplicate that drifts from the shipped skill.

## Decision outcome

Chosen option: **an eval overlay on a staged copy**, because the copy is the shipped plugin plus only the overlay's files, so the with-arm tests exactly what users get with the docs server added, and the no-plugin arm is untouched:
- `evals.yml` copies `plugins/<plugin>` into the runner's temp folder, copies `evals/_overlay/.` over it, and runs `claude plugin eval` on the copy, failing the job if staging fails. A plugin without `_overlay/` runs as before.
- hook-engineering's overlay is one `.mcp.json` with the `claude-code-docs` HTTP server. The tools are `mcp__plugin_hook-engineering_claude-code-docs__*`, which `.github/evals.json` grants, with `--allow-real-servers`.
- A local run stages the same copy by hand before `claude plugin eval`.
- The mechanism was Claude's, as a technical choice the owner delegated on 2026-11-15; the tool rule is the owner's.

### Consequences

- Good, because the with-skill arm has the real plugin and the docs MCP, and users still get the plugin without it.
- Bad, because a local run needs the same staging step, which the evals rule now states.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The staged with-arm has both skills and the docs tools; the baseline has neither | A one-turn probe case on a staged copy, reading each arm's trace | 2026-11-15: with-arm `hook-engineering:hook-development`, `hook-engineering:writing-hooks` and `mcp__plugin_hook-engineering_claude-code-docs__*`; baseline `NONE` and `NONE` | After a Claude Code upgrade that changes eval arms |
| The shipped plugin has no MCP server | `claude --plugin-dir plugins/hook-engineering plugin details hook-engineering` | 2026-11-15: `MCP servers (0)` | After the overlay or the plugin changes |
| The workflow stages and stays valid | The staging block run locally, and `npm run lint:workflows` | 2026-11-15: staged copy lists `MCP servers (1)`; no findings | After `evals.yml` changes |
