# Phase 1: Local state

- **HEAD:** attached or detached, and any operation in progress (merge, rebase, cherry-pick, revert, bisect, am).
- **Working tree:**
  - staged, unstaged, untracked and conflicted entries;
  - ignored files, collapsed to directories;
  - noise files (editor, OS, build);
  - tracked files that match ignore rules.
- **Nested content:** nested repositories, submodules (status, URL, pinned SHA), subtrees, LFS pointers, and LFS files that were never downloaded.
- **Symlinks:** links inside the repository, broken links, and links that point outside it.
- **Worktrees:** every registration with its path, branch and HEAD, and whether it is dirty, locked, prunable, missing on disk or detached.
- **Stashes:** each entry's date, base commit and subject, its tracked changes, and its untracked files in `^3`. Also whether its content is already in the base.
- **Local branches:**
  - ahead and behind against the base;
  - author and last activity;
  - upstream gone, or never set;
  - stale.
- **Tags:** lightweight or annotated, signed or not, and what each one points to.
- **Other ref namespaces:** notes, `refs/pull` and tool refs. `refs/original`, `refs/replace` and `refs/bisect` are residue and belong to Phase 4.
