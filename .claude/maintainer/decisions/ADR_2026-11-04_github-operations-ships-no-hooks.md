---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: ADR_2026-10-29_github-operations-hooks-limit-only-reviewer-agents
superseded-by: none
---

# github-operations ships no hooks

## Scope

`plugins/github-operations/hooks/` (`hooks.json`, `run-hook.sh`, `github_hooks.py`), removed in commit addcea1, and their maintainer tests, removed in commit 8ce8098. Out of scope: the agents' frontmatter tool limits (ADR_2026-11-04_pr-agents-deny-tools-in-frontmatter).

## Context and problem statement

Version 0.5.0 shipped hooks that denied the reviewer agents state-changing `git`, `gh` and GitHub MCP writes. They needed `python3` 3.12 or later and intercepted every GitHub call on the user's machine. Should the redesigned plugin keep them?

## Decision drivers

- A hook runs on the user's machine on every matching call and has to be declared and maintained.
- The redesigned agents are self-contained, each with its own limits.
- `python3` would remain a requirement only for the hooks.

## Considered options

- **Remove the hooks**: chosen.
- **Keep them for the reviewer agents**: rejected; the redesigned agents carry their limits in their own files, and the hooks kept a Python requirement for every user.

## Decision outcome

Chosen option: **remove the hooks**, because the plugin no longer intercepts the user's calls and no longer needs `python3` for that.

### Consequences

- Good, because the plugin runs nothing on the user's tool calls, and `python3` is needed only by the repository setup's label comparison.
- Bad, because the agents' GitHub write bans are kept by their instructions, not by a control. Only the tools named in each agent's `disallowedTools` are removed by Claude Code, and the README shows users how to add hard deny rules.

## More information

Committed by Nery in addcea1 ("hooks removed"). The 0.6.0 CHANGELOG records it as breaking. ADR_2026-10-29_github-operations-hooks-enforce-its-own-rules was already superseded.
