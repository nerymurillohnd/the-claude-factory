# Phase 10: Plan (gate 2)

Turn the approved recommendations into exact actions. This phase changes nothing.

## Action fields

Every action, `A-1`, `A-2`, …, carries:

- The recommendation it implements, and its class.
- The exact commands, with full object IDs.
- Its containment check.
- Its backup coverage.
- Its rollback.
- Its validation criterion, written now so it cannot be bent afterwards.

## Action classes

In execution order:

1. **prep:** the backup first, then switching to a clean base.
2. **investigate:** Phase 9 work not yet done.
3. **fix:** corrections on a new branch in a separate worktree, with the repository's own checks, landing through a pull request. Never committed straight to the base.
4. **integrate:** merge, squash, cherry-pick or revert into the local base.
5. **publish:** a plain push of the integrated base, never forced.
6. **local delete:** local branches, worktrees, stashes, tags and stale remote-tracking refs.
7. **remote delete:** remote branches and tags, one per action.
8. **close on GitHub:** a pull request, issue or discussion, one per action, with an explanatory comment.
9. **unlink external:** disable a workflow, delete old artifacts and caches, remove a webhook, stop a tunnel or a scheduled job. One per action, with its reversibility.
10. **files:** named noise files, previewed and backed up first.
11. **maintenance:** `gc`, repack, reflog expiry, prune. Last, each approved by name.

**History rewrites** become actions only when the user asks for one by name, and never join a bulk approval.

## Containment checks

An item may be deleted only when one of these holds:

- It is an ancestor of the published base.
- Its content is already in the base.
- It is in the backup bundle, and the user approved that specific action.

A remote deletion also re-reads the live SHA and acts only if it equals the audited one.

## Gate 2

- The user approves actions by naming their IDs. Silence approves nothing.
- Security-sensitive items never appear as actions.

## Done when

- [ ] Every action implements an approved recommendation and has all six fields.
- [ ] Every deletion has a containment check that runs before it.
- [ ] Actions are ordered by class.
- [ ] The user's answer names the approved action IDs.
