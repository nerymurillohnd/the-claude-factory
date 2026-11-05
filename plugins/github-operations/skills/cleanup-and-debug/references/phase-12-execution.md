# Phase 12: Execution

Run the approved actions. Nothing outside the approved plan runs.

## Order

- Run one action at a time, in class order, each after its containment check.
- Publish every integration before deleting anything it makes redundant.
- Preview every integration first with `git merge-tree --write-tree` against a temporary object store.

## Branches, stashes and files

- Delete local branches with `git branch -d`, from the base branch. It refuses a branch not fully merged into its upstream or HEAD ([git-branch][git-branch]). Report the refusal; `-D` needs its own approved action with the reason.
- Never drop a stash holding work not in the base before it is in a rescue branch: `git branch rescue/stash-<n> 'stash@{<n>}'`.
- Preview every clean with `git clean -n -d -X`, which covers ignored files only ([git-clean][git-clean]). Never use `-x`, and never a second `-f`, which removes untracked nested repositories ([git-clean][git-clean]).
- Remove worktrees with `git worktree remove`, which refuses unclean ones ([git-worktree][git-worktree]).

## External links on GitHub

- One approved action per item, each with its reversibility stated in the plan.
- Disable a workflow with `gh workflow disable <name or id> -R <owner>/<repo>`; `gh workflow enable` undoes it.
- Delete an artifact with `gh api -X DELETE repos/<owner>/<repo>/actions/artifacts/<id>`, and a cache with `gh cache delete <id> -R <owner>/<repo>`. Neither can be undone.

## Signing

- Merges and reverts follow the repository's signing configuration. Never use `--no-gpg-sign`.

## Maintenance

- Runs last, after everything else is validated, because pruning cannot be undone.
- `git gc` with the repository's own expiry settings is the default.
- `git gc --prune=now` and `git reflog expire --expire=now --all` are separate actions approved by name. Nothing else may write to the repository while they run ([git-gc][git-gc]).

## History rewrite

- Only when the user asked for it by name, with its own approval.
- Use `git filter-repo` in a fresh mirror clone: it refuses to run outside a fresh clone without `--force` ([git-filter-repo][filter-repo]).
- Publish with `--force-with-lease` and nothing broader ([git-push][git-push]).

## Never

- `reset --hard`, `checkout --`, `restore` that discards work, or `clean -x`.
- Any force push other than `--force-with-lease` inside an approved history rewrite.
- `fsck --lost-found`.
- Reading credential helpers or credential stores.
- Touching other people's content or security-sensitive items.

## Failure

- Record a failed action with its raw output, and skip every action that depends on it.
- A conflict stops that action and its dependents. Never discard changes to force an operation through.

## Done when

- [ ] Every approved action ran, failed with its output recorded, or was skipped because a dependency failed.
- [ ] No action ran outside the plan.
- [ ] Maintenance ran last, if it was approved.

## Sources

Checked on 2026-11-04.

- [git-branch][git-branch]: "The branch must be fully merged in its upstream branch, or in HEAD"; `-D` is a "Shortcut for --delete --force".
- [git-clean][git-clean]: `-X` "Remove only files ignored by Git"; Git refuses untracked nested repositories "unless a second -f is given".
- [git-worktree][git-worktree]: "remove refuses to remove an unclean worktree unless --force is used".
- [git-gc][git-gc]: "--prune=now prunes loose objects regardless of their age and increases the risk of corruption if another process is writing to the repository concurrently".
- [git-filter-repo][filter-repo]: aborts "if run from a repo that is not a fresh clone"; requires git 2.36.0 or later and python3 3.6 or later.
- [git-push][git-push]: `--force-with-lease` updates the remote ref only "if the current value of the remote ref is the expected value".

[git-branch]: https://git-scm.com/docs/git-branch
[git-clean]: https://git-scm.com/docs/git-clean
[git-worktree]: https://git-scm.com/docs/git-worktree
[git-gc]: https://git-scm.com/docs/git-gc
[filter-repo]: https://github.com/newren/git-filter-repo
[git-push]: https://git-scm.com/docs/git-push
