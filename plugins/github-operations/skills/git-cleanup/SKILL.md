---
name: git-cleanup
description: Guidelines and workflows for safely auditing, evaluating, and cleaning up Git repositories, worktrees, branches, untracked/ignored paths, submodules, object stores, integration states, and isolating regressions without accidental data loss, history corruption, or secret exposure.
disable-model-invocation: true
---

# Git Repository Cleanup Skill

Provides a structured, multi-phase procedure for safely inspecting, auditing, and cleaning up a Git repository. It prioritizes data retention, worktree safety, object store provenance, safe configuration inspection, and verified revision ancestry over aggressive deletion or destructive history rewrites.

## Core Operating Protocol & Execution Lifecycle

Any repository cleanup or audit request must follow a strictly gated, 3-stage lifecycle. **Zero destructive or mutating actions may occur before explicit, itemized user authorization.**

```text
[STAGE 1: Non-Destructive Discovery & Audit]
                       │
                       ▼
[STAGE 2: User-Facing Audit Report & Stop Gate] ───► (Execution HALTED; Awaiting Granular Approval)
                       │ (User approves specific IDs: e.g., "Approve R1, retain R2")
                       ▼
[STAGE 3: Pre-Flight Check, Mutation & Verification] ──► (State Re-check ➔ Backups ➔ Ordered Mutations ➔ Report)
```

### Stage 1: Non-Destructive Discovery & Classification (Read-Only)

Read [stage-1.md](references/stage-1.md) before the first command of the audit: the read-only boundary, the six classification buckets, what to record, and which phases to read.

### Stage 2: User-Facing Audit Report & Recommendation Gate (MANDATORY HALT)

Read [stage-2.md](references/stage-2.md) when the audit is complete: the plain-language report, the finding and recommendation IDs, the report template, and the approval request.

### Stage 3: Approved Execution, Re-Validation & Post-Verification (Cleanup Starts Here)

Read [stage-3.md](references/stage-3.md) only after the user authorizes specific recommendation IDs: the pre-flight check, the rollback points, the ordered mutations, the closing report, and which phases to read.

---

## Phases

The command suites and guardrails behind the stages. Read the ones the stage names.

- [phase-1.md](references/phase-1.md): context discovery and topology. Worktrees, refs, stashes, reflogs, remotes.
- [phase-2.md](references/phase-2.md): path and workspace inventory. Untracked and ignored files, deletion previews.
- [phase-3.md](references/phase-3.md): submodules, subtrees and large storage (LFS).
- [phase-4.md](references/phase-4.md): object store, provenance and configuration security.
- [phase-5.md](references/phase-5.md): branch ancestry and verification before deleting a branch.
- [phase-6.md](references/phase-6.md): revisions and integration. Resolving revisions, dot syntax, merge, squash, rebase, conflicts.
- [phase-7.md](references/phase-7.md): diagnostic and defect isolation. Grep, blame, bisect.

---

## Reference Documentation

* **Commands:** [git-clean](https://git-scm.com/docs/git-clean) | [git-check-ignore](https://git-scm.com/docs/git-check-ignore) | [git-branch](https://git-scm.com/docs/git-branch) | [git-worktree](https://git-scm.com/docs/git-worktree) | [git-stash](https://git-scm.com/docs/git-stash) | [git-submodule](https://git-scm.com/docs/git-submodule) | [git-merge-tree](https://git-scm.com/docs/git-merge-tree) | [git-bisect](https://git-scm.com/docs/git-bisect) | [git-blame](https://git-scm.com/docs/git-blame) | [git-grep](https://git-scm.com/docs/git-grep) | [Git reference](https://git-scm.com/docs/git)
* **Revisions:** [gitrevisions](https://git-scm.com/docs/gitrevisions)
