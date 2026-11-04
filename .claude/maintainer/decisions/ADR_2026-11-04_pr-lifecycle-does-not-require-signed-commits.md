---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# The PR lifecycle does not require signed commits

## Scope

`plugins/github-operations/agents/pr-lifecycle/pr-fixer.md`, `skills/auto-pr-lifecycle/SKILL.md` and `skills/github-files-setup/SKILL.md` (commit c90db85).

## Context and problem statement

The fixer had to commit signed and check that signing was set up, and the skill verified that every commit was signed. A user who does not sign commits had no fixer status for that case and was blocked. Should the plugin require signing?

## Decision drivers

- Third-party users with any git setup must be able to use the plugin.
- Git signs on its own when the user's configuration says to.

## Considered options

- **Commit as the user's git setup does, with no signing requirement**: chosen.
- **Require signed commits**: rejected because it blocks every user who does not sign.

## Decision outcome

Chosen option: **no signing requirement**. The plugin stays silent about signing: commits are signed when the user's git is configured to sign. The rule that forbids changing git's configuration and the ban on `--no-gpg-sign` in `cleanup-and-debug` stay.

### Consequences

- Good, because users who do not sign are no longer blocked.
- Bad, because nothing checks a repository's signed-commit rule before a push; a ruleset that requires signatures rejects the push, and the main session sees that error when it pushes.

## More information

Decided by Nery on 2026-11-04: "eliminar lo referente a firmar. Cuando existe una firma, claude code por default se utiliza".
