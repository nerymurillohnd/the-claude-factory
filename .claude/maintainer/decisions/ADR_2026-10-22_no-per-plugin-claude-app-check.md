---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-20_discard-svelte-development-claude-app-check
superseded-by: none
---

# No plugin waits on a Claude app check run by the maintainer

## Scope

- In scope: the release requirements in `.claude/CLAUDE.md`, the closing checks of a new plugin in `.claude/rules/WORKFLOW.md`, the MCP test step of the `plugin-mcp-guidance` skill and the issue-confirmation step of the `github-workflow` skill, for every plugin that is not Claude Code-only.
- Out of scope: what `docs/compatibility.md` and each README claim about the Claude app, which stays required to match the official pages.

## Context and problem statement

`.claude/CLAUDE.md` required "the Claude app check passes" before a release, and `.claude/rules/WORKFLOW.md` said Nery runs that check in a Cowork session and a chat conversation. ADR_2026-10-20_discard-svelte-development-claude-app-check dropped the check for svelte-development 0.1.0 only and kept the rule. On 2026-10-22 a missing app check for hook-engineering 0.2.0 was logged as debt, and Nery rejected it: "Yo no tengo porque estar instalando cada plugin para verificarlo. esto es para terceros. si yo instalo alguno es porque lo considero util tambien para mi, y lo hago como lo haria cualquier otro usuario" (stated by Nery on 2026-10-22, who said it had been agreed before).

## Decision drivers

- The plugins are built for third parties; Nery installs one only when it is useful to him, as any user would.
- A requirement that waits on the maintainer's manual check leaves open items and debt that never close.

## Considered options

- **Drop the per-plugin Claude app check; Claude app support comes from `docs/compatibility.md` and the official claude.com and support.claude.com pages, and what was not observed live is stated as unverified**: chosen.
- **Keep the check and discard it plugin by plugin, as for svelte-development**: rejected, because it keeps a rule the maintainer does not run.

## Decision outcome

Chosen option: **drop the per-plugin Claude app check**, because the plugins are for third parties and Nery does not install each one to verify it. What was not observed live is stated as unverified in the README or the report, and is never logged as debt, an open item or a release blocker.

### Consequences

- Good, because releases and records no longer wait on a manual check that does not happen.
- Bad, because Claude app behavior is known only from the official docs until a user reports otherwise; a user report or issue is the signal to look again.

## More information

- Applied in commit 54d8a15 (`.claude/CLAUDE.md`, `.claude/rules/WORKFLOW.md`, `plugin-mcp-guidance`, `github-workflow`) on 2026-10-22; this record was written afterwards, the same day.
