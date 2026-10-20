# Existing records

## What this is

- A procedure for projects that already keep decisions, technical debt or pending items somewhere else.
- It runs before the first records folder of each kind is created.
- Its goal is one source of truth. The same information never lives in two places.
- Templates: [ADR template](../assets/ADR_YYYY-MM-DD_decision-slug.md), [pending debt](../assets/pending-debt.md).

## Rules

- Never move, overwrite or delete an existing document without the user's explicit OK.
- Migrate only what the user approved.
- Copy the source's own words. Add no fact the source does not state.
- Write "not recorded in the source" in every field the source cannot fill.
- Migrate only items that qualify as records. Leave task lists in place.
- Never migrate an item the source marks as done. It has no verification evidence.
- Never decide for the user what happens to the original. Ask.
- In a non-interactive session, find and migrate nothing. Name what you found in your one-line note.

## Steps

### 1. Find candidates

1. List the project's files, ignoring vendored folders:

   ```bash
   git ls-files --cached --others --exclude-standard
   ```

   Outside git, list files up to four levels deep and skip `.git` and `node_modules`.

2. Keep the paths that match one of these words as a whole word in any folder or file name, ignoring case: `adr`, `adrs`, `decision`, `decisions`, `debt`, `known-issues`, `pending`, `backlog`, `todo`.

   ```bash
   grep -iE '(^|[/_.-])(adrs?|decisions?|debt|known[-_]?issues?|pending|backlog|todo)([/_.-]|$)'
   ```

3. Read the project's `CLAUDE.md` and `AGENTS.md`. Add any path they name for decisions, debt or pending items.
4. Drop what does not apply:
   - the plugin's own folder, `.claude/maintainer/`,
   - changelogs,
   - vendored or generated files.

### 2. Check each candidate

1. Read the candidate in full.
2. Classify it:
   - **Decisions:** records of choices already made or still open.
   - **Postponed problems:** known problems that wait on a decision, access, spend or an outside party.
   - **Task list:** work that can be done now. Not a record.
   - **Unrelated:** anything else.
3. Keep only the first two classes. Leave the rest untouched and unmentioned.
4. Do not count a candidate twice. A file that mixes classes counts once per class.

### 3. Ask the user

Do this before you create any folder.

1. Show what you found, one line per candidate: the path, what it holds and how many items it has.
2. Ask one question with your question tool. Put the recommendation first and give its reason.
   - **Migrate (Recommended):** the items become the first records, so each fact lives in one place.
   - **Choose which:** the user picks the candidates to migrate. Ask one follow-up listing them.
   - **Leave them:** touch nothing. Warn that new records and the old documents will live in two places.
3. Do not ask again for the same batch.

### 4. Migrate

Do this after the git question. Write every record with the Write tool. Write creates the folders.

1. Write the records, one candidate at a time, in the order the source lists them.
2. For a decision, write one ADR per decision with the ADR template. Follow the ADRs reference. Never group decisions, even when the source does.
   - Status: `accepted` when the source presents it as decided. `proposed` when it is open. `rejected`, `deprecated` or `superseded` only when the source says so.
   - Date: the date the source gives. Without one, use today and write "original date not recorded" in More information.
   - Decision makers: the people the source names. Otherwise "not recorded in the source".
   - More information: "Migrated from `<source path>` on `<today>`."
3. For a postponed problem, log one debt item with the pending debt template. Follow the Technical debt reference.
   - Status: Pending, unless the source says Blocked or accepts the risk.
   - Next action when the source has none: "not recorded in the source; confirm with the owner".
   - Skip a problem that can be fixed now. Tell the user it stays where it is.
4. Compare the result with the source:
   - Every source item is migrated or listed as left in place, with the reason.
   - Each migrated record keeps the source's wording.

### 5. Close the old source

Do this once per original, after the comparison passes. Ask separately, because the step changes the user's file.

1. Ask one question with your question tool. Put the recommendation first and give its reason.
   - **Replace with a pointer (Recommended):** the file keeps one line that names the new location, so readers are not lost.
   - **Delete it:** the file is removed. Git history keeps a tracked original.
   - **Keep it as is:** two sources remain. Warn the user.
2. Apply the answer to that original only.
3. Never touch an original the user did not answer for.

### 6. Report

- Tell the user in one line what you migrated and from where.
- Name what you left in place and why.

## Checklist

- [ ] Every candidate was read in full before you classified it.
- [ ] The user approved the migration before any folder or record existed.
- [ ] Every migrated item keeps the source's wording and invents no fact.
- [ ] Unknown fields say "not recorded in the source".
- [ ] No source item is missing: each is migrated or listed as left in place.
- [ ] No original changed before the user answered for it.
- [ ] No item now lives in two places, or the user chose to keep both.
