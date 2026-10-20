---
name: write-records
description: Writes architecture decision records (ADRs) and keeps a technical-debt ledger. Use when an important decision is made, a problem cannot be fixed now, or logged debt is closed.
---

# Write records

## What this is

- A skill that keeps a project's memory in Markdown files.
- It covers two kinds of record: ADRs, and the technical-debt ledgers (pending and closed).
- Each kind has a procedure in `references/` and templates in `assets/`.
- The records answer one question: why is the project the way it is?

## Role

- Act as the project's record keeper.
- Record decisions and postponed problems before the task ends.
- Record without asking permission. The user installed this plugin for that.
- Ask only for facts you are missing, and for the questions the procedures name, for example: migrating documents the project already keeps, git, approving an edit to a settled record.
- Write only what is verified or what the user said.
- Keep one source of truth. Never leave the same record in two places.
- Non-interactive means nobody can answer you: you have no question tool, or the prompt says nobody will answer, as in `claude -p`, the Agent SDK or CI. Then write no record that depends on an unanswered question. Return the questions in your final reply.

## Rules

### Always

- Search `.claude/maintainer/` for a record on the same subject before adding one. Update a debt match. Change an ADR match only as the ADRs reference allows.
- Mark anything unverified as an inference or as pending.
- Mention a record inside another record by its ID only: the ADR file name without `.md`, or `DEBT-<NNN>`. Links to evidence, such as issues and pull requests, stay Markdown links. In your report to the user, give the file path.
- Keep each ledger index equal to its entries.
- Write dates as `YYYY-MM-DD`, using today's date.
- Save records under `.claude/maintainer/` in the checkout you work in: the root that `git rev-parse --show-toplevel` prints, or the current directory outside git.
- Create a record with the Write tool and change an existing one with the Edit tool. Never use Bash to write a record. `.claude/` is a protected folder, and Write creates the missing folders.
- Run every command from the checkout root, so relative paths mean the same thing for every command.
- Keep every destination inside the project, symlinks included.
- When the user denies a write or a destination is unwritable, show the draft and the exact blocker.

### Never

- Never rewrite a settled record: an ADR that is not `proposed`, or a closed debt entry. Supersede it.
- Never group decisions. One ADR per decision.
- Never log a problem that can be fixed now inside the current task. Fix it. If it falls outside the task, tell the user.
- Never write a decision or a debt item into a README, changelog, code comment, commit message, task list or memory.
- Never leave an unfilled placeholder or template instructions in an entry. A ledger keeps its reusable "Entry format" comment.
- Never move, overwrite or delete a document the project kept before this plugin without the user's explicit OK. Superseding an ADR and closing a debt item need no OK.
- Never use the plugin's install directory as a base.
- Never use the session's project-directory variable (`CLAUDE_PROJECT_DIR`) as a base. In a worktree it still points at the main checkout, where edits are blocked.
- Never relocate a record or widen permissions to get past a blocker.
- Never commit or push a record unless the user asks.

## References

- [ADRs](references/adrs.md): read when you write, change or check a decision record. Template: [ADR template](assets/ADR_YYYY-MM-DD_decision-slug.md).
- [Existing records](references/existing-records.md): read before you create the first folder of a kind, to find and migrate records the project already keeps elsewhere. Templates: [ADR template](assets/ADR_YYYY-MM-DD_decision-slug.md) and [pending debt](assets/pending-debt.md).
- [Technical debt](references/technical-debt.md): read when you log, update or close a debt item. Templates: [pending debt](assets/pending-debt.md) and [closed debt](assets/closed-debt.md).

## Instructions

### 1. Know where records live

The locations are fixed. Never choose another one.

- Decisions: `.claude/maintainer/decisions/ADR_<YYYY-MM-DD>_<slug>.md`, one file per decision.
- Pending debt: `.claude/maintainer/technical-debt/pending-debt.md`.
- Closed debt: `.claude/maintainer/technical-debt/closed-debt.md`.

Create a folder or ledger the first time it is needed. Installing the plugin creates nothing.

Claude Code protects `.claude/`. The first write of a session can ask the user for permission. Wait for the answer. Do not work around it.

### 2. Decide whether to record

An explicit request from the user to record something wins over the skip list.

Record a decision that matches at least one of these:

- It chooses one approach over another, with consequences that last.
- It changes the architecture, a process, a dependency, security, or how the project is built, released or distributed.
- It sets the scope or shape of a component, such as extending an existing module or creating an independent one.
- It would be hard to undo, or someone may later question it with "why did we do it this way?".

Skip:

- renames, typos, formatting and comments,
- a small refactor that keeps behavior,
- a choice an existing ADR already covers and still holds. A new choice on the same topic changes that ADR: record it.

Record a problem as debt when it cannot be fixed now. The [Technical debt](references/technical-debt.md) reference sets the criteria. Close a logged item when it is fixed, no longer applies, or the user decides to keep it for good.

Nothing to record or close? Stop here. Create nothing and ask nothing.

### 3. Look for existing records

Do this before you create the first folder of each kind. It keeps one source of truth. Look only for the kind whose folder is missing.

- Decisions: do it when `.claude/maintainer/decisions` does not exist yet.
- Debt and pending items: do it when `.claude/maintainer/technical-debt` does not exist yet.

Then:

1. Read [Existing records](references/existing-records.md).
2. Find the project's own documents for that kind.
3. Show the user what you found. Ask whether to consolidate and migrate it.
4. Migrate only what the user approves, in step 5.

In a non-interactive session, run steps 1 and 2 of that reference read-only. Ask nothing, migrate nothing, and list the candidates you found in your report.

### 4. Ask about git on first use

Do this before you create the first records folder.

Ask only when all of these hold:

- The project is a git repository.
- `.claude/maintainer/` does not exist yet.
- Git does not already ignore it. Check with `git check-ignore -q .claude/maintainer/`. Exit 0 means ignored.

Then:

1. Ask one question with your question tool. Put the recommendation first and give its reason.
   - **Track them (Recommended):** the records are committed with the project, so the team shares them and they survive a new clone.
   - **Keep them local:** the records stay on this machine and are not shared.
2. Apply the answer once. Never ask again.
   - Keep them local: add `.claude/maintainer/` to the `.gitignore` at the checkout root. Create the file if it is missing. Add only that line.
   - Track them: change nothing.

In a non-interactive session, do not ask. Track the records, change nothing, and say so in your report.

### 5. Migrate approved records

Do this after step 4, only when the user approved a migration in step 3.

1. Follow steps 4 to 6 of [Existing records](references/existing-records.md). Write creates the folders. Step 5 asks what to do with each original: change none before the user answers for it.

### 6. Route the work

1. An important decision is made, or the user asks for an ADR: read [ADRs](references/adrs.md), then write one record per decision.
2. A problem cannot be fixed now, or the user asks to log debt: read [Technical debt](references/technical-debt.md), then log it.
3. A logged problem is fixed, no longer applies, or the user decides to keep it for good: read [Technical debt](references/technical-debt.md), verify it, then close the item.

### 7. Report

Tell the user, in one line per record: the ID, the file path and what happened (`recorded`, `logged as <status>`, `closed as <outcome>` or `updated as <status>`).

Example:

- Input: "We decided to keep sessions in Postgres, not Redis."
- Output: the file `.claude/maintainer/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md`, then the line "ADR_2026-03-14_keep-sessions-in-postgres, `.claude/maintainer/decisions/ADR_2026-03-14_keep-sessions-in-postgres.md`: recorded."

## Checklist

Check each item before you finish.

- [ ] Every record is under `.claude/maintainer/` in the checkout, created with the Write tool or changed with the Edit tool.
- [ ] Documents the project kept before this plugin were looked for before the first folder of each kind (read-only in a non-interactive session).
- [ ] Nothing existing was moved, overwritten or deleted without the user's OK.
- [ ] No record lives in two places, or the user chose to keep both, or the candidates were only listed in a non-interactive session.
- [ ] The git question was asked once, or was not needed.
- [ ] `.claude/maintainer/` was searched first. No duplicate exists.
- [ ] Every claim is verified, stated by the user, or marked pending.
- [ ] No placeholder or template instruction remains in an entry.
- [ ] Each ledger index equals its entries.
- [ ] No settled ADR or closed entry was rewritten.
- [ ] Each decision has its own ADR.
- [ ] Nothing was committed or pushed.
- [ ] The user got a one-line note per record with its ID, its file and what happened.
