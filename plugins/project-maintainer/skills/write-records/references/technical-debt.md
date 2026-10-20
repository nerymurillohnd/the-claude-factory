# Technical debt

## What this is

- A ledger of problems that cannot be fixed now.
- Pending debt: `.claude/maintainer/technical-debt/pending-debt.md`.
- Closed debt: `.claude/maintainer/technical-debt/closed-debt.md`, in the same folder.
- Debt is recorded nowhere else.
- Other documents mention an item by its ID only: `DEBT-<NNN>`.
- Templates: [pending debt](../assets/pending-debt.md) and [closed debt](../assets/closed-debt.md).

## Rules

- Fix a problem that can be fixed now and sits inside the current task. Never log it.
- A fixable problem outside the current task: tell the user. Log nothing.
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
- Never delete a pending item without a closed entry.
- Never rewrite a closed entry. Only its "Superseded by" field may change.
- Close an item as resolved or obsolete without asking, as soon as the evidence is verified.
- Close an item as accepted only after the user decides to keep the condition for good.
- Write the ledgers with the Write tool, never with Bash. Write creates the folder.
- In a non-interactive session, write no entry that depends on an unanswered question. Return the questions in your final reply.

## Open an item

### 1. Search both ledgers

1. Search for the same condition: the same file, symptom or cause.

   ```bash
   grep -il "<keyword>" .claude/maintainer/technical-debt/*.md
   ```

   If no ledger exists yet, the search finds nothing. Continue.

2. An open entry already tracks it? Add no new item. Update that entry when the new finding adds evidence.
3. A closed entry covers it and the problem is back? Continue with step 2, then write the new ID in that closed entry. See "Keep history".

### 2. Create the ledger if it is missing

1. Read the [pending debt template](../assets/pending-debt.md).
2. Write everything below its first comment into `pending-debt.md`.
3. Keep the closing "Entry format" comment. Leave out only the first comment.

### 3. Find the next free ID

1. Read each ledger that exists, whole.
2. List the heading IDs of the ledgers that exist. Pass only files that exist:

   ```bash
   grep -hoE '^### DEBT-[0-9]+' .claude/maintainer/technical-debt/pending-debt.md .claude/maintainer/technical-debt/closed-debt.md | sort | uniq -d
   ```

   A heading ID printed twice is a discrepancy.

3. List every ID, links inside entries included, and take the numeric maximum:

   ```bash
   grep -hoE 'DEBT-[0-9]+' .claude/maintainer/technical-debt/pending-debt.md .claude/maintainer/technical-debt/closed-debt.md | sed 's/DEBT-//' | sort -n | tail -1
   ```

4. Add one to the maximum. Pad to at least three digits.
5. Use `DEBT-001` only when neither ledger holds an ID.
6. Never sort IDs as text: `DEBT-1000` follows `DEBT-999`.
7. A command error, a malformed ID or a heading ID that repeats is a discrepancy. Stop, show the user the lines, and ask how to fix it. Never restart the sequence.

### 4. Write the entry

1. Copy the text inside the "Entry format" comment. Leave out the `<!--` and `-->` markers and the instruction lines.
2. Paste it right before that comment, after the last item.
3. Fill every field. Set Logged to today's date.
4. Remove the "*No open items.*" line when you add the first item.

### 5. Update the index

- Add the item's row at the bottom of the Index: ID, title, status icon and name.

### 6. Report

- Tell the user in one line which ID you logged and why it is not fixed now.

## Fill an entry

- Put only verified facts under Confirmed facts: paths, revisions, commands, dates.
- Put reasoned but unverified conclusions under Inferences.
- Write "none" in a field with nothing to report. Owner is the exception: write "unassigned" when nobody owns the item.
- Category is a free word, such as security, compatibility, cost or quality.
- Write the smallest concrete action in Next action.
- Write the event, date or evidence that permits closure in Review condition.
- Link the related issues, ADRs and pull requests.

## Update an item

- Revise the entry in place when evidence, impact, owner or next action changes.
- Set Status to one of: Pending, In progress, Blocked, Risk accepted.
- Keep the Index row's ID, title and status equal to the entry.
- Keep a Risk accepted item open. Its review condition still applies.
- The user decides to keep the condition for good? Close the item as accepted. Do not leave it as Risk accepted.

## Close an item

Use this when a logged problem is fixed, no longer applies, or the user decides to keep it for good.

### 1. Pick the outcome

| Outcome | Use when |
| --- | --- |
| resolved | A fix was made and it works. |
| obsolete | The condition no longer exists, with no fix aimed at it: code removed, architecture changed, or the item was logged in error or duplicates another. |
| accepted | The user decided to keep the condition for good. An accepted ADR records that decision. |

### 2. Verify the closure

Run the checks yourself. Quote the output.

1. resolved:
   - Positive: the fix works.
   - Negative: the original failure no longer reproduces. Showing that the new path works is not enough.
2. obsolete:
   - Negative: the condition no longer exists. Show the evidence.
   - Name what changed: an ADR ID, a commit or a pull request. Write "none" when nothing caused it.
   - Logged in error, or a duplicate? Say so, and name the item it duplicates.
3. accepted:
   - The ADR exists with status `accepted`. Cite its ID.
   - No ADR yet? Write it first, following the ADRs reference.
4. Any check fails? Keep the item open. Update it instead.

### 3. Create the closed ledger if it is missing

1. Read the [closed debt template](../assets/closed-debt.md).
2. Write everything below its first comment into `closed-debt.md`.
3. Keep the closing "Entry format" comment. Leave out only the first comment.

### 4. Move the item

1. Copy the text inside the "Entry format" comment. Leave out the markers and the instruction lines. Paste it right before that comment, after the last item.
2. Fill it. Keep the same ID.
3. Set Outcome to resolved, obsolete or accepted.
4. Copy Logged on and Owner from the pending entry.
5. Set Closed on to today's date.
6. Write "not applicable" in a Verification row the outcome does not use.
7. Add the item's row at the bottom of the Index: closed date, ID, outcome, closure title, and "none" under Superseded by.
8. Remove the "*No closed items yet.*" line when you add the first closed item.
9. Only after the closed entry exists, remove the entry and its Index row from `pending-debt.md`.
10. Restore the "*No open items.*" line when the last item leaves.

### 5. Report

- Tell the user in one line which ID you closed and with which outcome.

## Keep history

- Keep closed entries as dated records. Never rewrite them.
- A later change invalidates a closure? Keep the original entry. Open a new pending item that links back to it.
- Write the new item's ID in Superseded by, in the old closed entry and in its Index row. This is the only edit a closed entry accepts.
- Keep each closed Index row's date, ID, outcome, closure and Superseded by equal to its entry.

## Checklist

- [ ] No identical open entry existed before logging.
- [ ] The new ID is the numeric maximum plus one, with at least three digits.
- [ ] Every entry field is filled. Unknown fields say "none", and Owner says "unassigned".
- [ ] Confirmed facts and inferences are kept apart.
- [ ] Each Index row equals its entry.
- [ ] A closed item has the evidence its outcome needs, quoted.
- [ ] A closed entry carries Outcome, Closed on, Logged on and Owner.
- [ ] No pending item was deleted without a closed entry.
- [ ] No closed entry was rewritten, except "Superseded by".
- [ ] Each ledger keeps its "Entry format" comment.
