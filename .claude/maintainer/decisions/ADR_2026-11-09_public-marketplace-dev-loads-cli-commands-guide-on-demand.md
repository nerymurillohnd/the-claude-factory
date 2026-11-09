---
status: accepted
date: 2026-11-09
decision-makers:
  - "Nery Murillo"
supersedes: none
superseded-by: none
---

# public-marketplace-dev loads cli-commands-guide only before a plugin command

## Scope

`plugins/plugin-engineering/skills/public-marketplace-dev/SKILL.md` (its `## Standing rules`, the Gotchas pointer and Workflow Step 6) and its relation to the `cli-commands-guide` skill of the same plugin. Out of scope: the content of `cli-commands-guide` and the "load it" pointers in `references/01-plugins-core/cli-reference.md`, which stay as they are.

## Context and problem statement

`public-marketplace-dev` only mentioned `cli-commands-guide`, so while it was active Claude could run or write plugin commands (the Step 6 `claude plugin validate --strict` run, README install lines, `plugin tag`, `marketplace remove`) from memory, without that skill's flags, gotchas and exit codes. Nery asked for `cli-commands-guide` to load whenever `public-marketplace-dev` loads, and for the cost to be weighed first: `claude plugin details plugin-engineering` on Claude Code 2.1.319 reported about 3k tokens on invoke for `cli-commands-guide` and about 6.9k for `public-marketplace-dev`. How should one skill bring in the other?

## Decision drivers

- The Claude Code skills docs (2026-11-09): no skill frontmatter preloads another skill in the main conversation; only a subagent's `skills` field preloads. Claude loads a skill through the Skill tool.
- Skill content lifecycle: invoked content stays across turns, a re-invoke with identical content adds only a note, and after compaction only the first 5,000 tokens of each skill are re-attached, within a 25,000-token budget.
- Every invocation of `public-marketplace-dev` should not pay about 3k tokens when the task uses no plugin command.
- The rule must work on every surface the plugin targets, Claude Code and the Claude app.

## Considered options

- **Conditional standing rule near the top of SKILL.md**: chosen.
- **Unconditional load at skill start**: rejected because it adds about 3k tokens to every invocation, including questions that use no plugin command, and takes that share of the post-compaction budget.
- **A slimmer pointer only**: rejected because the load stays optional, which is the original failure.
- **Copy the key gotchas into public-marketplace-dev**: rejected because two copies drift.
- **Merge the two skills**: rejected because it is a breaking rename and makes every invocation cost both.
- **`!` dynamic injection of the other SKILL.md**: rejected because some sessions do not run `!` commands and it runs shell on users' machines.
- **A subagent with `skills:` preloading both**: rejected because the knowledge would exist only inside that subagent.
- **A skill hook on `Bash(claude plugin *)`**: kept as an escalation only, because it ships an executable hook and covers shell runs only, not README or CI text.

## Decision outcome

Chosen option: **Conditional standing rule near the top of SKILL.md**. Before Claude runs, writes or explains a plugin command (`claude plugin …`, `claude plugin marketplace …`, any `/plugin` form, `/reload-plugins`, `--plugin-dir` or `--plugin-url`), Step 6 included, it invokes `cli-commands-guide` with the Skill tool. It does so once per conversation unless the conversation was compacted, and reads the official CLI reference page when the skill is not available. This protects the tasks that carry the risk at no cost to the others.

### Consequences

- Good, because answers that use no plugin command don't load the extra ~3k tokens.
- Good, because the rule sits inside the first 5,000 tokens, so it survives compaction.
- Bad, because every change task loads it, since Step 6 always validates.
- Bad, because the rule is an instruction that Claude follows, not a mechanical guarantee.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| With `public-marketplace-dev` active, a plugin-command task loads `cli-commands-guide` | `claude -p --plugin-dir plugins/plugin-engineering` probe, README install/update/uninstall task | 2 of 2 on the change, 0 of 2 on `main` before it | When either skill changes, or a Claude Code release changes skill loading |
| A question with no plugin command does not load it | Same probe with a hooks-events question | 1 of 1 loaded only `public-marketplace-dev`; the second run picked another plugin's skill | Same |
| The plugin still validates | `claude plugin validate --strict` on the plugin and the marketplace | exit 0, `Validation passed` | Every release |

## More information

Shipped in plugin-engineering 0.2.1: PR [#97](https://github.com/nerymurillohnd/the-claude-factory/pull/97), merge commit d17df23, tag `plugin-engineering--v0.2.1`. Nery approved this option over the unconditional load he first asked for.
