# Phase 7: Classification and coverage

Turn everything the audit collected into findings. This phase is read-only.

## Classes

Give every item exactly one class:

- **Residue:** state left behind by finished or interrupted work.
- **Dirty:** uncommitted or unpushed changes.
- **Orphaned:** refs, worktrees or registrations whose target is gone.
- **Dead:** branches, tags, workflows or files that nothing uses.
- **Deferred:** work started and never finished: abandoned pull requests, stale stashes, failed jobs never rerun.
- **External link:** anything outside the repository that still points to it.
- **Needs investigation:** a problem whose cause is unknown and needs a bisect, a blame or a reproduction.

## Evidence

Every finding carries:

- The command that produced it.
- The full object ID or GitHub identifier.
- A pointer to the raw output file.

## Branches

Every branch also carries its sync state and its integration state from Phase 2.

## Security-sensitive items

Deploy keys, tokens, secrets, installed apps and collaborator access are classified as **report-only**. They never become actions.

## Coverage ledger

- One row for every audit domain, with its status: `checked`, `BLOCKED` with the call that failed, or `not reachable` with the reason and what the owner can check personally.
- Refused consent scopes appear as refused.

## Done when

- [ ] Every collected item has exactly one class and its evidence.
- [ ] Every branch has its sync and integration states.
- [ ] Every security-sensitive item is marked report-only.
- [ ] Every audit domain has one row in the coverage ledger, and no failed domain is reported as empty.
