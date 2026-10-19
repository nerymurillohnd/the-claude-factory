# git-cleanup: exhaustive audit and two-gate lifecycle (design)

Date: 2026-10-19. Owner: Nery. Status: draft v3. Decision of 2026-10-19: no scripts. The skill is `SKILL.md` plus references that hold the commands; Claude runs them from its scratch folder and installs nothing. Implemented in the working tree, awaiting Nery's review.

Plugin: `github-operations` (skill `git-cleanup`). Replaces the staged rewrite committed in `6710187` and builds on the design that preceded it (`ef5534b`).

## 1. Goal

The skill audits a repository from the day it was created to its current state, and then executes the cleanup the user approves. The audit is never superficial and never a sample. It looks for everything that is residue, dirty, orphaned, dead or deferred, and for every link or copy that ties the repository to a place outside it and is still alive: local, remote, tunnelled or anywhere else. Whatever the audit finds that needs a refactor, a cleanup, a bisect, a debugging session or any other work goes into the report, and once the user approves it, into the plan and the execution. Nothing is excluded by kind of work, only by the user's approval.

## 2. Starting point (measured on 2026-10-19)

| Version | Strong | Weak |
| :-- | :-- | :-- |
| `ef5534b` (before the rewrite) | `inventory.py` (856 lines, read-only, JSON sections, paging); `merge-tree --write-tree` in a temporary object store with exit-code reading; `git cherry`; mandatory bundle backup with restore test; containment check before every deletion; live SHA re-check for remote deletions; open PRs, protections and rulesets through `gh` | Local Git only: no issues, discussions, forks, closed or merged PRs, Actions, external links or history content audit; one approval gate (findings, questions and plan together) |
| `6710187` (the rewrite) | Clean stage split; six-bucket taxonomy; plain-language report with F and R IDs; state-drift abort | No inventory tool; no remote or GitHub data; no squash or rebase detection (`--is-ancestor` and `branch --merged` miss them, `branch -d` refuses them: tested); `merge-tree` in its deprecated mode; no second gate; rollback only for refs |

Decision: start from `ef5534b`, bring in the rewrite's strong parts, and add what neither has. The 856-line `inventory.py` is not carried over: Claude runs the commands written in the references, and a command that fails is reported as `BLOCKED`.

## 3. Lifecycle: nine steps, two approval gates

| # | Step | Output | Gate |
| :-: | :-- | :-- | :-- |
| 0 | Intake: repository, remote, `gh` identity and permission, which scans outside the repository the user allows (section 4.4) | `scratch/context.md` | none |
| 1 | Audit (read-only): run the audit commands over local Git, the full history, residue, GitHub and external links | files in the scratch folder, `audit-log.md` | none |
| 2 | Inventory and classify: every item gets a bucket and its evidence; anything unverifiable is recorded in the coverage ledger | `findings.md`, `coverage.md` | none |
| 3 | Report and recommendations: plain-language summary, findings `F-n`, recommendations `R-n` with risk and reversibility, questions with a recommended answer, the coverage ledger | the report | **Gate 1**: the user approves recommendation IDs (a generic "clean it up" approves nothing) |
| 4 | Implementation plan for the approved IDs only: actions `A-n` in class order, exact commands, containment check, backup coverage, rollback and the validation criterion of each action | `plan.md` | **Gate 2**: the user approves action IDs |
| 5 | Backup (`A-01`, always) and revalidation: re-run the relevant audit sections and compare them with the plan's evidence | backup folder, `plan.md` with statuses | state drift stops the run |
| 6 | Execute, one action at a time, each preceded by its pre-flight check | `plan.md` statuses | none |
| 7 | Validate: fresh read-only proof against the criteria written in step 4 | raw command output | none |
| 8 | Results report: done, kept and why, not verifiable, backup location | the final report | the user decides whether to keep the backup |

Gate rules: an answer counts only if the user chose explicitly and named the IDs; silence, a timeout or an auto-close is not approval; a partial approval that leaves a deletion without the integration that makes it safe is warned about and the deletion is skipped by its containment check; an explicit refusal or "audit only" ends the run with the report delivered.

## 4. Audit domains

Every domain is collected completely. Display is paged, collection is not capped. A cap exists only for how many items Claude reads at once, and the true count is always reported.

### 4.1 Git, from the first commit

| Area | What is collected |
| :-- | :-- |
| Repository | root, git dir, common dir, bare, shallow, partial, HEAD state, operations in progress, Git version, remotes (credentials redacted), config keys that affect safety |
| Refs | heads, remote-tracking, tags, notes, replace refs, stash, any other namespace; ahead and behind against the base; merged, patch-equivalent, content already in the base (merge-tree tree equals base tree), conflicts, stale, upstream gone, author, last activity |
| Worktrees, stashes, working tree | registration, locked, prunable, dirty entries; each stash with its untracked third parent; staged, unstaged, untracked, conflicted, ignored (collapsed to directories), noise, nested repositories, submodules, subtrees, LFS |
| History | commit count, root commits (more than one root means unrelated or orphan histories), merge count and styles, WIP-style subjects, empty commits, author identities that need a mailmap, unsigned commits when the repository signs, future-dated commits |
| Object store | `count-objects`, alternates, connectivity, largest blobs across all history, large files no longer in HEAD, tracked generated noise |
| Secrets in history | names of secret-like files that were ever committed and whether each still exists; never contents |

### 4.2 Residue: anything started and never finished

| Kind | Examples |
| :-- | :-- |
| Unfinished work | open and draft pull requests with their age and state; branches with exclusive commits; stashes; half-done operations (merge, rebase, cherry-pick, bisect) |
| Failed and forgotten automation | workflows whose latest run on the default branch failed and was never followed by a success; scheduled workflows that stopped running; runs stuck in queued or in progress; disabled workflows; workflows that reference deleted branches, files or secrets names; Dependabot updates that failed |
| Deferred work | TODO, FIXME and HACK markers with `git blame` age; skipped or expected-failure tests; issues and discussions open for a long time or waiting for an answer; pinned old versions the project itself flags |
| Dead weight | generated files tracked in Git; files that exist only in history and are large; branches and tags nobody references; caches and artifacts of old runs |
| Dead code | only through the project's own tools when they exist (for example `knip`, `vulture`, `ruff`'s unused rules), quoted as their evidence; the skill does not invent language analysis |

### 4.3 External links: everything outside the repository that still points to it

| Where | What is collected |
| :-- | :-- |
| GitHub, this repository | webhooks; deploy keys (name, access, last use); Actions artifacts and caches (size, age); environments and their protection; secrets and variables (names only, never values); self-hosted runners; Pages; Codespaces; installed GitHub Apps; collaborators, outside collaborators and teams with access; linked packages, releases and assets; Projects linked; wiki; renames and transfers (old URLs still used in remotes); forks and the whole fork network; open secret-scanning, Dependabot and code-scanning alerts |
| GitHub, other repositories | code search for references to this repository: `uses: owner/repo@`, git URLs, submodule URLs, marketplace manifests, dependency specs (subject to the search API's limits; verify when building) |
| Other hosts and services | mirrors and remotes on other hosts found in Git config; CI, hosting and deploy configuration committed in the tree (`.circleci`, `Jenkinsfile`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `netlify.toml`, `vercel.json`, `render.yaml`, `fly.toml` and similar), recorded as "references found, live state unverified" because the skill has no credentials for them |
| Package and plugin registries | public registries queried read-only for packages whose repository field points here; Claude plugin marketplaces that list this repository |
| This machine, outside the repository | other clones of the same remote; linked worktree registrations pointing to or from other paths; `objects/info/alternates` in other repositories that point here; submodules of other local repositories whose URL is this one; symlinks into the repository; IDE workspace files; launchd, cron and systemd jobs that reference the path or the remote |
| Tunnels and listeners | processes and listening ports serving from the repository or forwarding to it: cloudflared, ngrok, `ssh -L` and `-R`, tailscale serve and funnel, localtunnel, editor port forwards |

### 4.4 Reachability and consent

| Class | Meaning | Handling |
| :-- | :-- | :-- |
| Reachable | read-only `git`, `gh` or a public registry query | collected |
| Needs consent | scans outside the repository: other clones, launchd or cron, processes and ports, workspace files | asked once at step 0 with the exact roots and commands; refused scope is recorded, not skipped silently |
| Not reachable | other people's machines, third-party services without credentials, deleted forks, anything behind a credential the skill must not read | recorded in the coverage ledger with the reason and what the user can check themselves |

The skill never reads credential stores, key files or secret values, and never prints a token. Scans outside the repository are read-only.

The audit cannot prove that nothing exists beyond what the tools can see. What it guarantees is the **coverage ledger**: for every domain above, `checked`, `BLOCKED` (with the failed call) or `not reachable` (with the reason). The report always carries it, so the user can see exactly what "everything" meant in that run.

### 4.5 Git-native residue and risk surfaces

| Surface | Why it matters |
| :-- | :-- |
| Hooks (`.git/hooks`, `core.hooksPath`) | non-sample hooks run code on every Git operation; one that calls a service or a path outside the repository is a live link |
| Config in every scope (system, global, local, worktree, `includeIf`) | `url.<base>.insteadOf` silently redirects remotes; `core.hooksPath`, `core.worktree`, `core.fsmonitor`, registered maintenance, `gc` and `receive` settings; credential helper names only, never values |
| Leftovers of interrupted or old operations | `refs/original/*` (filter-branch backups), `refs/bisect/*`, `ORIG_HEAD`, `rebase-merge`, `rebase-apply` (also from `git am`), `MERGE_HEAD`, `CHERRY_PICK_HEAD`, stale `*.lock`, `gc.log`, `gc.pid`, old `FETCH_HEAD`, `git-svn` refs and `.git/svn`, `refs/replace/*`, `refs/notes/*` |
| Dangling and unreachable objects, pack layout, loose objects, need for `gc` | read-only through `fsck --no-reflogs --unreachable`, `count-objects`, `verify-pack`; never `fsck --lost-found`, which writes into the repository |
| Ignore and attribute hygiene | tracked files that match ignore rules (`ls-files -ci --exclude-standard`); `.gitattributes` filters (LFS) with no matching tool; stray `*.patch` and `*.mbox` files |
| Serving the repository | `git daemon` and `git instaweb` processes, `git-daemon-export-ok`, `info/refs` left by `update-server-info`, `fsmonitor` daemons, `git maintenance` schedules |

### 4.6 Command universe

The git-scm.com command reference (pasted by Nery on 2026-10-19) is the universe the design is checked against. Every command has exactly one role:

| Role | Commands |
| :-- | :-- |
| Read in the audit | `status`, `diff`, `log`, `show`, `shortlog`, `blame`, `grep`, `range-diff`, `rev-list`, `rev-parse`, `for-each-ref`, `show-ref`, `symbolic-ref`, `cat-file`, `ls-files`, `ls-tree`, `check-ignore`, `merge-base`, `count-objects`, `fsck` (read-only flags), `verify-pack`, `reflog`, `worktree list`, `stash list` and `show`, `remote` (URLs redacted), `config --list --show-origin` (redacted), `submodule status`, `notes list`, `cherry`, `merge-tree --write-tree`, `ls-remote`, `bundle verify` |
| Change something, only as an approved action of a class | `branch -d`, `tag -d`, `worktree remove` and `prune`, `stash drop`, `remote prune`, `push` (`publish`, `remote-delete`), `merge`, `cherry-pick`, `revert`, `rebase`, `commit`, `restore`, `switch` (`integrate`, `fix`), `clean` (`files`), `gc`, `repack`, `reflog expire`, `prune` (`maintenance`), `filter-repo` (`history-rewrite`; `filter-branch` is not used), `bundle create` and `clone` (backup and its restore test), `bisect` (`investigate`) |
| Never | `reset --hard`, `checkout --`, `clean -x`, any force-push other than `--force-with-lease` in `history-rewrite`, `fsck --lost-found`, reading credential helpers or credential stores |
| Detected only, never operated | interactive tools (`mergetool`, `difftool`, `add -p`, `gui`, `instaweb`); mail workflow (`am`, `send-email`, `imap-send`, `request-pull`, `format-patch`) and its leftovers; `svn` and `fast-import` and their refs; `daemon` and `update-server-info` and what they leave behind |

Where the plan stops one of these from being the right tool (for example `filter-branch` against `filter-repo`), the current Git documentation decides, checked when the reference is written.

## 5. Scale rules

- Commands write their output to files in the scratch folder, and Claude reads them in pieces (`wc -l`, `head`, `sort | uniq -c`, `awk`, `jq`, `gh --jq`). The true count is always reported.
- No sampling for correctness and no time budget that silently drops work: when a limit is hit (for example GitHub's 1,000-result cap on filtered run lists) the audit splits the query, or the item goes to the ledger with what is missing.
- Full 40-character SHAs for anything the plan will act on.
- Network calls are paginated and rate-limit aware; a failed call is recorded and the facts that depend on it are never read as empty.

## 6. Actions, classes and invariants

Classes, in execution order:

| Class | What it contains |
| :-- | :-- |
| `prep` | `A-01` backup first; fetches; switching to a clean base |
| `investigate` | `bisect`, `blame`, reproduction and diagnosis in an isolated worktree outside the repository, restoring the starting state; produces a finding, changes no source |
| `fix` | refactors and corrections the findings call for, in a new branch in a separate worktree, with the repository's own gates, landing through a pull request (`auto-pr-lifecycle`); never committed straight to the base |
| `integrate` | merge, squash, cherry-pick or revert into the local base |
| `publish` | a plain, non-force push of the integrated base |
| `local-delete` | local branches, worktrees, stashes, tags, stale tracking refs |
| `remote-delete` | remote branches and tags, one per action |
| `github-close` | closing a pull request, issue or discussion, one per action, with an explanatory comment |
| `external-unlink` | disabling a workflow, deleting old artifacts and caches, removing a webhook, stopping a tunnel or launchd job: one per action, each with its own approval, reversibility stated |
| `files` | named noise files, previewed and backed up first |
| `maintenance` | `gc`, `repack`, `reflog expire`, `prune` to reclaim space, only after the backup is verified and everything else is done; unreachable objects are gone afterwards, so it is irreversible and individually approved |
| `history-rewrite` | secrets or giant blobs in published history; see below |

Invariants:

- Every integration is published before anything it makes redundant is deleted.
- Every deletion carries a containment check that runs first: ancestor of the published base, or content already in the base, or saved in the backup bundle with the user's explicit approval of that action. A remote deletion also re-reads the live SHA and acts only if it equals the audited one.
- `git branch -d` only, from the base branch. If it refuses, report it; `-D` needs its own approved action with the reason.
- Backup (`A-01`): a bundle of all refs outside the repository with a restore test and checksum, plus patches and copies of uncommitted work and of the ignored files the plan names. Rollback refs live in `refs/git-cleanup-backup/` and are removed at the end.
- Security-sensitive external items (deploy keys, tokens, secrets, installed apps, collaborator access) are report-only: the skill names the item, the risk and how the user changes it, and does not change it.
- Nothing on GitHub is deleted by the skill other than remote branches, and other people's content is never touched.
- `history-rewrite` is not part of any bulk approval. The audit reports it; it becomes a plan only when the user asks for it by name, with a full mirror clone as backup, `--force-with-lease` and its own approval.
- Merges and reverts the cleanup creates follow the repository's signing configuration; never `--no-gpg-sign`.
- A conflict stops that action and its dependents; changes are never discarded to force an operation through.

### 6.1 Rules for stashes, clean, blame and bisect

Source: the Pro Git chapters "Debugging with Git" and "Stashing and Cleaning" that Nery attached on 2026-10-19, checked against the official `git-bisect` and `git-clean` pages and against tests on Git 2.43 (2026-10-19). Where the book and the manual differ, the manual decides.

Stashes

- A stash holds tracked changes only. Untracked files live in its third parent (`stash -u`), ignored files only with `--all`. The audit reads all three.
- A stash with work that is not in the base is preserved, not dropped: `git branch rescue/stash-<n> 'stash@{<n>}'`. Tested: it does not touch the working tree or HEAD, keeps the untracked files reachable through `^3`, and survives `git stash drop`. A stash is dropped only after its content is in the base or in a rescue branch.
- `git stash branch` is not used: it checks out a new branch in the current worktree. `git stash --all` is not used as a backup either: it changes the user's working tree. Backups are copies outside the repository.
- `stash save` is deprecated in favour of `stash push`; the skill only reads stashes and never creates one on the user's behalf.

Clean

- Always previewed first with `git clean -n -d -X` (ignored files only). `-x` is never used: it also removes untracked files that are not ignored (tested: the preview lists both).
- Never a second `-f`. One `-f` skips untracked nested repositories (tested); the second `-f` removes them (manual). Nested repositories are reported by the audit (`audit.md` 1.7 and `audit-links.md`), never cleaned.
- `clean.requireForce` is read as configuration; the skill does not change it.
- Interactive `-i` is out; the plan lists the exact paths instead.

Blame

- `git blame -w -M -C` follows moved and copied lines across files, which is what finds the true origin of a refactored block, and is slow on large repositories. `audit-history.md` uses plain `blame` for age; `investigate` uses `-w -M -C` for origin. Lines prefixed `^` are the root commit's.

Bisect

- Bisect state is per worktree (tested: refs `refs/bisect/*` and the `BISECT_*` files appeared in the linked worktree and not in the main checkout). Every bisect runs in a throwaway worktree outside the repository; the main checkout is never bisected.
- `bisect run <cmd>`: exit 0 is good, 1 to 127 except 125 is bad, 125 skips the revision, any other code aborts (manual). Skipping a commit next to the culprit leaves a range, not a commit, and the report says so.
- The test script lives outside the repository (manual) and is audited before it runs, because it executes code from every checked-out revision.
- `--first-parent` is used when the history is merge-based and a branch had broken intermediate commits.
- The run ends with `git bisect reset`; step 7 proves that no `refs/bisect/*` or `BISECT_*` remains and the worktree is gone.

### 6.2 Maintenance, recovery and history rewrite

Source: the Pro Git chapter "Maintenance and Data Recovery" that Nery attached on 2026-10-19, checked against the official `git-gc` and `git-filter-branch` pages, the `git-filter-repo` README and tests on Git 2.43. Where the book and the manual differ, the manual decides. The book is out of date on three points: `gc.auto` defaults to 6700 (the book says about 7000), `gc.pruneExpire` defaults to 2 weeks (the book says a few months), and `filter-branch` is no longer recommended.

Finding what is heavy or lost, read-only

- Largest blobs: `git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)'`. Tested on a repository that never ran `gc`: it names the file and size of a blob that is no longer in HEAD. The book's `verify-pack` route needs a packed repository, so the book's way would require running `gc` first, which is a change; the audit uses `cat-file`. `--batch-all-objects` also counts unreachable objects.
- Lost-work candidates: `git fsck --no-reflogs --unreachable`, filtered to commits (tested: it lists a commit that no ref or reflog reaches). Each candidate is reported with author, date and subject, never with content. Preserving one is a `prep` action: `git branch rescue/lost-<short sha> <sha>`.
- Need for `gc`: loose-object and pack counts against the repository's own `gc.auto` (default 6700) and `gc.autoPackLimit` (default 50). The `packed-refs` file is never read or edited directly; `for-each-ref` covers loose and packed refs.
- Recovery promises: `gc` prunes unreachable objects older than `gc.pruneExpire` (default 2 weeks), and reflog entries expire after 90 days (30 days if unreachable). The report never promises recovery from a reflog or from an unreachable object.

`maintenance` class

- `git gc` with the repository's own expiry settings is the default. `git gc --prune=now` and `git reflog expire --expire=now --all` are separate actions the user must approve by name: the manual warns that `--prune=now` can corrupt the repository if another process writes to it at the same time, so nothing else may touch the repository while it runs.
- The manual's safer alternative for a post-rewrite cleanup is a clone through `file://`, which carries no removed objects (a plain path hardlinks everything).
- Maintenance comes last, after step 7 has validated the rest, because pruning cannot be undone: once it runs, only the bundle of `A-01` can bring back what an earlier action deleted.

`history-rewrite` class

- The tool is `git filter-repo`, not `filter-branch` (the `git-filter-branch` manual says its use is not recommended). `filter-repo` is a Python script placed on `PATH`, listed as a prerequisite in the plugin README (its README states git 2.36.0 or later and Python 3.6 or later; whether it ships with Git is not stated there, so the README tells users how to install it).
- It refuses to run outside a fresh clone unless `--force` is given, so the rewrite is planned in a fresh mirror clone, not in the working repository. Unverified until the reference is written: what it does with the `origin` remote after rewriting; the plan re-adds and checks remotes explicitly.
- `refs/original/*` is not a backup (the `filter-branch` manual: it dereferences tags). The real backup is the bundle of `A-01`.
- A rewrite removes the objects from this repository's history only. Forks, other clones, GitHub's `refs/pull/*` and cached views can still hold them; the audit lists them (`audit-github.md`, `audit-links.md`), and the plan says so. A credential that was ever committed is treated as exposed whatever the rewrite does: the report tells the user to rotate it, and the skill never handles the credential. Verify the GitHub side against GitHub's own documentation when the reference is written.

## 7. Validation (step 7)

Criteria are written in step 4 so they cannot be bent afterwards, for example: the ref is gone, the remote head list equals the planned one, every exclusive tip recorded in step 1 is an ancestor of the base or in the bundle, no `refs/git-cleanup-backup/*` remains, the workflow is disabled, the tunnel process is gone. Step 7 runs fresh read-only commands and quotes their raw output; the final report separates verified from reported.

## 8. Files

```text
skills/git-cleanup/
  SKILL.md                 router: lifecycle table, invariants, folders, read-when triggers
  references/
    audit.md               steps 0 to 2: ground rules, intake, local Git commands, classification, ledger
    audit-history.md       whole history, object store, large blobs, secret names, deferred markers
    audit-github.md        pull requests, issues, discussions, forks, Actions, protection, integrations, alerts
    audit-links.md         everything outside the repository that still points at it
    report.md              step 3: questions, template, IDs, Gate 1
    plan.md                step 4: action fields, classes, containment, backup, history rewrite, Gate 2
    execute.md             steps 5 and 6: backup and restore test, revalidation, commands by class, failures
    validate.md            steps 7 and 8: fresh proof, results report, backup retention
    integrate.md           merge, squash, cherry-pick, revert; merge preview; signing; publishing
    investigate.md         grep, blame, bisect in a throwaway worktree, fixes through a pull request
```

There are no scripts, no hooks and no dependencies other than `git`, and `gh` for GitHub. The references are named for what they hold. `SKILL.md` links each one with a read-when trigger. If the references grow past what a router can hold, the audit domains become a second skill that this one calls; decide when the size is known.

## 9. Defaults taken until Nery decides otherwise

1. History rewriting: separate class, never in a bulk approval, only when requested by name.
2. Security-sensitive external items: report only.
3. Fix work lands through a branch and a pull request, never on the base.
4. Hooks: not designed yet. Decide after the plan and execution references exist, from the exact commands they use.

## 10. Build, test and release

- No scripts. Every command was run on throwaway fixture repositories (squash-merged, rebased, conflicting, unrelated and ahead branches, a linked worktree, a stash with untracked files, bundle and restore test) before it was written into a reference. GitHub commands were checked against `gh --help` and the current GitHub documentation; they were not run against the live API in this session.
- Versions are not hardcoded and nothing probes for features: the plugin runs whatever `git` and `gh` are on the user's `PATH`, and a failing command is reported.
- Tests: plugins are tested with `claude plugin eval` (the `plugin-evals` plugin), only once `SKILL.md` exists and only with Nery's approval of any paid run.
- Docs: plugin README, plugin CHANGELOG, root CHANGELOG line and a minor version bump to `0.4.0`. An ADR records the guard decision when it is made.
- Push and PR: only with Nery's approval (GitHub Gate).

## 11. Open decisions for Nery

- The defaults in section 9.
- Whether the audit domains stay inside one skill or become a second skill (decided once the size is known).
