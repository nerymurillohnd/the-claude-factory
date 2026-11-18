---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Rename the skills whose names contain `claude` to the `cc-` prefix

## Scope

The skill `claude-github-actions` in `plugins/github-operations/` and the skill `claude-md-and-rules` in `plugins/instruction-engineering/`: their folders, their `name` fields, every live reference to them in the repository, and the plugin versions that ship the change. Out of scope: session handoffs and released changelog sections, which keep the old names as history.

## Context and problem statement

On 2026-11-18 the frontmatter scripts of `skills-engineering:auditing-skills` ran on the 31 skills under `plugins/`. Two skills failed one check each, `frontmatter.name` rule `reserved-word`, basis `official`, surface `upload`: `claude-github-actions` and `claude-md-and-rules` contain the reserved word `claude`. The Agent Skills overview on the Claude Platform says the `name` field "Cannot contain reserved words: `anthropic`, `claude`" (platform.claude.com/docs/en/agents-and-tools/agent-skills/overview, read 2026-11-18). Claude Code loads both skills, but claude.ai and the Claude API reject them, so a user of this public marketplace can't upload either skill outside Claude Code.

## Decision drivers

- Every skill in the marketplace must work on every surface a user can take it to, not only Claude Code.
- The owner chose the replacement prefix: `cc`, for Claude Code, in place of `claude`.
- A rename breaks every saved `/plugin:skill` invocation, so it ships as a breaking change with notice.

## Considered options

- **Rename both skills, replacing `claude` with `cc`**: chosen.
- **Keep the names**: rejected because the skills would stay unusable on claude.ai and through the Claude API.

## Decision outcome

Chosen option: **rename both skills, replacing `claude` with `cc`**, because the owner chose it and it removes the reserved word while keeping each name recognizable. `claude-github-actions` became `cc-github-actions` and `claude-md-and-rules` became `cc-md-and-rules`.

### Consequences

- Good, because both skills now pass every frontmatter check, `reserved-word` included, and can be uploaded to claude.ai and the Claude API.
- Bad, because users who invoke `/github-operations:claude-github-actions` or `/instruction-engineering:claude-md-and-rules`, or name them in their own instructions, must switch to the new names after updating. The marketplace's `renames` map covers plugins only, so the changelog is the only notice.
- Bad, because the copies synced from claude.ai keep the old names until the new versions reach the owner's account.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Both renamed skills pass the frontmatter checks | `frontmatter-checks.py run` on each `SKILL.md` | 11 of 11 checks with 0 findings each, 2026-11-18 | Each release of either plugin |
| Each plugin loads the renamed skill | `claude plugin details` | Lists `cc-github-actions` and `cc-md-and-rules`, 2026-11-18 | Each release of either plugin |
| No live file names the old skills | `grep -rIl` over the repository, without `node_modules`, `.venv` and `.git` | Only session handoffs and released changelog sections match, 2026-11-18 | Before the merge |
| Users receive both versions | `release.yml` tags `github-operations--v0.9.0` and `instruction-engineering--v0.2.0` | pending | After the pull request merges |

## More information

- The owner decided the rename on 2026-11-18, in the session that found the findings.
- The change ships as github-operations 0.9.0 and instruction-engineering 0.2.0. Both are breaking changes, which bump the minor version in 0.x.
