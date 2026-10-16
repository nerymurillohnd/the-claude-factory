---
name: project-records
description: Use to record an important decision, to log pending technical debt, and every time logged debt is resolved.
---

# Project records

Keep the maintainers' decisions and unfixed technical debt in files, so nobody has to rediscover why the project is the way it is. Each kind of record has a procedure in `references/` and a template in `assets/`.

## Where records live

- Decisions: `.claude/maintainer/decisions/ADR_<YYYY-MM-DD>_<slug>.md`, one file per decision.
- Pending debt: `.claude/maintainer/technical-debt/pending-debt.md`.
- Resolved debt: `.claude/maintainer/technical-debt/resolved-debt.md`.
- Create a folder or ledger the first time it is needed. There is no setup step.

## When to act

Act before finishing the task, not after. Record without asking permission. Ask only for facts you are missing, then tell Nery in one line what you recorded and where.

1. An important decision is made: read `references/decision-records.md`, then write the ADR.
2. A problem is found that cannot be fixed now: read `references/debt-ledger-open.md`, then log it.
3. A logged problem is fixed: read `references/debt-ledger-resolve.md`, verify the fix, then move the entry to resolved.

## What counts as an important decision

Record a decision that:

- chooses one approach over another, with consequences that last,
- changes the architecture, a process, a dependency, security, or how the project is built, released or distributed,
- sets the scope or shape of a plugin, such as integrating into an existing plugin or creating an independent one,
- would be hard to undo, or that someone may later question with "why did we do it this way?".

Do not record renames, typos, formatting, comments, a small refactor that keeps behavior, or a choice an existing ADR already covers.

## Do

- Search the existing records before adding one. Update the match instead of duplicating it.
- Write only what is verified or what Nery said. Mark the rest as an inference or as pending, because a record that guesses misleads the next reader.
- Mention a record elsewhere by its ID only: the ADR file name without `.md`, or `DEBT-<NNN>`.
- Keep each ledger index equal to its entries.
- Use today's local date, from `date +%F`.

## Do not

- Do not rewrite an accepted ADR or a resolved entry. Supersede it, so the history stays true.
- Do not log a problem that can be fixed now. Fix it.
- Do not write a decision or a debt item into a README, changelog, code comment, commit message, task list or memory.
- Do not leave a placeholder or a template comment in a record.

## References

- `references/decision-records.md`: write, supersede and check an ADR. Template: `assets/ADR_YYYY-MM-DD_decision-slug.md`.
- `references/debt-ledger-open.md`: what belongs in the ledger, how to log and update an item. Template: `assets/pending-debt.md`.
- `references/debt-ledger-resolve.md`: verify a fix, move the item, keep history. Template: `assets/resolved-debt.md`.
