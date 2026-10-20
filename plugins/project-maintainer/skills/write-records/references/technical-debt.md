# Technical debt

## What this is

- A ledger of problems that cannot be fixed now.
- Pending debt: `<debt>/pending-debt.md`.
- Resolved debt: `<debt>/resolved-debt.md`, in the same folder.
- Debt is recorded nowhere else.
- Other documents mention an item by its ID only: `DEBT-<NNN>`.
- Templates: [pending debt](../assets/pending-debt.md) and [resolved debt](../assets/resolved-debt.md).

## Rules

- Fix a problem that can be fixed now. Never log it.
- Log a problem only when it waits on one of these:
  - a decision or a spend only the user or the project's owners can make,
  - access or an external party,
  - a risk that was accepted on purpose.
- Log it only when all of these also hold:
  - the condition is observable or backed by traceable evidence,
  - it has a real impact,
  - a next action or a reassessment trigger exists,
  - no other record tracks it, such as an open issue or an ADR follow-up.
- Never log improvement ideas, speculation or backlog tasks.
- Never reuse an ID from either ledger.
- Never delete a pending item without a resolved entry.
- Never rewrite a resolved entry. Only its "Superseded by" field may change.
- Resolve an item without asking, as soon as the fix is verified.

## Open an item

### 1. Search both ledgers

1. Search for the same condition: the same file, symptom or cause.

   ```bash
   grep -il "<keyword>" <debt>/*.md
   ```

2. An open entry already tracks it? Add no new item. Update that entry when the new finding adds evidence.
3. A resolved entry covers it and the problem is back? Open a new item that links back to it. See "Keep history".

### 2. Create the ledger if it is missing

1. Read the [pending debt template](../assets/pending-debt.md).
2. Write everything below its first comment into `pending-debt.md`.
3. Keep the closing "Entry format" comment. Leave out only the first comment.

### 3. Find the next free ID

1. List the IDs in both ledgers:

   ```bash
   grep -hoE 'DEBT-[0-9]+' <debt>/*.md 2>/dev/null | sort -u
   ```

2. Read each existing ledger first. Treat a ledger confirmed absent as empty.
3. Take the numeric maximum of every ID in both ledgers, links inside entries included.
4. Add one. Pad to at least three digits.
5. Never sort IDs as text: `DEBT-1000` follows `DEBT-999`.
6. Use `DEBT-001` only when neither ledger holds an ID.
7. Treat a failed search, a malformed ID or a duplicate as a discrepancy. Resolve it. Never restart the sequence.

### 4. Write the entry

1. Copy the "Entry format" block above its comment.
2. Fill every field.
3. Set Logged to today's date.
4. Remove the "*No open items.*" line when you add the first item.

### 5. Update the index

- Add the item's row: ID, title, status icon and name.

### 6. Report

- Tell the user in one line which ID you logged and why it is not fixed now.

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

Use this when a logged problem is fixed.

### 1. Verify the fix

1. Run both checks yourself.
   - Positive: the fix works.
   - Negative: the original failure no longer reproduces. Showing that the new path works is not enough.
2. Either check fails? Keep the item open. Update it instead.
3. Record both checks with evidence: commands, tests or review. Quote the output.
4. The condition disappeared without a fix, such as removed code? Say so as the fix. The negative check is then the evidence that the condition is gone.

### 2. Create the resolved ledger if it is missing

1. Read the [resolved debt template](../assets/resolved-debt.md).
2. Write everything below its first comment into `resolved-debt.md`.
3. Keep the closing "Entry format" comment. Leave out only the first comment.

### 3. Move the item

1. Copy the "Entry format" block above its comment and fill it.
2. Keep the same ID.
3. Copy Logged on from the pending entry.
4. Set Resolved on to today's date.
5. Add the item's row to the Index: resolved date, ID, resolution title, and "none" under Superseded by.
6. Remove the "*No resolved items yet.*" line when you add the first resolved item.
7. Only after the resolved entry exists, remove the entry and its Index row from `pending-debt.md`.
8. Restore the "*No open items.*" line when the last item leaves.

### 4. Report

- Tell the user in one line which ID you resolved.

## Keep history

- Keep resolved entries as dated records. Never rewrite them.
- A later change invalidates a resolution? Keep the original entry. Open a new pending item that links back to it.
- Write the new item's ID in Superseded by, in the old resolved entry and in its Index row. This is the only edit a resolved entry accepts.
- Keep each resolved Index row's date, ID, title and Superseded by equal to its entry.

## Checklist

- [ ] No identical open entry existed before logging.
- [ ] The new ID is the numeric maximum plus one, with at least three digits.
- [ ] Every entry field is filled. Unknown fields say "none".
- [ ] Confirmed facts and inferences are kept apart.
- [ ] Each Index row equals its entry.
- [ ] A resolved item has both checks with quoted evidence.
- [ ] No pending item was deleted without a resolved entry.
- [ ] No resolved entry was rewritten, except "Superseded by".
- [ ] Each ledger keeps its "Entry format" comment.
