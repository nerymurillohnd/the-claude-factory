# Phase 2: Local versus remote

Compare the local clone with the live remote. This phase is read-only: it reads the remote without fetching, because `fetch` moves remote-tracking refs.

## Rules

- Compare by full object ID, never by abbreviated SHA. Its length follows the object format found in [Phase 0](phase-0-intake-and-preflight.md#repository-format).
- Read live remote heads and tags without fetching.

## Branch sync state

Give every branch exactly one state, local against its live remote counterpart:

- Identical.
- Local only.
- Remote only.
- Ahead (unpushed commits).
- Behind.
- Diverged.

## Tags

- Tags whose SHA differs between local and remote.
- Tags present on only one side.

## Upstreams and remote-tracking refs

- Upstream gone: the remote branch was deleted.
- No upstream ever set.
- Remote-tracking refs out of date against the live remote.

## Pull request heads

- Each open pull request's head SHA against the local branch of the same name.

## Integration state

Test every branch against the live base, in this order, and keep the first state that applies:

1. Merged.
2. Patch-equivalent (rebased).
3. Content already in the base (squash-merged).
4. Would conflict with the base.
5. Holds exclusive commits, or has unrelated history.

States 3 and 4 come from `git merge-tree --write-tree`: exit status 0 means a clean merge and 1 means conflicts ([git-merge-tree][git-merge-tree]). It writes tree objects, so point it at a temporary object store and the repository gets nothing new.

## Default branch and repository identity

- Local and remote default branches that disagree.
- Renamed or transferred repositories whose old URLs are still in the remotes.

## Sources

Checked on 2026-11-04.

- [git-merge-tree][git-merge-tree]: "For a successful, non-conflicted merge, the exit status is 0. When the merge has conflicts, the exit status is 1"; "a new toplevel tree object is created".

[git-merge-tree]: https://git-scm.com/docs/git-merge-tree
