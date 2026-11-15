---
status: superseded
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-11-15_eval-overlays-add-files-to-the-with-plugin-arm-only
---

# writing-hooks quality evals give the docs MCP only to the with-skill arm, through a support plugin

## Scope

`plugins/hook-engineering/evals/`: the five quality cases, the support plugin in `evals/_support/docs-mcp/`, and hook-engineering's entry in `.github/evals.json`. The loading suite in `evals-loading/` is out of scope.

## Context and problem statement

The owner set the eval rules for `writing-hooks`: at most five non-trivial cases, each aimed at a point where Claude without the skill tends to fail (the wrong event, the wrong location, the wrong quoting or exec versus shell form, a gate that lets bad input through, an event or field the user's version lacks); two arms in every case, with network in both; native tools, WebSearch and WebFetch in both arms, and the Claude Code docs MCP only in the with-skill arm, because a user without the plugin may not have it; and a mean gain of at least 25 points over all cases, with the detail per case. The plugin doesn't bundle the docs MCP, by the owner's decision, and an eval run loads no personal MCP server.

## Decision drivers

- The docs MCP must reach the with-skill arm and never the baseline.
- The plugin users install must stay without a bundled docs server.
- The 25-point target is a mean over all five cases, not over effort groups.

## Considered options

- **A support plugin inside `evals/` that declares only the docs server, listed with hook-engineering in each case's `plugins`, its real server started with `--allow-real-servers` and its tools granted by name**: chosen.
- **No docs MCP in either arm**: rejected, because it breaks the owner's tool rule for the with-skill arm.
- **Bundle the docs server in hook-engineering**: rejected, because the owner decided the plugin doesn't bundle it, and a bundled server renames its tools for every user.

## Decision outcome

Chosen option: **a support plugin listed only in the cases**, because the docs say the baseline arm runs "with no plugin at all" and a case's `plugins` names the plugin directories under test:
- `evals/_support/docs-mcp/` holds a manifest and a `.mcp.json` with the `claude-code-docs` HTTP server; it is not a case, because it has no `prompt.md` or `case.yaml`.
- Each quality case lists `plugins: ["../..", "../_support/docs-mcp"]`.
- `.github/evals.json` adds `--allow-real-servers` and `mcp__plugin_eval-docs-mcp_claude-code-docs__*` to the grants, beside `--scaffold`, Write, Edit, Bash, WebSearch and WebFetch for both arms.
- The five cases map one to one to the owner's failure points: `batch-note-posttoolbatch` (event), `plugin-subagent-tunnel` (location), `local-cross-platform-format` (quoting and form), `plugin-mcp-gate` (gate), `pinned-version-gate` (version). The broad-request case was retired, because clarifying a request is not one of the five points.
- All five carry `effort-high`, so CI runs them as one group and the gate in ADR_2026-11-15_evals-gate-on-a-per-plugin-delta-floor reads the mean over all five.
- The mechanism was Claude's, as a technical choice the owner delegated on 2026-11-15; the rules are the owner's.

### Consequences

- Good, because the with-skill arm has the docs MCP and the baseline has only the web, as a user without the plugin would.
- Bad, because the docs server is a real remote server, so its availability affects the with-skill arm, and the docs say such runs are advisory outside an isolated environment such as a CI runner.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The support plugin declares the docs server | `claude --plugin-dir plugins/hook-engineering/evals/_support/docs-mcp plugin details eval-docs-mcp` | 2026-11-15: `MCP servers (1) claude-code-docs` | After the support plugin changes |
| The support plugin and hook-engineering validate | `claude plugin validate --strict` on both | 2026-11-15: passed | After either changes |
| A case with two `plugins` loads both in the with-arm, starts the docs server and leaves the baseline without it | Probe runs, from each arm's trace | 2026-11-15: failed; `../..` is refused and the support plugin alone replaces the plugin under test | Superseded |
