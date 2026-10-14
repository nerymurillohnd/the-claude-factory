# Phase 2: findings, plan and approval

## 1. Findings

Present what Phase 1 found, grouped: context and risks, branches (fully integrated / holding exclusive work / conflicting / unknown), worktrees, stashes, pull requests, files and noise, history, `BLOCKED` items. Quote the commands you ran and the relevant lines of their results. Keep it scannable: a table for branches (ref, kind, ahead, behind, signals, last commit, author, open PR, your recommendation), prose only for what needs reasoning.

## 2. Questions

Before drafting the plan, ask the user about every ambiguous finding, preservation priority, integration choice or acceptable risk, with `AskUserQuestion` (up to four questions per call; put your recommended option first and say why in its description). Typical questions: what to do with each branch holding unmerged work, whether remote branches of other authors may be touched at all, what to do with stale pull requests, where to put the backup, whether stashes whose content is already in `main` can go.

Choose the integration strategy by the work's intent:

| Intent | Strategy |
| :-- | :-- |
| Keep shared history and the branch's commits | `git merge --no-ff` (or fast-forward) |
| One tidy commit for a messy branch | `git merge --squash` then commit |
| Take only some commits | `git cherry-pick <commits>` |
| Compensate a published change | `git revert` |
| Tidy a private, unpublished branch | `git rebase`, only with a reviewed recovery path (the backup bundle) |

Rewriting published history and force-pushing are never options.

## 3. The plan

One action per operation. Give each a unique ID (`A-01`, `A-02`, …) and these fields:

- **ID and title**
- **Class**: `prep` (non-destructive preparation), `integrate`, `local-delete`, `remote` (affects the remote or other people), `files`
- **Purpose**
- **Affected items** (exact refs, selectors, paths)
- **Commands** (exact, with the repository path)
- **Evidence** (the Phase 1 facts that justify it)
- **Risk**
- **Backup coverage** (which backup artifact restores it)
- **Expected result**

Order by dependency and preservation: `prep` (backup first) → `integrate` → `local-delete` → `remote` → `files`. State what stays untouched and why. Per branch, worktree and stash decide: integrate, preserve, delete, or leave. Remote deletions are judged one by one against visibility, protections, authors and open pull requests; never assume all remote branches go. Secret-like files are left untouched.

### The mandatory backup (always A-01)

Created outside the repository, in a folder the user chose, before anything is deleted or pruned:

1. `git bundle create <dir>/all.bundle --all` for every branch, tag and remote-tracking ref.
2. Stashes and reflog-only commits are not refs a bundle can hold. For each one at risk, create a temporary ref `refs/git-hygiene-backup/<name>` first (a state change the plan lists as its own action), include it in the bundle, and delete the temporary refs after the backup is verified.
3. A text file `manifest.txt` with every branch and its SHA, every worktree, every stash selector and SHA, the untracked non-secret files that the plan would remove, and the exact restore commands.
4. Untracked files the plan would delete are copied into `<dir>/files/`. Secret-like files are never copied or deleted.

Verification the plan promises: `git bundle verify`, the ref list of the bundle equals the refs it should hold, a restore test into a throwaway repository (`git init --bare` then `git fetch <bundle> 'refs/*:refs/*'`) whose ref list matches, and a recorded checksum.

## 4. Approval

End the plan with its summary (counts per class, what is irreversible, what is `BLOCKED`) and ask the user, with `AskUserQuestion`, to approve the whole plan, approve specific action IDs, or revise. Approval of IDs is exactly those IDs. Do nothing else until you have it.
