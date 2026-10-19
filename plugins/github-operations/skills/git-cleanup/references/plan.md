# Implementation plan, step 4 (Gate 2)

Gate 1 approved a list of recommendation IDs. Plan only those, as numbered actions with exact commands. Save the draft as `plan-draft.md` in the scratch folder.

## Action fields

One action per operation: `A-01`, `A-02`, ... Each has:

- **ID and title**, and the recommendation IDs it implements.
- **Class** (below).
- **Purpose.**
- **Affected items**: exact refs, full 40-character SHAs, stash selectors, paths, URLs.
- **Commands**: exact, with the repository path (`git -C "<repo>" ...`, `gh -R <o>/<r> ...`).
- **Evidence**: the audit facts that justify it (file and line in the scratch folder).
- **Risk** and **reversibility**.
- **Backup coverage**: which part of the backup restores it, or "none: irreversible".
- **Expected result.**
- **Recovery** if it fails: by default the matching `--abort` (`merge`, `cherry-pick`, `rebase`, `revert`).
- **Containment check** for every deletion, and the **audited SHA** of the item (below).
- **Validation criterion**: the read-only command and the exact result that prove it worked. Write it now, in step 4, so it cannot be bent after the fact. Examples: "`git rev-parse --verify -q refs/heads/x` prints nothing", "`git ls-remote --heads origin x` prints nothing", "`git merge-base --is-ancestor <tip> origin/main` exits 0", "`git for-each-ref refs/git-cleanup-backup` prints nothing", "`gh workflow list --all` shows `disabled_manually`", "no process matches `cloudflared`".

## Classes, in execution order

| # | Class | Contains |
| :-: | :-- | :-- |
| 1 | `prep` | `A-01` the backup, always first; fetches; switching to a clean base; rescue branches for lost or stashed work |
| 2 | `investigate` | bisect, blame, reproduction and diagnosis in an isolated worktree outside the repository, restoring the starting state; produces a finding and changes no source (see `investigate.md`) |
| 3 | `fix` | refactors and corrections the findings call for, in a new branch in a separate worktree, with the repository's own gates, landing through a pull request; never committed straight to the base |
| 4 | `integrate` | merge, squash, cherry-pick or revert into the local base (see `integrate.md`) |
| 5 | `publish` | a plain, non-force push of the integrated base |
| 6 | `local-delete` | local branches, worktrees, stashes, tags, stale remote-tracking refs |
| 7 | `remote-delete` | remote branches and tags, one per action |
| 8 | `github-close` | closing a pull request, issue or discussion, one per action, with an explanatory comment |
| 9 | `external-unlink` | disabling a workflow, deleting old artifacts and caches, removing a webhook, stopping a tunnel or scheduled job: one per action, each with its own approval and its reversibility stated |
| 10 | `files` | named, non-secret noise files that are not ignored, previewed with `git clean -n` and backed up first |
| 11 | `maintenance` | `gc`, `repack`, `reflog expire`, `prune`: last, individually approved, irreversible |
| 12 | `history-rewrite` | secrets or giant blobs in published history; only when the user asked for it by name (below) |

Two rules make the order safe:

- **Every integration is published before anything it makes redundant is deleted.** Each `integrate` is followed by its `publish`: a branch whose only home is an unpushed local merge is not safe to delete. An `integrate` action's commands include its checkout: `git switch <base branch>` in a clean worktree and, if the remote base is ahead, a fast-forward first (merging into a stale local base makes the push non-fast-forward, and force-pushing is not allowed). If the working tree is dirty or the base is checked out in another worktree, ask the user; never stash, commit or discard their changes on your own.
- **Every deletion carries a containment check that runs first.** An item is deleted only if one of these holds, and the action says which:
  1. its tip is an ancestor of the published base: `git merge-base --is-ancestor <audited sha> <remote>/<base>`;
  2. its content is already in the base (`in-base` in the branch-state table, or `git cherry` shows every commit as `-`), with the evidence;
  3. it is saved in the backup bundle, only with the user's explicit approval of that action, marked `backup-only`.

  By kind: a **branch**, as above, deleted with `git branch -d` from the base branch (it compares against HEAD or the upstream); if `-d` refuses, report it, and `-D` needs its own approved action with the reason. A **stash**: its content is in the base (`git diff --stat <base> 'stash@{N}'` empty and its `^3` untracked files empty or saved) or it is in a rescue branch (`git branch rescue/stash-N 'stash@{N}'`, which keeps the untracked files reachable through `^3` and survives the drop); several drops go in descending index order. A **worktree**: clean status and a contained branch; the branch is deleted only after the worktree is removed. A **remote branch or tag**: the branch's check plus its live SHA still equals the audited SHA (`git ls-remote --heads origin <branch>`). A **tag**: the commit it points to (`git rev-parse <tag>^{commit}`) is contained, or it is in the bundle and the action says `backup-only`.

## The backup (always A-01)

One action, made outside the repository in the folder the user chose, before anything is integrated, pushed, deleted or pruned. Its steps, in order:

1. **Rescue refs** under `refs/git-cleanup-backup/`: one per stash (`stash-N`) and per reflog-only or unreachable commit worth keeping (`lost-<first 10 SHA characters>`), so the bundle contains them: `git update-ref refs/git-cleanup-backup/stash-N 'stash@{N}'`.
2. **The bundle:** `git -C "<repo>" bundle create "<dir>/all.bundle" --all`. In a shallow clone it can fail or be incomplete: say so and mark the affected items `BLOCKED`.
3. **Uncommitted work**, for the main checkout (`main-checkout`) and every worktree the plan would remove or switch away from (`wt-<folder name>`): the tracked changes with `git -C "<path>" diff HEAD --binary -- . ':(exclude,glob)**/.env' ':(exclude,glob)**/*.pem' ':(exclude,glob)**/*.key'` (one exclusion per secret-like name found) into `<dir>/uncommitted-<name>.patch`, and the untracked non-secret files into `<dir>/untracked-<name>.tar`:

   ```sh
   git -C "<path>" ls-files --others --exclude-standard -z | grep -zvE "$secret" | tar -cf "<dir>/untracked-<name>.tar" --null -C "<path>" -T -
   ```

   where `$secret` is `(^|/)(\.env(\..+)?|.+\.(pem|key|p12|pfx|keystore|kdbx|tfstate)|id_(rsa|dsa|ecdsa|ed25519)|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd|credentials(\..+)?|secrets?(\..+)?|terraform\.tfvars)$`. Secret-like files are never copied; the manifest lists their names.
4. **`<dir>/manifest.txt`**: every branch and its SHA, every worktree, every stash selector and SHA, the files saved above, the exact restore commands, and the bundle's checksum (`shasum -a 256`, or `sha256sum` where that is what exists).
5. **Verify** (`execute.md` gives the commands), then **delete the rescue refs** (`git update-ref -d`).

Rollback refs live only in `refs/git-cleanup-backup/` and are removed at the end. The backup folder is the user's recovery copy; the skill never deletes it on its own.

## Specific classes

**`maintenance`**: only after the backup is verified and step 7 has validated everything else, because pruning cannot be undone: once it runs, only the bundle of `A-01` can bring back what an earlier action deleted. `git gc` with the repository's own expiry settings is the default (`gc.pruneExpire` defaults to 2 weeks, reflog entries expire after 90 days, 30 if unreachable). `git gc --prune=now` and `git reflog expire --expire=now --all` are separate actions the user must approve by name: the `git-gc` manual warns that `--prune=now` can corrupt the repository if another process writes to it at the same time, so nothing else may touch the repository while it runs.

**`history-rewrite`**: never part of a bulk approval. Plan it only when the user asks for it by name, and say first that revoking and rotating the exposed credential may be enough on its own (GitHub's guidance), so the rewrite may be unnecessary. If it goes ahead:

- The tool is `git filter-repo` (not `filter-branch`, whose manual says its use is not recommended). It is a Python script that must be on `PATH`; its README states git 2.36.0 or later and Python 3.6 or later. If it is missing, the plan stops and tells the user how to install it; the skill installs nothing.
- It refuses to run outside a fresh clone unless `--force` is given, so the rewrite happens in a fresh mirror clone made from the backup, not in the working repository. After the rewrite, check `git remote -v` in the clone and re-add the remote explicitly if it is missing (what filter-repo does with `origin` is unverified).
- For a removed file: `git filter-repo --sensitive-data-removal --invert-paths --path <path>` (GitHub's documentation requires filter-repo 2.47 or later for that flag; check `git filter-repo --version`). Before pushing, list the `refs/pull/*` refs that will change.
- The push is `--force-with-lease` per ref, or `git push --force --mirror` as GitHub documents it; `refs/pull/*` refuses pushes because GitHub treats them as read-only, and a branch protection that blocks the other refs may have to be lifted temporarily: that is a separate approved `external-unlink` action.
- State the consequences before approval: commit hashes change from the first changed commit on, signatures are removed, open pull requests are disrupted, forks and other clones keep the old objects (collaborators must re-clone and must not merge old branches), and GitHub keeps cached views and pull request refs until GitHub Support removes them (it needs the repository name, the affected pull requests and the "First Changed Commit(s)"). The audit lists forks, other clones and pull requests so the plan can name them.
- `refs/original/*` is not a backup. The real backup is the bundle of `A-01`.

**`external-unlink`**: one action per item, each approved on its own. Security-sensitive items (deploy keys, tokens, secrets, installed apps, collaborator access) are never actions: they stay report-only. Nothing on GitHub is deleted by the skill other than remote branches, and other people's content is never touched.

## Approval, Gate 2

End the plan with a summary: counts per class, what is irreversible, what is `BLOCKED`. Ask the user, with `AskUserQuestion`, to choose one: approve the whole plan; approve specific action IDs (ask for the IDs, then restate the resulting list, including any "everything except" request, for confirmation); revise; or stop with the audit and plan only.

- **A-01 is part of every approval**, whole or partial. Tell the user it was added. Nothing else runs until it has run and verified.
- An answer counts only if the user explicitly chose and, for a partial approval, named the IDs. A closed, timed-out, auto-continued or ambiguous answer is not approval: ask again.
- An explicit refusal or "audit only" ends the run: change nothing and deliver the report and `plan-draft.md`.
- A partial approval may leave a deletion without the integration and publication that make it safe; its containment check will then skip it at execution. Warn the user when you see it.
