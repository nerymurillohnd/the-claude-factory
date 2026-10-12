---
name: write-handoff
description: Writes this project's end-of-session handoff, the file the next session starts from with what was done, decided, corrected, learned and left open. Use when the user is wrapping up a work session, says they are stopping for now, or asks for a handoff, session summary or notes for the next session.
---

# Write handoff

Write the next session's only account of this one. The next session reads it in full at its start and reports what is still open, so every line must be true, checked and understandable without this conversation. Durable conventions belong in `CLAUDE.md`, rules and memories, not here.

**Leave the working tree as the session left it: the handoff describes that state.** Run only commands that change neither the working tree nor the index: the ones below (`git fetch` updates only remote-tracking refs). Files change only in step 2, if the user accepts committing, pushing or a PR, and in step 5, the handoff itself.

**Never invent commits, results, dates or decisions**: anything not checked against git, a command or the user is marked `unverified`. **Never write a secret**, even one that appeared in the session.

**Run every command below verbatim against the project directory `${CLAUDE_PROJECT_DIR}`**, never the shell's current directory: the session may have moved with `cd`, and the start-of-session hook reads handoffs from this project's `.claude/session-handoff/` only. If that path is not an absolute path, this session has no project folder the skill can reach (a chat conversation): stop, and tell the user to write the handoff in Claude Code or in a Cowork session on their computer.

- [ ] Step 1: Inspect
- [ ] Step 2: Offer to settle the work
- [ ] Step 3: Reconcile the previous handoff
- [ ] Step 4: Draft and review with the user
- [ ] Step 5: Save
- [ ] Step 6: Confirm

## Step 1: Inspect

1. STORE is `${CLAUDE_PROJECT_DIR}/.claude/session-handoff`, and `Project:` is `${CLAUDE_PROJECT_DIR}`. List STORE with `ls "${CLAUDE_PROJECT_DIR}/.claude/session-handoff"`: the previous handoff is the last name of the form `YYYY-MM-DD-HHMM.md`, since those names sort by date. `No such file or directory`, or no name of that form → `No previous handoff.` Any other failure, such as a denial: stop and tell the user, because a guessed `No previous handoff.` would drop every open item. Read the previous handoff whole now with Read: step 1.5 needs its `HEAD:` line and step 3 its Open items.

   Today's date for the Stale rule: `date -u +%Y-%m-%d`.
2. `git -C "${CLAUDE_PROJECT_DIR}" rev-parse --is-inside-work-tree` fails → `Branch:` and `HEAD:` are `Not a git repository.`, Repository state is the single line `Not a git repository.`, and the rest of this step is skipped.
3. If `git -C "${CLAUDE_PROJECT_DIR}" remote` lists a remote, run `git -C "${CLAUDE_PROJECT_DIR}" fetch --quiet`: it prints nothing when it works, and the tool result shows an error when it fails.
4. Record:
   - `git -C "${CLAUDE_PROJECT_DIR}" status --short --branch` and `git -C "${CLAUDE_PROJECT_DIR}" stash list`.
   - The branch: `git -C "${CLAUDE_PROJECT_DIR}" branch --show-current`; empty → `detached at <short hash>`. HEAD: `git -C "${CLAUDE_PROJECT_DIR}" rev-parse HEAD`; it fails with no commits → `none`.
   - The upstream: `git -C "${CLAUDE_PROJECT_DIR}" rev-parse --abbrev-ref --symbolic-full-name '@{u}'` prints `<remote>/<branch>`; `<remote>` is the text before the first `/`. It fails → no upstream, and `<remote>` is `origin`.
   - Unpushed and behind, in this order: no upstream → both are `no upstream`; the fetch failed → both are `unverified (fetch failed)`; otherwise `git -C "${CLAUDE_PROJECT_DIR}" rev-list --left-right --count 'HEAD...@{u}'` prints `<unpushed> <behind>`, and `git -C "${CLAUDE_PROJECT_DIR}" log --oneline '@{u}..HEAD'` lists the unpushed hashes.
   - The default branch: `git -C "${CLAUDE_PROJECT_DIR}" rev-parse --symbolic-full-name '<remote>/HEAD'` prints `refs/remotes/<remote>/<branch>`, and the default branch is `<branch>`. If it fails, `git -C "${CLAUDE_PROJECT_DIR}" branch --list main master`: both or only `main` → `main`, only `master` → `master`, neither → `unknown`.
   - Branch vs default: `on default` when the branch equals the default branch, `on another branch` when it differs, `detached` when HEAD is detached, `unknown` when the default branch is `unknown`.
5. Commits since the previous handoff's `HEAD:`:
   - HEAD is `none` → `none (no commits)`.
   - The previous `HEAD:` is a commit hash and `git -C "${CLAUDE_PROJECT_DIR}" merge-base --is-ancestor <previous HEAD> HEAD` passes → `git -C "${CLAUDE_PROJECT_DIR}" log --oneline <previous HEAD>..HEAD`, or `none (no new commits)` when it prints nothing.
   - Otherwise `git -C "${CLAUDE_PROJECT_DIR}" log --oneline -20`, with the reason: no previous handoff, its HEAD is `none` or `Not a git repository.`, or that commit is not an ancestor of HEAD.
6. PRs: `(cd "${CLAUDE_PROJECT_DIR}" && gh pr list --state all --limit 20)`, in a subshell so the session's working directory does not move; every row it prints goes in with its state, and no rows → `none`. If gh fails: `not checked (gh failed)`.

## Step 2: Offer to settle the work

If step 1 found uncommitted changes, stashes, unpushed commits, or a branch with no upstream while the repository has a remote (its commits are on no remote), list them and ask whether to commit, push or open a PR first. Do only what the user accepts, with git and gh and following the user's and the project's git rules, then repeat step 1. Anything declined goes into the handoff.

## Step 3: Reconcile the previous handoff

Give each Open item of the previous handoff one verdict:

- `done`: finished; cite a commit, PR or test run.
- `partial`: advanced this session but not finished; say what was done and what is missing.
- `open`: no progress this session.
- `dropped`: no longer wanted; only the user drops an item, and their reason is recorded. An item that looks obsolete stays `open`; name it when you show the draft in step 4 so the user can drop it.

**The Reconciliation table has one row per `done`, `partial` and `dropped` item, and that row gives what the verdict above asks for; every `open` item is counted in one line under it, `Still open, unchanged: <n> (see Open items)`.** Carry every `partial` and `open` item into Open items with its original date. Where the previous handoff contradicts the repository, the repository wins: record the conflict.

## Step 4: Draft and review with the user

Fill [the template](references/handoff-template.md), keeping its headings, labels and fixed lines literal and in order. Check the draft against the Quality bar, then show it complete and apply the user's changes until they approve.

## Step 5: Save

1. Take the time once, at save: `date -u +%Y-%m-%d-%H%M` gives the name, and the same time goes in `Written:`.
2. Read `STORE/<name>.md`: if it exists, add one minute until Read finds no file, and update `Written:` to match. Never overwrite or delete an earlier handoff.
3. Write `STORE/<name>.md` with the **Write tool** (see Gotchas), which also creates STORE. If the write fails, show the error and stop.

## Step 6: Confirm

Report the saved path, the number of open items, the first next step, and that the session can end.

## Quality bar

The next session has only this file and the repository:

- **Standalone:** a commit hash or PR number goes next to what it did; internal IDs and abbreviations are spelled out.
- **Done** says what changed, how, and its evidence.
- **Decisions** carry their reason, and the rejected alternative when there was one.
- **Corrections** state the behaviour to follow from now on.
- **Learnings** are non-obvious facts with their source.
- **Open items** say where the work stands and what finishing needs, enough to start without asking.
- **Next steps** are ordered, one line each: `1. <Open item> — <first action>`. Every next step is also an Open item.
- **Nothing silently dropped:** every thread the session touched ends in Done, Open items or Unverified and gaps. Never merge or drop an item to shorten the file, and never invent one.
- **Stale:** an open item opened more than 30 days before today's date from step 1 carries exactly one `Stale: confirm or drop.`, right after its date: `- [2026-08-01] Stale: confirm or drop. <item>: …`. An item carried with the prefix keeps it once; never add a second.

## Gotchas

- **The project's `.claude/` is protected**: a Bash write there goes to the auto-mode classifier or a prompt, and allow rules can't pre-approve it. The Write tool shows the user what is saved and asks through Claude Code's permission prompt.
- **Headless `claude -p` in default mode can't save**: no one answers the permission prompt. Run the skill in an interactive session.
