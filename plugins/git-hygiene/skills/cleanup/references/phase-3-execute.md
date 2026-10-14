# Phase 3: execution and final verification

The user approved either the whole plan or specific action IDs, and A-01 was added. Run only those. Each command that changes state will also raise a confirmation prompt from the guard; that is expected. Name the action ID before each command, so the user can match the prompt to it, and tell the user to refuse any prompt that does not match. Every Git command takes `-C "<repo>"`, every `gh` subcommand `-R <owner>/<repo>`.

## 1. Save the approved plan

Create the backup folder the user chose (`mkdir -p`, nothing else yet), then write the plan exactly as approved, with its action IDs and the approved IDs, to `<backup dir>/plan.md`. Context can be compacted mid-run: after a compaction, re-read this file, `plan.md` and `SKILL.md` before the next action (ask the user for the backup folder if you no longer know it). Only the IDs listed there may run. Append each action's status to `plan.md` right after it finishes (`done`, `failed` or `skipped`, with the time), so a resumed run starts at the first action that is not `done`. If you re-plan an action later, update `plan.md` and get the new approval first.

## 2. Revalidate

Re-run the inventory (with `--ls-remote` if the plan touches remotes) into `<backup dir>/inventory-revalidated.json` and compare it with the plan's evidence: branch SHAs, worktrees, stashes, open pull requests, working tree. When resuming, compare only the actions that are not `done`. If anything affecting an approved action changed materially (a branch moved, a stash appeared, a pull request opened), stop, report the difference and re-plan only the affected actions with the user.

## 3. Backup first (A-01)

Run A-01 as one action, in the order of Phase 2 §3, then verify it before any other action:

- `git bundle verify <dir>/all.bundle` succeeds.
- `git bundle list-heads <dir>/all.bundle`, leaving out `HEAD`, equals the refs it should hold.
- A restore test: `git init --bare <temp dir>/restore.git`, then `git -C <temp dir>/restore.git fetch <dir>/all.bundle 'refs/*:refs/*'`; its ref list must match. Remove the temp dir afterwards.
- Record the checksum in the manifest (`shasum -a 256`, or `sha256sum` where that is what exists).
- Delete the temporary `refs/git-hygiene-backup/*` refs.

Show the user the backup path, size and checksum. Do not run any other action until the backup verifies. If it does not, fix it or stop.

## 4. Execute in order

Order: the class order of Phase 2 §3 (`prep`, `integrate`, `publish`, `local-delete`, `remote-delete`, `files`), A-01 first. For each approved action:

1. Say which ID you are running.
2. Run the exact planned commands. Remote deletions one at a time.
3. Verify the result with a read-only command (the ref is gone, the merge commit exists, the worktree list changed).
4. If a result is unexpected, or any step fails, do not run dependent actions (§5).

Before every deletion, local or remote, run the containment check the plan recorded for it. For a remote branch or tag also re-read its live SHA (`git ls-remote --heads <remote> <branch>`, or `--tags` for a tag) and delete only if it equals the audited SHA: someone may have pushed since. If a check fails, skip that deletion, report it, and carry on only as §5 says.

Branch deletion: use `git branch -d` for branches Git considers merged; use `-D` only when the plan recorded the accepted reason (Phase 2 §3) and the user approved that ID. Delete a worktree's branch only after the worktree is removed. When you finish, the base branch must be checked out, so a branch is never deleted while it is checked out.

## 5. Conflicts and failures

A conflict stops that action. Inspect the active operation (`git status`, and the files `git rev-parse --git-path MERGE_HEAD`, `CHERRY_PICK_HEAD`, `rebase-merge` name; `.git` is a file in a linked worktree), tell the user what conflicts, and use the action's Recovery field (by default the matching `git merge --abort`, `git cherry-pick --abort` or `git rebase --abort`). Never discard changes (`reset --hard`, `checkout --`, `clean`) merely to force completion, and never resolve a conflict by guessing: show it to the user.

Abort the conflicted operation with its Recovery step, then handle it like any other failure: skip only the actions that depend on it, report it, and ask the user before continuing with the independent actions. Whatever the user decides, still run §6 and §8 for what was done.

## 6. Final verification

Prove the end state with fresh read-only output, not memory:

- `git branch -a -vv`, `git for-each-ref refs/heads refs/remotes`, and `git ls-remote --heads <remote>` for the actual remote branches.
- `git worktree list`, `git stash list`, `git status --short --branch --ignored`, `git for-each-ref refs/git-hygiene-backup` (must be empty).
- Open pull requests (`gh -R <owner>/<repo> pr list --state open`).
- No integration lost work: for every exclusive tip recorded in Phase 1 (`<scratch>/audit-log.md`), `git merge-base --is-ancestor <tip> <remote>/<base branch>` succeeds, or the tip is in the backup bundle and the plan said so; and the local base branch equals `<remote>/<base branch>`.
- The aim is only `main` and `origin/main`, no extra worktrees, stashes or leftovers. Anything kept because deleting it could lose data, break a protection, affect unapproved remote work, or was never verified stays, with the reason.

## 7. The backup and temporary artifacts

The temporary refs were removed by A-01; the check above proves it. The backup folder itself is the user's recovery copy: never delete it on your own. Once everything is verified, tell the user where it is and ask whether to keep or remove it. If any deleted item relied on the backup alone (`backup-only`), list those items first and require a second explicit yes that names them: removing the backup then makes the loss permanent. Remove the folder only after an explicit yes, and verify it is gone. Never delete the only recoverable copy of valuable data without that explicit, informed yes. The scratch folder holds no user data; remove it with the same care once the user has what they need.

## 8. Report

Report what was integrated, removed, preserved and blocked, what was verified and how (with the commands), the retained backup with its location and why, and any limitation.
