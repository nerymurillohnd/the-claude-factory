# Phase 2: Local versus remote

Every comparison is made by full object ID.

- Live remote heads and tags, read without fetching.
- **Sync state of every branch,** local against its live remote counterpart. Each branch gets exactly one state:
  - identical;
  - local only;
  - remote only;
  - ahead (unpushed commits);
  - behind;
  - diverged.
- **Tags** whose SHA differs between local and remote, and tags present on only one side.
- **Upstreams:** the remote branch was deleted (upstream gone), or no upstream was ever set.
- **Remote-tracking refs** that are out of date against the live remote.
- **Pull request heads:** each open pull request's head SHA against the local branch of the same name.
- Integration state of every branch against the live base, tested in this order:
  1. merged;
  2. patch-equivalent (rebased);
  3. content already in the base (squash-merged);
  4. would conflict with the base;
  5. holds exclusive commits, or has unrelated history.
- Local and remote default branches that disagree, and renamed or transferred repositories whose old URLs are still in the remotes.
