---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# project-maintainer's guardrails follow the engine's declarations and require Claude Code v2.1.307

## Scope

Applies to the `tool.check` answers of the project-maintainer mod (`plugins/project-maintainer/hooks/register.ts`), its tests and the minimum Claude Code version its README and CHANGELOG state. Other plugins and the rules of the records themselves are out of scope.

## Context and problem statement

Claude Code 2.1.307 removed `decider` from a mod's `tool.check` result, with no changelog entry (2.1.295 to 2.1.308 read in full). The guardrails returned `decider: 'person'`, so 5 of 50 tests failed (DEBT-005). The mod docs pages describe a `tool.check` answer only as `{ decision, reason }`. They also say to trust the declarations the engine writes for the installed build over any page (Create a mod → Get type definitions for your version; Reference, opening note). The 2.1.308 declarations pin `plugin` on a hook's `ask`, put it to a person, and let no classifier's allow settle it. Which contract should the guardrails, their tests and the README follow?

## Decision drivers

- The guard must keep putting a settled-record change to the person, in every permission mode where someone can answer.
- The live official docs win over project text, and the docs name the installed declarations as the authority.
- Tests must fail on an engine that does not route a hook's `ask` to a person.

## Considered options

- **Answer `{ decision: 'ask', reason }`, assert `plugin`, require v2.1.307**: chosen.
- **Keep `decider: 'person'` alongside for 2.1.304 to 2.1.306**: rejected because the field is no longer part of the installed contract, and writing a field the engine ignores copies a dead pattern.
- **Follow the docs pages only (assert `decision` and `reason`, drop the auto-mode promise from the README)**: applied first, then rejected the same day, because the docs themselves make the declarations the authority and that option dropped a guarantee the engine gives.

## Decision outcome

Chosen option: **answer `{ decision: 'ask', reason }`, assert `plugin`, require v2.1.307**, because it follows the contract the docs designate and makes the suite prove the routing the README promises.

### Consequences

- Good, because the suite passes 54/54 on 2.1.307 and 2.1.308 and fails on 2.1.306, so an engine without the routing is caught.
- Good, because the README can promise that no classifier approves a guardrail prompt, citing the version.
- Bad, because users on 2.1.304 to 2.1.306 who update the plugin first can have auto mode's classifier approve a guarded edit.
- Bad, because the declarations are early access: the next silent change can break the guardrails again.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| The mod API changes again without a changelog entry | Any Claude Code release | Gate red, or the guard weakens for users | `.claude/rules/mods.md` lessons; planned stale-declarations gate and weekly mod check | Nery |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The guard's ask reaches a person in auto mode | Live run, accepted ADR, `--permission-mode auto` | Passed on 2026-10-22 (2.1.308): dialog shown, declined, file unchanged | After a Claude Code release that touches mods |
| The suite detects an engine without the routing | `claude plugin test` on 2.1.306, 2.1.307 and 2.1.308 | 44/50 on 2.1.306; 50/50 on the others at that commit | When the declarations change |

## More information

Shipped in project-maintainer 0.2.0 ([PR #43](https://github.com/nerymurillohnd/the-claude-factory/pull/43)). Closes DEBT-005. Related: ADR_2026-10-22_mod-guardrails-fail-closed-for-records.
