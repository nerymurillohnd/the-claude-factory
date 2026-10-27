---
status: superseded
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-20_procedures-live-in-project-skills
superseded-by: ADR_2026-10-26_workflow-contract-lives-in-claude-md
---

# WORKFLOW.md is a stage map; instructions live in rules, procedures in skills

## Scope

- In scope: `.claude/WORKFLOW.md` (moved from `.claude/rules/WORKFLOW.md`), `.claude/CLAUDE.md` (its import of the map and the Quality gates section), the rule files in `.claude/rules/`, the template `.claude/templates/plugin-review-brief.md`, and the references to the old file and its sections in the project skills and memories.
- Out of scope: the content of the project skills' procedures, the mods rule (`.claude/rules/mods.md`), and plugins.

## Context and problem statement

`.claude/rules/WORKFLOW.md` (131 lines, loaded in every session) mixed three kinds of content: the order of work, standing instructions ("never", "only when") and a delegation brief. Instructions about skills, evals and user docs loaded in every session although they matter only when those files are touched, and a CLAUDE.md restructure left five references to sections that no longer existed. Where should each kind of content live?

## Decision drivers

- Each instruction lives in one place, so nothing drifts or contradicts (the evals default did: WORKFLOW.md said evals by default, `plugin-tooling.md` said only on request).
- Instructions that matter only for some files load only with those files.
- The order of work stays visible in every session.
- A delegated reviewer loads no CLAUDE.md, rule or memory, so its brief must be self-contained.

## Considered options

- **Three layers: WORKFLOW.md as a map, instructions in rule files, procedures in skills**: chosen.
- **Keep WORKFLOW.md as rules plus short skill triggers** (ADR_2026-10-20_procedures-live-in-project-skills): rejected because it keeps instructions and order in one file that loads whole in every session.
- **Keep WORKFLOW.md in `.claude/rules/`**: rejected because it no longer holds rules; it moves to `.claude/` and `CLAUDE.md` imports it with `@WORKFLOW.md`, so it still loads in every session.
- **Merge the skill, eval and user-docs instructions into one rule file**: rejected because one unscoped file loads in every session; three files with `paths` load only when a matching file is read or edited.

## Decision outcome

Chosen option: **three layers**, because each instruction then has one home, file-specific rules cost context only when needed, and the map shows the order without restating any rule.

- `.claude/WORKFLOW.md`: stages and steps in order, each naming the skill, rule or file that governs it.
- `.claude/rules/`: `skill-triggers.md` and `plugin-design.md` load in every session; `skill-authoring.md`, `evals.md` and `user-docs.md` load through `paths`.
- The quality gates (post-edit commands, Before every push, the reporting format) stay in `.claude/CLAUDE.md` → Quality gates until Nery orders a rule file for them.
- The plugin review steps are a template, `.claude/templates/plugin-review-brief.md`, pasted into the delegation message.

### Consequences

- Good, because the evals contradiction is gone: `plugin-tooling.md` holds the only rule.
- Good, because skill, eval and user-docs rules stop loading in sessions that never touch those files.
- Bad, because a path-scoped rule loads only when Claude reads, writes or edits a matching file (code.claude.com/docs/en/memory#path-specific-rules); work that touches no such file does not see it.
- Bad, because a skill still loads when Claude decides to; the trigger table makes it likely, not guaranteed, as before.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Every sentence of the old WORKFLOW.md has exactly one destination | Sentence-by-sentence map against the old file | Passed on 2026-10-24: every line mapped; the two evals lines were replaced by `plugin-tooling.md` by decision, and what `new-plugin.mjs` creates is left to the script | When WORKFLOW.md or a rule changes |
| No reference points to `.claude/rules/WORKFLOW.md` or a removed section | `grep` over `.claude/`, `scripts/`, `docs/`, ADRs and handoffs excluded as history | Passed on 2026-10-24 | When a rule or section is renamed |
| The map is imported and a path-scoped rule loads on a matching file | `claude -p` in a new session | Passed on 2026-10-24: the import answered `# Workflow`; `user-docs.md` was absent before reading `plugins/turn-meter/README.md` and present after (`before=no after=yes`) | After a Claude Code update that changes memory loading |

## More information

- Decided by Nery in the session of 2026-10-24, together with the move of the quality gates into `.claude/CLAUDE.md`.
- Related: ADR_2026-10-22_mod-knowledge-in-a-path-scoped-rule (the same path-scoped pattern for mods).
