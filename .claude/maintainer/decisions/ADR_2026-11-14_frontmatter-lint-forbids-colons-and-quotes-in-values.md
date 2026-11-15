---
status: accepted
date: 2026-11-14
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Check every skill, agent and command with frontmatter-lint: no colon and no quotes in values

## Scope

`scripts/validators/frontmatter-lint.py`, the package `scripts/validators/frontmatter_lint/`, its tests in `scripts/testers/frontmatter_lint/`, the stubs it adds in `scripts/typings/ruamel/yaml/`, and the `lint:frontmatter` npm script. It checks the files matched by `plugins/*/skills/*/SKILL.md`, `plugins/*/agents/**/*.md`, `plugins/*/commands/**/*.md` and the same three under `.claude/`. Maintainer scope: it never writes to a plugin.

## Context and problem statement

Three github-operations agents (`pr-fixer`, `pr-tracker`, `health-diagnostics`) shipped in 0.8.0 with a `description` that holds ": ". ruamel.yaml rejects it ("mapping values are not allowed here"), while Claude Code's own parser accepts it: the agents load with their descriptions and `claude plugin validate --strict plugins/github-operations` exits 0 (Claude Code 2.1.325, 2026-11-14). Strict YAML parsers elsewhere, such as uploads and other clients, reject such a file. skill-lint's CO-01 parses only `SKILL.md` files, and the agent procedure and template said nothing about `description`.

The owner set the rule on 2026-11-14: a colon goes only after a field name, and no value holds a colon or is wrapped in quotes; a value is reworded instead.

## Decision drivers

- Catch the defect mechanically in every file type Claude Code reads frontmatter from, not only skills.
- Enforce the owner's rule as stated: no colon and no quotes in any value.
- Keep skill-lint's scope and its two discovery globs as its rule sets them.

## Considered options

- **A new validator, frontmatter-lint, for skills, agents and commands, reusing skill-lint's strict ruamel parsing approach**: chosen.
- **A rule inside skill-lint (CO-13)**: rejected because skill-lint discovers only `SKILL.md` files, so agents, where the defect was, stay unchecked.
- **Widen skill-lint's discovery to agents and commands**: rejected because it changes skill-lint's spec, its discovery rule and what `lint:skills` means.

## Decision outcome

Chosen option: **a new validator, frontmatter-lint**, because it covers every file type with frontmatter and leaves skill-lint as it is.

The owner set these terms on 2026-11-14:

- **Rules:** FM-01, the frontmatter parses as strict YAML (a value with ": " fails here); FM-02, no value holds a colon; FM-03, no value is wrapped in quotes. Every text value is checked, nested maps, lists and block scalars included.
- **One exception:** a `<plugin>:<skill>` item of the top-level `skills` list keeps its colon, since Claude Code requires that qualified name. Block-scalar hook prompts and quoted `argument-hint` values get no exception.
- **Rollout:** `npm run lint:frontmatter` exists now; it joins `npm run lint` once the plugin fixes land (DEBT-005).

### Consequences

- Good, because the first run found 16 findings in 53 files that `claude plugin validate --strict` passes, including two nobody had seen: a block-scalar `description` with colons in `instruction-engineering`'s `reviewer` agent and quoted `metadata` values in two `svelte-development` skills.
- Good, because the code has 20 unittest tests with fixtures written to temporary directories, so no broken file is committed.
- Bad, because `lint:frontmatter` stays out of `npm run lint` and `npm run check` until those plugins are fixed.
- Bad, because an `argument-hint` such as `[PR number or URL]` cannot be written plain: YAML reads a bare `[` as a list, so those hints must be reworded without brackets.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The tests pass and the code has no suppressions | `npm run test:scripts`, `npm run lint:python`, `npm run typecheck:python` | 257 tests OK, ruff and basedpyright 0 errors (2026-11-14) | Every change under `scripts/` |
| The check reports the known defects | `npm run lint:frontmatter` on the repository | 53 files, 16 findings, exit 1 (2026-11-14) | After each plugin fix in DEBT-005 |
| The repository is clean and the check joins `lint` | `npm run lint:frontmatter` exits 0, then `npm run lint` | pending | When DEBT-005 closes |

## More information

- The owner made the three choices on 2026-11-14 in this session: the new validator, only the `plugin:skill` exception, and chaining into `lint` after the fixes.
- The rule is also stated in `.claude/references/agent.md`, `.claude/references/skill.md` and both templates (commit 50662ee).
- Related: ADR_2026-11-13_own-deterministic-skill-linter, ADR_2026-11-13_local-stubs-type-ruamel-yaml, DEBT-005.
