# Technical debt

Pending debt lives in `<debt>/pending-debt.md`. Verified fixes live in `resolved-debt.md` in the same folder. Debt is recorded nowhere else. Other documents mention an item by its ID only: `DEBT-<NNN>`.

## What belongs in the ledger

A problem that can be fixed now gets fixed, not logged. Log it only when it cannot be fixed now because it waits on:

- a decision or a spend only the user or the project's owners can make,
- access or an external party,
- or a risk that was accepted on purpose.

All of these must also hold: the condition is observable or backed by traceable evidence, it has a real impact, a next action or reassessment trigger exists, and no other record tracks it, such as an open issue or an ADR follow-up. Do not log improvement ideas, speculation or backlog tasks.

## Before logging

1. Search both ledgers for the same condition: the same file, symptom or cause.

   ```bash
   grep -il "<keyword>" <debt>/*.md
   ```

2. If an open entry already tracks it, do not add a new one. Update that entry when the new finding adds evidence.
3. If a resolved entry covers it and the problem is back, open a new item that links back to it (see "Keep history").

## Add an item

1. Create the ledger from the [pending debt template](../assets/pending-debt.md) when `pending-debt.md` does not exist. Read the template and write everything below its first comment into the new file, including the closing "Entry format" comment. Leave out only that first comment.
2. Find the next free ID. Never reuse an ID from either ledger.

   ```bash
   grep -hoE 'DEBT-[0-9]+' <debt>/*.md 2>/dev/null | sort -u
   ```

   Read each existing ledger first. A ledger confirmed absent counts as empty. Take the numeric maximum of every ID in both ledgers, links inside entries included, and add one, padded to at least three digits: `DEBT-1000` follows `DEBT-999`, so never sort IDs as text. Use `DEBT-001` only when neither ledger holds an ID. A failed search, a malformed ID or a duplicate is a discrepancy to resolve, never a reason to restart the sequence.
3. Copy the "Entry format" block above its comment. Fill every field, and set Logged to today's date.
4. Remove the "*No open items.*" line when adding the first item.
5. Add the item's row to the Index: ID, title, status icon and name.
6. Tell the user in one line which ID you logged and why it is not fixed now.

## Fill an entry

- Put only verified facts under Confirmed facts: paths, revisions, commands, dates.
- Put reasoned but unverified conclusions under Inferences.
- Write "none" in a field with nothing to report.
- Write the smallest concrete action in Next action.
- Write the event, date or evidence that permits closure in Review condition.
- Link the related issues, ADRs and pull requests.

## Update an item

- Revise the entry in place when evidence, impact, owner or next action changes.
- Set Status to one of: Pending, In progress, Blocked, Risk accepted.
- Keep the Index row's ID, title and status equal to the entry.
- Keep a Risk accepted item open. Its review condition still applies.

## Resolve an item

A logged problem is fixed. Move its item from `pending-debt.md` to `resolved-debt.md`. Do it without asking, as soon as the fix is verified.

1. Run both checks yourself. If either fails, keep the item open and update it instead.
   - Positive: the fix works.
   - Negative: the original failure no longer reproduces. Showing that the new path works is not enough.
2. Record both checks with evidence: commands, tests or review. Quote the output.
3. If the condition disappeared without a fix, such as the code was removed, say so as the fix. The negative check is then the evidence that the condition is gone.
4. Create the ledger from the [resolved debt template](../assets/resolved-debt.md) when `resolved-debt.md` does not exist. Read the template and write everything below its first comment into the new file, including the closing "Entry format" comment.
5. Copy the "Entry format" block above its comment and fill it. Keep the same ID. Copy Logged on from the pending entry. Set Resolved on to today's date.
6. Add the item's row to the Index: resolved date, ID, resolution title, and "none" under Superseded by.
7. Remove the "*No resolved items yet.*" line when adding the first resolved item.
8. Only after the resolved entry exists, remove the entry and its Index row from `pending-debt.md`.
9. Restore the "*No open items.*" line when the last item leaves.
10. Tell the user in one line which ID you resolved.

Never delete a pending item without a resolved entry.

## Keep history

- Keep resolved entries as dated records. Never rewrite them.
- When a later change invalidates a resolution, keep the original entry and open a new pending item that links back to it.
- Write the new item's ID in Superseded by, in the old resolved entry and in its Index row. This is the only edit a resolved entry accepts.
- Keep each resolved Index row's date, ID, title and Superseded by equal to its entry.
