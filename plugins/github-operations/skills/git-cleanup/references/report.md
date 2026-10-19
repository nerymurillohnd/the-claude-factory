# Report and recommendations, step 3 (Gate 1)

The audit is complete before the report starts. Read `findings.md` and `coverage.md` from the scratch folder; do not rely on memory. The report is for a person who may not know Git: lead with what matters, explain a Git term the first time it appears ("worktree: a second checkout folder sharing one repository", "stash: uncommitted work set aside", "reflog: a local, expiring log of where branches pointed"), and use commands and SHAs only as supporting evidence, never as the explanation.

## What to ask before the recommendations

Ask the user, with `AskUserQuestion` (up to four questions per call, your recommended option first and the reason in its description), about every ambiguity that changes a recommendation. Group branches that get the same recommendation into one question. Typical questions:

- What to do with each group of branches that hold work not in the base: integrate it, keep it, or abandon it.
- Whether branches by other authors, or with an open pull request, may be touched at all.
- What to do with stale pull requests and issues.
- Whether stashes whose content is already in the base may go.
- Where the backup goes. Recommend a folder outside the repository, such as `~/git-cleanup-backups/<repo>-<date>`, written as an absolute path. Refuse a folder inside the repository.
- Which of the audit's follow-up work the user wants (refactor, bisect, a fix): see `investigate.md`.

## Report template

Write it to `report.md` in the scratch folder and present it.

```markdown
## Repository cleanup report: <repo> (<date>)

**Summary.** [Three to six sentences: what was audited, from which commit to which, what is at risk,
what is simply clutter, and the statement that nothing has been changed.]

**Scope.** Checked out: `<path>` on `<branch>` at `<short sha>`. Base: `<ref>` (`<sha>`). Audited: <n> commits,
<n> refs, <n> pull requests, <n> issues. Not inspected, and why: <list from the ledger>.

### Findings
- **F-1 <title>** — what it is, in plain words. *Effect:* what it costs or risks today. *Evidence:* the
  command and the relevant line or count. *Confidence:* high / medium / low. *If left alone:* …
- **F-2 …**

### Recommendations (awaiting your approval)
| ID | For | Target | Proposed action | Risk | How to undo it |
| :-- | :-- | :-- | :-- | :-- | :-- |
| R-1 | F-1 | `branch: x` | Delete the local branch; its content is already in `origin/main` | Low | Restore from the backup bundle |

### Questions
1. <question> — my recommendation: <answer>, because <reason>.

### Coverage ledger
| Domain | Status | Note |
| :-- | :-- | :-- |
| Branches against the base | checked | `branch-states.tsv` |
| Pull requests | BLOCKED | `gh pr list` returned 403: needs repository read access |
| Other clones on this machine | declined | you chose not to scan |
| Installed GitHub Apps | not reachable | check Settings → Integrations |

### Decision
Approve by ID, for example "approve R-1 and R-3, keep R-2". "Clean it up" approves nothing.
```

Findings are grouped: context and risks first; then branches (integrated / holding work / conflicting / unrelated / unknown); worktrees; stashes; tags; pull requests, issues and discussions; Actions and automation; external links and integrations; files and noise; history, objects and secrets by name; deferred work; refactors, bisects or debugging the audit calls for; everything `BLOCKED`. Summarize fully merged branches as a count with their list in the scratch folder, and list individually only what needs a decision. Use tables for branches (ref, state, ahead, behind, last commit, author, open pull request, recommendation), prose only where reasoning is needed.

A secret that was ever committed is reported as exposed, with the instruction to rotate it; the report names the file, never the content.

## Recommendations

Each recommendation has an ID `R-n`, the finding it answers, the exact target, the action, its risk and how it is undone. A recommendation is one of: **integrate** (its work goes into the base), **delete** (its work is already safe, with the reason), **keep** (untouched, with the reason), **investigate** (a diagnosis the audit calls for), **fix** (a change the findings call for, which lands through a branch and a pull request), **unlink** (an external item to disable, one per recommendation), or **report-only** (security-sensitive items such as deploy keys, tokens, secrets, installed apps and collaborator access: name the item, the risk and how the user changes it; the skill does not change it). Secret-like files are always kept. Rewriting history is never offered in a bulk list: the report states what a rewrite would remove and why, and it becomes a recommendation only when the user asks for it by name.

## The gate

End with the decision request and stop. Gate 1 passes only when the user chooses explicitly and names the IDs:

- A generic "clean it up", silence, a timeout, an auto-closed question or an ambiguous answer is not approval: ask again.
- An explicit refusal, or "audit only", is an answer: the run ends, with the report delivered as the final answer. Change nothing.
- If the user approves "everything except X", restate the resulting list of IDs and have them confirm it.
