# Stage 1: Non-Destructive Discovery & Classification (Read-Only)

* **Execution Boundary:** Run only read-only commands. Use the command suites of Phases 1 to 6 (the integration practices of Phase 6 belong to Stage 3), and Phase 7 when diagnosing an issue.
* **Command Suites:** Read `phase-1.md` to `phase-6.md` before you inspect, and `phase-7.md` when the user brought a defect to isolate.
* **Zero Mutations:** Do not run mutating commands (`git branch -d/-D`, `git clean -f`, `git worktree remove/prune`, `git reset`, `git gc`). Use dry-run flags only (e.g., `git clean -ndX`, `git worktree prune --dry-run`). Run `git status` as `GIT_OPTIONAL_LOCKS=0 git status` so it does not refresh the index.
* **Taxonomy Assignment:** Classify every ref, file, worktree, and submodule into one of the 6 taxonomy buckets:
  1. **Active Work:** Uncommitted changes, in-flight worktree checkouts, currently active task branches.
  2. **Authoritative Ref:** Protected default branches (`main`, `master`, production tracking heads), release tags.
  3. **Retained Recovery Evidence:** Stashes, emergency backup refs, temporary WIP commits awaiting verification.
  4. **Stale Operational Risk:** Detached worktrees pointing to deleted paths, orphaned remote branches with open upstream revisions, uninitialized or dirty submodule checkouts.
  5. **Deletion Candidate:** Branches fully merged into target upstream, verified clean and unreferenced elsewhere; unneeded build caches with verified low rebuild cost.
  6. **Unknown:** Items requiring user clarification (e.g., unvetted ignored folders, unclassified tool refs, detached heads).
* **Scope & Limitation Capture:** Record exact commit SHAs, timestamps, inspected branch contexts, and explicitly note uninspected boundaries (e.g., provider merge state, unpulled remote heads).
* **Secret Redaction:** Redact credential-bearing configurations, auth tokens, and private remote URLs from all outputs.
