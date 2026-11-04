# Phase 3: History and object store

- **Whole history, from the first commit:**
  - commit count, root commits and orphan histories;
  - merge styles in use;
  - WIP-style commits, empty commits and commits dated in the future.
- **Authors:** identities that need a mailmap, and unsigned commits when the repository signs.
- **Object store:**
  - loose and packed counts, against the repository's `gc` thresholds;
  - pack layout, alternates (file and environment), connectivity, and integrity (`fsck`).
- **Weight:** the largest blobs across all history, files that exist only in history, and generated noise committed to Git.
- **Secrets in history:** the names of secret-like files ever committed, and whether each one still exists. Names only, never contents. Each one is treated as exposed.
- **Lost work:** unreachable and dangling commits, with author, date and subject. Each is checked against refs, reflogs, stashes and bundles before it is called lost.
- **Reflogs:** what can only be recovered from a reflog, and when it expires.
