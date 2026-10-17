# Debt ledger: open and update

Pending debt lives in `.claude/maintainer/technical-debt/pending-debt.md`. Verified fixes live in `resolved-debt.md` in the same folder. Debt is recorded nowhere else. Other documents mention an item by its ID only: `DEBT-<NNN>`.

## What belongs in the ledger

A problem that can be fixed now gets fixed, not logged. Log it only when it cannot be fixed now because it waits on:

- a decision or a spend only Nery can make,
- access or an external party,
- or a risk that Nery accepted on purpose.

All of these must also hold: the condition is observable or backed by traceable evidence, it has a real impact, a next action or reassessment trigger exists, and no other record tracks it, such as an open issue or an ADR follow-up. Do not log improvement ideas, speculation or backlog tasks.

## Before logging

1. Search both ledgers for the same condition: the same file, symptom or cause.

   ```bash
   grep -il "<keyword>" .claude/maintainer/technical-debt/*.md
   ```

2. If an open entry already tracks it, do not add a new one. Update that entry when the new finding adds evidence.
3. If a resolved entry covers it and the problem is back, open a new item that links back to it (see "Keep history" in the resolve procedure).

## Add an item

1. Create the ledger from the [pending debt template](../assets/pending-debt.md) when `pending-debt.md` does not exist. Read the template and write the file with the Write tool.
2. Find the next free ID. Never reuse an ID from either ledger.

   ```bash
   grep -ho 'DEBT-[0-9]\{3\}' .claude/maintainer/technical-debt/*.md 2>/dev/null | sort -u | tail -n 1
   ```

   Add one to the number it prints. Use `DEBT-001` when it prints nothing or fails because the folder does not exist yet.
3. Copy the "Entry format" block above its comment. Fill every field, and set Logged to today's date (`date +%F`).
4. Remove the "*No open items.*" line when adding the first item.
5. Add the item's row to the Index: ID, title, status icon and name.
6. Tell Nery in one line which ID you logged and why it is not fixed now.

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
