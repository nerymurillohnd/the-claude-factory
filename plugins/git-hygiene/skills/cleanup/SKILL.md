---
name: cleanup
description: Audits a Git repository end to end, plans the cleanup with the user, and executes only what the user approves, keeping every piece of valuable work safe. Runs only when the user types /git-hygiene:cleanup.
argument-hint: "[absolute path to the repository, or a problem to investigate]"
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash|Read|Grep|Write|Edit|NotebookEdit|mcp__.*"
      hooks:
        - type: command
          command: "\"${CLAUDE_PLUGIN_ROOT}/hooks/guard.py\""
          timeout: 15
          onFailure: block
---

# Git cleanup

Leave the repository as clean as safely possible, ideally with only `main` and `origin/main`, without losing any valuable work. The user decides every consequential step: nothing is deleted, integrated or pushed before they approve the plan.

Arguments: `$ARGUMENTS`. If it is an existing directory, that is the target repository; otherwise the target is the current directory and the text is a specific problem to investigate (read `references/debugging.md` for it). Run every Git command as `git -C "<absolute repo path>" …`; the shell does not expand `~` inside quotes.

## Rules that hold in every phase

- Work in this order and never skip ahead: Audit → Plan → Approval → Backup → Execute → Verify → Remove the backup. The audit is read-only; the backup is made only after approval; the backup is removed only after the user explicitly says so, and its removal is verified.
- A guard hook is active for the rest of the session. It refuses force-pushes, deleting `main` on the remote, history rewriting, `git clean -x`, default-branch changes and anything that prints credentials or reads secret files, and it makes the user confirm every command, file write or MCP action that changes state or prints file contents. Never work around a denial; stop and tell the user. Approving a confirmation prompt is not approval of the plan.
- Evidence beats assumption. Mark what cannot be verified `BLOCKED`, keep that item untouched, and say exactly what stopped you. Never call something safe because it looks merged.
- Never rewrite published history, never force-push, never change the remote default branch.
- Secrets: never open or print secret-bearing files (`.env`, keys, tokens, credentials); report their names only. Committed secrets can hide in diffs, so audit with `--stat`, `--name-status` and `--name-only`, and when you need content exclude secret-like paths with `':(exclude)<path>'` pathspecs. Redact credentials in every command and report.
- Never go beyond the approved scope: a changed or additional operation needs new approval. Approval is an explicit answer that names the plan or the action IDs, and every approval includes A-01, the backup: if A-01 is not approved, no integration, deletion or prune runs. An empty, timed-out, auto-closed or ambiguous answer is not approval: ask again.
- Keep the approved plan on disk (Phase 3 step 1). After a context compaction, re-read it and these rules; if this skill's guidance is gone, ask the user to type `/git-hygiene:cleanup` again.

## Phases

- [ ] Phase 1: Audit and diagnosis (read-only)
- [ ] Phase 2: Findings, plan and approval
- [ ] Phase 3: Execution and final verification

### Phase 1: Audit and diagnosis

Read `references/phase-1-audit.md` now and follow it. It is strictly read-only: no fetch, no write of any kind. Its first step proves the guard is active; if the probe is not refused, stop. Then run the inventory, which gathers the facts in one pass (give the Bash call a long timeout, or run it in the background):

```bash
"${CLAUDE_SKILL_DIR}/scripts/inventory.py" --repo "<repo>" --out "<scratch dir outside the repo>/inventory.json"
```

It prints a summary; read a section with `--from <file> --section <name>` and page branches with `--signal` and `--limit`. Then investigate everything it flags, in depth. The repository may have thousands of commits, branches and pull requests: use targeted, aggregated, machine-readable commands, never an unbounded history dump.

### Phase 2: Findings, plan and approval

Read `references/phase-2-plan.md` and follow it. Present the evidence, ask the user about every ambiguous finding with your recommendation, then present the complete plan with one action ID per operation, a mandatory backup first, and ask for explicit approval. The user may approve the whole plan or specific IDs.

### Phase 3: Execution and final verification

Read `references/phase-3-execute.md` and follow it. Save the approved plan, revalidate the state, create and verify the backup outside the repository, run only the approved actions in dependency order, verify each one, then verify the final state. Say which action ID each command belongs to before you run it.

## Debugging

Only when the user brought a specific problem (a regression, where a line came from) or an audit finding needs it, read `references/debugging.md`. Debugging never authorizes source changes or history rewrites.

## Example

User: `/git-hygiene:cleanup /Users/ada/code/shop`
Claude, after Phase 1: "42 local and 118 remote branches. 31 are fully merged, 6 hold unmerged work (listed with evidence), 1 worktree points to a folder that no longer exists, 3 stashes. Three questions before I draft the plan…" then, after the answers, the plan: "A-01 backup … A-07 merge `feat/x` into `main` … A-08 push `main` … A-12 delete local `feat/old` …" and "Approve the whole plan, or tell me which IDs."
