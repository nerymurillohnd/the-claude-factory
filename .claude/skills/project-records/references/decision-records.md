# Decision records

One file per decision in `.claude/maintainer/decisions/`, named `ADR_<YYYY-MM-DD>_<slug>.md`. The file name without `.md` is the record's ID. Other documents mention a record by that ID only.

## Before writing

1. Search the folder for a record on the same decision. If one exists, do not add a duplicate: change it only as "Change a decision" says.

   ```bash
   ls .claude/maintainer/decisions/
   grep -ril "<keyword>" .claude/maintainer/decisions/
   ```

2. Collect from the conversation. Ask Nery only for what is missing:
   - Context: the situation and the problem.
   - Decision drivers.
   - The chosen option and why.
   - Each rejected option and why.
   - Consequences, good and bad.
   - Decision makers. Default: Nery.
   - Optional: consulted, informed, risks, confirmation.
3. Set the status. Use `accepted` when Nery decided in this conversation. Use `proposed` when the decision is still open.
4. With more than one decision, ask Nery how to register them before writing: see "Choose how to register".

Do not ask permission to record. Record, then tell Nery in one line which file you wrote.

## Choose how to register

Do this when there is more than one decision to record. With one decision, skip it and write one individual ADR.

Ask Nery with `AskUserQuestion`: one question, three options. Put the recommended option first, label it "(Recommended)", and give the reason in its description.

- **Individual:** one ADR per decision.
- **Single:** one ADR that holds all the decisions.
- **Classified:** one ADR per class, grouping the decisions that share a theme, such as process, architecture, security or distribution.

Pick the recommendation by this rule, and say why in one sentence:

- Individual, when the decisions can change independently. Each one can be superseded alone, so the history stays precise. This is the default.
- Single, when the decisions were made together and stand or fall as one package.
- Classified, when there are many decisions and several share a theme. It keeps the folder short without mixing unrelated decisions.

After the answer:

- Name the slug after the decision (individual), the package (single) or the class (classified).
- In a single or classified ADR, list each decision as a numbered item under "Decision outcome".
- Do not ask again for the same batch.

## Write the record

1. Get the date and create the folder.

   ```bash
   date +%F
   mkdir -p .claude/maintainer/decisions
   ```

2. Read the [ADR template](../assets/ADR_YYYY-MM-DD_decision-slug.md).
3. Write `.claude/maintainer/decisions/ADR_<date>_<slug>.md` with the Write tool. The slug is lowercase kebab-case and names the decision, such as `merge-git-hygiene-into-github-operations`.
4. Keep the frontmatter `date` equal to the date in the file name.
5. Replace every `{placeholder}`. Leave the template's HTML comments out.
6. Remove the `consulted` and `informed` lines when they would be empty. Remove the optional sections that add nothing.
7. Link the evidence: issues, pull requests, tests, documentation.
8. Mark planned evidence as pending in Confirmation. Never present it as observed.

## Change a decision

1. Never rewrite the reasoning of an accepted record.
2. Write a new record for the new decision. Set its `supersedes` to the earlier file name.
3. In the earlier record, set `status` to `superseded` and `superseded-by` to the new file name. Touch nothing else in it.
4. Check both links point at files that exist.

## Check before finishing

- The file name date equals the frontmatter `date`.
- No `{placeholder}` and no HTML comment from the template remains.
- Every claim is verified, stated by Nery, or marked pending.
- There is no second record for the same decision.
- No index to update: the folder listing, sorted by name, is the index.
