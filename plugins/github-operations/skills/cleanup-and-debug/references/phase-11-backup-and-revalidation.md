# Phase 11: Backup and revalidation

Make every approved change recoverable, and confirm the repository still matches the audit. This runs after gate 2 and before any change.

## Backup

- Bundle every ref, outside the repository: `git bundle create <path>/backup.bundle --all` ([git-bundle][git-bundle]).
- Record the bundle's checksum.
- Prove it restores: `git bundle verify` exits zero for a valid bundle, and a clone from the bundle into a throwaway location succeeds ([git-bundle][git-bundle]).
- Save patches and copies of uncommitted work, and of the ignored files the plan names.
- `git stash --all` is not a backup: it changes the working tree.
- When the plan includes a history rewrite, also make a full mirror clone.

## Revalidation

- Re-run the audit sections the plan relies on, and compare them with the evidence in the plan.
- Stop on any drift: a ref that moved, a branch that gained commits, a pull request that changed state, a stash added or dropped.
- Resume only after the plan is rebuilt for the new state and its changed actions are approved again.

## Done when

- [ ] The bundle exists outside the repository, with its checksum.
- [ ] `git bundle verify` passed, and the restore clone succeeded.
- [ ] Every uncommitted change and named ignored file is saved.
- [ ] Revalidation found no drift, or the plan was rebuilt and approved again.

## Sources

Checked on 2026-11-04.

- [git-bundle][git-bundle]: "`--all` can be used to package all refs"; `verify` checks "that a bundle file is valid and will apply cleanly", and "The exit code is zero for success"; "It is possible git-clone a new repository from a bundle."

[git-bundle]: https://git-scm.com/docs/git-bundle
