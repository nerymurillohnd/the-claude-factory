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
- Write dates as `YYYY-MM-DD`, using today's date.
- Save records under `.claude/maintainer/` in the checkout you work in: the root that `git rev-parse --show-toplevel` prints, or the current directory outside git.
- Write records with the Write tool, never with Bash. `.claude/` is a protected folder, and Write creates the missing folders.
- Keep every destination inside the project, symlinks included.
- When the user denies a write or a destination is unwritable, show the draft and the exact blocker.

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

### 1. Know where records live

The locations are fixed. Never choose another one.

- Decisions: `.claude/maintainer/decisions/ADR_<YYYY-MM-DD>_<slug>.md`, one file per decision.
- Pending debt: `.claude/maintainer/technical-debt/pending-debt.md`.
- Resolved debt: `.claude/maintainer/technical-debt/resolved-debt.md`.

Create a folder or ledger the first time it is needed. Installing the plugin creates nothing.

Claude Code protects `.claude/`. The first write of a session can ask the user for permission. Wait for the answer. Do not work around it.

### 2. Look for existing records

Do this before you create the first folder of each kind. It keeps one source of truth.

- Decisions: do it when `.claude/maintainer/decisions` does not exist yet.
- Debt and pending items: do it when `.claude/maintainer/technical-debt` does not exist yet.

Then:

1. Read [Existing records](references/existing-records.md).
2. Find the project's own documents for that kind.
3. Show the user what you found. Ask whether to consolidate and migrate it.
4. Migrate only what the user approves, in step 4.

In a non-interactive session, find and migrate nothing. Name what you found in your one-line note.

### 3. Ask about git on first use

Do this before you create the first records folder.

Ask only when all of these hold:

- The project is a git repository.
- `.claude/maintainer/` does not exist yet.
- Git does not already ignore it. Check with `git check-ignore -q .claude/maintainer/`.

Then:

1. Ask one question with your question tool. Put the recommendation first and give its reason.
   - **Track them (Recommended):** the records are committed with the project, so the team shares them and they survive a new clone.
   - **Keep them local:** the records stay on this machine and are not shared.
2. Apply the answer once. Never ask again.
   - Keep them local: add `.claude/maintainer/` to the `.gitignore` at the checkout root. Create the file if it is missing. Add only that line.
   - Track them: change nothing.

In a non-interactive session, do not ask. Track the records, change nothing, and say so in your one-line note.

### 4. Migrate approved records

Do this after step 3, only when the user approved a migration in step 2.

1. Follow the migration steps in [Existing records](references/existing-records.md). Write creates the folders.
2. Ask what to do with each original. Change nothing before the user answers.

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
- Output: the file `.claude/maintainer/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md`, then the line "Recorded the decision in `.claude/maintainer/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md`."

## Checklist

Check each item before you finish.

- [ ] Every record is under `.claude/maintainer/` in the checkout, written with the Write tool.
- [ ] Existing records were looked for before the first folder of each kind.
- [ ] Nothing existing was moved, overwritten or deleted without the user's OK.
- [ ] No record lives in two places, or the user chose to keep both.
- [ ] The git question was asked once, or was not needed.
- [ ] The existing records were searched first. No duplicate exists.
- [ ] Every claim is verified, stated by the user, or marked pending.
- [ ] No placeholder or template instruction remains in an entry.
- [ ] Each ledger index equals its entries.
- [ ] No accepted ADR or resolved entry was rewritten.
- [ ] Nothing was committed or pushed.
- [ ] The user got a one-line note with the file and its ID.
