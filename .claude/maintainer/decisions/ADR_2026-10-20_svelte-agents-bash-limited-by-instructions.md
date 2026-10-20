---
status: accepted
date: 2026-10-20
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The svelte-development agents keep Bash limited by their instructions only

## Scope

The two agents of `plugins/svelte-development`: `svelte-code-auditor` and `svelte-component-editor`.

Out of scope: the other plugins' agents and the `pr-tracker` guard of DEBT-001.

## Context and problem statement

Both agents list `Bash` in their `tools`. `svelte-code-auditor` says it audits "without changing" code and "never edits files", but the tools list does not enforce that: Bash can write. Its limit lives in the instructions of the agent file. This was open item N10 of the plugin's review: accept that, or add a plugin `PreToolUse` guard that blocks Bash writes for these agents.

## Decision drivers

- The plugin works well in Nery's use.
- A guard adds a hook, tests and a version bump to the plugin.
- Keep the setup simple.

## Considered options

- **Accept instruction-only limits**: chosen.
- **Add a plugin `PreToolUse` hook that blocks Bash writes for these agents**: rejected for now because of its cost in code, tests and maintenance against a plugin that already works.

## Decision outcome

Chosen option: **accept instruction-only limits**, because the plugin works well in practice and a guard would add code and maintenance (Nery, 2026-10-20).

### Consequences

- Good, because the agents stay as published in 0.1.0, with no new hook to maintain.
- Bad, because the auditor's read-only promise is not enforced: if it ignores its instructions, Bash can change files. No test covers that.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The auditor does not change files in practice | Not checked | Pending | If a user reports an unwanted edit by the auditor |

## More information

Decided in the conversation of 2026-10-20 together with ADR_2026-10-20_discard-svelte-development-claude-app-check. The same conversation also kept three things as they were, without a record of their own: the two `SKILL.md` files of about 24 KB are not slimmed, references may name each other in prose (the Skill Gate bans only links), and the README's Claude Code 2.1.303 stays worded as the version the agent skill preload was verified on, not a proven minimum.
