---
status: accepted
date: 2026-11-04
decision-makers:
  - "Claude, in the session of 2026-11-04"
informed:
  - "Nery"
supersedes: none
superseded-by: none
---

# The init commands run only when the user types them

## Scope

`plugins/github-operations/commands/init-pr-lifecycle.md` and `init-cleanup-and-debug.md` (commit 978e294). The skills keep their default invocation.

## Context and problem statement

Both commands had only a `description` in their frontmatter, so Claude could run them on its own. Their bodies open with "You are authorized to use the … skill", which would then be an authorization Claude gave itself. Command files take the same frontmatter as skills (code.claude.com/docs/en/skills, read 2026-11-04).

## Decision drivers

- An authorization must come from the user.
- The skills stay available for Claude to load on its own, behind their own "ask first" rule.

## Considered options

- **`disable-model-invocation: true` on both commands**: chosen.
- **Also on the skills**: rejected because it removes their descriptions from Claude's context, so Claude could no longer pick them for a request.
- **Leave the commands as they were**: rejected because of the self-authorization.

## Decision outcome

Chosen option: **`disable-model-invocation: true` on both commands**, plus an `argument-hint` on the commands and on three skills for the PR, run or repository they take.

### Consequences

- Good, because a command runs only when the user types it, and its description no longer takes context.
- Neutral, because the commands remain in the older `commands/` format, which Nery chose; the docs prefer skills for new work.

## More information

Applied while checking the plugin against the Claude Code skills documentation Nery shared on 2026-11-04. Nery did not object.
