---
name: cleanup-and-debug
description:
---

## Workflow

Copy this checklist into your response and check off each phase once it passes the "Done when" list at the end of its reference:

```text
Progress:
- [ ] Phase 0: Intake and preflight
- [ ] Phase 1: Local state
- [ ] Phase 2: Local versus remote
- [ ] Phase 3: History and object store
- [ ] Phase 4: Git-native residue
- [ ] Phase 5: GitHub state
- [ ] Phase 6: External links
- [ ] Phase 7: Classification and coverage
- [ ] Phase 8: Report (gate 1)
- [ ] Phase 9: Investigation
- [ ] Phase 10: Plan (gate 2)
- [ ] Phase 11: Backup and revalidation
- [ ] Phase 12: Execution
- [ ] Phase 13: Validation and results
```

Run every phase the same way:

1. Read the phase's reference when the phase starts.
2. Do every section of the reference.
3. Check the result against the reference's "Done when" list.
4. If an item fails, redo it or record why it cannot pass, then check again.
5. Only move to the next phase when every item passes.

### 1. Audit

Rules for Phases 0 to 6:

- Change nothing in the repository, on GitHub or on the machine.
- Run every git command with `GIT_OPTIONAL_LOCKS=0`, because a plain `git status` writes the index, and with `GIT_NO_LAZY_FETCH=1`, because a partial clone otherwise fetches missing objects ([git](https://git-scm.com/docs/git), [git-status](https://git-scm.com/docs/git-status#_background_refresh)).
- Read the remote without fetching.
- Never read a credential. Mask any credential-bearing value inside the command, before its output reaches you.
- Write large outputs to files in a scratch folder outside the repository, and read them in pieces. Collect everything; never sample.
- Record every audit domain in the coverage ledger with one status: `checked`; `BLOCKED`, with the call that failed; or `not reachable`, with the reason. A domain whose call failed is never reported as empty.

Phases:

0. **Intake and preflight.** Identify the repository, its format, the tools and the GitHub identity, and get consent for scans outside the repository. Read `references/phase-0-intake-and-preflight.md` before anything else.
1. **Local state.** Inventory HEAD, the working tree, nested content, symlinks, worktrees, stashes, branches, tags and other refs. Read `references/phase-1-local-state.md` when Phase 0 passes.
2. **Local versus remote.** Compare every branch and tag with the live remote by full object ID, and find each branch's integration state. Read `references/phase-2-local-versus-remote.md` when Phase 1 passes.
3. **History and object store.** Audit the whole history, authors, object store health, weight, secrets ever committed and lost work. Read `references/phase-3-history-and-object-store.md` when Phase 2 passes.
4. **Git-native residue.** Find hooks, risky configuration, leftovers of interrupted operations, stray files and processes serving the repository. Read `references/phase-4-git-residue.md` when Phase 3 passes.
5. **GitHub state.** Audit pull requests, issues, branches and rules, Actions, Dependabot, security alerts, integrations, access, distribution and forks. Read `references/phase-5-github-state.md` when Phase 4 passes.
6. **External links.** Find everything outside the repository that still points to it, on GitHub, on other hosts and on this machine. Read `references/phase-6-external-links.md` when Phase 5 passes.

### 2. Planning

Rules for Phases 7 to 10:

- Change nothing, except the throwaway worktree of Phase 9, which is removed before the phase ends.
- Every gate needs the user's explicit answer naming the approved IDs. Silence, a timeout or a generic "clean it up" approves nothing; ask again.
- Security-sensitive items (deploy keys, tokens, secrets, installed apps, collaborator access) are report-only and never become actions.

Phases:

7. **Classification and coverage.** Give every collected item one class and its evidence, and complete the coverage ledger. Read `references/phase-7-classification-and-coverage.md` when Phase 6 passes.
8. **Report (gate 1).** Present findings, recommendations, questions and the coverage ledger, and get the approved recommendation IDs. Read `references/phase-8-report.md` when Phase 7 passes. When the user answers "audit only" or refuses, end the run here.
9. **Investigation.** Reproduce, bisect and blame in a throwaway worktree, for the approved recommendations that need a diagnosis. Read `references/phase-9-investigation.md` when gate 1 approves one that needs it; otherwise skip to Phase 10.
10. **Plan (gate 2).** Turn the approved recommendations into ordered actions with containment checks, backup, rollback and validation criteria, and get the approved action IDs. Read `references/phase-10-plan.md` when Phase 9 passes or is skipped.

### 3. Debug execution

Rules for Phases 11 to 13:

- Run only the actions approved at gate 2.
- A failed action stops every action that depends on it. Report the failure with its raw output; never improvise a workaround.

Phases:

11. **Backup and revalidation.** Bundle every ref outside the repository, prove it restores, and stop on any drift from the audit. Read `references/phase-11-backup-and-revalidation.md` when gate 2 approves.
12. **Execution.** Run the approved actions one at a time, in class order, each after its containment check. Read `references/phase-12-execution.md` when Phase 11 passes.
13. **Validation and results.** Check every action against its criterion with fresh reads, and report what was done, kept, unverifiable and open. Read `references/phase-13-validation-and-results.md` when Phase 12 ends.
