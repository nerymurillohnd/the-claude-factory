---
status: superseded
date: 2026-10-20
decision-makers:
  - "Nery"
supersedes: ADR_2026-10-16_maintainer-operating-model
superseded-by: ADR_2026-10-24_workflow-is-a-stage-map
---

# Procedures live in project skills; WORKFLOW.md keeps the triggers

## Scope

Applies to how Nery and Claude Code keep the working procedures of The Claude Factory: `.claude/rules/WORKFLOW.md`, `.claude/CLAUDE.md` and `.claude/skills/`. It covers plugin writing, docs consistency, and issues and GitHub. It does not change what any plugin ships, and it leaves the other WORKFLOW.md sections as they are.

## Context and problem statement

On 2026-10-20 every gate file, stage rule, project skill and project agent was folded into `.claude/CLAUDE.md` and `.claude/rules/WORKFLOW.md`, so Nery had one place to read the rules. That fold left no ADR (see the [handoff](../../session-handoff/2026-10-21-0132.md)) and replaced the layout chosen on 2026-10-16. The result worked as a reference but not as a procedure: WORKFLOW.md carried long sections that had to be read and applied by hand, and nothing made a procedure run each time a file was touched. How should the procedures be kept so they run whenever the work touches them, with each rule stated once?

## Decision drivers

- A procedure must run every time a plugin file, a changelog, a README, a doc or GitHub is touched, not only on request.
- The goal of the docs check is to guarantee consistency across files, not to review them now and then.
- Each rule lives in one place; WORKFLOW.md must summarize a skill, never duplicate it.
- The work runs in the main session, without delegating to a read-only subagent.

## Considered options

- **Three project skills for the procedures, with WORKFLOW.md keeping short triggers**: chosen.
- **Keep the full procedures as long sections in WORKFLOW.md** (the 2026-10-20 layout): rejected because a section is read when someone remembers it and nothing loads it when a file is touched, and Nery wants the procedure to run every time.
- **Separate rule and gate files with skills** (the 2026-10-16 layout): rejected on 2026-10-20 because Nery wanted one place for the rules, with no duplication.
- **A read-only subagent for the docs review and audit**: rejected because Nery said the work is not a subagent's; the skills run in the main session.
- **A periodic review and audit of the docs**: rejected because the goal is consistency on every change, not a review from time to time.

## Decision outcome

Chosen option: **three project skills, with WORKFLOW.md keeping short triggers**, because the skill holds each procedure once and the WORKFLOW.md trigger tells Claude when to load it.

1. **Skills.** `plugin-development` (building a plugin), `plugin-consistency` (every file that must agree with a change, checked and fixed, with proof) and `github-workflow` (issues, commits, pushes and PRs).
2. **WORKFLOW.md.** "When Writing Plugins", "When Keeping Docs Consistent" and "When Using GitHub" each state the cases ("Every time you ...") and four steps, the first of which invokes the skill. They replace the sections for plugin writing, docs drift, the user-docs audit, GitHub and issue handling.
3. **Rules that stay.** The sections not listed above are unchanged, including the delegated read-only reviews in "When Reviewing a Plugin".

### Consequences

- Good, because each procedure exists once and WORKFLOW.md cannot drift from it.
- Good, because the triggers name the cases, so the skill loads when the file is touched.
- Bad, because a skill loads when Claude decides to load it; the trigger in WORKFLOW.md makes it likely, not guaranteed.
- Bad, because `Explore` and `Plan` subagents load no CLAUDE.md and no project skills, so a delegated review sees these procedures only if the delegation message carries them.
- Bad, because the three skills are not discovered by a session that started before `.claude/skills/` existed; it needs a restart.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Each skill is discovered and loads when its case occurs | Restart the session, then touch a plugin file, a changelog and an issue | Pending: no skill was loadable in the session that wrote them | After the first restart |
| A model can follow each skill | A dry run of the skill by a read-only subagent on a realistic scenario | `plugin-development` and `github-workflow`: one run each on 2026-10-20, gaps fixed. `plugin-consistency`: not run | After any rewrite of a skill |
| The repo checks stay green | `node .github/scripts/check-repo.mjs` | Passed on 2026-10-20 | When WORKFLOW.md or a skill changes |

## More information

Commits that carry it: `3b3158f` (the skills) and `a33ff6e` (WORKFLOW.md). The memory `rules-live-in-workflow`, which said not to recreate project skills, was deleted at Nery's order the same day.

The 2026-10-16 record is superseded as a whole because the layout it chose no longer exists. These points of it still hold and are not changed here: fixed issues are referenced with `Refs #n` and never `Closes #n`, the version-bump push hook, and decisions and debt kept under `.claude/maintainer/`.
