# Phase 1: audit and diagnosis

Goal: an evidence-based inventory complete enough that nothing in Phase 2 is a guess. Keep a log of every command you ran and its relevant result in `<scratch>/audit-log.md`; Phase 2 quotes it. Every Git command takes `-C "<repo>"`; `gh` subcommands take `-R <owner>/<repo>` and `gh api` names the repository in its path. Use full 40-character SHAs when you record a tip, not abbreviations.

## Read-only means read-only

- Phase 1 changes nothing in the repository: no ref, no object, no file, no remote. The only files you write are in the scratch folder.
- Allowed: any command that does not write. Examples: `status` (run it as `GIT_OPTIONAL_LOCKS=0 git -C … status` so it does not refresh the index), `log`, `diff --stat`, `show --stat`, `rev-list`, `for-each-ref`, `cherry`, `merge-base`, `range-diff`, `shortlog`, `config user.name`, `worktree list`, `worktree prune --dry-run`, `stash list/show`, `reflog show`, `ls-files`, `ls-remote`, `gh … list/view`, `gh auth status`, `gh api` with GET only, and the inventory script. `ls-remote` queries the remote but changes nothing locally.
- Not allowed: `git fetch` (it moves remote-tracking refs), `gh pr close`, anything that writes. Remote-tracking refs may therefore be stale: `ls-remote` is the source of truth for what the remote has, and the inventory's `remote_live` section shows the differences.

## 0. Prove the guard is active

The skill's hook is set to block when it cannot run, but a policy that disables hooks would silently remove it, so prove it works before anything else. Run this command, which is harmless even if nothing stops it because it is a dry run:

```bash
git -C "<repo>" push --dry-run --force origin HEAD
```

It must be refused with a message starting `git-hygiene:`. **That refusal is the expected success: do not stop, and ignore its "Cleanup stops here" ending, which applies to real denials.** If the command runs, or fails for any other reason than that refusal, the guard is not working: stop, tell the user (a missing `python3` is the usual cause), and do not continue.

## 1. Context

Ask the user once, with `AskUserQuestion`, whether read-only network queries are acceptable (`git ls-remote` and `gh`; they cover this whole audit). If they decline, run the inventory without `--ls-remote`, mark everything that needs the remote or GitHub `BLOCKED`, and say that remote branches cannot be judged. Otherwise run the inventory with `--ls-remote` (the remote is the source of truth for what branches exist). On a large repository it takes a while: set a long Bash timeout. Useful options: `--detail-limit N` (branches measured in depth, newest unmerged first, default 500), `--time-budget SECONDS` (default 60), `--base REF` (use it when the live default branch differs from the cached one).

Read these first:

- The summary's `failed_git_calls` and the saved file's `errors` section. A failed call is recorded there instead of being read as an empty result: treat every fact that depends on a failed call as `BLOCKED`.
- Lists in the output (`untracked`, `ignored`, noise, secret-like names, nested repositories) are samples of at most 50 with a `count` and a `truncated` flag; use `count`, and get the full list with the matching Git command when you need it.

The `context` section answers: checkout root, git dir and common dir, bare / linked worktree / shallow / partial clone, HEAD (branch, detached, unborn), remotes (credentials already redacted), whether `main` and `origin/main` exist, each remote's cached default branch, operations in progress (merge, rebase, cherry-pick, revert, bisect), submodules and nested repositories, and tools.

- An operation in progress, a detached HEAD, a conflicted index, a bare or partial clone, a linked worktree as target, or an unborn HEAD: report it first and ask the user how to proceed before planning anything else.
- No `main`: say so and use the remote default branch as the base. Never rename or change it. The live default is `git -C "<repo>" ls-remote --symref <remote> HEAD`; if it differs from the cached one, re-run the inventory with `--base`.
- Submodules and nested repositories are separate repositories. List them; never act inside them without a separate approval of its own action.

## 2. Provider, visibility, permissions, pull requests

Needed to judge remote deletions. Use `gh` if it is installed and signed in (`gh auth status`); else the read-only GitHub tools (`get`, `list`, `search`) of a connected MCP server, never one that writes; else mark these items `BLOCKED`. If the remote host is not GitHub, mark them `BLOCKED`. Never print tokens. Take `<owner>/<repo>` from `context.remotes.<name>.url.path` in the inventory (use the remote the base ref belongs to) and always name it: `gh` otherwise reads the repository of the current directory, which may not be the target. Subcommands take `-R <owner>/<repo>`; `gh api` takes the repository in the path.

```bash
gh -R <owner>/<repo> repo view --json nameWithOwner,visibility,defaultBranchRef,viewerPermission,isFork
gh api repos/<owner>/<repo>/branches/<branch>/protection
gh api repos/<owner>/<repo>/rules/branches/<branch>
gh -R <owner>/<repo> pr list --state open --limit 5000 --json number,title,headRefName,baseRefName,isDraft,mergeable,updatedAt,author
```

Replace `<branch>` with each branch you are judging, not the checked-out one. Protection can come from classic branch protection or from rulesets: check both. A 404 from the protection call means "not protected" only when `viewerPermission` is `ADMIN` or `MAINTAIN`; with less permission it means "unknown", and remote deletions of that branch are `BLOCKED`.

Without `gh` and without MCP, `git ls-remote <remote> 'refs/pull/*/head'` counts GitHub pull request heads, open or not; it cannot tell which are open, so open-PR state is `BLOCKED`. For each open pull request record its head branch, base, state (draft, conflicting, stale over 90 days) and whether its head branch also appears in the branch list. A remote branch with an open pull request is never a deletion candidate on its own.

## 3. Branches

The `branches` section compares every local and remote branch with the base ref: commits ahead and behind, exclusive commits, authors, a `merge-tree` preview, patch-equivalence with `git cherry`, and `signals` such as `merged-into-base`, `no-net-change-vs-base`, `has-exclusive-commits`, `conflicts-with-base`, `merge-preview-unavailable`, `upstream-gone`, `stale-over-180-days`, `wip-subject`. The entries come in `for-each-ref` order (alphabetical by ref name). `detail_truncated` means the detail limit or the time budget left some unmerged branches without deep detail (`detail_skipped`): re-run with higher limits, or measure those branches yourself. A branch's `patch_equivalence` starting with `skipped` means it is too far from the base for `git cherry`; the merge preview still tells whether merging would change anything. Read the section in pages: `--from F --section branches --signal has-exclusive-commits --limit 40 --offset 0`, then `--offset 40`, and so on; `matching_branches` gives the total.

Signals point; they do not decide. For every branch with exclusive commits, conflicts, or a `no-net-change` you cannot explain from its commits:

1. `git log --format='%h %an %ad %s' --date=short <base ref>..<ref>` and `git diff --stat <base ref>...<ref>`: what is the work, who wrote it, how old is it. To read content, first list the names (`git diff --name-only <base ref>...<ref>`), pick the secret-like ones (`.env`, keys, certificates, token and credential files; the inventory's `files.secret_like_file_names` is the list for the checkout), and exclude each with its own pathspec: `-- . ':(exclude,glob)**/.env'`. Committed secrets exist: never fall back to an unfiltered patch.
2. Is the content already in the base under different commits (a squash or cherry-pick)? `no-net-change-vs-base` says merging would change nothing; confirm by reading the diff of the branch against the base for its files.
3. Was it rebased elsewhere? `git range-diff` compares patch series: use it to match a branch with its rewritten twin, never as proof of graph containment.
4. Prefer the inventory's `merge_preview` (it is computed in a temporary object store). For a manual preview run `git merge-tree --write-tree --no-messages <base ref> <ref>` with the temporary store, so the repository gets no new objects: `GIT_OBJECT_DIRECTORY=<scratch>/objects GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git -C "<repo>" rev-parse --path-format=absolute --git-path objects)" git -C "<repo>" merge-tree …`. Exit 0 is a clean merge, exit 1 means conflicts, anything else is an error. Read the exit status; silence is not proof. Before Git 2.38 the preview does not exist: say so.
5. Remote branches: authors other than the user (compare with `git config user.name`), an open pull request, protection, repository visibility. Public repositories and other people's branches raise the deletion risk: any other author means ask. Record each remote branch's live SHA from `ls-remote --heads`, because Phase 3 re-checks it.

A branch checked out in a worktree cannot be deleted until that worktree is gone. Branches the inventory could not measure because the remote has them but nothing was fetched (`remote_live.not_fetched_yet`) have no local objects: mark them `BLOCKED` and leave them untouched, unless the user wants an early `prep` fetch and a second audit of them.

## 4. Worktrees

The `worktrees` section lists each registration with `exists`, `locked` and `prunable` when set, and `dirty_entries` (the number of uncommitted entries; `null` means the status call failed, which is `BLOCKED`). A missing path may still hold a registration and an important branch: inspect both (the branch's exclusive work from §3) before proposing a prune. Preview with `git worktree prune --dry-run --verbose`; `prune` and `remove` change state. A worktree with uncommitted changes is never removed without the user deciding what happens to them.

## 5. Stashes and tags

For each stash: `git stash show --stat --include-untracked <exact selector>` (for example `stash@{3}`) and the message and date from the inventory. Untracked files live in the stash's third parent: `git show --stat --format= <selector>^3` (it fails when there are none). Is its content already in the base? Compare with `git diff --stat <base ref> <selector>`. A stash holds uncommitted work that exists nowhere else.

Tags: compare local tags with the remote's (`git ls-remote --tags <remote>`). A tag that exists only locally is reported to the user in Phase 2; pushing it is a `publish` action, deleting it a `local-delete`.

## 6. Working tree, files and noise

The `working_tree` and `files` sections list staged, unstaged, untracked, conflicted and ignored paths, hidden files, noise (`.DS_Store`, temp and editor files, bytecode, caches, generated folders), tracked files that look like noise, large tracked files, and secret-like file names. `build`, `dist`, `target` and `coverage` are only candidates: check before treating them as noise. You may list hidden and ignored files. You may not read or print their contents; if a name looks like a secret, report only the name. Noise that is tracked is a finding (it is in history); noise that is ignored is harmless.

## 7. History noise and reflog

The `history` section counts commits and flags WIP-style subjects on the base and across all refs (`truncated` marks a cap). The `reflog` section lists recent HEAD commits no branch or tag contains. Reflogs are local and expire (`gc.reflogExpire`, 90 days by default for reachable entries): treat them as a hint about lost work and never promise recovery from them. Rewriting noisy history that is already published is not an option; report it.

## 8. Large repositories

Prefer aggregates to dumps: `git rev-list --count`, `for-each-ref --format --sort --count`, `git shortlog -sn --no-merges <range>`, `git log --since … --format`. Page long outputs with `--max-count`. Read inventory sections one at a time. In Phase 2 list individually only the branches that need a decision and summarize the fully merged ones as counts plus a file in the scratch folder.

## 9. When you cannot verify

If something exists and you can reach it, investigate it. If verification truly is impossible (no permission, tool missing, remote unreachable, a failed call), write the specific limitation, keep the item untouched in the plan and mark it `BLOCKED`.

## 10. Save what you found

Write your findings to `<scratch>/findings.md` (grouped as Phase 2 §1 lists them) and keep `<scratch>/audit-log.md` current, so a compaction or a declined plan loses nothing.
