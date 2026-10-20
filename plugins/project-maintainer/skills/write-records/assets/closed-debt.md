<!--
Template for .claude/maintainer/technical-debt/closed-debt.md.
Create the ledger from this template the first time a debt item is closed: write everything below this
comment into the new file and leave this comment out.
Keep the "Entry format" comment at the end of the new file. Each item is copied from it, above that comment.
Fill every {{placeholder}}. Write "none" in a field with nothing to report. Leave no placeholder behind.
-->

# ✅ Closed Debt

> [!NOTE]
> The history of technical and maintenance debt that is no longer open: fixed, no longer applicable, or kept for good on purpose. Each entry holds the evidence that closes it. Entries arrive here from `pending-debt.md` with the same ID.

**Important:** a closed entry is a dated historical record. If a later change invalidates the closure, keep the original entry and open a new pending item that links back to it. The only field that changes afterwards is "Superseded by".

## 🚦 Outcomes

| Outcome | Meaning | Evidence it needs |
| --- | --- | --- |
| resolved | A fix was made and it works | A positive check and a negative check |
| obsolete | The condition no longer exists, with no fix aimed at it: code removed, architecture changed, logged in error or duplicated | A negative check, and what changed |
| accepted | The user decided to keep the condition for good | The accepted ADR that records the decision |

## 📚 Index

| Date | ID | Outcome | Closure | Superseded by |
| --- | --- | --- | --- | --- |

## 🏁 Closed items

*No closed items yet.*

<!--
Entry format. Copy this block above this comment for each closed item and add its row to the Index.
Use the ID the item had in pending-debt.md. Delete these instructions from the copy.

### DEBT-NNN — {{Short closure title}}

| Field | Value |
| --- | --- |
| **Outcome** | {{resolved, obsolete or accepted}} |
| **Closed on** | {{YYYY-MM-DD}} |
| **Logged on** | {{YYYY-MM-DD, copied from the pending entry}} |
| **Owner** | {{Copied from the pending entry}} |

#### ❗ The problem

{{The original limitation, risk or follow-up, as it stood in the pending entry.}}

#### 🔧 The closure

{{resolved: the corrective change and the resulting state. obsolete: what changed and why the condition no longer applies, or that it was logged in error or duplicates DEBT-NNN. accepted: the ADR ID and the decision to keep the condition.}}

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | {{resolved: the fix works, with commands, tests or review. obsolete: "not applicable". accepted: the ADR ID with status accepted.}} |
| 🚫 **Negative:** the original failure or condition is gone | {{resolved or obsolete: it no longer reproduces or exists; showing that a new path works is not enough. accepted: "not applicable".}} |

#### 🔗 Follow-up

- **Residual risk:** {{Anything left over, or "none".}}
- **Closed by:** {{The ADR ID, commit or pull request that caused the closure, or "none".}}
- **Related records:** {{Links to issues, ADRs or PRs, or "none".}}
- **Superseded by:** {{The ID of a newer item when this closure no longer describes the current state, or "none".}}
-->
