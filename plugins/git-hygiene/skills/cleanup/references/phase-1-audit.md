# Phase 1: audit and diagnosis

Goal: an evidence-based inventory complete enough that nothing in Phase 2 is a guess. Keep a log of every command you ran and its relevant result; Phase 2 quotes it. **Phase 1 is read-only**: it changes no ref, no object, no file and no remote.

## 0. Prove the guard is active

The cleanup relies on a hook that Claude Code can skip if `python3` is missing or the hook is disabled by managed settings. Before anything else run this command, which is harmless even if nothing stops it because it is a dry run:

```bash
git -C "<repo>" push --dry-run --force origin HEAD
```

It must be refused with a message starting `git-hygiene:`. If it runs, or fails for any other reason than the refusal, the guard is not working: stop, tell the user (a missing `python3` is the usual cause), and do not continue.

## Read-only means read-only

- Allowed: `status` (run it as `GIT_OPTIONAL_LOCKS=0 git -C … status` so it does not refresh the index), `log`, `diff --stat`, `show --stat`, `rev-list`, `for-each-ref`, `cherry`, `merge-tree`, `range-diff`, `worktree list`, `stash list/show`, `reflog show`, `ls-files`, `ls-remote`, `gh … list/view`, and the inventory script. `ls-remote` queries the remote but changes nothing locally.
- Not allowed in Phase 1: `git fetch` (it moves remote-tracking refs), `gh pr close`, anything that writes. Remote-tracking refs may therefore be stale: `ls-remote` is the source of truth for what the remote has, and the inventory's `remote_live` section shows the differences. If a fetch is needed, it becomes an action in the plan (`prep` class) that the user approves.

## 1. Context

Run the inventory with `--ls-remote` once the user accepts a network query (the remote is the source of truth for what branches exist). On a large repository it takes a while: set a long Bash timeout. Useful options: `--detail-limit N` (branches measured in depth, newest unmerged first, default 500), `--time-budget SECONDS` (default 60), `--base REF`. The `context` section answers: checkout root, git dir and common dir, bare/linked worktree/shallow/partial clone, HEAD (branch, detached, unborn), remotes (credentials already redacted), whether `main` and `origin/main` exist, each remote's cached default branch, operations in progress (merge, rebase, cherry-pick, revert, bisect), submodules and nested repositories, and tools.

- An operation in progress, a detached HEAD or a conflicted index: report it first and ask the user how to proceed before planning anything else.
- No `main`: say so and use the remote default branch as the base. Never rename or change it.
- The remote default branch: `git -C "<repo>" ls-remote --symref <remote> HEAD` shows the live one.
- Submodules and nested repositories are separate repositories. List them; never act inside them without a separate approval.

## 2. Provider, visibility, permissions, pull requests

Needed to judge remote deletions. Use `gh` if it is installed and signed in (`gh auth status`); else the GitHub tools of any connected MCP server; else mark these items `BLOCKED`. Never print tokens. Take `<owner>/<repo>` from the inventory's redacted remote and always pass it with `-R`: `gh` otherwise reads the repository of the current directory, which may not be the target.

```bash
gh -R <owner>/<repo> repo view --json nameWithOwner,visibility,defaultBranchRef,viewerPermission,isFork
gh api repos/<owner>/<repo>/branches/<branch>/protection   # 404 means unprotected or no permission
gh api repos/<owner>/<repo>/rules/branches/<branch>        # repository rulesets that apply to the branch
gh -R <owner>/<repo> pr list --state open --limit 5000 --json number,title,headRefName,baseRefName,isDraft,mergeable,updatedAt,author
```

Replace `<branch>` with each branch you are judging, not the checked-out one. Protection can come from classic branch protection or from rulesets: check both.

Without `gh` and without MCP, `git ls-remote <remote> 'refs/pull/*/head'` counts GitHub pull request heads. For each open pull request record its head branch, base, state (draft, conflicting, stale over 90 days, abandoned author) and whether its head branch also appears in the branch list. A remote branch with an open pull request is never a deletion candidate on its own.

## 3. Branches

The `branches` section compares every local and remote branch with the base (`origin/main`, else `main`): commits ahead and behind, exclusive commits, authors, a `merge-tree` preview, patch-equivalence with `git cherry`, and `signals` such as `merged-into-base`, `no-net-change-vs-base`, `has-exclusive-commits`, `conflicts-with-base`, `upstream-gone`, `stale-over-180-days`, `wip-subject`. `detail_truncated` means the detail limit or the time budget left some unmerged branches without deep detail (`detail_skipped`): re-run with higher limits, or measure those branches yourself. `patch_equivalence: skipped` means the branch is too far from the base for `git cherry`; the merge preview still tells whether merging would change anything. Read the section in pages: `--from F --section branches --signal has-exclusive-commits --limit 40`.

Signals point; they do not decide. For every branch with exclusive commits, conflicts, or an unexplained `no-net-change`:

1. `git log --format='%h %an %ad %s' --date=short <base>..<ref>` and `git diff --stat <base>...<ref>`: what is the work, who wrote it, how old is it. Read content only with secret-like paths excluded (`-- . ':(exclude).env'`): committed secrets exist.
2. Is the content already in the base under different commits (a squash or cherry-pick)? `no-net-change-vs-base` says merging would change nothing; confirm by reading the diff of the branch against the base for its files.
3. Was it rebased elsewhere? `git range-diff` compares patch series: use it to match a branch with its rewritten twin, never as proof of graph containment.
4. Preview an integration with `git merge-tree --write-tree --no-messages <base> <ref>`: exit 0 is a clean merge, exit 1 means conflicts, anything else is an error. Read the exit status; silence is not proof. Before Git 2.38 this flag does not exist: say the preview is unavailable.
5. Remote branches: authors other than the user, an open pull request, protection, repository visibility. Public repositories and other people's branches raise the deletion risk.

A branch checked out in a worktree cannot be deleted until that worktree is gone.

## 4. Worktrees

The `worktrees` section lists each registration with `exists`, `locked`, `prunable` and the number of uncommitted entries. A missing path may still hold a registration and an important branch: inspect both (the branch's exclusive work from section 3) before proposing a prune. Preview with `git worktree prune --dry-run --verbose`; compare local tags with the remote's (`git ls-remote --tags`) so no tag exists only here; `prune` and `remove` change state. A worktree with uncommitted changes is never removed without the user deciding what happens to them.

## 5. Stashes

For each stash: `git stash show --stat --include-untracked <exact selector>` (for example `stash@{3}`) and the message and date from the inventory. Is its content already in the base? Does it include untracked files? A stash holds uncommitted work that exists nowhere else.

## 6. Working tree, files and noise

The `working_tree` and `files` sections list staged, unstaged, untracked, conflicted and ignored paths, hidden files, noise (`.DS_Store`, temp and editor files, bytecode, caches, generated folders), tracked files that look like noise, large tracked files, and secret-like file names. You may list hidden and ignored files. You may not read or print their contents; if a name looks like a secret, report only the name. Noise that is tracked is a finding (it is in history); noise that is ignored is harmless.

## 7. History noise and reflog

The `history` section counts commits and flags WIP-style subjects on the base and across all refs. The `reflog` section lists recent HEAD commits no branch or tag contains. Reflogs are local and expire (`gc.reflogExpire`, 90 days by default for reachable entries): treat them as a hint about lost work and never promise recovery from them. Rewriting noisy history that is already published is not an option; report it.

## 8. Large repositories

Prefer aggregates to dumps: `git rev-list --count`, `for-each-ref --format --sort --count`, `git shortlog -sn --no-merges <range>`, `git log --since … --format`. Page long outputs with `--max-count`. Read inventory sections one at a time.

## 9. When you cannot verify

If something exists and you can reach it, investigate it. If verification truly is impossible (no permission, tool missing, remote unreachable), write the specific limitation, keep the item untouched in the plan and mark it `BLOCKED`.
