---
name: cleanup-and-debug
description:
---

## Workflow

### 1. Audit

Read-only: nothing changes in the repository, on GitHub or on the machine. Run the phases in order, and read each phase's reference only when you reach it.

0. **Intake and preflight:** identify the repository, its format, the tools and the GitHub identity, and get consent for scans outside the repository. See [phase-0-intake-and-preflight.md](references/phase-0-intake-and-preflight.md).
1. **Local state:** inventory HEAD, the working tree, nested content, symlinks, worktrees, stashes, branches, tags and other refs. See [phase-1-local-state.md](references/phase-1-local-state.md).
2. **Local versus remote:** compare every branch and tag with the live remote, by full SHA, and find each branch's integration state. See [phase-2-local-versus-remote.md](references/phase-2-local-versus-remote.md).
3. **History and object store:** audit the whole history, authors, object store health, weight, secrets ever committed, and lost work. See [phase-3-history-and-object-store.md](references/phase-3-history-and-object-store.md).
4. **Git-native residue:** find hooks, risky configuration, leftovers of interrupted operations, stray files, and processes serving the repository. See [phase-4-git-residue.md](references/phase-4-git-residue.md).
5. **GitHub state:** audit pull requests, issues, branches and rules, Actions, Dependabot, security alerts, integrations, access, distribution and forks. See [phase-5-github-state.md](references/phase-5-github-state.md).
6. **External links:** find everything outside the repository that still points to it, on GitHub, on other hosts and on this machine. See [phase-6-external-links.md](references/phase-6-external-links.md).

### 2. Planning

### 3. Debug execution
