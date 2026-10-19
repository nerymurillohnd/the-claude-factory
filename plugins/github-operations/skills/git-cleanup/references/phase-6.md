# Phase 6: Revisions & Integration Verification

Resolve user-provided revisions to concrete commit OIDs before drawing conclusions or performing integration/cleanup actions.

## Revision Commands

```sh
git rev-parse --verify --end-of-options '<rev>^{commit}'
git merge-base <base> <topic>
git rev-list --left-right --count <base>...<topic>
git log --graph --decorate --oneline --boundary <base>...<topic>
git diff --stat <base>...<topic>
```

## Revision Walking & Comparison Rules

* **Record Object IDs:** Record the resolved base, topic, and merge-base OIDs before evaluating divergence.
* **Dot Syntax Distinctions:**
  * In revision walks (`git rev-list`, `git log`): `A..B` means commits reachable from `B` but not `A`. `A...B` is their symmetric difference (commits reachable from either ref, but not both).
  * In `git diff`: `A...B` compares `B` against the merge base of `A` and `B`—it is **not** a symmetric diff.
* **Remote Parity Caveat:** A clean `main...origin/main` relation proves only that those two refs agree; it does **not** verify that every worktree, open PR, stash, or hidden ref is reconciled.

## Safe Integration Practices

* **Integration Strategy by Intent:**
  * **Merge:** Retains shared graph history.
  * **Squash:** Produces a single atomic commit from a series.
  * **Cherry-pick:** Selects explicit, discrete commits.
  * **Revert:** Safely compensates for published changes without rewriting history.
  * **Rebase:** Rewrites private commits only; requires an explicit, reviewed recovery path before execution.
* **History Rewrite Ban:** Never rewrite published history or force-push as a cleanup shortcut.
* **Merge Simulation:** For a non-mutating merge preview, resolve the merge base and run:

  ```sh
  git merge-tree <merge-base> <base> <topic>
  ```

* **Patch Comparison:** Use `git range-diff` to compare patch series changes across rebased branches, not for graph containment checks.
* **Conflict Handling:** Stop immediately when conflicts arise. Inspect the operation state (`MERGE_HEAD`, `REBASE_HEAD`, `CHERRY_PICK_HEAD`) and choose the corresponding `--abort` or recovery command rather than improvising destructive resets.
