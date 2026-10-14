---
name: cleanup
description: Audits a Git repository end to end, plans the cleanup with the user, and executes only what the user approves, keeping every piece of valuable work safe. Runs only when the user types /git-hygiene:cleanup.
argument-hint: "[absolute path to the repository, optionally followed by a problem to investigate]"
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

Leave the repository as clean as safely possible, ideally with only `main` and `origin/main` (the base branch and its published copy), without losing any valuable work. The user decides every consequential step: nothing is integrated, pushed, deleted or pruned before they approve the plan.

## Target and vocabulary

Arguments: `$ARGUMENTS`.

- If the first word is an existing directory, that is the repository and any text after it is a problem to investigate. Otherwise the repository is the current directory (get its absolute path with `pwd`) and the text, if any, is the problem. If the text looks like a path that does not exist, ask the user.
- Use absolute paths: the shell does not expand `~` inside quotes. Run every Git command as `git -C "<repo>" …` and every `gh` command with `-R <owner>/<repo>`.
- If the inventory answers `error: not a Git repository`, stop and tell the user.
- **Scratch folder**: a folder you create once outside the repository (`mktemp -d "${TMPDIR:-/tmp}/git-hygiene-XXXXXX"`). Phase 1 writes only here: `inventory.json`, `audit-log.md` (every command and its relevant result), `findings.md` and `plan-draft.md`. Tell the user its path.
- **Backup folder**: chosen by the user in Phase 2, outside the repository. Holds the backup, `plan.md` and the revalidation inventory. Tell the user its path.
- **Base branch**: the local branch the others are compared with, `main` unless the remote's default branch is another one. **Base ref**: its published copy, `<remote>/<base branch>`, for example `origin/main`. The inventory's `branches.base` is the base ref.
- **Action IDs and classes** (`A-01`, `prep`, `integrate`, `publish`, `local-delete`, `remote-delete`, `files`) are defined in `${CLAUDE_SKILL_DIR}/references/phase-2-plan.md`. **A-01 is always the backup.**

## Rules that hold in every phase

- Work in this order and never skip ahead: Audit → Plan → Approval → Backup → Execute → Verify → ask whether to remove the backup. The audit changes nothing in the repository; the backup is made only after approval; the backup is removed only after the user explicitly says so, and its removal is verified.
- A guard hook is active for the rest of the session. It refuses force-pushes, deleting `main` on the remote, the history-rewriting tools `filter-branch`, `filter-repo` and `bfg`, `git clean -x`, default-branch changes and anything that prints credentials or reads secret files. It makes the user confirm every other command, file write or MCP action that changes state, and every git command that prints file contents (except stat listings and commands with an `:(exclude)` pathspec). `rebase`, `reset` and `commit --amend` are confirmed, not refused: use them only as the plan says. Never work around a denial; stop and tell the user. The only refusal you expect is the Phase 1 probe.
- Approving a confirmation prompt is not approving the plan, and approving the plan is not approving a prompt: the user gives both.
- Evidence beats assumption. Mark what cannot be verified `BLOCKED`, keep that item untouched, and say exactly what stopped you. Never call something safe because it looks merged.
- Never rewrite published history, never force-push, never change the remote default branch.
- Secrets: never open or print secret-bearing files (`.env`, keys, tokens, credentials); report their names only. Committed secrets can hide in diffs, so audit with `--stat`, `--name-status` and `--name-only`, and when you need content exclude secret-like paths (Phase 1 §3). Redact credentials in every command and report.
- Never go beyond the approved scope: a changed or additional operation needs new approval.
- Approval is an explicit answer that names the whole plan or the action IDs. A-01 is added to every approval (tell the user it was added), and nothing else runs until A-01 has run and verified. An empty, timed-out, auto-closed or ambiguous answer is not approval: ask again. An explicit refusal, or "audit only", is an answer: stop and deliver the findings and the plan.
- Keep state on disk so a context compaction cannot lose it: the scratch folder in Phase 1 and 2, the backup folder's `plan.md` from Phase 3. After a compaction re-read those files and this skill's rules; if you cannot find them, ask the user for the folder paths or to type `/git-hygiene:cleanup` again. If the user gives you a backup folder that contains `plan.md`, resume at Phase 3 step 2.

## Phases

### Phase 1: Audit and diagnosis

Read `${CLAUDE_SKILL_DIR}/references/phase-1-audit.md` now and follow it. It is strictly read-only: no fetch, no change to the repository; the only files written are in the scratch folder. Its first step proves the guard is active; if the probe is not refused, stop. Then ask once whether read-only network queries (`git ls-remote`, `gh`) are acceptable, and run the inventory, which gathers the facts in one pass (give the Bash call a long timeout, or run it in the background):

```bash
"${CLAUDE_SKILL_DIR}/scripts/inventory.py" --repo "<repo>" --out "<scratch>/inventory.json" --ls-remote
```

Leave out `--ls-remote` if the user declined the network. It prints a summary; read a section with `--from <file> --section <name>`, and read branches in pages with `--signal`, `--limit` and `--offset`. Then investigate everything it flags, in depth. The repository may have thousands of commits, branches and pull requests: use targeted, aggregated, machine-readable commands, never an unbounded history dump.

### Phase 2: Findings, plan and approval

Read `${CLAUDE_SKILL_DIR}/references/phase-2-plan.md` and follow it. Present the evidence, ask the user about every ambiguous finding with your recommendation, then present the complete plan with one action ID per operation, the backup first, and ask for explicit approval. The user may approve the whole plan, specific IDs, or nothing.

### Phase 3: Execution and final verification

Read `${CLAUDE_SKILL_DIR}/references/phase-3-execute.md` and follow it. Save the approved plan, revalidate the state, create and verify the backup outside the repository, run only the approved actions in the plan's order, verify each one, then verify the final state. Say which action ID each command belongs to before you run it, so the user can match it to the confirmation prompt.

## Debugging

Only when the user brought a specific problem (a regression, where a line came from) or an audit finding needs it, read `${CLAUDE_SKILL_DIR}/references/debugging.md`. Debugging never authorizes source changes or history rewrites.

## Example

User: `/git-hygiene:cleanup /Users/ada/code/shop`
Claude, after Phase 1: "42 local and 118 remote branches. 31 are fully merged, 6 hold unmerged work (listed with evidence), 1 worktree points to a folder that no longer exists, 3 stashes. Three questions before I draft the plan…" then, after the answers, the plan: "A-01 backup … A-02 merge `feat/x` into `main` … A-03 publish `main` … A-04 delete local `feat/x` … A-09 delete `origin/feat/old`" and, as the approval question: "Approve the whole plan, approve only some IDs, or stop here with the audit only?"
