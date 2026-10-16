# Debt ledger: resolve

A logged problem is fixed. Move its item from `.claude/maintainer/technical-debt/pending-debt.md` to `resolved-debt.md` in the same folder. Do it without asking, as soon as the fix is verified.

## Resolve an item

1. Run both checks yourself. If either fails, keep the item open and update it instead.
   - Positive: the fix works.
   - Negative: the original failure no longer reproduces. Showing that the new path works is not enough.
2. Record both checks with evidence: commands, tests or review. Quote the output.
3. If the condition disappeared without a fix, such as the code was removed, say so as the fix. The negative check is then the evidence that the condition is gone.
4. Create the ledger from `.claude/skills/project-records/assets/resolved-debt.md` when `resolved-debt.md` does not exist. Read the asset and write the file with the Write tool.
5. Copy the "Entry format" block above its comment and fill it. Keep the same ID. Copy Logged on from the pending entry. Set Resolved on to today's date.

   ```bash
   date +%F
   ```

6. Add the item's row to the Index: resolved date, ID, resolution title, and "none" under Superseded by.
7. Remove the "*No resolved items yet.*" line when adding the first resolved item.
8. Only after the resolved entry exists, remove the entry and its Index row from `pending-debt.md`.
9. Restore the "*No open items.*" line when the last item leaves.
10. Tell Nery in one line which ID you resolved.

Never delete a pending item without a resolved entry.

## Keep history

- Keep resolved entries as dated records. Never rewrite them.
- When a later change invalidates a resolution, keep the original entry and open a new pending item that links back to it.
- Write the new item's ID in Superseded by, in the old resolved entry and in its Index row. This is the only edit a resolved entry accepts.
- Keep each resolved Index row's date, ID, title and Superseded by equal to its entry.
