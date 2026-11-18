# Plan: restructure authoring-skills' references by phase and topic

## Context

The owner found that several references of `plugins/skills-engineering/skills/authoring-skills/` serve more than one phase, and that SKILL.md never states the order in which to read them. The clearest case is `scripts-and-hooks.md`: it is read in phase 3, but its first section decides whether a script is needed, a phase-2 architecture decision. A model can then apply a rule late, partially or in the wrong step.

Sources checked on 2026-11-18:
- agentskills.io specification: subfolders are allowed, and "Keep individual reference files focused".
- Platform best practices: "Organize for discovery … by domain or feature", "Name files descriptively", and "Observe how Claude navigates Skills" (unexpected reading order and missed connections).
- agentskills.io best practices: "telling the agent *when* to load each file".

No official source sets a reading order or recommends phase subfolders; the order has to be written in SKILL.md. The owner chose option A: keep `references/` flat, put the phase prefix on every file, give each file one phase and one topic, and state the reading order in SKILL.md.

Intended outcome: every reference belongs to exactly one phase and one topic. SKILL.md lists each file under its phase, in the order of the steps that use it. No sentence of the current content is lost; the only removals are the duplicates listed below, each shown before it is removed.

## Organizing principle

- **Phase 2 decides what and where:** placement, consumers, whether a script or hook is needed and where it lives, dependencies and state.
- **Phase 3 specifies:** frontmatter values, the description text, which task mechanisms to use, the body/file split and the plan.
- **Phase 4 writes:** the text, the scripts, the hook configuration and the mechanisms, following the plan.

## Target layout (references/, flat)

| File | Phase | Built from |
| :-- | :-- | :-- |
| phase-1-intent.md | 1 | unchanged |
| phase-2-environment-and-architecture.md | 2 | unchanged steps; steps 5 and 6 name the phase-2 references |
| phase-2-placements.md | 2 | decision parts of special-placements.md |
| phase-2-scripts-and-hooks.md | 2 | "Script or instructions" criterion, "Where the script lives", whether a skill hook fits and where a subagent's checks go, whether to inject a command |
| phase-2-components.md | 2 | MCP fallback choice, other skills that must be model-invocable and optional, where config and state live |
| phase-3-design-and-plan.md | 3 | unchanged, except step 10 (register) moves to phase 4 |
| phase-3-descriptions.md | 3 | "Descriptions" section of writing-patterns.md |
| phase-3-frontmatter.md | 3 | frontmatter.md (rename) |
| phase-3-task-mechanisms.md | 3 | "Name the task's parts" and each mechanism's use-when and skip-when, the validator choice, the task-tools note, the template strictness choice |
| phase-4-build.md | 4 | adds the order in which the phase-4 references apply |
| phase-4-writing-patterns.md | 4 | Pointers, Register, Instructions, Examples and snippets, Anti-patterns |
| phase-4-task-mechanisms.md | 4 | how to build each mechanism: steps and controls, checklist items, loop exits, plan file, template wording, gotchas |
| phase-4-scripts-and-hooks.md | 4 | run or read, script listing, how the body reaches a script, how it starts, interface, dependencies, injected-command rules and examples, hook configuration, paths, `once` |
| phase-4-components.md | 4 | naming tools and skills, stating dependencies, teaching across tools, coexisting, the config procedure, the log, least surprise |
| phase-4-placements.md | 4 | writing rules per placement: upload body and scripts, subagent bodies, the default instead of asking, the users-only body, the upload archive layout |
| phase-5-self-review.md, phase-6-deliver.md, phase-7-audit-and-evals.md | 5–7 | names of referenced files updated only |

**Duplicates to drop, each shown with evidence in the task that touches it:**
1. special-placements "Frontmatter: only name, description…" duplicates frontmatter.md "Fields only Claude Code accepts". The fact stays in phase-3-frontmatter.md.
2. special-placements "Write the description for the person choosing it from the menu" duplicates writing-patterns "A skill with `disable-model-invocation: true` is read by the user…". The fact stays in phase-3-descriptions.md.

## Tasks

Progress: each task is ticked here when its commit lands.

Each task ends with a signed commit and no push. Each task's verification, and the background verifier's report on that task, must pass before the next task starts.

- [x] -1. **Save the plan first.** Copy this plan to `.claude/maintainer/plans/2026-11-18-authoring-skills-reference-restructure.md`, as `.claude/rules/architecture/claude-dir.md` requires for plans, and commit it alone. Then tick each task in that file as its commit lands.
- [x] 0. **Baseline and block inventory.**
   - Record HEAD.
   - Copy the skill to the scratchpad as the baseline.
   - Write `scratchpad/inventory.py`. It extracts every non-empty content line of the 13 references and SKILL.md, normalized for whitespace and list markers, and reports each baseline line that is missing from a given folder.
   - Write `scratchpad/blocks.py`. For every file it gives the total line count and every block with its exact line range and line count: each `##` section and each `###` subsection, plus the intro before the first heading. Fenced code blocks are tracked as part of their section and never split. Save the baseline block table as `scratchpad/blocks-baseline.md`.
   - Save the raw output of biome, `lint:frontmatter`, `claude plugin validate` and `npm run lint:skills` on the baseline.
   - Verify: the inventory runs against the baseline itself and reports 0 missing, and the block ranges of each file add up to its total line count.
- [x] 0b. **Background verifier.** Before task 1, launch one background subagent (general-purpose, Sonnet, read-only by instruction: never edits, writes or commits). Its brief: the baseline folder, `blocks-baseline.md`, `mapping.md` once it exists, the list of approved duplicates, and the two scripts.
    - After each task's commit, I send it the task number and the commit. It reads the changed files in full, runs both scripts against the baseline, and checks every moved block against the ledger: the same lines, in the destination the ledger names, nothing dropped, nothing duplicated, nothing altered except the link and mention lines the task allows.
    - It reports PASS or a list of FLAGS, each with file, line and the baseline text.
    - I fix every flag and send the fix back for re-verification before the next task starts. Its reports are shown to the owner at the end.
- [x] 1. **Mapping ledger.**
   - Write `scratchpad/mapping.md` from the block table. For each file being split, list every block (section or subsection, with its baseline line range and line count) and, inside a block that splits, every paragraph or bullet. Map each to its destination file and the phase step that uses it.
   - Verify: a script checks that every baseline line of the five files being split appears exactly once in the ledger, and that each destination's planned line count equals the sum of the blocks mapped to it.
   - **Re-validation in every later task:** before a move, re-run `blocks.py` on the source and confirm the ranges still match the ledger. After the move, confirm that each destination holds the planned lines and that the source's remaining lines equal its total minus the moved ones.
- [x] 2. **Renames only.**
   - `git mv` for: `frontmatter.md` → `phase-3-frontmatter.md`, and `writing-patterns`, `task-mechanisms`, `scripts-and-hooks`, `special-placements` and `components` to temporary phase-prefixed names. Update every link and plain mention: SKILL.md, the phase files, the references.
   - Verify:
     - `git diff -M` shows the renames, and only link or mention lines changed.
     - Inventory: 0 missing, apart from the renamed names.
     - No broken links, no nested links.
     - All checks match the baseline.
- [x] 3. **Split scripts-and-hooks** into phase-2 and phase-4 by the ledger. Each new file gets a one-line purpose, and a table of contents if it exceeds 100 lines. Verify: inventory 0 missing, plus the checks.
- [x] 4. **Split special-placements** into phase-2 and phase-4. Drop duplicates 1 and 2. Verify: the inventory reports exactly those two lines missing, and each one's surviving text is shown by grep.
- [ ] 5. **Split components** into phase-2 and phase-4. Verify as in task 3.
- [ ] 6. **Split task-mechanisms** into phase-3 and phase-4. Verify as in task 3.
- [ ] 7. **Split writing-patterns** into phase-3-descriptions and phase-4-writing-patterns. Verify as in task 3.
- [ ] 8. **Phase files.**
   - phase-2 steps 5 and 6 name their references.
   - phase-3 steps 2–4 name theirs, and step 10 moves to phase-4.
   - phase-4-build lists the order in which its references apply.
   - phase-5 and phase-6 get the updated names.
   - Verify: inventory, and that each step names exactly the files SKILL.md lists for that phase.
- [ ] 9. **SKILL.md workflow.**
   - Under each phase, one bullet per file, in step order, each with its step and condition.
   - Add the line "Within a phase, read its files in the order listed, each at the step it names, and apply it before you move on."
   - Verify:
     - Every reference is listed exactly once.
     - No reference is listed under two phases.
     - Body size is under 5,000 tokens (estimate).
- [ ] 9b. **Teach the pattern.** Add to phase-3-design-and-plan.md, step 8 (one phase and one topic per reference in a phased skill, named with its phase and topic, and a topic two phases use split by phase) and step 9 (list each phase's files under that phase in step order, with step and condition, and say to read them in that order). Cite the official bases (focused files, organize by domain or feature, descriptive names, say when to load each file) and mark the phase prefix and explicit order as the owner's convention. Verify: the inventory, the checks, and that the rule text matches the structure this restructure produced.
- [ ] 10. **Full verification.**
    - Inventory against the baseline: missing equals exactly the two approved duplicates.
    - Link checker: no broken links, no nested links.
    - A table of contents in every file over 100 lines.
    - biome on every file, `lint:frontmatter`, `claude plugin validate`.
    - `npm run lint:skills`: no finding that the baseline doesn't have.
    - Fresh-context review: Explore subagents with no CLAUDE.md, on a copy outside the repository, one per phase. Each reads SKILL.md and the files of its phase in the listed order, and reports whether it can apply each one at its step without a reference from another phase.
    - The background verifier runs its final full pass against the baseline, and its reports for every task are collected.
    - Present all raw outputs.

## Separate items (reported, not done in this plan)

- **`npm run lint:skills` reports 9 findings in the current files**, which I didn't run during this session's edits:
  - CO-08: two example paths that leave the skill folder;
  - CO-10: three files whose table of contents the linter doesn't find in the first lines;
  - SC-03: four example script paths.

  Per `skill-standards.md`, I report them to the owner with one question per rule id before fixing any, after this restructure.
- Closing work already pending:
  - `README.md:40` still says "six phases";
  - the CHANGELOG 0.2.0 entry;
  - the superseding ADRs;
  - `.claude/maintainer/specs/authoring-skills-*` still name the old files (historical; noted in the ADR);
  - the PR body.

## Critical files

- `plugins/skills-engineering/skills/authoring-skills/SKILL.md`
- `plugins/skills-engineering/skills/authoring-skills/references/*.md`, all 13 files

## Verification commands

- `npx biome lint <file>`
- `npm run -s lint:frontmatter -- <SKILL.md>`
- `claude plugin validate plugins/skills-engineering`
- `npm run -s lint:skills -- plugins/skills-engineering/skills/authoring-skills`
- `python3 scratchpad/inventory.py <baseline> <current>`
- the link and table-of-contents checker already used in this session
