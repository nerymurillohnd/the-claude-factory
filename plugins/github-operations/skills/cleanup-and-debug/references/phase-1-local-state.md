# Phase 1: Local state

Inventory everything in the local clone. This phase is read-only, and every command runs as [Phase 0](phase-0-intake-and-preflight.md#side-effect-free-inventory) sets.

## HEAD

- Attached or detached.
- Any operation in progress: merge, rebase, cherry-pick, revert, bisect or am.

## Working tree

- Staged, unstaged, untracked and conflicted entries.
- Ignored files, collapsed to directories.
- Noise files: editor, OS and build leftovers.
- Tracked files that match ignore rules.

## Nested content

- Nested repositories.
- Submodules, with their status, URL and pinned SHA.
- Subtrees.
- LFS pointers, and LFS files that were never downloaded.

## Symlinks

- Links inside the repository.
- Broken links.
- Links that point outside the repository.

## Worktrees

- Every registration, with its path, branch and HEAD.
- Whether each one is dirty, locked, prunable, missing on disk or detached.

## Stashes

- Each entry's date, base commit and subject.
- Its tracked changes, and its untracked files, which a stash made with `-u` keeps in its third parent (`stash@{N}^3`). The manual does not document the third parent; it was confirmed on the installed Git ([git-stash][git-stash]).
- Whether its content is already in the base.

## Local branches

- Ahead and behind counts against the base.
- Author and last activity.
- Upstream gone, or never set.
- Stale branches.

## Tags

- Lightweight or annotated.
- Signed or not.
- What each one points to.

## Other ref namespaces

- Notes, `refs/pull` and tool refs.
- `refs/original`, `refs/replace` and `refs/bisect` are residue, audited in [Phase 4](phase-4-git-residue.md#leftovers-of-interrupted-operations).

## Sources

Checked on 2026-11-04.

- [git-stash][git-stash]: the stash commit's first parent is HEAD and its second records the index; `stash save` "is deprecated in favour of `git stash push`". The third parent for untracked files was confirmed with a probe on git 2.43.0.

[git-stash]: https://git-scm.com/docs/git-stash
