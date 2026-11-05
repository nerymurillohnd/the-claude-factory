# Phase 3: History and object store

Audit the whole history, from the first commit, and the health of the object store. This phase is read-only.

## History

- Commit count.
- Root commits and orphan histories.
- Merge styles in use: merge commits, squash, rebase.
- WIP-style commits, empty commits, and commits dated in the future.

## Authors

- Identities that need a mailmap: the same person under several names or emails.
- Unsigned commits, when the repository signs commits.

## Object store

- Loose and packed object counts, against the repository's own `gc.auto` (default 6700) and `gc.autoPackLimit` (default 50) ([git-gc][git-gc]).
- Pack layout and alternates, both the file and the `GIT_ALTERNATE_OBJECT_DIRECTORIES` environment variable.
- Connectivity and integrity with `git fsck`. `--connectivity-only` skips format checks and blob contents ([git-fsck][git-fsck]). Never use `--lost-found`: it writes into `.git/lost-found/` ([git-fsck][git-fsck]).

## Weight

- The largest blobs across all history.
- Files that exist only in history.
- Generated noise committed to Git: build output, caches, vendored artifacts.

## Secrets in history

- The names of secret-like files ever committed, and whether each one still exists in the current tree.
- Names only, never contents.
- Each one is treated as exposed, whatever a later rewrite does.

## Lost work

- Unreachable and dangling commits, each with author, date and subject.
- Check each one against refs, reflogs, stashes and bundles before calling it lost. `fsck --no-reflogs` counts commits reachable only from a reflog as unreachable, so its list alone does not prove loss.

## Reflogs

- What can only be recovered from a reflog.
- When it expires: reflog entries after 90 days, or 30 days when unreachable; unreachable objects are pruned after 2 weeks ([git-gc][git-gc]).

## Done when

- [ ] The history figures cover every commit from every root.
- [ ] Author identities and unsigned commits are listed.
- [ ] Object counts are compared with the repository's own `gc` thresholds, and `fsck` ran without `--lost-found`.
- [ ] The largest blobs and the files that exist only in history are listed.
- [ ] Every secret-like file name ever committed is listed, with no content.
- [ ] Every unreachable commit is checked against refs, reflogs, stashes and bundles.
- [ ] Every section that could not be collected is in the coverage ledger.

## Sources

Checked on 2026-11-04.

- [git-gc][git-gc]: `gc.auto` "The default value is 6700"; `gc.autoPackLimit` "The default value is 50"; `--prune` "default is 2 weeks ago"; `gc.reflogExpire` "defaults to 90 days"; `gc.reflogExpireUnreachable` "defaults to 30 days".
- [git-fsck][git-fsck]: `--connectivity-only` does "not do any semantic checks"; `--lost-found` writes "into .git/lost-found/".

[git-gc]: https://git-scm.com/docs/git-gc
[git-fsck]: https://git-scm.com/docs/git-fsck
