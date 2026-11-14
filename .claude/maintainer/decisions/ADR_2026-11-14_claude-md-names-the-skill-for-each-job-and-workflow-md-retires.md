---
status: accepted
date: 2026-11-14
decision-makers:
  - "Nery (project owner)"
supersedes: ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md
superseded-by: none
---

# CLAUDE.md names the skill for each job once, and WORKFLOW.md retires

## Scope

`.claude/CLAUDE.md` ("How to run this project"), the deleted `.claude/WORKFLOW.md`, and the project skills that now hold its last commands: `plugin-releases` and `plugin-catalog-changes`. Maintainer scope.

## Context and problem statement

`WORKFLOW.md` has gone back and forth:
- It was created as a stage map (ed180b8).
- It was folded into a Workflow section of `CLAUDE.md` that named each stage's skill (30eb294).
- It was re-created as a command catalog by the redesign of #104 (ced195b).
- On branch `ccr-60dfcba3-fsbz16`, it was retired (ff28e21), then restored without any instruction pointing to it, because the deletion had not been authorized (f9153a2).

ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md kept it as the target of a pointer. It also planned a `plugin-lifecycle` skill to take over its stage catalog. That skill was never created.

Meanwhile, the `CLAUDE.md` of that branch gained a "How to run this project" section. The section says which skill to load and use for each job, and every command `WORKFLOW.md` listed is also held by a project skill, a rule, `package.json` or `plugin-engineering:cli-commands-guide`. Two places listed the same commands and drifted. On 2026-11-14, `WORKFLOW.md` said `npm run labels:sync` "changes GitHub", while it only compares unless `--apply` is passed, and it described `claude plugin validate` as it behaved before Claude Code 2.1.289.

On 2026-11-14 the owner stated that `CLAUDE.md` must define this once, under "How to run this project". It names the skill to load and use for each job, and `WORKFLOW.md` disappears once its contents have a home.

## Decision drivers

- One definition of which skill governs each job, loaded in every session.
- No command written in two places, so none drifts.
- No fact lost when `WORKFLOW.md` goes.

## Considered options

- **`CLAUDE.md`'s "How to run this project" names the skill for each job; each skill holds its own commands; `WORKFLOW.md` is deleted**: chosen.
- **Keep `WORKFLOW.md` as a command catalog beside the skills**: rejected because it repeats what the skills, the rules and `package.json` hold, and drifts from them.
- **Move the stage catalog into a new `plugin-lifecycle` skill (ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md)**: rejected for the catalog, because the existing skills already hold every stage's commands and `CLAUDE.md` already routes to them.

## Decision outcome

Chosen option: **`CLAUDE.md` names the skill for each job, and `WORKFLOW.md` is deleted**, because the owner set this design and it leaves one source for each command.

What moved before the deletion:
- `npm run release:notes` went into `plugin-releases` step 1.
- `claude plugin marketplace remove`, with the data loss the official reference warns of, went into `plugin-catalog-changes`.
- A line for evals went into "How to run this project", with its billing note.

Every other term of ADR_2026-11-13_claude-configuration-architecture-on-the-owners-claude-md carries over unchanged, except two:
- the pointer to `WORKFLOW.md`;
- the `plugin-lifecycle` skill's role as the stage catalog.

### Consequences

- Good, because the always-loaded instructions carry one routing table, and each skill owns its commands.
- Good, because the stale `labels:sync` and `validate` descriptions are gone with the file.
- Bad, because the general checks (`lint`, `typecheck`, `validate`, `check`) are now described only by `package.json` and the rules that call them. A reader learns what each does from `npm run` and the script itself.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Nothing points to `WORKFLOW.md` | `git grep -n 'WORKFLOW\.md'`, outside dated records, plans and handoffs | Only `.claude/maintainer/audits/2026-11-13-claude-configuration-inventory-audit.md`, a dated record (2026-11-14) | Each change to `CLAUDE.md` |
| The skills that took commands still lint clean | `npm run lint:skills -- .claude/skills/plugin-releases .claude/skills/plugin-catalog-changes` | 0 errors, 0 warnings (2026-11-14) | Each change to those skills |

## More information

- The owner decided on 2026-11-14, in this session, and approved the plan `.claude/maintainer/plans/2026-11-14-merge-config-branch-and-retire-workflow.md`.
- Open for the owner: whether a `plugin-lifecycle` skill is still wanted for anything besides the stage catalog, such as the orphaned templates.
