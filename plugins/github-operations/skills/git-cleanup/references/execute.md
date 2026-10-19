# Backup, revalidation and execution, steps 5 and 6

Run only what Gate 2 approved, in the plan's class order. The audit was read-only; from here the commands change things, so every action is checked before it runs and recorded after.

## Before the first action

1. **Save the approved plan** as `plan.md` in the backup folder (not in the repository), with the approved IDs marked. Everything below is appended to it, so a run that is interrupted or compacted can resume from the file instead of from memory.
2. **Revalidate.** The world may have moved since the audit. Re-run the audit sections the approved actions depend on (branch states, worktrees and stashes, `git ls-remote`, pull requests) and compare with the audited SHAs in the plan. Any difference that touches an approved action stops that action: report it and ask. Do not "adapt" an action to new facts on your own.
3. **Check the starting state** with `git status --porcelain=v1 --branch` in the repository and each worktree the plan touches. Work that is not in the backup stops the run until `A-01` covers it.
4. **Set the ground rules for this step:** no force flag anywhere (`--force`, `-f`, `+refspec`, `--force-with-lease` included) except in a `history-rewrite` action that names it; no `git clean -x`, no `git stash --all`, no `git stash branch`; no `git reset --hard`, `git checkout .`, `git restore .` or `git switch --discard-changes` on work that is not in the backup; no `--no-verify`; commits are made with the user's own signing configuration (see `integrate.md`).

## A-01, the backup, always first

Make it as `plan.md` describes, in the folder the user chose, then verify it. All of this must pass before any other action starts:

```sh
git -C "<repo>" bundle verify "<dir>/all.bundle"                              # "okay", and "records a complete history"
git -C "<repo>" bundle list-heads "<dir>/all.bundle" | wc -l                    # the head count is not zero
sha256sum "<dir>/all.bundle" > "<dir>/all.bundle.sha256"                       # macOS: shasum -a 256
git clone --quiet --mirror "<dir>/all.bundle" "<dir>/restore-test.git"          # the restore test, in a fresh folder
git -C "<dir>/restore-test.git" fsck --connectivity-only
git -C "<dir>/restore-test.git" for-each-ref --format='%(refname) %(objectname)' | sort > "<dir>/restored-refs.txt"
git -C "<repo>" for-each-ref --format='%(refname) %(objectname)' refs/heads refs/tags refs/remotes refs/git-cleanup-backup | grep -v '/HEAD ' | sort > "<dir>/live-refs.txt"
diff "<dir>/live-refs.txt" "<dir>/restored-refs.txt"                           # no difference
git -C "<repo>" apply --check < "<dir>/uncommitted-<name>.patch"                # only when the tree is as it was when the patch was taken
```

Then read the backup's contents with `tar -tf` and `wc -l` and compare them with `manifest.txt`. If any check fails, fix the backup and repeat; if it cannot be fixed, stop the run and tell the user what is not covered. Finally delete the rescue refs (`git update-ref -d refs/git-cleanup-backup/<name>`, one per ref) and confirm `git for-each-ref refs/git-cleanup-backup` prints nothing.

Remove `restore-test.git` only after the user has kept or discarded the backup at step 8.

## For every other action

Run these in order. A failure at any point stops the action, not the whole run, unless a later action depends on it (then it stops too).

1. **Pre-flight.** Re-read the audited SHA of each item (`git rev-parse --verify -q <ref>`, `git ls-remote --heads origin <branch>` for remote items) and compare it with the plan. Run the action's containment check (`plan.md`, "Every deletion carries a containment check"). If the check fails, skip the action and say why.
2. **Run the commands exactly as planned.** One at a time, capturing the output and exit code (`out=$(...); code=$?`). Do not chain deletions in one command so that one failure hides the others.
3. **Check the result** with the action's validation criterion (the read-only command and the exact result written in step 4). If it does not hold, the action failed, whatever the exit code said.
4. **Record it** by appending to `plan.md`: action ID, time, status (`done`, `failed`, `skipped`), the command, and the raw output or the first and last ten lines of it.

### Commands by class

**`prep`**
- Fetch: `git -C "<repo>" fetch --prune <remote>` is allowed here and only here (it changes remote-tracking refs, which the backup contains). State what `--prune` removed (`git for-each-ref refs/remotes` before and after).
- Rescue branch for a stash: `git -C "<repo>" branch rescue/stash-<N> 'stash@{<N>}'` (the stash commit carries its untracked files in `^3`, and the branch keeps them reachable). For a lost commit: `git branch rescue/lost-<short sha> <sha>`. A rescue branch is never deleted by the skill.
- Switching to a clean base: `git -C "<repo>" switch <base>` only when `git status --porcelain` prints nothing.

**`investigate`, `fix`**: see `investigate.md`. **`integrate`, `publish`**: see `integrate.md`.

**`local-delete`**
- Branch, from the base branch with the base checked out and clean: `git -C "<repo>" branch -d <branch>`. If `-d` refuses, record it as `failed` with Git's message and report it. Never retry with `-D` unless an approved action names `-D` for that branch.
- Worktree: `git -C "<repo>" worktree remove "<path>"` (no `--force`; it refuses on a dirty or locked worktree, which is what you want). Then `git worktree prune` only if `git worktree list --porcelain` still shows a missing path flagged `prunable`. The branch is deleted afterwards, in its own command.
- Stash: drop in descending index order, `git -C "<repo>" stash drop 'stash@{<N>}'`, re-reading `git stash list` after each drop, because indexes shift.
- Tag: `git -C "<repo>" tag -d <tag>`.
- Stale remote-tracking ref: `git -C "<repo>" branch -dr <remote>/<branch>` (this only edits the local ref).

**`remote-delete`** (one branch or tag per action, after the live SHA matches the audited SHA)
- Branch: `git -C "<repo>" push <remote> --delete <branch>`. Tag: `git -C "<repo>" push <remote> --delete refs/tags/<tag>`.
- Never delete the default branch, a protected branch, or a branch with an open pull request unless that pull request is closed by an approved `github-close` action that ran before it. Deleting a pull request's head branch closes the pull request: say so in the plan.

**`github-close`** (one item per action, always with a comment explaining why; the comment text is part of the plan)
- Pull request: `gh pr close <number> -R <o>/<r> --comment "<text>"`. Issue: `gh issue close <number> -R <o>/<r> --reason "not planned" --comment "<text>"` (or `completed`, as the plan says). Discussion: through the GraphQL `closeDiscussion` mutation, only if the plan names it.
- Nothing is deleted, and other people's comments are not touched. Closing is reversible by reopening (`gh pr reopen`, `gh issue reopen`).

**`external-unlink`** (one action per item)
- Disable a workflow: `gh workflow disable <name or id> -R <o>/<r>`; undone with `gh workflow enable`.
- Delete an artifact or cache: `gh api -X DELETE repos/<o>/<r>/actions/artifacts/<id>`; `gh cache delete <id> -R <o>/<r>`. Irreversible: the plan says so.
- Remove a webhook: `gh api -X DELETE repos/<o>/<r>/hooks/<id>`. Irreversible; the plan records its URL (credentials redacted) and events so the user can recreate it.
- Stop a tunnel or job: only the process or entry the plan names (`kill <pid>` after re-checking that the pid still runs the audited command; `launchctl bootout` / `crontab` edits only for the exact entry). Never `kill -9` as a first move.

**`files`**: preview with `git -C "<repo>" clean -n -d -- <paths>` and compare with the plan; then `git clean -f -d -- <paths>` with exactly those paths. Never `-x`, never a second `-f`, never without a path list. Secret-like files are never in the list.

**`maintenance`**: `git -C "<repo>" gc` (repository defaults), or the exact approved forms (`git reflog expire --expire=now --all`, `git gc --prune=now`). Nothing else may touch the repository while it runs. Check `git count-objects -vH` before and after and record both.

**`history-rewrite`**: only as `plan.md` describes, in a fresh mirror clone made from the backup, never in the working repository.

## When something goes wrong

- A merge, cherry-pick, rebase or revert stops on a conflict: `git <command> --abort` (that command's own abort), confirm `git status` is clean and `git rev-parse HEAD` equals the pre-action SHA, record the action as `failed`, and report which files conflicted. Resolving conflicts is a new decision for the user, not something to improvise.
- A push is rejected: do not force. Fetch, show what moved (`git log --oneline <local>..<remote>`), mark the action `failed` and ask.
- A deletion is refused by Git, a hook or branch protection: record the message and stop that action. Do not lift protection or bypass a hook.
- A check you did not expect fails (a different SHA, a branch that vanished, a dirty tree): stop the run, say what you saw, and ask.
- Restoring is a plan of its own: the backup's `manifest.txt` has the commands (`git fetch "<dir>/all.bundle" '<ref>:<ref>'` for a branch, `git apply` / `tar -x` for uncommitted work). Never restore silently; tell the user what you are about to put back and why.

## Resuming after an interruption

Read `plan.md` in the backup folder: every action has a status, and everything not `done`, `failed` or `skipped` is still pending. Re-run the revalidation for the pending actions, then continue in class order. Never repeat an action marked `done`.
