---
status: accepted
date: 2026-10-28
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# instruction-engineering joins the marketplace as a documentation plugin, without its evals

## Scope

- `plugins/instruction-engineering/`: its identity (name, display name, category, surfaces, component names) and what it ships.
- The plugin's eval suite, which stays out of the repository.
- The maintainer tests of its checker in `scripts/testers/instruction-engineering/`.
- Out of scope: the other changes released the same day (`tailwind-development` 0.3.1, `.nvmrc` 26.13.0, `@types/node` 26.6.6, the root `tsconfig.json`); none of them is a new decision. They are listed in More information.

## Context and problem statement

Nery brought a finished plugin, `~/Downloads/instruction-engineering.plugin`, that writes, audits and refactors `CLAUDE.md`, `CLAUDE.local.md` and `.claude/rules` against Claude Code's loading rules. It shipped a skill, an agent, a Python checker and an eval suite he had already run (594 files under `evals/`). To publish it, the marketplace needed its identity, a decision on the evals, and its code brought up to this repository's gates. What does the marketplace publish, under which names, and what stays out?

## Decision drivers

- A public plugin runs on users' machines: the checker must not hang or crash on hostile or malformed input.
- Names are permanent once published (`release-and-versioning`, rule 10), and the component call reads `<plugin>:<component>`.
- Nery had already run and accepted the evals; the repository should carry the plugin, not its test bench.
- The plugin is for third parties: nothing personal or project-specific inside.

## Considered options

- **Publish it as `instruction-engineering`, category `documentation`, for Claude Code and the Claude app, with the skill `claude-md-and-rules` and the agent `reviewer`, and its evals kept outside the repository**: chosen.
- **Keep the evals under `plugins/instruction-engineering/evals/`**: rejected by Nery, because he already tested them, and their 594 files would ship to every user and need Biome exclusions.
- **Skill name `claude-instructions-files` or similar**: rejected; Nery chose `claude-md-and-rules`, which pairs with the plugin name as `instruction-engineering:claude-md-and-rules`.
- **Agent name `instruction-reviewer`** (the imported file's name): rejected; Nery chose `reviewer`. His reason was not stated.

## Decision outcome

Chosen option: **publish `instruction-engineering` 0.1.0 with the identity above and without its evals**, because it gives users the skill, the agent and the read-only checker under short, permanent names, keeps the eval bench out of every install, and fixes the checker's defects before anyone runs it.

- Display name: Instruction Engineering. Category: `documentation`. Surfaces: Claude Code and the Claude app.
- Components: skill `claude-md-and-rules` (nine references, `scripts/check_instructions.py`), agent `reviewer`. Claude Code v2.1.271 or later (the agent's `omitClaudeMd`); `python3` 3.12 or later for the checker.
- The checker was refactored with output identical to the original, and fixed before release: `paths` globs run through a linear-time matcher, brace expansion is capped at 1,000 patterns per rule, an invalid range such as `[z-a]` is reported instead of crashing, and a non-UTF-8 `package.json` no longer crashes it.
- The reviewer agent gained five checks taken from Nery's global skill `maintaining-instruction-files`, which he then deleted.
- 23 unittest tests of the checker live in `scripts/testers/instruction-engineering/` (maintainer scope; they never ship).
- The evals are kept at `~/Claude/ideas-and-brainstorm/instruction-engineering/evals/` (594 files); the original `.plugin` archive stays in `~/Downloads`.

### Consequences

- Good, because users install ~606 always-on tokens (skill ~250, agent ~350, `claude plugin details` on 2026-10-28), not a test bench.
- Good, because a hostile `paths` list in a scanned project can no longer hang or crash the checker.
- Bad, because no CI or local gate runs the evals; a later change to the skill or agent is checked against them only by hand, from the copy outside the repository.
- Bad, because the checker's 3.12 floor is checked statically only (Ruff and Basedpyright against 3.12); no 3.12 interpreter exists on the maintainer machine (DEBT-039).

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| The word "claude" in the skill name is refused where Anthropic reserves it | Possible on surfaces that apply the API's skill-name rule; not checked for plugin installs in the Claude app | The skill would not load on that surface | Rename in a later version through `plugin-renames-and-removals` if a user reports it | Nery Samuel Murillo |
| The checker fails on Python 3.12 at runtime | Only through a construct the static checks miss | The skill's checker step fails for users on 3.12 | DEBT-039 | Nery Samuel Murillo |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Users receive 0.1.0 with one skill and one agent | `claude plugin details instruction-engineering` after an HTTPS install from `main` in a throwaway config | Passed on 2026-10-28: 0.1.0, `claude-md-and-rules`, `reviewer`, ~606 tok always-on | Each new version |
| The release exists | `gh release view instruction-engineering--v0.1.0` | Passed on 2026-10-28 | Each new version |
| The checker survives hostile globs | `scripts/testers/instruction-engineering/test_check_instructions.py` (brace budget at 1,000 and 1,001, hostile patterns under a 10 s timeout) | Passed in `npm test` on 2026-10-28 | Each checker change |

## More information

- Decided by Nery during the 2026-10-28 session; released through [PR #70](https://github.com/nerymurillohnd/the-claude-factory/pull/70), merge commit `d7258fe`, release run 40773715149.
- Shipped in the same PR, with no new decision: `tailwind-development` 0.3.1 (the execute bit on `mcp/server.mjs`), `// @ts-check` on every maintainer `.mjs`, execute bits on six maintainer scripts, `scripts/testers/schemas/test_schemas.py` as a PEP 723 script, `.claude/CLAUDE.md` referencing `@~/.claude/LESSONS.md`, `.nvmrc` 26.13.0 (Node 26 became Active LTS that day), and the root `tsconfig.json`. After the merge: `@types/node` 26.6.6.
- The pinned versions in ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies are the ones of that day; `package.json` holds the current ones.
