# Phase 4: Git-native residue and risk surfaces

Find the places inside `.git` and in Git's configuration where old state or live links hide. This phase is read-only.

## Hooks

- Active hooks in `.git/hooks`, ignoring `*.sample`.
- Active hooks in the directory named by `core.hooksPath`.
- Hooks that call services or paths outside the repository: each one is a live external link.

## Configuration

Read every scope (system, global, local, worktree and conditional includes) with the origin of each value. Mask credential-bearing values inside the command, before the output is read. Look for:

- `url.<base>.insteadOf` rewrites, which silently redirect remotes.
- `core.hooksPath`, `core.worktree` and `core.fsmonitor`.
- Filters.
- Registered maintenance.
- The names of credential helpers, never their values.

`git config --list` and `--get-regexp` are deprecated in favor of `git config list` and `git config get --all --show-names --regexp` ([git-config][git-config]). Use the form the installed Git supports.

## Leftovers of interrupted operations

- `ORIG_HEAD`, `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REBASE_HEAD` and `REVERT_HEAD`.
- Rebase directories: `rebase-merge` and `rebase-apply`, which `git am` also leaves.
- Bisect leftovers: `refs/bisect/*`, `BISECT_LOG`, `BISECT_START` and the other `BISECT_*` files.
- `refs/original/*`, the backups `filter-branch` leaves.
- `refs/replace/*`, which silently changes what history Git shows.
- Stale `.lock` files.
- `gc.log` and `gc.pid`.
- An old `FETCH_HEAD`.

## Attributes

- Filters in `.gitattributes`, LFS and others, whose tool is not installed.

## Stray files

- `*.patch`, `*.mbox` and `*.orig`.

## Serving the repository

- `git daemon` and `git instaweb` processes.
- `git-daemon-export-ok`.
- Files left by `update-server-info`.
- fsmonitor daemons.

## Done when

- [ ] Every active hook is listed, and each one that calls outside the repository is marked as an external link.
- [ ] Every configuration scope was read with its origins, and no credential value appears in the output.
- [ ] Every leftover of an interrupted operation is listed.
- [ ] Every attribute filter without its tool is listed.
- [ ] Every stray file and every process serving the repository is listed.
- [ ] Every section that could not be collected is in the coverage ledger.

## Sources

Checked on 2026-11-04.

- [git-config][git-config]: "The following modes have been deprecated in favor of subcommands"; `--get-regexp` is "Replaced by `git config get --all --show-names --regexp`".

[git-config]: https://git-scm.com/docs/git-config
