---
paths:
  - "plugins/*/evals/**"
  - "scripts/evals-config.json"
  - "scripts/run-evals.sh"
---

# Eval Rules

- Never work from memory: load the plugin-evals skill, use the Claude Code Docs MCP tools, and read the Claude Code changelog for the installed version, the four before it and every newer one. Apply what changed. Never invent or assume a format or behavior.
- Runs never ask for permission: a tool you did not grant is removed, Bash writes stay in the run's workspace, no `.claude/` directory loads (not even one a `scaffold_script` wrote), and the temporary home has no `userConfig` values. Grade the attempt and the reply. Source: `/en/plugin-evals` → "Grant tools" and "How runs are isolated".
- Give the plugin an entry in `scripts/evals-config.json`: the tools the cases need, `max_cost_usd` and the `cost_basis` it was measured from.
- CI runs the suite only for plugins with an `evals/` folder that changed.
- A plugin without evals is tested with the methods the official docs recommend for its component types.
