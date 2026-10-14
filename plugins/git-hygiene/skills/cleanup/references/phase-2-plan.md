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

Order by dependency and preservation: `prep` (backup first) → `integrate` → `remote` (publish the integrations) → `local-delete` → `remote` (deletions) → `files`. State what stays untouched and why.

Two rules make that order safe:

- **Integrations are published before anything is deleted.** Every `integrate` action is followed by its own `remote` action: a plain, non-force `git push origin <base>`. The aim of only `main` and `origin/main` cannot be reached without it, and a branch whose only home is an unpushed local merge is not safe to delete.
- **Every deletion carries a containment check.** The plan states, for each branch to delete, the check Phase 3 runs first: `git merge-base --is-ancestor <branch tip SHA> origin/main` (the work is in the published base), or the recorded reason it is preserved elsewhere (patch-equivalent or no net change, with the evidence) and the user's approval of that reason. Remote deletions also record the remote branch's audited SHA, which Phase 3 re-checks just before deleting. Per branch, worktree and stash decide: integrate, preserve, delete, or leave. Remote deletions are judged one by one against visibility, protections, authors and open pull requests; never assume all remote branches go. Secret-like files are left untouched.

### The mandatory backup (always A-01)

One action that includes every step below, created outside the repository in a folder the user chose, before anything is deleted, pruned or integrated:

1. Stashes and reflog-only commits are not refs a bundle can hold. For each one at risk, create a temporary ref `refs/git-hygiene-backup/<name>` first. These temporary refs are part of A-01, and A-01 ends by deleting them once the backup is verified.
2. `git bundle create <dir>/all.bundle --all` for every branch, tag, remote-tracking ref and temporary ref. In a shallow clone a bundle may fail or be incomplete: say so and mark the affected items `BLOCKED`.
3. Uncommitted work: for the main checkout and every worktree the plan would remove or switch away from, save the tracked changes (`git diff HEAD --binary > <dir>/uncommitted-<name>.patch`) and copy the untracked non-secret files into `<dir>/files/`. Secret-like files are never copied or deleted.
4. A text file `manifest.txt` with every branch and its SHA, every worktree, every stash selector and SHA, the files saved above, and the exact restore commands.

Verification the plan promises: `git bundle verify`, the ref list of the bundle equals the refs it should hold, a restore test into a throwaway repository (`git init --bare` then `git fetch <bundle> 'refs/*:refs/*'`) whose ref list matches, and a recorded checksum.

## 4. Approval

End the plan with its summary (counts per class, what is irreversible, what is `BLOCKED`) and ask the user, with `AskUserQuestion`, to approve the whole plan, approve specific action IDs, or revise. Approval of IDs is exactly those IDs.

A-01 is part of every approval, whole-plan or partial: if the user does not approve A-01, no `integrate`, `local-delete`, `remote` or `files` action may run. An answer counts only if the user explicitly chose to approve and, for a partial approval, named the IDs. A question that was closed without an answer, timed out, was auto-continued or was answered with something else is not approval: ask again. Do nothing else until you have it.
