# Integrating work into the base, and publishing it

Read this when an approved action is `integrate` or `publish`. An integration brings the work of a branch, a stash or a pull request into the base branch; publishing sends that base to the remote. Nothing the integration makes redundant is deleted until the base is published (`plan.md`, class order).

## Choose the method by intent, in the plan

Pick the method while planning, say why, and write the exact commands in the action. Ask the user when the repository's own history style is unclear.

| Intent | Method | Command |
| :-- | :-- | :-- |
| The branch is a clean line on top of the base; keep each commit | Fast-forward | `git merge --ff-only <branch>` |
| Keep the branch's history and mark where it joined | Merge commit | `git merge --no-ff <branch> -m "<message>"` |
| Land the branch as one commit (the repository squash-merges) | Squash | `git merge --squash <branch>` then `git commit -m "<message>"` |
| Take specific commits only | Cherry-pick | `git cherry-pick -x <sha>...` (`-x` records the source SHA) |
| Undo a published commit without rewriting history | Revert | `git revert <sha>` (a merge commit needs `-m 1`) |
| Work in a stash | Rescue branch first, then one of the above | `git branch rescue/stash-N 'stash@{N}'` |

Follow the style the audit found in `Shape of the history` (merge commits, squash `(#123)` subjects, linear). Rebasing a branch that exists on the remote is not an integration method here, because it needs a force push; if a rebase is truly wanted, it is a separate action the user approves by name, on a local-only branch.

## Preview before the plan, check before the run

Preview without touching the repository: no working tree, ref or index changes. `merge-tree --write-tree` does write tree objects, so point it at the temporary object store the audit uses (`intake-local.md`, section 1.4: `tmp="<scratch>/objects"`, `shared=$(git -C "<repo>" rev-parse --path-format=absolute --git-path objects)`):

```sh
GIT_OBJECT_DIRECTORY="$tmp" GIT_ALTERNATE_OBJECT_DIRECTORIES="$shared" git -C "<repo>" merge-tree --write-tree --name-only <base> <branch>   # exit 0: clean, prints the resulting tree; exit 1: conflicts, lists the files
git cherry -v <base> <branch>                                 # "+" commits the base lacks, "-" ones it already has by content
git log --oneline <base>..<branch>                            # exactly which commits would come in
git diff --stat <base>...<branch>                             # what they change
```

State the preview in the plan. A conflicting integration is not planned as an automatic action: tell the user which files conflict and ask how to proceed (see `execute.md`, "When something goes wrong").

## Running an integration

Each integration runs in the checkout where the base branch is clean:

1. `git -C "<repo>" status --porcelain` prints nothing, and the base branch is checked out here and in no other worktree (`git worktree list`). If not, ask; never stash, commit or discard the user's changes on your own.
2. If the remote base is ahead, fast-forward the local base first: `git fetch <remote> <base>` then `git merge --ff-only <remote>/<base>`. If that cannot fast-forward, the local base has commits the remote lacks: stop and ask.
3. Run the planned method. Record `git rev-parse HEAD` before and after.
4. Verify: `git merge-base --is-ancestor <audited branch tip> HEAD` exits 0 (merge, fast-forward) or the content check holds (squash and cherry-pick: `git cherry <base-before> HEAD` or `git diff <base-before> HEAD --stat` shows what the plan said).
5. If the repository defines its own checks (a test or lint command in its README, `Makefile`, `package.json`, CI file), run them and record the output; a failure stops the publish.

## Signing

Use the user's own configuration and never override it. Read it (`git config --get commit.gpgsign`, `gpg.format`, `user.signingkey`) and let `git commit` / `git merge` use it. If signing is configured and fails, or the environment cannot sign, stop and tell the user: commits made here would be unsigned, and an unsigned commit is not acceptable for this repository. Never pass `--no-gpg-sign` or `-c commit.gpgsign=false`, and never configure a key. When the session cannot sign (a remote or cloud session), prepare the commands and the preview, stop before the commit, and let the user run them.

## Publishing

- `git -C "<repo>" push <remote> <base>`: plain, never with a force flag. If the base is protected or requires pull requests, do not push to it: put the integration on a branch (`git push <remote> <base>:<new branch>` or from a new branch) and open a pull request only if the user authorized one (`gh pr create` with the repository's labels, following the PR lifecycle in `pr/lifecycle.md`). Fixes always travel this way.
- Check: `git ls-remote --heads <remote> <base>` returns the SHA that `git rev-parse <base>` gives.
- Push tags only if the plan names them: `git push <remote> refs/tags/<tag>`.

Only after a verified publish may the plan's `local-delete` and `remote-delete` actions for the integrated branches run, and each still runs its own containment check.
