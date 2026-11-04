---
name: cleanup-and-debug
description:
---

## Workflow

Copy this checklist into your response and check off each phase once it passes its "Done when" list:

```text
Audit progress:
- [ ] Phase 0: Intake and preflight
- [ ] Phase 1: Local state
- [ ] Phase 2: Local versus remote
- [ ] Phase 3: History and object store
- [ ] Phase 4: Git-native residue
- [ ] Phase 5: GitHub state
- [ ] Phase 6: External links
```

### 1. Audit

Rules for every audit phase:

- Change nothing in the repository, on GitHub or on the machine.
- Run every git command with `GIT_OPTIONAL_LOCKS=0`, because a plain `git status` writes the index, and with `GIT_NO_LAZY_FETCH=1`, because a partial clone otherwise fetches missing objects ([git](https://git-scm.com/docs/git), [git-status](https://git-scm.com/docs/git-status#_background_refresh)).
- Read the remote without fetching.
- Never read a credential. Mask any credential-bearing value inside the command, before its output reaches you.
- Write large outputs to files in a scratch folder outside the repository, and read them in pieces. Collect everything; never sample.
- Record every audit domain in the coverage ledger with one status: `checked`; `BLOCKED`, with the call that failed; or `not reachable`, with the reason. A domain whose call failed is never reported as empty.

Run the phases in order. For each phase:

1. Read its reference when you start the phase.
2. Collect every section of the reference.
3. Check the result against the reference's "Done when" list.
4. If an item fails, collect it again or record it in the coverage ledger, then check again.
5. Only move to the next phase when every item passes.

The phases:

0. **Intake and preflight:** identify the repository, its format, the tools and the GitHub identity, and get consent for scans outside the repository. Read [phase-0-intake-and-preflight.md](references/phase-0-intake-and-preflight.md) before anything else.
1. **Local state:** inventory HEAD, the working tree, nested content, symlinks, worktrees, stashes, branches, tags and other refs. Read [phase-1-local-state.md](references/phase-1-local-state.md) when Phase 0 passes.
2. **Local versus remote:** compare every branch and tag with the live remote by full object ID, and find each branch's integration state. Read [phase-2-local-versus-remote.md](references/phase-2-local-versus-remote.md) when Phase 1 passes.
3. **History and object store:** audit the whole history, authors, object store health, weight, secrets ever committed and lost work. Read [phase-3-history-and-object-store.md](references/phase-3-history-and-object-store.md) when Phase 2 passes.
4. **Git-native residue:** find hooks, risky configuration, leftovers of interrupted operations, stray files and processes serving the repository. Read [phase-4-git-residue.md](references/phase-4-git-residue.md) when Phase 3 passes.
5. **GitHub state:** audit pull requests, issues, branches and rules, Actions, Dependabot, security alerts, integrations, access, distribution and forks. Read [phase-5-github-state.md](references/phase-5-github-state.md) when Phase 4 passes.
6. **External links:** find everything outside the repository that still points to it, on GitHub, on other hosts and on this machine. Read [phase-6-external-links.md](references/phase-6-external-links.md) when Phase 5 passes.

### 2. Planning

### 3. Debug execution
