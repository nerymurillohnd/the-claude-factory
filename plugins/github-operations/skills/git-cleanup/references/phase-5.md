# Phase 5: Branch Ancestry & Verification

Before deleting or pruning local branches:

1. **Resolve Base:** Identify the intended base branch (e.g., `main`, `master`, `develop`).
2. **Worktree Check:** Verify across all active worktrees that the branch under review is not checked out elsewhere.
3. **Ancestry Verification:** Verify ancestry using safe checks before deletion:

   ```sh
   git merge-base --is-ancestor <branch> <base>
   git branch --merged <base>
   ```
