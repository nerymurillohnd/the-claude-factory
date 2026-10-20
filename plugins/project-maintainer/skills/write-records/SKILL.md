---
name: write-records
description: Writes and maintains a project's architecture decision records (ADRs) and its technical-debt ledger. Use when an important decision is made, when a problem is found that cannot be fixed now, when logged debt is fixed, or when the user asks to record a decision, write an ADR, log technical debt or resolve a debt item. Searches for duplicates first, writes from templates and never rewrites an accepted record.
---

# Write records

Keep a project's important decisions and the technical debt it cannot fix yet in files, so nobody has to rediscover why the project is the way it is. There are two kinds of record. Each has a procedure in `references/` and templates in `assets/`.

## Where records live

Settle the location once per task, before the first search or write.

1. Use the location the project already defines: a path in its `CLAUDE.md` or `AGENTS.md`, or an existing decisions or debt folder such as `docs/adr/`, `doc/adr/` or `docs/decisions/`.
2. Otherwise use `docs/decisions/` and `docs/technical-debt/`.

Below, `<decisions>` and `<debt>` stand for the two folders.

- Decisions: `<decisions>/ADR_<YYYY-MM-DD>_<slug>.md`, one file per decision.
- Pending debt: `<debt>/pending-debt.md`.
- Resolved debt: `<debt>/resolved-debt.md`.
- Create a folder or ledger the first time it is needed. There is no setup step. Installing the plugin creates nothing.
- Paths are relative to the checkout you are working in: the root that `git rev-parse --show-toplevel` prints, or the current directory outside git. Never use the plugin's install directory, and never the session's project-directory variable (`CLAUDE_PROJECT_DIR`): in a worktree it still points at the main checkout, where edits are blocked.
- Never move a project's existing records to another location.
- Check that the destination stays inside the project, symlinks included. If it is protected or unwritable, show the draft and the exact blocker. Do not relocate the record or widen permissions.

## When to act

Act before finishing the task, not after. Do not ask permission to record: the user installed this plugin to have these records kept. Ask only for facts you are missing. Then tell the user in one line what you recorded and where. In a non-interactive session, such as `claude -p`, return the unanswered questions and leave the records that depend on them pending.

1. An important decision is made, or the user asks for an ADR: read [ADRs](references/adrs.md), then write the record. With several decisions, ask how to register them first: [choose how to register](references/adrs.md#choose-how-to-register).
2. A problem is found that cannot be fixed now, or the user asks to log debt: read [Technical debt](references/technical-debt.md), then log it.
3. A logged problem is fixed: read [Technical debt](references/technical-debt.md), verify the fix, then move the entry to resolved.

## What counts as an important decision

Record a decision that:

- chooses one approach over another, with consequences that last,
- changes the architecture, a process, a dependency, security, or how the project is built, released or distributed,
- sets the scope or shape of a component, such as extending an existing module or creating an independent one,
- would be hard to undo, or that someone may later question with "why did we do it this way?".

Do not record renames, typos, formatting, comments, a small refactor that keeps behavior, or a choice an existing ADR already covers.

## Do

- Search the existing records before adding one. Update the match instead of duplicating it.
- Write only what is verified or what the user said. Mark the rest as an inference or as pending, because a record that guesses misleads the next reader.
- Mention a record elsewhere by its ID only: the ADR file name without `.md`, or `DEBT-<NNN>`.
- Keep each ledger index equal to its entries.
- Use today's date in `YYYY-MM-DD`.

## Do not

- Do not rewrite an accepted ADR or a resolved entry. Supersede it, so the history stays true.
- Do not log a problem that can be fixed now. Fix it.
- Do not write a decision or a debt item into a README, changelog, code comment, commit message, task list or memory.
- Do not leave an unfilled placeholder or template instructions in an entry. A ledger keeps its reusable "Entry format" comment.
- Do not commit or push a record unless the user asks.

## References

- [ADRs](references/adrs.md): write, supersede and check a decision record. Template: [ADR template](assets/ADR_YYYY-MM-DD_decision-slug.md).
- [Technical debt](references/technical-debt.md): what belongs in the ledger, how to log, update and resolve an item. Templates: [pending debt](assets/pending-debt.md) and [resolved debt](assets/resolved-debt.md).
