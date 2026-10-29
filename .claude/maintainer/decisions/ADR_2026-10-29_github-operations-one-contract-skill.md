---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# github-operations ships one contract skill, github, in place of its PR and cleanup skills

## Scope

- `plugins/github-operations/`: the skills `auto-pr-lifecycle` and `git-cleanup`, removed in 0.5.0, and the new skill `skills/github/` with its references, scripts and assets.
- The merge approval of the PR lifecycle.
- Out of scope: the hook layer (ADR_2026-10-29_github-operations-hooks-enforce-its-own-rules) and the `repo-auditor` agent's file reads (ADR_2026-10-29_repo-auditor-reads-skill-references). Nery's personal `github-tooling` skill and the `pr-coauthoring` draft live outside this repository; this record covers only what the plugin absorbs from them.

## Context and problem statement

Three skills competed for the same requests ("open a PR", "merge it"): the plugin's `auto-pr-lifecycle`, the personal `github-tooling` skill and the `pr-coauthoring` draft. They contradicted each other on the tool for PR creation and merge, on where to merge, on labels and on how the merge is approved, and their shared invariants were written three times in three wordings. Both plugin skills also wrote `$ARGUMENTS` inside a sentence, which renders as an empty subject when no argument is given. How should the plugin present GitHub work so that one set of rules applies to every GitHub task?

## Decision drivers

- One wording of each rule, loaded for any GitHub task, however the request is phrased.
- The contract must survive compaction whole: Claude Code re-attaches only the first 5,000 tokens of an invoked skill.
- Procedures load only when their task needs them.
- A public plugin carries nothing personal: no owner name, no signing-key wording, no pointer to a private skill.

## Considered options

- **One contract skill, `github`, holding only invariants, the tooling rule, the preflight, a routing map and the state rule, with every procedure a reference linked from it; audit and cleanup included, started only on an explicit request**: chosen.
- **Keep `auto-pr-lifecycle` and `git-cleanup` and add an authoring skill from `pr-coauthoring`**: rejected, because three skills would keep competing for the same requests and repeat the invariants.
- **Merge approval through AskUserQuestion, as `auto-pr-lifecycle` did**: rejected; the merge hook's `ask` permission prompt is the approval, because a hook's `ask` forces a prompt even in auto mode ([hooks](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)).

## Decision outcome

Chosen option: **one contract skill, `github`**, because one file states each rule once, stays under about 3,000 tokens so compaction keeps it whole, and routes every task to the reference that holds its procedure.

- Arguments route through the `ARGUMENTS:` line Claude Code appends; the body has no placeholders.
- PRs are created and merged with `gh` (`gh pr create`, `gh pr merge --match-head-commit`); the GitHub MCP stays first for reads and monitoring.
- The repository's own templates, labels and conventions win over the plugin's assets.

### Consequences

- Good, because the rules exist once, and the `$ARGUMENTS` defect disappears.
- Good, because PR authoring, repository templates, issue to PR and CI repair join the plugin from material that already existed.
- Bad, because `/github-operations:auto-pr-lifecycle` and `/github-operations:git-cleanup` disappear: a breaking change, shipped as 0.5.0 under ADR_2026-10-18_breaking-changes-bump-minor-in-0x.
- Bad, because whether invoking the skill twice with different arguments adds the contract twice is unverified.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The contract fits its budget | `wc -c` on `SKILL.md` at most 12,000; `description` plus `when_to_use` at most 1,536 characters | pending | Each change to `SKILL.md` |
| Every reference is reachable from the contract | A link check over `skills/github/references/` | pending | Each change to the references |
| Re-invocation does not duplicate the contract | Eval case `reinvoke-no-duplicate` | pending | Each Claude Code release that changes skill loading |

## More information

- Spec: `.claude/specs/2026-10-29-github-operations-0.5.0-design.md`; plan: `.claude/plans/2026-10-29-github-operations-0.5.0.md`.
- Decided by Nery in the 2026-10-29 design conversation; the build runs on `feat/github-operations-0.5.0`.
