---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# project-maintainer's guardrails fail closed for the records only

## Scope

Applies to the `.catch` handlers of the format guard (`tool.call`) and the authority guard (`tool.check`) in `plugins/project-maintainer/hooks/register.ts`, and to `mayWriteRecord` in `hooks/guard.ts`. The Bash guard and the rules of the records are out of scope.

## Context and problem statement

In 0.1.0, a broken format check logged and saved the record unchecked, which is what the guard exists to prevent. A broken authority check asked the person before every Write and Edit in the project. The mod docs (Events → Handle a hook that fails) say a blocking hook fails closed with `.catch`. How should each guard behave when its own check breaks?

## Decision drivers

- A record must never be saved unchecked or rewritten without the person because a check broke.
- A broken check must not block or prompt on files outside the records.
- The decision in `.catch` must not depend on a `$` call, which may be what failed.

## Considered options

- **Fail closed for the records only**: chosen. The format guard refuses a record it could not check and tells Claude to retry. The authority guard asks for a record, keeps the verdict beneath for any other file, never turns a deny into an ask, and still asks when that verdict cannot be read. `mayWriteRecord` decides with no `$` call; a relative or unreadable path counts as a record.
- **Fail closed for every Write and Edit**: rejected because one broken check would block or prompt on every edit in the project.
- **Keep 0.1.0's fail-open format guard**: rejected because it saves exactly the malformed record the guard exists to stop.

## Decision outcome

Chosen option: **fail closed for the records only**, because it holds the guard where it matters and keeps a broken check from disrupting work elsewhere.

### Consequences

- Good, because a broken check can no longer let a malformed or settled record through.
- Good, because other files keep the verdict they would get without the mod.
- Bad, because a relative path outside the records is refused or asked about while a check is broken. Write and Edit take absolute paths, so this is rare.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Each case behaves as decided | Tests in `tests/register.test.ts` and `tests/guard.test.ts`, each shown to fail against the previous code | Passed on 2026-10-22 | When either `.catch` changes |

## More information

Two of the cases (relative paths, an unreadable verdict beneath) came from findings of the automated security review on the branch. Shipped in project-maintainer 0.2.0 ([PR #43](https://github.com/nerymurillohnd/the-claude-factory/pull/43)). Related: ADR_2026-10-22_mod-guardrails-follow-engine-declarations.
