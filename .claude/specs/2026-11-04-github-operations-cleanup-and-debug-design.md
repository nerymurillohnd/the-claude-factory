# github-operations: cleanup-and-debug skill — design

- **Date:** 2026-11-04
- **Status:** draft, for Nery's review
- **Plugin:** `plugins/github-operations` (Phase 2 of the three-skill refactor)
- **Component:** skill `github-operations:cleanup-and-debug`

## Purpose

Audit one repository exhaustively as a Git and GitHub object, local and remote, and compare the two. The goal is to find everything left behind: residue, work started and never finished, and anything loose, broken or forgotten. The audit becomes an approved plan, which the main session then executes and validates.

## Scope

- **In:** the repository as a Git and GitHub object. That covers refs, branches, tags, worktrees, stashes, the working tree, history and the object store, Git configuration and residue, pull requests, issues, discussions, Actions, Dependabot, security alerts, integrations, access, distribution, forks, and external links. It also covers how each local item compares with its remote counterpart.
- **Out:** code quality, and the repository's documentation.

## Design decisions

- **One skill holds the whole procedure.** It uses headers, bullets and sections, with what each phase must do.
- **No fixed agent team.** The task is too large for a single agent. A dedicated agent per domain would be tedious to build and maintain. Claude measures the repository's size and delegates to subagents on its own when the work calls for it.
- **The main session owns the gates, the plan, execution and validation.**

## Operating principles

- **Exhaustive collection.** Every domain is collected completely. Display is paged, but collection is never capped or sampled. When a limit is hit, the query is split, or the gap goes to the coverage ledger along with the true count.
- **Read-only until approved.** Phases 0 to 8 change nothing in the repository, on GitHub or on the machine.
- **No side effects while inventorying.** Inventory commands run without optional locks, so `status` does not write the index. In partial clones they run with lazy fetch off.
- **Credentials are never read.** Secrets are identified by name only. Credential-bearing values are masked inside the command, before the output reaches the model.
- **A failed call is recorded.** No fact that depends on a failed call is ever reported as empty.
- **Full object IDs.** Anything the plan acts on is named by its full object ID, whose length follows the repository's object format.
- **Output goes to files** and is read in pieces, so large repositories never exhaust what can be read at once.
- **Network calls** are paginated and aware of rate limits.

## Workflow

### Phase 0: Intake and preflight

- Repository: path, git dir, common dir, remotes (credentials redacted), default branch and base branch.
- Clone type: bare, shallow, partial (promisor remotes), sparse checkout.
- Repository format:
  - ref storage (`files` or `reftable`);
  - object format (SHA-1 or SHA-256), which sets the object ID length.
- Tooling: git and gh versions against the declared minimums. A domain whose command the installed version lacks is marked BLOCKED.
- GitHub identity, and its permission on the repository (admin, write or read). Every call the identity cannot make goes to the coverage ledger.
- Reachability of each domain:
  - reachable;
  - needs consent (scans outside the repository);
  - not reachable.
- The user approves the scans outside the repository once, with their exact roots.
- Every inventory command runs without side effects: no optional locks and no lazy fetch.

### Phase 1: Local state

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
- **Other ref namespaces:** notes, replace refs, `refs/original`, `refs/bisect`, `refs/pull`, and tool refs.

### Phase 2: Local versus remote

- Live remote heads and tags, read without fetching.
- Remote-tracking refs that are out of date, or whose branch was deleted on the remote.
- Branches that exist only locally, or only on the remote.
- Diverged branches and unpushed commits.
- Tags that differ in either direction.
- Integration state of every branch against the live base, tested in this order:
  1. merged;
  2. patch-equivalent (rebased);
  3. content already in the base (squash-merged);
  4. would conflict with the base;
  5. holds exclusive commits, or has unrelated history.
- Local and remote default branches that disagree, and renamed or transferred repositories whose old URLs are still in the remotes.

### Phase 3: History and object store

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

### Phase 4: Git-native residue and risk surfaces

- **Hooks:** active hooks in `.git/hooks` and in `core.hooksPath`, and hooks that call services or paths outside the repository.
- **Configuration in every scope** (system, global, local, worktree, conditional includes), with the origin of each value and credentials masked:
  - `insteadOf` rewrites;
  - `hooksPath`, `worktree`, fsmonitor;
  - filters;
  - registered maintenance;
  - the names of credential helpers, never their values.
- **Leftovers of interrupted operations:**
  - `ORIG_HEAD`, `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REBASE_HEAD`, `REVERT_HEAD`;
  - rebase directories;
  - stale `.lock` files;
  - `gc.log` and `gc.pid`;
  - an old `FETCH_HEAD`.
- **Attributes:** filters (LFS and others) whose tool is not installed.
- **Stray files:** `*.patch`, `*.mbox` and `*.orig`.
- **Serving the repository:** daemon, instaweb, `git-daemon-export-ok`, files left by `update-server-info`, and fsmonitor daemons.

### Phase 5: GitHub state

- **Pull requests:**
  - open, draft and abandoned ones, with age, author, review state and checks;
  - closed without merging while their branch still exists;
  - merged while their branch still exists;
  - pull requests from forks.
- **Issues and discussions:** open for a long time, waiting for an answer, stale, or with no labels.
- **Branches on GitHub:**
  - stale branches;
  - branches whose pull request was merged or closed;
  - protections and rulesets, with their bypass lists.
- **Actions:**
  - every workflow, enabled or disabled, with its latest result;
  - workflows whose last run on the default branch failed, with no success after it;
  - failed jobs that were never rerun or fixed;
  - scheduled workflows that stopped running;
  - runs stuck in queued or in progress;
  - runs waiting for approval;
  - workflows that point to deleted branches, files or secrets.
- **Storage:** artifacts and caches, with size and age.
- **Environments:** each one and its protection rules.
- **Secrets and variables:** names only.
- **Runners:** self-hosted runners that are offline or unused.
- **Dependabot:**
  - open alerts;
  - update pull requests that are open, failed or ignored;
  - its configuration.
- **Other security alerts:** secret scanning and code scanning.
- **Integrations and access:** webhooks (with failed deliveries), deploy keys (with last use), installed GitHub Apps, collaborators, invitations and teams.
- **Distribution:** releases and their assets, packages, Pages, Codespaces and wiki.
- **Forks:**
  - the whole fork network;
  - forks holding work that was never sent back.

### Phase 6: External links

- **Other GitHub repositories that reference this one:** `uses:` lines, submodules, marketplaces and dependency specifications. Code search indexes only default branches and files under 384 KB, so everything else goes to the ledger.
- **Mirrors and other hosts** found in the configuration.
- **Committed configuration for other CI and deploy services** (CircleCI, Netlify, Vercel and similar), reported as "referenced, live state unverified".
- **Public registries** whose packages point to this repository.
- **This machine, with consent:**
  - other clones of the same remote;
  - worktrees and alternates that point here;
  - symlinks into the repository;
  - IDE workspaces;
  - cron, launchd and systemd jobs;
  - tunnels and listening ports.

### Phase 7: Classification and coverage

- **Every finding gets:**
  - exactly one class: residue, dirty, orphaned, dead, deferred, external link, or needs investigation;
  - its evidence: the command, the full object ID and the raw output.
- **Branches** also carry their integration state.
- **Security-sensitive items** (keys, tokens, apps, access) are report-only.
- **Coverage ledger:** each domain is marked checked, BLOCKED (with the call that failed) or not reachable (with the reason). A domain that failed is never reported as empty.

### Phase 8: Report (gate 1)

- A plain-language summary of the repository's state.
- **Findings:** `F-n`, each with its class and its evidence.
- **Recommendations:** `R-n`, each with the findings it covers, its risk and whether it can be undone.
- **Questions for the user:** each with a recommended answer.
- The full coverage ledger.
- The user approves recommendations by ID. Silence, or a generic "clean it up", approves nothing.

### Phase 9: Debugging (only for approved recommendations that need it)

- Reproduce the problem in a throwaway worktree outside the repository.
- Bisect with a test that is read before it runs, then confirm that no bisect state is left behind.
- Use `blame -w -M -C` to find where a line really comes from.
- Diagnose the cause and report it as a finding. This phase changes no source.

### Phase 10: Plan (gate 2)

- **Actions:** `A-n`. Each one has its class, its exact commands with full IDs, a containment check, its backup coverage, its rollback, and a validation criterion written in advance.
- **Classes, in execution order:** prep → investigate → fix → integrate → publish → local delete → remote delete → close on GitHub → unlink external → files → maintenance.
- **History rewrites** are planned only when the user asks for one by name.
- The user approves actions by ID.

### Phase 11: Backup and revalidation

- **Backup:** a bundle of every ref, stored outside the repository, with its checksum and a restore test, plus patches of uncommitted work.
- **Revalidation:** re-run the audit sections the plan relies on. Any drift stops the run until the plan is rebuilt for the new state.

### Phase 12: Execution

- Run one action at a time, in class order, each one after its check.
- Publish every integration before deleting what it makes redundant.
- Do nothing destructive outside the plan.
- A failed action stops every action that depends on it.

### Phase 13: Validation and results

- Fresh reads against each criterion, with the raw output.
- The results report says:
  - what was done;
  - what was kept, and why;
  - what could not be verified;
  - what remains open.
- It also says where the backup is, with its checksum. The user decides whether to keep it.

## Open items

- **Minimum git version.** It must be confirmed in Git's release notes before the README declares it. Four features set it, and none has a verified version yet:
  - `merge-tree --write-tree`;
  - `rev-parse --show-ref-format`;
  - `GIT_NO_LAZY_FETCH`;
  - the `git config get` and `git config list` syntax.
- **Existing Phase 2 files.** With no fixed team, the three `agents/repo-hygiene/` agents and the `init-cleanup-and-debug` command need Nery's decision. The proposal: delete the agents, keep the command and adapt it to this workflow.
- **Enforcement of the execution invariants.** Decide whether a PreToolUse hook enforces them, now that there is no `security-guard` agent.
