---
name: write-records
description: Writes architecture decision records (ADRs) and keeps a technical-debt ledger. Use when an important decision is made, a problem cannot be fixed now, or logged debt is fixed.
---

# Write records

## What this is

- A skill that keeps a project's memory in Markdown files.
- It covers two kinds of record: ADRs and the technical-debt ledger.
- Each kind has a procedure in `references/` and templates in `assets/`.
- The records answer one question: why is the project the way it is?

## Role

- Act as the project's record keeper.
- Record decisions and postponed problems before the task ends.
- Record without asking permission. The user installed this plugin for that.
- Ask only for facts you are missing.
- Write only what is verified or what the user said.
- Keep one source of truth. Never leave the same record in two places.

## Rules

### Always

- Search the existing records before adding one. Update the match instead of duplicating it.
- Mark anything unverified as an inference or as pending.
- Mention a record elsewhere by its ID only: the ADR file name without `.md`, or `DEBT-<NNN>`.
- Keep each ledger index equal to its entries.
- Name an ADR with the pattern of the ADRs already in its folder.
- Write dates as `YYYY-MM-DD`, using today's date.
- Save records relative to the checkout you work in: the root that `git rev-parse --show-toplevel` prints, or the current directory outside git.
- Keep every destination inside the project, symlinks included.
- When a destination is protected or unwritable, show the draft and the exact blocker.

### Never

- Never rewrite an accepted ADR or a resolved entry. Supersede it.
- Never log a problem that can be fixed now. Fix it.
- Never write a decision or a debt item into a README, changelog, code comment, commit message, task list or memory.
- Never leave an unfilled placeholder or template instructions in an entry. A ledger keeps its reusable "Entry format" comment.
- Never move, overwrite or delete a project's existing records without the user's explicit OK.
- Never use the plugin's install directory as a base.
- Never use the session's project-directory variable (`CLAUDE_PROJECT_DIR`) as a base. In a worktree it still points at the main checkout, where edits are blocked.
- Never relocate a record or widen permissions to get past a blocker.
- Never commit or push a record unless the user asks.

## References

- [ADRs](references/adrs.md): read when you write, supersede or check a decision record. Template: [ADR template](assets/ADR_YYYY-MM-DD_decision-slug.md).
- [Existing records](references/existing-records.md): read before you create the first folder of a kind, to find and migrate records the project already keeps elsewhere. Templates: [ADR template](assets/ADR_YYYY-MM-DD_decision-slug.md) and [pending debt](assets/pending-debt.md).
- [Technical debt](references/technical-debt.md): read when you log, update or resolve a debt item. Templates: [pending debt](assets/pending-debt.md) and [resolved debt](assets/resolved-debt.md).

## Instructions

### 1. Settle the location

Do this once per task, before the first search or write.

1. Use the location the project already defines: a path in its `CLAUDE.md` or `AGENTS.md`, or an existing folder such as `docs/adr/`, `doc/adr/` or `docs/decisions/`.
2. Otherwise use `docs/decisions/` and `docs/technical-debt/`.

Below, `<decisions>` and `<debt>` stand for the two folders.

- Decisions: one file per decision, named `<decisions>/ADR_<YYYY-MM-DD>_<slug>.md`. If `<decisions>` already holds ADRs with another naming pattern, copy that pattern.
- Pending debt: `<debt>/pending-debt.md`.
- Resolved debt: `<debt>/resolved-debt.md`.

Create a folder or ledger the first time it is needed. Installing the plugin creates nothing.

### 2. Look for existing records

Do this before you create the first folder of each kind. It keeps one source of truth.

- Decisions: do it when `<decisions>` does not exist yet.
- Debt and pending items: do it when `<debt>` does not exist yet.

Then:

1. Read [Existing records](references/existing-records.md).
2. Find the project's own documents for that kind. Skip any folder you settled in step 1.
3. Show the user what you found. Ask whether to consolidate and migrate it.
4. Migrate only what the user approves, in step 4.

In a non-interactive session, find and migrate nothing. Name what you found in your one-line note.

### 3. Ask about git on first use

Do this before you create the first records folder.

Ask only when all of these hold:

- The project is a git repository.
- Neither `<decisions>` nor `<debt>` exists yet, even if the project's `CLAUDE.md` or `AGENTS.md` names them.
- Git does not already ignore both paths. Check with `git check-ignore -q <path>`.

Then:

1. Ask one question with your question tool. Put the recommendation first and give its reason.
   - **Track them (Recommended):** the records are committed with the project, so the team shares them and they survive a new clone.
   - **Keep them local:** the records stay on this machine and are not shared.
2. Apply the answer to both folders at once. Never ask again.
   - Keep them local: add `<decisions>/` and `<debt>/` to the `.gitignore` at the checkout root. Create the file if it is missing. Add only those two lines.
   - Track them: change nothing.

In a non-interactive session, do not ask. Track the records, change nothing, and say so in your one-line note.

### 4. Migrate approved records

Do this after step 3, only when the user approved a migration in step 2.

1. Create the folders.
2. Follow the migration steps in [Existing records](references/existing-records.md).
3. Ask what to do with each original. Change nothing before the user answers.

### 5. Decide whether to record

Record a decision that:

- chooses one approach over another, with consequences that last,
- changes the architecture, a process, a dependency, security, or how the project is built, released or distributed,
- sets the scope or shape of a component, such as extending an existing module or creating an independent one,
- would be hard to undo, or that someone may later question with "why did we do it this way?".

Skip:

- renames, typos, formatting and comments,
- a small refactor that keeps behavior,
- a choice an existing ADR already covers.

### 6. Route the work

1. An important decision is made, or the user asks for an ADR: read [ADRs](references/adrs.md), then write the record.
   - Several decisions? Ask how to register them first: [choose how to register](references/adrs.md#choose-how-to-register).
2. A problem cannot be fixed now, or the user asks to log debt: read [Technical debt](references/technical-debt.md), then log it.
3. A logged problem is fixed: read [Technical debt](references/technical-debt.md), verify the fix, then move the entry to resolved.

In a non-interactive session, return the unanswered questions. Leave the records that depend on them pending.

### 7. Report

Tell the user in one line what you recorded and where.

Example:

- Input: "We decided to keep sessions in Postgres, not Redis."
- Output: the file `docs/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md`, then the line "Recorded the decision in `docs/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md`."

## Checklist

Check each item before you finish.

- [ ] The location is settled and every path stays inside the checkout.
- [ ] Existing records were looked for before the first folder of each kind.
- [ ] Nothing existing was moved, overwritten or deleted without the user's OK.
- [ ] No record lives in two places, or the user chose to keep both.
- [ ] The git question was asked once, or was not needed.
- [ ] The existing records were searched first. No duplicate exists.
- [ ] Every claim is verified, stated by the user, or marked pending.
- [ ] No placeholder or template instruction remains in an entry.
- [ ] The ADR file name follows the pattern of its folder.
- [ ] Each ledger index equals its entries.
- [ ] No accepted ADR or resolved entry was rewritten.
- [ ] Nothing was committed or pushed.
- [ ] The user got a one-line note with the file and its ID.
