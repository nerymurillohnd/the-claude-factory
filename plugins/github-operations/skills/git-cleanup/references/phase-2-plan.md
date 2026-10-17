# Phase 2: findings, plan and approval

## 1. Findings

Present what Phase 1 found (the same grouping as `<scratch>/findings.md`): context and risks, branches (fully integrated / holding exclusive work / conflicting / unknown), worktrees, stashes, tags, pull requests, files and noise, history, `BLOCKED` items. Quote the commands you ran and the relevant lines of their results. Keep it scannable: a table for the branches that need a decision (ref, kind, ahead, behind, signals, last commit, author, open PR, your recommendation), prose only for what needs reasoning; summarize the fully merged branches as a count with their list in the scratch folder.

## 2. Questions

Before drafting the plan, ask the user about every ambiguous finding, preservation priority, integration choice or acceptable risk, with `AskUserQuestion` (up to four questions per call; put your recommended option first and say why in its description). Group branches that get the same recommendation into one question instead of asking per branch. Typical questions: what to do with each group holding unmerged work, whether remote branches of other authors may be touched at all, what to do with stale pull requests, whether stashes whose content is already in the base can go, and where to put the backup. Recommend a backup folder outside the repository such as `~/git-cleanup-backups/<repo>-<date>` (written as an absolute path); refuse a folder inside the repository.

Choose the integration strategy by the work's intent:

| Intent | Strategy |
| :-- | :-- |
| Keep shared history and the branch's commits | `git merge --no-ff` (or fast-forward) |
| One tidy commit for a messy branch | `git merge --squash` then commit |
| Take only some commits | `git cherry-pick <commits>` |
| Compensate a published change | `git revert` |
| Tidy a private, unpublished branch | `git rebase`, only with a reviewed recovery path (the backup bundle) |

Rewriting published history and force-pushing are never options.

For every branch, worktree, stash and tag decide one of: **integrate** (its work goes into the base), **delete** (its work is already safe, with the reason), or **keep** (not touched, with the reason). Remote deletions are judged one by one against repository visibility, protections, authors and open pull requests; never assume all remote branches go. Secret-like files are always kept.

## 3. The plan

One action per operation. Give each a unique ID (`A-01`, `A-02`, …) and these fields:

- **ID and title**
- **Class** (table below)
- **Purpose**
- **Affected items** (exact refs, full SHAs, selectors, paths)
- **Commands** (exact, with the repository path)
- **Evidence** (the Phase 1 facts that justify it)
- **Risk**
- **Backup coverage** (which backup artifact restores it)
- **Expected result**
- **Recovery** if it fails (default: the matching `--abort` for merge, cherry-pick or rebase)
- For a deletion: the **containment check** (below), the **audited SHA** of the item, and for a branch whether it is `-d` or `-D` with the reason

### Classes and order

Run and list the actions in this class order; inside a class, in dependency order:

| Order | Class | What it contains |
| :--: | :-- | :-- |
| 1 | `prep` | A-01 the backup first; then non-destructive preparation: a `git fetch`, switching to the base branch in a clean worktree, fast-forwarding the local base branch to the base ref, a temporary worktree for debugging |
| 2 | `integrate` | Merging, squashing, cherry-picking or reverting work into the local base branch |
| 3 | `publish` | A plain, non-force push of the integrated base branch: `git push <remote> <base branch>`; also pushing a local-only tag the user wants kept |
| 4 | `local-delete` | Deleting local branches, removing or pruning worktrees, dropping stashes, deleting local tags, pruning stale remote-tracking refs (`git remote prune <remote>`) |
| 5 | `remote-delete` | Deleting branches or tags on the remote, one per action |
| 6 | `files` | Deleting named untracked non-secret noise files that are not ignored, after `git clean -n` previewed them and the backup copied them. Ignored noise is harmless and stays. Tracked noise is only reported; removing it needs a commit, so the user must ask for it, and then it is an `integrate` plus a `publish` |

Two rules make that order safe:

- **Integrations are published before anything is deleted.** Every `integrate` action is followed by a `publish` action. The aim of only `main` and `origin/main` cannot be reached without it, and a branch whose only home is an unpushed local merge is not safe to delete. An `integrate` action's commands include its checkout: `git switch <base branch>` in a clean worktree and, if the base ref is ahead, a fast-forward first (a merge into a stale local base branch makes the push non-fast-forward, and a force push is forbidden). If the working tree is dirty or the base branch is checked out in another worktree, do not plan around it silently: ask the user (finish or move the work themselves, or approve a plan that leaves that checkout alone), and never stash, commit or discard their changes on your own.
- **Every deletion carries a containment check.** Phase 3 runs it first:
  - Branch: `git merge-base --is-ancestor <audited tip SHA> <remote>/<base branch>`, or one of the other accepted reasons below.
  - Stash: its content is patch-equivalent to the base (`git diff --stat <base ref> <selector>` is empty) or it is saved in the backup. Several stash drops go in descending index order.
  - Worktree: its status is clean and its branch is contained.
  - Remote branch: the containment check of the branch, plus its live SHA still equals the audited SHA.
  - Tag: the commit it points to (`git rev-parse <tag>^{commit}`) is an ancestor of `<remote>/<base branch>`, or the tag is in the backup bundle and the plan says `backup-only`. A remote tag also needs its live SHA (`git ls-remote --tags <remote> <tag>`) to equal the audited one.

Accepted reasons to delete a branch, as one list: (1) its tip is an ancestor of the published base; (2) `no-net-change-vs-base` or patch-equivalence, with the evidence; (3) it is saved in the backup bundle, only with the user's explicit approval of that action and marked `backup-only` in the plan. Say which reason each deletion uses.

### The mandatory backup (always A-01)

One action that includes every step below, created outside the repository in the folder the user chose, before anything is integrated, pushed, deleted or pruned. Its steps, in this order:

1. Temporary refs: for every stash (`refs/git-cleanup-backup/stash-<n>`) and every reflog-only commit worth keeping (`refs/git-cleanup-backup/reflog-<first 10 SHA characters>`).
2. `git bundle create <dir>/all.bundle --all`: every branch, tag, remote-tracking ref and temporary ref. In a shallow clone a bundle may fail or be incomplete: say so and mark the affected items `BLOCKED`.
3. Uncommitted work, for the main checkout (`main-checkout`) and every worktree the plan would remove or switch away from (`wt-<folder name>`): the tracked changes with `git diff HEAD --binary -- . ':(exclude,glob)**/<secret-like name>'` into `<dir>/uncommitted-<name>.patch`, and the untracked non-secret files into `<dir>/files/`. Take the untracked list from `git ls-files --others --exclude-standard`, not from the inventory's capped sample, minus the secret-like names, and copy exactly those paths.
4. `<dir>/manifest.txt`: every branch and its SHA, every worktree, every stash selector and SHA, the files saved above, and the exact restore commands.
5. Verify (Phase 3 §3 gives the commands) and append the bundle's checksum to the manifest.
6. Delete the temporary refs.

### Remote-tracking refs, stashes and tags

The aim of only `main` and `origin/main` needs three more decisions in the plan: stale remote-tracking refs (`remote_live.stale_tracking_refs`) are pruned with `git remote prune <remote>` (`local-delete`), stashes are integrated or dropped (`local-delete`, containment as above), and local-only tags are published, deleted or kept.

## 4. Approval

Save the plan as `<scratch>/plan-draft.md`. End it with its summary (counts per class, what is irreversible, what is `BLOCKED`) and ask the user, with `AskUserQuestion`, to choose one of: approve the whole plan; approve specific action IDs (ask for the IDs in a free-text follow-up, and restate the resulting list, including any "everything except" request, for confirmation); revise; or stop here with the audit only.

- A-01 is part of every approval, whole-plan or partial. Tell the user it was added. Nothing else runs until A-01 has run and verified.
- An answer counts only if the user explicitly chose, and for a partial approval named the IDs. A question that was closed without an answer, timed out, was auto-continued or was answered with something else is not approval: ask again.
- An explicit refusal or "audit only" ends the run: change nothing, deliver the findings and `plan-draft.md` as the final answer.
- A partial approval may leave a deletion without the integration and publication that make it safe; Phase 3's containment check then skips it. Warn the user when you see that.
