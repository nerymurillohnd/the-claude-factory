# Audit, steps 0 to 2: intake, local Git, classification

The audit is read-only and complete. It covers the repository from its first commit to now, whatever the size. Display is paged; collection is never capped. Everything it finds is written down in the scratch folder, so a context compaction loses nothing.

## Ground rules

- **Read-only.** Allowed: commands that write nothing to the repository (`status`, `log`, `diff`, `show`, `blame`, `grep`, `rev-list`, `rev-parse`, `for-each-ref`, `cat-file`, `ls-files`, `ls-remote`, `merge-base`, `merge-tree --write-tree` into a temporary object store, `cherry`, `fsck` without `--lost-found`, `count-objects`, `worktree list`, `worktree prune --dry-run`, `stash list`/`show`, `gh` read commands, `gh api` GET). Not allowed: `fetch` (it moves remote-tracking refs), `gc`, `prune`, `clean` without `-n`, `fsck --lost-found`, anything that edits a ref, the index or a file.
- **No locks.** Run every audit git command as `GIT_OPTIONAL_LOCKS=0 git -C "<repo>" ...` so that `status` does not rewrite the index. Below, `git` means that.
- **Scratch folder.** Use your session scratchpad directory if the session names one, otherwise `mktemp -d "${TMPDIR:-/tmp}/repo-cleanup-XXXXXX"`. It is outside the repository. Write every command's output to a file there and read it in pieces (`wc -l`, `head`, `sort | uniq -c`, `awk`). Never print an unbounded history, ref list or PR list into the conversation. Keep `audit-log.md` (the command and the relevant result) and the findings there. Do not install anything and do not leave files anywhere else.
- **Secrets.** Report secret-like file names only. Never open `.env`, keys, tokens or credential stores, and never print a token. Redact credentials in every URL you show: `sed -E 's#(//)[^/@[:space:]]*@#\1***@#'`.
- **Failure is not zero.** If a command fails, the fact it would have given is `BLOCKED`, with the failing command and its error. Never read a failed call as an empty result.
- **Full SHAs** (40 characters) for anything the plan will act on.
- **Stash internals.** `refs/stash` points at commits that are not history (each stash with untracked files adds a root commit). Every history-wide query below uses `--exclude=refs/stash --all`.

## Step 0: intake

1. Resolve the repository from the request, or from the target on the `ARGUMENTS:` line when one is given: an absolute path to an existing directory is the repository and any text after it is a problem to investigate; with no path, use the current directory. Run `git -C "<path>" rev-parse --show-toplevel` and tell the user if the root differs from what they gave. If it is not a repository, stop.
2. Create the scratch folder and tell the user its path.
3. Identify the remote and host: `git remote -v` (redacted). If the host is GitHub, take `<owner>/<repo>` from the URL; check `gh auth status` and the viewer's permission with `gh repo view -R <owner>/<repo> --json viewerPermission,visibility,isFork,defaultBranchRef`. Without `gh`, use the read-only tools of a connected GitHub server; with neither, every GitHub fact is `BLOCKED` in the ledger. A host that is not GitHub: the GitHub domains are `not reachable`.
4. Ask once, with `AskUserQuestion`, which scans outside the repository are allowed: (a) read-only network queries (`git ls-remote`, `gh`, public registries); (b) searching this machine for other clones, workspace files, symlinks and scheduled jobs, and if so which folders to search; (c) listing processes and listening ports to find tunnels. A scope the user declines is recorded as `declined` in the ledger, not skipped silently.
5. Write `context.md` in the scratch folder with the answers.

## Step 1: collect

Run the sections below. Independent commands may run in parallel. Save each output as a file named after the section (`refs.tsv`, `worktrees.txt`, ...).

### 1.1 Context and operations in progress

```sh
git rev-parse --show-toplevel --absolute-git-dir --git-common-dir --is-bare-repository --is-shallow-repository
git branch --show-current            # empty means detached or unborn
git rev-parse --verify -q HEAD       # empty means unborn
git config --get-regexp '^remote\..*\.(url|pushurl)$' | sed -E 's#(//)[^/@[:space:]]*@#\1***@#'
git config --get-regexp '^remote\..*\.promisor$'                        # partial clone
ls "$(git rev-parse --absolute-git-dir)" | grep -E '^(MERGE_HEAD|CHERRY_PICK_HEAD|REVERT_HEAD|BISECT_LOG|rebase-merge|rebase-apply|ORIG_HEAD)$'
git ls-files --stage | grep '^160000'                                  # submodules
```

An operation in progress (merge, rebase, cherry-pick, revert, bisect; `rebase-apply` also means `git am`), a detached or unborn HEAD, a bare, shallow or partial clone, or a linked worktree as the target is reported first; ask the user how to proceed before planning anything else.

### 1.2 Base branch

The base is the ref every other ref is compared with. Pick the first that exists, and say which and why:

```sh
for ref in origin/main main "$(git symbolic-ref -q --short refs/remotes/origin/HEAD)" origin/master master; do
  [ -n "$ref" ] && git rev-parse --verify -q "$ref^{commit}" >/dev/null && { echo "$ref"; break; }
done
git ls-remote --symref origin HEAD       # the live default branch (needs the network scope)
```

If the live default branch differs from the cached one, use the live one. If the base exists only locally (`origin/main` missing), say so: nothing proves what the remote has, so remote facts are `BLOCKED` and no remote deletion is planned. Never rename or change the default branch.

### 1.3 Every ref

```sh
git for-each-ref --format='%(refname)%09%(objectname)%09%(objecttype)%09%(upstream:short)%09%(upstream:track)%09%(creatordate:short)%09%(authorname)%09%(subject)' > refs.tsv
git for-each-ref --format='%(refname)' | awk -F/ '{print $2}' | sort | uniq -c      # counts per namespace
```

This lists heads, remote-tracking refs, tags, notes, replace refs, the stash and any other namespace. `[gone]` in the track column means the upstream no longer exists.

### 1.4 Where every branch stands against the base

One pass over every local and remote-tracking branch: how far it is ahead and behind, and whether its content is already in the base even though its commits are not (a squash or rebase merge; `branch --merged` and `merge-base --is-ancestor` miss those). `merge-tree --write-tree` writes tree objects, so it is pointed at a temporary object store and the repository gets nothing new.

```sh
base=origin/main; repo="<repo>"; tmp="<scratch>/objects"; mkdir -p "$tmp"
base_sha=$(git -C "$repo" rev-parse --verify "$base^{commit}"); base_tree=$(git -C "$repo" rev-parse "$base^{tree}")
shared=$(git -C "$repo" rev-parse --path-format=absolute --git-path objects)
git -C "$repo" for-each-ref --format='%(refname)' refs/heads refs/remotes | grep -v '^refs/remotes/[^/]*/HEAD$' | while read -r ref; do
  sha=$(git -C "$repo" rev-parse "$ref^{commit}")
  read -r behind ahead < <(git -C "$repo" rev-list --left-right --count "$base_sha...$sha")
  if [ "$ahead" = 0 ]; then state=merged
  elif ! git -C "$repo" merge-base "$base_sha" "$sha" >/dev/null 2>&1; then state=unrelated
  else
    out=$(GIT_OBJECT_DIRECTORY="$tmp" GIT_ALTERNATE_OBJECT_DIRECTORIES="$shared" git -C "$repo" merge-tree --write-tree --no-messages "$base_sha" "$sha" 2>/dev/null); code=$?
    if [ "$code" = 1 ]; then state=conflicts
    elif [ "$code" != 0 ]; then state="error($code)"
    elif [ "${out%%$'\n'*}" = "$base_tree" ]; then state=in-base
    else state=differs; fi
  fi
  printf '%s\t%s\t+%s\t-%s\t%s\n' "$state" "$ref" "$ahead" "$behind" "$sha"
done | sort > branch-states.tsv
```

| State | Meaning |
| :-- | :-- |
| `merged` | the tip is reachable from the base |
| `in-base` | not reachable, yet merging it changes nothing: its content already landed |
| `differs` | it has work the base does not have |
| `conflicts` | merging it into the base conflicts |
| `unrelated` | it shares no history with the base (an orphan or greenfield lineage) |
| `error(n)` | git failed: `BLOCKED` |

States point; they do not decide. For every `differs`, `conflicts`, `unrelated` or unexplained `in-base` branch, look at the work itself:

```sh
git log --format='%h %an %ad %s' --date=short <base>..<ref>      # what the work is, who, how old
git diff --stat <base>...<ref>                                    # three dots: against the merge base
git cherry -v <base> <ref>                                        # '-' already in the base as an equivalent patch, '+' not
git range-diff <base>...<ref>                                     # only to match a branch with its rewritten twin
```

To read content, list names first (`git diff --name-only <base>...<ref>`) and exclude secret-like names with `-- . ':(exclude,glob)**/.env'`; committed secrets exist, so never fall back to an unfiltered patch. A branch checked out in a worktree cannot be deleted until that worktree is gone. A remote branch that was never fetched has no local objects: mark it `BLOCKED` and leave it untouched.

For remote branches also record the author (other authors raise the risk: ask), any open pull request (from `github.md`), and the live SHA (`git ls-remote --heads origin`), because execution re-checks it.

### 1.5 Worktrees

```sh
git worktree list --porcelain          # locked and prunable carry a reason; a missing path may still hold a registration
git worktree prune --dry-run -v        # preview only
git -C "<worktree path>" status --porcelain=v1 -b | head -50     # for each worktree that exists
```

A missing worktree folder can still hold an important branch: judge the branch (1.4) before proposing a prune. A worktree with uncommitted changes is never removed without the user deciding what happens to them.

### 1.6 Stashes

```sh
git stash list --format='%gd|%H|%ci|%gs'
git stash show --stat 'stash@{N}'                  # tracked changes
git show --stat --format= 'stash@{N}^3'            # untracked files (fails when there are none)
git diff --stat <base> 'stash@{N}'                 # empty means the tracked content is already in the base
```

A stash is uncommitted work that exists nowhere else: it is never dropped unless its content is in the base or in a rescue branch.

### 1.7 Working tree, ignored files and noise

```sh
git status --short --branch --ignored
git status --porcelain=v1 | cut -c1-2 | sort | uniq -c                        # staged / modified / untracked / conflicted counts
git ls-files --others --ignored --exclude-standard --directory                 # ignored, collapsed to directories
git clean -n -d -X                                                             # preview only: ignored files
git ls-files -ci --exclude-standard                                            # tracked files that match an ignore rule
git ls-files | grep -E '(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini|__pycache__|node_modules|\.pytest_cache|\.mypy_cache|\.ruff_cache)(/|$)|\.(swp|swo|tmp|bak|orig|rej|pyc|pyo|log)$|~$'   # tracked noise
find . -maxdepth 4 -name .git -not -path './.git' -not -path '*/node_modules/*'                # nested repositories (compare with the submodule list)
git lfs ls-files --size 2>/dev/null; git log -n 5 --grep='git-subtree-dir' --oneline         # LFS pointers, subtrees
```

You may list hidden and ignored files by name. You may not open them. `build`, `dist`, `target` and `coverage` are candidates for noise only after checking they are regenerable. Noise that is tracked is a finding (it is in history); noise that is ignored is harmless. Submodules and nested repositories are separate repositories: list them and never act inside them without their own approved action.

### 1.8 Residue of interrupted or old operations

```sh
gitdir=$(git rev-parse --absolute-git-dir); common=$(git rev-parse --path-format=absolute --git-common-dir)
git for-each-ref refs/original refs/bisect refs/replace refs/notes refs/svn          # filter-branch backups, bisect, replace, notes, git-svn
ls "$gitdir" | grep -E '^(ORIG_HEAD|FETCH_HEAD|gc\.log|gc\.pid|MERGE_MSG|SQUASH_MSG)$'
find "$common" -name '*.lock' -type f 2>/dev/null                                     # stale locks
ls "$common/svn" 2>/dev/null; ls "$common/hooks" | grep -v '\.sample$'                 # git-svn leftovers, non-sample hooks
git ls-files '*.patch' '*.mbox' '*.rej' '*.orig'                                       # stray patch files
```

### 1.9 Hooks and configuration that tie the repository outward

```sh
git config --get core.hooksPath
for f in $(ls "$(git rev-parse --git-path hooks)" | grep -v '\.sample$'); do echo "== $f"; grep -nE 'https?://|ssh://|/Users/|/home/|curl|wget' "$(git rev-parse --git-path hooks)/$f" | sed -E 's#(//)[^/@[:space:]]*@#\1***@#'; done
git config --list --show-origin --show-scope | grep -iE '^[a-z]+[[:space:]]+[^[:space:]]+[[:space:]]+(url\..*(insteadof|pushinsteadof)|core\.(hookspath|worktree|fsmonitor|sshcommand)|maintenance\.|gc\.|credential\.helper|includeif|include\.path)' | sed -E 's#(//)[^/@[:space:]]*@#\1***@#'
```

`url.<base>.insteadOf` silently redirects remotes; `core.hooksPath` and `core.fsmonitor` run code; `maintenance` registers background jobs. For credentials, report the helper name only; never read a credential store.

### 1.10 The live remote

```sh
git ls-remote --heads --tags origin > remote-live.txt                    # needs the network scope
git for-each-ref --format='%(objectname) %(refname)' refs/remotes/origin > tracking.txt
```

Compare the two: refs the remote has that were never fetched, tracking refs whose branch is gone (stale; `git remote prune origin --dry-run` previews them), and branches whose live SHA differs from the tracking ref. Tags that exist only locally are reported to the user.

## History, objects, GitHub and links

After 1.10, read the other audit references as the user's scopes allow: `history.md` (all history, objects, secrets by name, deferred work), `github.md` (pull requests, issues, discussions, forks, Actions, protection, integrations, alerts), `links.md` (everything outside the repository that still points at it). They write to the same scratch folder.

## Step 2: classify and keep the ledger

Give every ref, file, worktree, stash, submodule and external item one bucket, with its evidence:

1. **Active work**: uncommitted changes, checked-out worktrees, branches with an open pull request or recent activity.
2. **Authoritative**: the base and its published copy, protected branches, release tags.
3. **Recovery evidence**: stashes, rescue refs, reflog-only commits, anything holding work that exists nowhere else.
4. **Stale risk**: worktrees pointing at deleted paths, branches whose upstream is gone, failed and forgotten automation, links that are still alive.
5. **Deletion candidate**: fully integrated work with the containment proof, regenerable noise, and dead weight.
6. **Unknown**: needs the user (unvetted ignored folders, other authors' branches, unexplained refs).

Anything the audit finds that calls for a refactor, a cleanup, a bisect, debugging or other work is a finding too; it goes to the report and, once approved, to the plan (`investigate.md`).

Write `coverage.md`: one line per domain (refs, branches against base, worktrees, stashes, working tree, residue, hooks and config, remote live, history, objects, secrets by name, deferred work, pull requests, issues, discussions, forks, Actions, protection and rulesets, integrations, alerts, mentions, other clones, jobs, tunnels, registries) with exactly one of:

- `checked`: collected, with the file that holds it.
- `BLOCKED`: the failed command and its error.
- `not reachable`: the reason, and what the user can check themselves.
- `declined`: the scope the user did not allow.

The audit cannot prove that nothing exists beyond what these commands can see. What it guarantees is this ledger, and the report always carries it.
