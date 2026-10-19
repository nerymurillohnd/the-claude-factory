# Phase 1: Context Discovery & Topology Inspection

Before proposing deletions, record the common Git directory and audit every worktree, ref, stash, and reflog.

## Topology Commands

```sh
git rev-parse --show-toplevel --git-common-dir
git worktree list --porcelain
git branch --all --verbose --no-abbrev
git stash list --date=iso-local
git reflog show --all --date=iso-local
git remote
```

## Safety & Audit Rules

* **Worktrees:** Check status and `HEAD` across all reachable worktrees. Note that a missing worktree path may still hold a valid registration and an active branch; inspect it before pruning.
* **Worktree Dry-Runs:** `git worktree prune --dry-run --verbose` is a safe preview; `prune` and `remove` mutate repository state.
* **Stashes & Reflogs:** Inspect stashes with `git stash show --stat <stash_selector>` before dropping. Remember that reflog selectors are local and subject to expiration—never promise indefinite recovery from a reflog.
* **Remotes:**
  * Use `git ls-remote --heads origin` to observe remote heads without altering local state.
  * `git fetch --prune` mutates remote-tracking refs; treat it as an active state change, not a read-only check.
  * Neither command reflects GitHub/GitLab Pull Request review or merge state.
* **Audit Boundaries:** Resolve all proposed recovery points to exact Object IDs (OIDs) and inspect commits before creating recovery refs. **Never** run `git reset`, delete refs, trigger garbage collection (`git gc`), or prune objects to "tidy" the graph during an audit.
