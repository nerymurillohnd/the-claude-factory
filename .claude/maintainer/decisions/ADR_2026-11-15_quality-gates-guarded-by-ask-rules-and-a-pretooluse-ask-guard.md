---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Quality gates are guarded by ask rules and a PreToolUse ask guard, not deny rules

## Scope

- `.claude/settings.json`: the `permissions.ask` entries for gate configuration, instructions, settings, workflows and `.claude/hooks/**`, and the `PreToolUse` hook registration.
- `.claude/hooks/guard-quality-gates.py`: the guard itself.
- Out of scope: the `permissions.deny` entries that stay hard refusals, such as force pushes, `pip` and direct lockfile edits.

## Context and problem statement

Claude can loosen a quality gate in several ways: editing the lint, format, type-check or workflow-audit configuration, the project instructions or settings, or the CI workflows, or adding an inline suppression. The owner wants to decide each such change, without forbidding the changes the owner approves.

A matching deny rule refuses the call even when a PreToolUse hook returns `ask`, so a deny rule never lets the owner's prompt appear (https://code.claude.com/docs/en/permissions). An ask rule or a hook's `ask` forces a prompt even in auto mode (https://code.claude.com/docs/en/permission-modes, https://code.claude.com/docs/en/hooks).

## Decision drivers

- The owner decides every change that could loosen a gate.
- An approved change must still go through, without editing settings first.
- The prompt must appear in every permission mode, auto mode included.
- Maintainer work under `scripts/` must not stop for a prompt on every edit.

## Considered options

- **Ask rules plus a PreToolUse guard that answers `ask`**: chosen.
- **Deny rules on the gate files**: rejected because a deny rule refuses the call before the hook's prompt reaches the owner, so an approved change could not land without editing settings first.
- **Guarding all of `scripts/`**: rejected because it would prompt on routine maintainer work. Only `scripts/pyrightconfig.json` stays protected.

## Decision outcome

Chosen option: **Ask rules plus a PreToolUse guard that answers `ask`**, because a prompt is the only outcome that both lets the owner decide and lets an approved change land, in every permission mode.

### Consequences

- Good, because every edit of a protected file, and every new inline suppression, reaches the owner as a prompt that gives the reason.
- Good, because the guard also covers Bash commands that name a protected file and can write it, which ask rules on `Edit` alone don't cover.
- Good, because input the guard cannot read blocks the call (exit 2), so the guard fails closed.
- Bad, because the Bash check reads the command's words: a path built at run time, a script file or an npm script passes. The guard is a barrier for Claude, not a security boundary.
- Bad, because edits to the protected files now always need the owner at the keyboard.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The guard answers `ask` on protected paths and new suppressions, and stays silent otherwise | 17 synthetic probes, 2026-11-14 | Passed | Any change to the guard |
| A live session shows the prompt | In a session started in the repository, ask Claude to add a `# noqa` and watch for the prompt | Not required: the owner dropped the live test on 2026-11-16 | none |

## More information

- The owner made this decision on 2026-11-14. It was built in commits a25cdfa, e5c1b11 and 8de5124 and reached `main` in ceecd50 ([#107](https://github.com/nerymurillohnd/the-claude-factory/pull/107)) on 2026-11-15.
- The live test was not observed on 2026-11-14 because that session's working directory became `/home/user` after a second repository was attached, so the project's hooks and ask rules did not load.
