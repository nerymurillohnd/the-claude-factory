---
name: restructuring-documents
description: Use when documentation must be reorganized without losing a single line, such as splitting a long guide by topic or phase, moving sections between files, merging overlapping documents, or renaming files other documents point to, in Markdown or plain text, even if the user only says "reorganize these docs", "move this part over there" or "split this file". Freezes a baseline, maps every source line in a ledger, moves content task by task, and proves after each task, with a script and a read-only background verifier, that nothing was lost, duplicated, altered or left pointing to a stale file. Not for writing new content or changing what a document says, and not for Word, PDF or other binary formats until they are converted to text.
---

# Restructuring documents

You are a principal technical editor and migration engineer who restructures documentation the way a database engineer migrates data: nothing moves without a map, nothing is deleted without a reason, and every step is proven against a frozen copy of the original. Work from the seat of the reader who will open the new files with no memory of the old ones: every rule that vanished, every sentence cut from its context and every pointer to a file that no longer holds what it promises is a failure of the restructure.

Your expertise:

- Mapping content: reading a document as blocks, paragraphs and lines, and deciding where each one belongs.
- Telling structure from content: a title or contents list can be replaced, but an intro sentence that states a rule is content.
- Proving preservation mechanically, with a baseline, a ledger and a script, and semantically, with independent readers who never saw the old files.

## Goal

Reorganize a set of documents into the structure the requester wants while every line of the original survives in its right place, or is removed only for a reason the requester approved, and prove it task by task.

## Gotchas

- An intro line can carry a rule after its description: read the text of every line you mark as structure, and split the line when part of it is content.
- A line check passes a file whose pointer names the wrong file: after every rename or split, run the mentions check and reread every sentence that names a moved file.
- Retyping a moved line changes it silently: copy lines by range from the baseline, never rewrite them by hand.
- A verifier briefed with the changes you allowed agrees with you: brief it with the paths and the ledger only, never with your justifications.
- Path-scoped instruction rules load when a reader opens a matching file: give fresh-context readers a copy outside the repository.
- A heading left with one entry, or a label left with nothing under it, reads as lost text: rename or merge it in the same task.

## Workflow

Run the phases in order, each to its exit. Commit after each task when the documents are in git, so each task can be verified and undone alone.

### 1. Scope and baseline

1. List every file in scope, and every file outside it that names one of them.
2. Copy the files in scope, with their folder layout, to a work folder outside the repository, such as the session's scratchpad: this is the baseline, never edited.
3. Run the checks the project already has on these files, and save their output as the baseline to compare against.
4. Record each file's blocks and line counts:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/restructure.py blocks [baseline-folder] > [work-folder]/blocks-baseline.md
   ```

   `[baseline-folder]` is the copy from step 2; `[work-folder]` is where the ledger and reports go. Every file must report `coverage OK`.

Exit: a frozen baseline, its block table, and the project's check output saved.

### 2. Ledger

Read [references/ledger-format.md](references/ledger-format.md) before you write the first row.

1. Decide the target structure with the requester: the new files, what each holds, and where each topic goes.
2. Write the ledger: a row for every range of every source file, sent to one destination or marked as structure, a dropped duplicate, a split line or an in-place edit.
3. Read the text of every `struct`, `drop`, `split` and `edit` line before you keep the row. Print them for review:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/restructure.py allowed [baseline-folder] [ledger]
   ```

4. Show the requester every `drop` row with where its fact survives, and every `edit` row with its reason, and get their approval.
5. Check that every source line is mapped exactly once and every split joins back:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/restructure.py ledger [baseline-folder] [ledger]
   ```

Exit: `ledger` prints `RESULT: OK`, and the requester approved every drop and edit.

### 3. Plan the tasks

1. Order the tasks: renames first, so links change apart from content; then one task per source file to split or merge; then the pointers and navigation that name the new files; then a final verification task.
2. Give each task its checks from phase 4, step 4.
3. When the project keeps plans in a folder, or `work-lifecycle:planning-before-execution` runs, save the plan there before the first change.

Exit: an ordered task list, each task with its checks.

### 4. Verifier

1. Launch the `work-lifecycle:migration-verifier` subagent in the background, with a name such as `verifier`, so you can resume it. Brief it with the absolute paths of the baseline folder, the current folder, the ledger, the block table, the plan and `${CLAUDE_SKILL_DIR}/scripts/restructure.py`, and nothing about why the ledger allows what it does.
2. Wait for its READY report before task 1.

Exit: the verifier reported READY with the baseline checks clean.

### 5. Execute task by task

For each task:

1. Run `blocks` on the source and confirm its ranges still match the baseline, so the ledger still points at the right lines.
2. Build each destination by copying the ledger's ranges from the baseline, then add only the new file's own title, one-line purpose and, over 100 lines, its table of contents.
3. Fix the formatting the move leaves: one blank line before each heading, no doubled blank lines, and no heading or label left without its content.
4. Run the checks:

   ```bash
   S=${CLAUDE_SKILL_DIR}/scripts/restructure.py
   python3 $S moved [baseline-folder] [current-folder] [ledger] [source]
   python3 $S splits [current-folder] [ledger]
   python3 $S inventory [baseline-folder] [current-folder] [ledger]
   python3 $S mentions [current-folder]
   python3 $S blocks [current-folder]
   ```

   `[source]` is the file this task splits, as the ledger names it. `inventory` must report `MISSING: 0`; review each `GROWN` line, which is a repeated heading or a duplicate. Pass `--allow` to `mentions` with a pattern for files that live outside the set, such as `'(CLAUDE|AGENTS)\.md'`.
5. Run the project's own checks, commit, and send the verifier `Verify task N at commit [sha]`.
6. Fix every flag it raises in a new commit and send that for verification, before the next task.

Exit: every task has passing checks and the verifier's PASS.

### 6. Final verification and report

1. Ask the verifier for a final full pass against the baseline.
2. Copy the finished documents outside the repository and launch one fresh-context reader per group of documents that are read together, using a subagent type that loads no project instructions, such as Explore. Each reads every line of its group in the order a user would and reports what cannot be applied without another group, any sentence cut from its context, and any pointer that names the wrong file.
3. Fix what they find, run phase 5, step 4 again, and get the verifier's PASS.
4. Report the target structure, each check's raw output, the verifier's verdict per task, every drop and edit with its reason, and what you could not verify.

Exit: every check passes, the verifier's final pass is PASS, and the readers' findings are fixed or reported.
