# Phase 13: Validation and results

Prove each action did what it promised, and report the run.

## Validation

- Run fresh read-only commands against each criterion written in Phase 10. Never validate from memory or from the action's own output.
- Quote the raw output.
- Typical proofs:
  - Each deleted ref is gone.
  - The remote head list equals the planned one.
  - Every exclusive tip recorded in the audit is an ancestor of the base, or is in the bundle.
  - No backup ref namespace remains.
  - No `refs/bisect/*` or `BISECT_*` file remains, and no throwaway worktree is registered.
  - Each disabled workflow is disabled, and each stopped process is gone.
- Report a criterion that cannot be checked as not verifiable, never as passed.

## Results report

- What was done, split into verified and reported.
- What was kept, and why.
- What could not be verified.
- What remains open, including the recommendations the user did not approve.
- Where the backup is, with its checksum. The user decides whether to keep it.

## Done when

- [ ] Every action has its criterion checked with fresh raw output, or marked not verifiable.
- [ ] The results report covers done, kept, unverifiable and open items.
- [ ] The user was told where the backup is and asked whether to keep it.
