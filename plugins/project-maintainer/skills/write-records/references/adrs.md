# ADRs

## What this is

- A decision record: one file per decision, in `.claude/maintainer/decisions/`.
- Name: `ADR_<YYYY-MM-DD>_<slug>.md`.
- The file name without `.md` is the record's ID. `supersedes` and `superseded-by` hold IDs.
- One ADR per decision. Never group several decisions in one file.
- Template: [ADR template](../assets/ADR_YYYY-MM-DD_decision-slug.md).

## Rules

- Search before writing. Never add a duplicate.
- Create the file with the Write tool and change it with the Edit tool. Never use Bash. Write creates the folder.
- Record without asking permission. Then report as the skill's Report step says.
- Set the status only as the Statuses table says.
- Once a record is not `proposed`, change it only as "Change a decision" says.
- Write only claims that are verified or that the user stated.
- Mark planned evidence as pending. Never present it as observed.
- Never copy a job title, company or other detail from outside the conversation and the project.
- In a non-interactive session, write no record that depends on an unanswered question. Return the questions in your final reply.

## Statuses

| Status | Use when | Notes |
| --- | --- | --- |
| `proposed` | The decision is still open | Write "proposed" and "Proposed option" in place of "chosen" and "Chosen option". Say what is still open. |
| `accepted` | The decision is made: the user decided in this conversation, or says it was made earlier and asks you to record it | A record of an earlier decision gets today's date. Say when it was made in More information. |
| `rejected` | A proposal was considered and refused as a whole, and the refusal will outlast the conversation | Describe the refused proposal in the context. Mark its option rejected. |
| `deprecated` | An accepted decision no longer applies and nothing replaces it | Set by editing the earlier record, as "Change a decision" says. |
| `superseded` | A newer ADR replaces it | Set `superseded-by` to the newer ID. |

## Steps

### 1. Check for an existing record

1. Run:

   ```bash
   ls .claude/maintainer/decisions/
   grep -ril "<keyword>" .claude/maintainer/decisions/
   ```

   Search with two or three keywords: the component, the choice and the option you rejected. One keyword can miss a duplicate. If the folder does not exist, there is nothing to find. Continue.

2. Found a record on the same decision? Do not add a duplicate. Change it only as "Change a decision" says.
3. Found a record on the same topic, but the user chose differently? That is a new decision, not a duplicate. Go to "Change a decision".

### 2. Collect the facts

Take every fact from the conversation. A fact is missing only when it is the chosen option, a rejected option, or the reason for the choice or for a rejection. Ask for it. In a non-interactive session write no record and return the question.

For everything else, write what the conversation supports, plus what you verify in the repository, and write "Not stated by the user." for the rest. Never invent.

- Context: the situation and the problem.
- Decision drivers.
- The chosen option and why.
- Each rejected option and why.
- Consequences, good and bad.
- Decision makers: who made the decision.
  - Use the name the user gave in this conversation.
  - Otherwise use the name `git config user.name` prints. The project's Git identity counts as the project.
  - The user says "we" with no names? Use a plain role such as "project owner", not the Git name.
- Optional: consulted, informed, risks, confirmation.

### 3. Set the status

- Pick the status from the Statuses table.
- Several decisions in one request? Collect the facts for each and write one file per decision.

### 4. Write the file

1. Get today's date:

   ```bash
   date +%F
   ```

2. Read the [ADR template](../assets/ADR_YYYY-MM-DD_decision-slug.md).
3. Name the file `ADR_<date>_<slug>.md`.
   - The slug is lowercase kebab-case.
   - The slug names the decision, such as `use-postgres-for-sessions`.
4. Write the file in `.claude/maintainer/decisions/` with the Write tool.
5. Keep the frontmatter `date` equal to the date in the file name.
6. Replace every `{placeholder}`.
7. Leave the template's HTML comments out.
8. Remove the `consulted` and `informed` keys, with their list items, when they would be empty. That is two lines each.
9. Remove the optional sections that add nothing: Risks and mitigations, Confirmation, Pros and cons of the options, More information.
10. Fill "Pros and cons of the options" only when the options need evidence. Write one subsection per option.
11. Link the evidence: issues, pull requests, tests, documentation.
12. Mark planned evidence as pending in Confirmation. Without a Confirmation section, write it in More information.

## Change a decision

1. A `proposed` record is not settled. Edit it in place, including setting `accepted` when the user decides.
2. A record that is not `proposed` keeps its text. These are the only edits it accepts:
   - `status` to `superseded` (with `superseded-by`) or to `deprecated`.
   - `superseded-by`.
   - The Confirmation section: record results and re-check dates.
3. A different choice, new reasoning or a correction needs a new record:
   1. Write a new ADR for the new decision. Set its `supersedes` to the earlier ID.
   2. In the earlier record, set `status` to `superseded` and `superseded-by` to the new ID.
   3. Touch nothing else in the earlier record.
   4. Check that both IDs have a file in `.claude/maintainer/decisions/`.
4. A typo or a wrong fact in a record that is not `proposed`: ask the user. Edit only after they approve. In a non-interactive session, edit nothing and return the question in your final reply.

## Checklist

- [ ] The file name date equals the frontmatter `date`.
- [ ] The status matches the Statuses table.
- [ ] No `{placeholder}` and no HTML comment from the template remains.
- [ ] Every claim is verified, stated by the user, or marked pending.
- [ ] No second record exists for the same decision, and each decision has its own file.
- [ ] The decision makers come from the conversation or the project only.
- [ ] `supersedes` and `superseded-by` hold IDs, and each ID has a file.
- [ ] A record that is not `proposed` changed only as "Change a decision" allows.
- [ ] No index needs an update. The folder listing, sorted by name, is the index.
