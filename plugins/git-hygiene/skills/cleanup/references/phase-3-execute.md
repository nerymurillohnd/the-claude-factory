# Phase 3: execution and final verification

The user approved either the whole plan or specific action IDs. Run only those. Each command that changes state will also raise a confirmation prompt from the guard; that is expected. Name the action ID before each command, and approve nothing that does not match it.

## 1. Revalidate

Re-run the inventory (with `--ls-remote` if the plan touches remotes) and compare with the plan's evidence: branch SHAs, worktrees, stashes, open pull requests, working tree. If anything affecting an approved action changed materially (a branch moved, a stash appeared, a pull request opened), stop, report the difference and re-plan only the affected actions with the user.

## 2. Backup first

Run the backup action, then its verification: `git bundle verify`, compare the bundle's `git bundle list-heads` with the refs it should contain, restore it into a throwaway repository and compare the ref lists, record the checksum (`shasum -a 256` or `sha256sum`). Show the user the backup path, size and checksum. Do not run any deletion or prune until the backup verifies. If it does not, fix it or stop.

## 3. Execute in order

Order: preparation → integration → local deletion → remote-impacting actions → files. For each approved action:

1. Say which ID you are running.
2. Run the exact planned commands. Remote deletions one branch at a time.
3. Verify the result with a read-only command (the ref is gone, the merge commit exists, the worktree list changed).
4. If a result is unexpected, or any step fails, do not run dependent destructive actions.

Branch deletion: use `git branch -d` for branches Git considers merged; use `-D` only when the plan recorded why the work is preserved elsewhere (integrated by another strategy, or in the backup) and the user approved that ID. Delete a worktree's branch only after the worktree is removed.

## 4. Conflicts and failures

Stop at the first conflict. Inspect the active operation (`git status`, `.git/MERGE_HEAD`, `rebase-merge/`), tell the user what conflicts, and use the recovery the plan approved: `git merge --abort`, `git cherry-pick --abort`, `git rebase --abort`. Never discard changes (`reset --hard`, `checkout --`, `clean`) merely to force completion, and never resolve a conflict by guessing: show it to the user.

## 5. Final verification

Prove the end state with fresh read-only output, not memory:

- `git branch -a -vv`, `git for-each-ref refs/heads refs/remotes`, and `git ls-remote --heads <remote>` for the actual remote branches.
- `git worktree list`, `git stash list`, `git status --short --branch --ignored`.
- Open pull requests (`gh pr list --state open`) and that no approved integration lost work: every exclusive commit is reachable from the base or from the backup bundle.
- The aim is only `main` and `origin/main`, no extra worktrees, stashes or leftovers. Anything kept because deleting it could lose data, break a protection, affect unapproved remote work, or was never verified stays, with the reason.

## 6. The backup and temporary artifacts

Remove the temporary `refs/git-hygiene-backup/*` refs once the backup is verified and no longer needed. The backup folder itself is the user's recovery copy: never delete it on your own. Once everything is verified, tell the user where it is and ask whether to keep it or remove it. Remove it only after an explicit yes, and verify it is gone. Never delete the only recoverable copy of valuable data.

## 7. Report

Report what was integrated, removed, preserved and blocked, what was verified and how (with the commands), the retained backup with its location and why, and any limitation.
