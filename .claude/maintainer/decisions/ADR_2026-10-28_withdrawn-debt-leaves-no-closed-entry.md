---
status: accepted
date: 2026-10-28
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A debt item whose subject Nery withdraws leaves the pending ledger without a closed entry

## Scope

- In scope: `.claude/maintainer/technical-debt/pending-debt.md` and `closed-debt.md` of this repository, and DEBT-017 as the first item handled this way.
- Out of scope: items closed as resolved, obsolete or accepted, which keep their closed entries; the `project-maintainer` plugin's `write-records` skill, which this record does not change.

## Context and problem statement

DEBT-017 tracked a contradiction: `testing-plugins/SKILL.md` told Claude to make sure CI runs the full eval suite, no eval workflow exists, and `release-and-versioning/SKILL.md` said no CI runs evals. On 2026-10-28 Nery decided that a skill holds abilities and knowledge, never the state of this project at a given moment, and had both lines removed from the skills (commit 845d4da). The subject of the item was withdrawn rather than fixed. The `write-records` skill says "Never delete a pending item without a closed entry", and a closed entry was first written for DEBT-017 as resolved. Does a withdrawn item need a closed entry?

## Decision drivers

- The closed ledger records how a tracked problem ended: fixed, gone for another reason, or kept on purpose. A withdrawn subject is none of these.
- Nery's decision: since the item was withdrawn, it did not need to be closed.

## Considered options

- **Remove the item from the pending ledger with no closed entry, and record the reason in this ADR**: chosen.
- **Close it in `closed-debt.md` as resolved, as `write-records` prescribes**: rejected by Nery, because the item was withdrawn, not resolved.

## Decision outcome

Chosen option: **remove the item from the pending ledger with no closed entry, and record the reason in this ADR**, because Nery withdrew the subject DEBT-017 tracked, so there is nothing to close.

### Consequences

- Good, because `closed-debt.md` holds only problems that ended as resolved, obsolete or accepted.
- Bad, because DEBT-017 no longer appears in either ledger; this ADR is its only trace.
- Bad, because this departs from the `write-records` rule "Never delete a pending item without a closed entry"; a later session that follows the skill would write a closed entry for a withdrawn item unless it finds this record.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| The ID DEBT-017 is reused, since the next-ID search reads only the two ledgers | Only if the highest ID in the ledgers falls below 017, which it does not (DEBT-040 is pending) | A second item with the same ID | This ADR names DEBT-017 as taken | Nery Samuel Murillo |

## More information

- Nery made the decision on 2026-10-28, after the closed entry for DEBT-017 had been written; that entry was removed before any push.
- Related: commit 845d4da removed the two skill lines; DEBT-017 left `pending-debt.md` in commit 3354394.
