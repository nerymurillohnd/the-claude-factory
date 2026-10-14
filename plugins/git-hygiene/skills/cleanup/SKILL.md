---
name: cleanup
description: Audits a Git repository end to end, plans the cleanup with the user, and executes only what the user approves, keeping every piece of valuable work safe. Runs only when the user types /git-hygiene:cleanup.
argument-hint: "[path to the repository, default: current directory]"
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash|Read"
      hooks:
        - type: command
          command: "\"${CLAUDE_PLUGIN_ROOT}/hooks/guard.py\""
          timeout: 15
---

# Git cleanup

Leave the repository as clean as safely possible, ideally with only `main` and `origin/main`, without losing any valuable work. The user decides every consequential step: nothing is deleted, integrated or pushed before they approve the plan.

Target repository: `$ARGUMENTS`, or the current directory when empty. Run every Git command as `git -C "<repo>" …`.

## Rules that hold in every phase

- Work in order: Audit → Plan and approval → Execute and verify. Never skip ahead.
- A guard hook is active for the rest of the session. It refuses force-pushes, deleting `main` on the remote, history rewriting, default-branch changes and anything that prints credentials or reads secret files, and it makes the user confirm every command that changes state. Never work around a denial; stop and tell the user. Approving a confirmation prompt is not approval of the plan.
- Evidence beats assumption. Mark what cannot be verified `BLOCKED`, keep that item untouched, and say exactly what stopped you. Never call something safe because it looks merged.
- Never rewrite published history, never force-push, never change the remote default branch.
- Never open or print secret-bearing files (`.env`, keys, tokens, credentials). Report their names only, and redact credentials in every command and report.
- Never go beyond the approved scope: a changed or additional operation needs new approval.
- After a context compaction, invoke `/git-hygiene:cleanup` again so these rules and the guard are back in context.

## Phases

- [ ] Phase 1: Audit and diagnosis (read-only)
- [ ] Phase 2: Findings, plan and approval
- [ ] Phase 3: Execution and final verification

### Phase 1: Audit and diagnosis

Read `references/phase-1-audit.md` now and follow it. It is non-destructive: nothing that updates repository state runs without the user's go-ahead, and a fetch counts as an update. Start with the inventory script, which gathers the facts in one pass:

```bash
"${CLAUDE_SKILL_DIR}/scripts/inventory.py" --repo "<repo>" --out "<scratch dir outside the repo>/inventory.json"
```

It prints a summary; read a section with `--from <file> --section <name>`. Then investigate everything it flags, in depth. The repository may have thousands of commits, branches and pull requests: use targeted, aggregated, machine-readable commands, never an unbounded history dump.

### Phase 2: Findings, plan and approval

Read `references/phase-2-plan.md` and follow it. Present the evidence, ask the user about every ambiguous finding with your recommendation, then present the complete plan with one action ID per operation, a mandatory backup first, and ask for explicit approval. The user may approve the whole plan or specific IDs.

### Phase 3: Execution and final verification

Read `references/phase-3-execute.md` and follow it. Revalidate the state, create and verify the backup outside the repository, run only the approved actions in dependency order, verify each one, then verify the final state. Say which action ID each command belongs to before you run it.

## Debugging

Only when the user brought a specific problem (a regression, where a line came from) or an audit finding needs it, read `references/debugging.md`. Debugging never authorizes source changes or history rewrites.

## Example

User: `/git-hygiene:cleanup`
Claude, after Phase 1: "42 local and 118 remote branches. 31 are fully merged, 6 hold unmerged work (listed with evidence), 1 worktree points to a folder that no longer exists, 3 stashes. Three questions before I draft the plan…" then, after the answers, the plan: "A-01 backup … A-07 merge `feat/x` into `main` … A-12 delete local `feat/old` …" and "Approve the whole plan, or tell me which IDs."
