# Example: a phased migration with rollback and authorization checkpoints

## Contents

- [Goal](#goal) and [Acceptance criteria](#acceptance-criteria)
- [File map](#file-map) and [Tasks](#tasks), in four phases
- [Rollback](#rollback) and [Risks](#risks)
- [Execution strategy](#execution-strategy) and [Handoff](#handoff)
- [Why each section holds what it does here](#why-each-section-holds-what-it-does-here)

Judgment to copy: data and deploys get phases, a rollback with its own check, and a stop before every irreversible step; independent tasks go to subagents in worktrees. Don't copy the language, names or commands.

<example>
<request>
Move the invoices table from integer cents to a numeric amount with a currency column. It's a Rails app on PostgreSQL in production, about 12 million rows. No downtime.
</request>

<plan>
# Plan: migrate invoices to amount and currency without downtime

Guardrail: plan mode on.

## Goal

Invoices store `amount numeric(12,2)` and `currency char(3)` instead of `amount_cents integer`, so multi-currency accounts can be billed; the app keeps serving traffic during the change.

## Acceptance criteria

- After phase 3, `SELECT count(*) FROM invoices WHERE amount IS NULL` returns 0 in production.
- Every report total matches the pre-migration totals per account (comparison query in Task 5).
- No request errors attributable to invoices during the deploys (error tracker, filtered on `InvoicesController`).

## Verified facts

- PostgreSQL 16.4 (`SELECT version()` on the replica); adding a nullable column without a default doesn't rewrite the table — PostgreSQL docs, ALTER TABLE, read 2026-05-11.
- Rails 8.0.2 (`bin/rails --version`); `amount_cents` is read in 14 places (`grep -rn amount_cents app lib` → 14 lines, listed in the File map).
- The `strong_migrations` gem is installed and blocks unsafe migrations in CI (`Gemfile.lock:212`).

## Assumptions and open questions

- Every existing invoice is in USD. Confirm with the user; Task 3's check counts rows per inferred currency.

## File map

- `db/migrate/*_add_amount_and_currency_to_invoices.rb` (create): nullable columns.
- `app/models/invoice.rb` (modify): dual-write both representations.
- `lib/tasks/invoices_backfill.rake` (create): batched backfill, 10,000 rows per batch.
- The 14 readers of `amount_cents` (modify): read `amount`.
- `db/migrate/*_finalize_invoice_amounts.rb` (create): NOT NULL constraint added as NOT VALID, then validated.
- `db/migrate/*_drop_amount_cents.rb` (create, phase 4): drops the old column.

## Tasks

Phase 1: expand.

### Task 1: add the columns

- Files: `db/migrate/*_add_amount_and_currency_to_invoices.rb`
- Produces: nullable `amount numeric(12,2)` and `currency char(3)`, no default.
- Test first: no; schema change.
- Steps:
  1. Generate the migration with the two nullable columns and no default.
- Check: `bin/rails db:migrate` on a production snapshot → finishes in under 1 second, `strong_migrations` reports nothing
- Done when: the check passes and its evidence is recorded.

### Task 2: dual write

- Files: `app/models/invoice.rb`, `test/models/invoice_test.rb`
- Consumes: the columns from Task 1
- Produces: `Invoice#save` writes `amount_cents` and `amount` together
- Test first: yes. `test_save_writes_both_amounts` fails first with `NoMethodError: undefined method 'amount'`.
- Steps:
  1. Write the test, see it fail for that reason, then add the dual write in a `before_save` callback.
- Check: `bin/rails test test/models/invoice_test.rb` → `0 failures, 0 errors`
- Done when: the check passes and its evidence is recorded. This task also closes phase 1.

Authorization checkpoint: deploy phase 1 to production. Stop and ask.

Phase 2: backfill.

### Task 3: batched backfill

- Files: `lib/tasks/invoices_backfill.rake`
- Consumes: the columns from Task 1 and the dual write from Task 2
- Produces: `bin/rails invoices:backfill`, which prints `remaining=<n>`
- Test first: no; a one-off data task, proven on the snapshot.
- Steps:
  1. Write the task: 10,000 rows per batch, a pause between batches, `amount` from `amount_cents / 100.0`, `currency` set from the open question's answer.
- Check: on the snapshot, `bin/rails invoices:backfill` ends with `remaining=0`, and the per-currency count matches the open question's answer.
- Done when: the check passes and its evidence is recorded. This task closes phase 2.

Authorization checkpoint: run the backfill in production. Stop and ask.

Phase 3: switch reads and constrain.

### Task 4: readers use amount

- Files: the 14 readers listed in the File map
- Consumes: `amount` filled by Task 3
- Produces: no reader of `amount_cents` outside the model's dual write
- Test first: no; the existing suite covers each reader.
- Steps:
  1. Replace each `amount_cents` read with `amount`, one directory per subagent.
- Delegated: the 14 readers split across three subagents by directory, each with `isolation: worktree` and the testing skill; the main session merges.
- Check: `bin/rails test` → `0 failures, 0 errors`, and `grep -rn amount_cents app lib` lists only the model's dual write.
- Done when: the check passes and its evidence is recorded.

### Task 5: constraint and totals

- Files: `db/migrate/*_finalize_invoice_amounts.rb`
- Consumes: the readers from Task 4
- Produces: a validated NOT NULL constraint on `amount`
- Test first: no; schema change.
- Steps:
  1. Add the constraint as NOT VALID, then validate it in a second statement.
- Check: the totals comparison query returns no rows, and the NOT VALID constraint validates without locking writes.
- Done when: the check passes and its evidence is recorded. This task closes phase 3.

Authorization checkpoint: deploy phase 3. Stop and ask.

Phase 4, a separate plan after a week of clean errors: drop `amount_cents`.

## Rollback

- Phases 1 to 3: revert the deploy; the dual write keeps `amount_cents` correct, so the old code works. Check: the previous release's test suite passes against the migrated schema.
- After phase 4 there is no rollback without a restore; that is why it is a separate plan.

## Risks

- The backfill locks rows under load — batches of 10,000 with a pause; Task 3 measures batch time on the snapshot.
- A reader is missed — Task 4's grep check.
- Currency inference is wrong — the open question and Task 3's count.

## Execution strategy

Main session for phases 1 and 2, three parallel worktree subagents for Task 4, the main session again for Task 5. `plan-verifier` reviewed this plan before handoff, and checks the work against the plan after Task 5.

## Handoff

Plan gate on, with `status` set to `awaiting-authorization` at each checkpoint. `/goal` condition referencing this plan, about 750 characters, Done when phase 3's acceptance criteria print.

Before Task 1, and after any resume or context clear, invoke the work-lifecycle:planning-before-execution skill and follow its Execution section.
</plan>
</example>

## Why each section holds what it does here

- The last destructive step is a separate plan, because it has no cheap rollback.
- Each deploy and the production backfill is an authorization checkpoint, so auto mode can't run through them.
- Task 4 goes to subagents because its pieces are independent and many; every other task stays in the main session.
