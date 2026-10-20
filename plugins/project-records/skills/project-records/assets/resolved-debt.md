<!--
Template for <debt>/resolved-debt.md.
Create the ledger from this template the first time a debt item is resolved: write everything below this
comment into the new file and leave this comment out.
Keep the "Entry format" comment at the end of the new file. Each item is copied from it, above that comment.
Fill every {{placeholder}}. Write "none" in a field with nothing to report. Leave no placeholder behind.
-->

# ✅ Resolved Debt

> [!NOTE]
> The history of technical and maintenance debt that was corrected and verified: what was wrong, what changed and the evidence that closes it. Entries arrive here from `pending-debt.md` with the same ID.

**Important:** a resolved entry is a dated historical record. If a later change invalidates a resolution, keep the original entry and open a new pending item that links back to it. The only field that changes afterwards is "Superseded by".

## 📚 Index

| Date | ID | Resolution | Superseded by |
| --- | --- | --- | --- |

## 🏁 Resolved items

*No resolved items yet.*

<!--
Entry format. Copy this block above this comment for each resolved item and add its row to the Index.
Use the ID the item had in pending-debt.md. Delete these instructions from the copy.

### DEBT-NNN — {{Short resolution title}}

| Field | Value |
| --- | --- |
| **Resolved on** | {{YYYY-MM-DD}} |
| **Logged on** | {{YYYY-MM-DD, copied from the pending entry}} |
| **Owner** | {{Person, team, system or repository area}} |

#### ❗ The problem

{{The original limitation, risk or follow-up, as it stood in the pending entry.}}

#### 🔧 The fix

{{The corrective change and the resulting state. If the condition disappeared without a fix, such as removed code, say so here.}}

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the fix works | {{Commands, tests or review.}} |
| 🚫 **Negative:** the original failure no longer reproduces | {{Not just that the new path works.}} |

#### 🔗 Follow-up

- **Residual risk:** {{Anything left over, or "none".}}
- **Related records:** {{Links to issues, ADRs or PRs, or "none".}}
- **Superseded by:** {{The ID of a newer item when this resolution no longer describes the current state, or "none".}}
-->
