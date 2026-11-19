# Plan: fix the four phase-placement findings in `authoring-skills`

## Context

The behavioral test of the new comprehension §2.7, run on the current `plugins/skills-engineering/skills/authoring-skills/`, found four defects. The restructure left them because its rule was to move lines unchanged. The owner approved fixing all four. Each one makes a rule reach the model in the wrong phase, or twice.

1. **Phase 3 lacks the script design rules.** Phase 3 step 4 (`phase-3-design-and-plan.md:8`) decides "each script's language, inputs, outputs and what it checks" and "each hook's events". The rules for those decisions sit only in `phase-4-scripts-and-hooks.md`, which is read after the plan is approved:
   - the interface, `:60-73`;
   - the language and dependency choices, `:79`, `:81`;
   - the hook-event lookup, `:114`.
2. **Duplicate.** `phase-2-placements.md:9` "Write it for the strictest surface it must run on" repeats `phase-4-placements.md:7`.
3. **A writing rule left in phase 2.** `phase-2-placements.md:22` "Write such a skill to work without the main conversation's context." No phase-4 file states it.
4. **Phase-3 decisions left in phase 4,** in `phase-4-task-mechanisms.md`:
   - `:30`, moving a long branch to its own file, which decides the plan's Files list;
   - `:85` and `:93`, when to use plan-validate-execute and when the user approves it;
   - `:118` and `:120`, what a gotcha is and that it goes in `SKILL.md`, which decides body or file.

**Intended outcome:**
- each rule sits in the phase whose step applies it, stated once;
- every line kept, or changed only by an approved ledger row;
- §2.7 applied to the result finds none of the four.

## Method

Run the procedure of this branch's `work-lifecycle:restructuring-documents` skill: read `plugins/work-lifecycle/skills/restructuring-documents/SKILL.md` and its `references/ledger-format.md`, and run its script from the repository path, because the installed plugin is an older copy. This is also its first real use.

- **Edit skill:** `skills-engineering:authoring-skills`, for the content and the reworded lines.
- **Verifier:** one background general-purpose subagent, briefed with the full text of `plugins/work-lifecycle/agents/migration-verifier.md` as its instructions, read-only, and resumed after each task.

## Changes, by finding

| # | From | To | How |
| :-- | :-- | :-- | :-- |
| 2 | `phase-2-placements.md:9` | the same line | `split`: drop "Write it for the strictest surface it must run on, and"; the line keeps "claude.ai, … run the skill without Claude Code's processing", and the clause becomes "Tell the requester each Claude Code feature that leaves out." The fact survives at `phase-4-placements.md:7`. |
| 3 | `phase-2-placements.md:22` | `phase-4-placements.md`, first bullet under "A skill a subagent loads on its own" | `split`: the decision clause stays in phase 2; "Write such a skill to work without the main conversation's context." moves unchanged. |
| 4a | `phase-4-task-mechanisms.md:30` | `phase-3-task-mechanisms.md`, end of "Workflows" | `move`, unchanged |
| 4b | `phase-4-task-mechanisms.md:85`, `:93` | new `## Plan, validate, execute` in `phase-3-task-mechanisms.md`, after "Validation loops" | `:85` splits: its choice ("For batch, destructive or costly work, …only then apply it") moves; phase 4 keeps an intro to the five steps (`edit`). `:93` moves unchanged. |
| 4c | `phase-4-task-mechanisms.md:118`, `:120` | new `## Gotchas` at the end of `phase-3-task-mechanisms.md` | `move`, unchanged; `:121-123` (how to write each) stay in phase 4 |
| 1 | `phase-4-scripts-and-hooks.md:60-73`, `:79`, `:81`, `:114` | new `references/phase-3-scripts-and-hooks.md` | `move` `:60-73` (the interface) and `:79`, `:81` under `## Language and dependencies` unchanged. `:114` is an `edit`: "Before writing the hook's script" becomes "Before choosing a hook's events", under `## Hook events`. |

### Pointers and navigation (`edit` rows)

- **`phase-3-design-and-plan.md:8`, step 4:** "each hook's events and how many; each script's language, inputs, outputs and what it checks" gains ", by phase-3-scripts-and-hooks.md".
- **`SKILL.md`, phase 3:** a new bullet before the step-4 task-mechanisms bullet: "At step 4, read [references/phase-3-scripts-and-hooks.md](references/phase-3-scripts-and-hooks.md) when the plan has a script or a hook." The standing order line already covers the order. The SKILL.md body grows by one line.
- **`phase-4-scripts-and-hooks.md`:**
  - the intro `:3` drops "the interface and dependencies it needs", keeping "the dependencies it states";
  - its Contents loses "The interface the model meets";
  - it goes under 100 lines, so its contents list becomes optional; keep it.
- **`phase-4-task-mechanisms.md`:**
  - the intro `:3` drops "the plan file", since the steps stay and the choice moves;
  - its Contents stays, because each heading still exists.
- **`phase-3-task-mechanisms.md`:**
  - the intro gains "plan-validate-execute and gotchas";
  - it gets a Contents list if it passes 100 lines; it won't, at about 60.

## Tasks

Each task ends with a signed commit and no push. The verifier's PASS is required before the next task.

0. **Baseline and verifier.**
   - Save this plan to `.claude/maintainer/plans/2026-11-18-authoring-skills-phase-placement-fixes.md`.
   - Copy `authoring-skills/` to the scratchpad as the baseline, and run `restructure.py blocks` on it.
   - Save the raw output of `lint:skills` (baseline: 9 findings) and `claude plugin validate`.
   - Launch the verifier and wait for READY.
1. **Ledger.**
   - Write the ledger from the table above: every line of the 6 changed files, as `move`, `split`, `edit` or `struct`.
   - Run `restructure.py allowed` and `ledger`, which must print `RESULT: OK`.
   - Show me no drop beyond the one in finding 2, whose fact survives at `phase-4-placements.md:7`.
2. **Placements** (findings 2 and 3).
3. **Task mechanisms** (finding 4).
4. **Scripts and hooks** (finding 1): the new file, the step-4 edit and the SKILL.md pointer.
5. **Final verification.**
   - Run the verifier's final pass.
   - Re-run the §2.7 test subagent on a copy of the result: none of the four may remain.
   - Run one fresh-context Explore reader over phases 2 to 4 in their listed order.
   - Report the raw outputs, every `split` and `edit` with its reason, and what the readers found.

## Verification, after every task

- Run the `restructure.py` checks:
  - `moved` on the task's source;
  - `splits`;
  - `inventory`, which must show `MISSING: 0`;
  - `mentions` with `--allow '(CLAUDE|AGENTS)\.md'`;
  - `blocks`.
- `npx biome lint` on each changed file.
- `npm run -s lint:skills -- plugins/skills-engineering/skills/authoring-skills`, with the same 9 findings as the baseline.
- `npm run -s lint:frontmatter -- …/authoring-skills/SKILL.md`.
- `claude plugin validate --strict plugins/skills-engineering`.
- `npm run -s check:consistency` exits 0.

## Out of scope, reported

The second test pass also flagged three smaller points of the same kind. The owner decides whether they follow the same method:
- `phase-4-placements.md:10`, "Write scripts that use only the standard library", is a script design rule for phase 3;
- `phase-4-components.md:27-33`, "Least surprise", also limits what phase 3 plans;
- `phase-2-components.md:7` and `:12`, "say what to do without it", are writing rules no phase-4 file states.

Other items:
- **CHANGELOG:** no separate entry. These fixes belong in the pending `authoring-skills` restructure entry for `skills-engineering` 0.2.0, which is still the owner's open item.
- **Push:** the push of the local commits (43 now) needs the owner's authorization.
