# ADRs

## What this is

- A decision record: one file per decision, in `.claude/maintainer/decisions`.
- Name: `ADR_<YYYY-MM-DD>_<slug>.md`.
- The file name without `.md` is the record's ID.
- Template: [ADR template](../assets/ADR_YYYY-MM-DD_decision-slug.md).

## Rules

- Search before writing. Never add a duplicate.
- Write the file with the Write tool, never with Bash. Write creates the folder.
- Never rewrite the reasoning of an accepted record. Supersede it.
- Record without asking permission. Then tell the user in one line which file you wrote.
- Set `accepted` only when the user decided in this conversation. Otherwise set `proposed`.
- Write only claims that are verified or that the user stated.
- Mark planned evidence as pending. Never present it as observed.
- Never copy a job title, company or other detail from outside the conversation and the project.

## Steps

### 1. Check for an existing record

1. Run:

   ```bash
   ls .claude/maintainer/decisions/
   grep -ril "<keyword>" .claude/maintainer/decisions/
   ```

2. Found a record on the same decision? Do not add a duplicate. Change it only as "Change a decision" says.

### 2. Collect the facts

Take every fact from the conversation. Ask the user only for what is missing.

- Context: the situation and the problem.
- Decision drivers.
- The chosen option and why.
- Each rejected option and why.
- Consequences, good and bad.
- Decision makers: who made the decision.
  - Default: the user.
  - Use the name the user gave in this conversation or the project's `git config user.name`.
  - Otherwise use a plain role such as "project owner".
- Optional: consulted, informed, risks, confirmation.

### 3. Set the status

- `accepted`: the user decided in this conversation.
- `proposed`: the decision is still open.

### 4. Register several decisions

- More than one decision? Follow "Choose how to register" before you write.
- One decision? Skip it. Write one individual ADR.

### 5. Write the file

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
8. Remove the `consulted` and `informed` lines when they would be empty.
9. Fill "Pros and cons of the options" only when the options need evidence. Write one subsection per option.
10. Remove the optional sections that add nothing.
11. Link the evidence: issues, pull requests, tests, documentation.
12. Mark planned evidence as pending in Confirmation.

## Choose how to register

Use this when there is more than one decision to record.

1. Ask the user one question with three options. Use your question tool when you have one.
   - **Individual:** one ADR per decision.
   - **Single:** one ADR that holds all the decisions.
   - **Classified:** one ADR per class, grouping decisions that share a theme such as process, architecture, security or distribution.
2. Put the recommended option first. Label it "(Recommended)". Give the reason in its description.
3. Pick the recommendation by this rule. Say why in one sentence.
   - Individual: the decisions can change independently. Each can be superseded alone, so the history stays precise. This is the default.
   - Single: the decisions were made together and stand or fall as one package.
   - Classified: there are many decisions and several share a theme. The folder stays short without mixing unrelated decisions.
4. After the answer:
   - Name the slug after the decision (individual), the package (single) or the class (classified).
   - In a single or classified ADR, list each decision as a numbered item under "Decision outcome".
   - Never ask again for the same batch.

## Change a decision

1. Never rewrite the reasoning of an accepted record.
2. Write a new record for the new decision. Set its `supersedes` to the earlier file name.
3. In the earlier record, set `status` to `superseded` and `superseded-by` to the new file name.
4. Touch nothing else in the earlier record.
5. Check that both links point at files that exist.

## Checklist

- [ ] The file name date equals the frontmatter `date`.
- [ ] No `{placeholder}` and no HTML comment from the template remains.
- [ ] Every claim is verified, stated by the user, or marked pending.
- [ ] No second record exists for the same decision.
- [ ] The decision makers come from the conversation or the project only.
- [ ] No index needs an update. The folder listing, sorted by name, is the index.
