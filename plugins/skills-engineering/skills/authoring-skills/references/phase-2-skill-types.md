# Phase 2: Skill types

Whether a skill is the right feature, the six types of skill, and what each type changes in the skill you write.

## Contents

- [Gotchas](#gotchas)
- [Is a skill the right feature](#is-a-skill-the-right-feature)
- [The six types](#the-six-types)
- [Reference skill](#reference-skill)
- [Task skill](#task-skill)
- [User-only task skill](#user-only-task-skill)
- [Background knowledge skill](#background-knowledge-skill)
- [Forked task skill](#forked-task-skill)
- [Preloaded knowledge skill](#preloaded-knowledge-skill)
- [Official sources](#official-sources)

## Gotchas

- Claude consults a skill only for work it can't handle well alone. A one-step request such as "read this PDF" may not load a PDF skill however well its description matches. A skill earns its place on specialized knowledge, an unfamiliar API, a domain workflow or an uncommon format.
- A skill is guidance, not enforcement. A rule that must hold every time belongs in a hook or a permission rule.
- Claude Code has none of Anthropic's pre-built document skills (pptx, xlsx, docx, pdf). In Claude Code, a skill for those formats is one you write.
- A scheduled task or `/loop` asks before it runs a skill that declares `allowed-tools` or `hooks`. For a skill meant to run unattended, tell its users to add `Skill(name)` to `permissions.allow`, and give the skill a default to take and a report to return instead of asking.

## Is a skill the right feature

Match the need to the feature that meets it, before you choose a type:

| The need | The feature |
| :-- | :-- |
| A task that won't repeat | Do the task, with no skill |
| Something Claude already does well | No skill |
| A fact or "always do X" rule every session needs | CLAUDE.md |
| A rule for some files or folders | A rule in `.claude/rules/` with `paths` |
| A voice, length or format for every response | An output style |
| A rule that must hold every time | A hook or a permission rule |
| Work that needs its own context and tools | A subagent; a skill can give it knowledge |
| Access to an external system | An MCP server; a skill teaches how to use it |
| Knowledge or a procedure Claude needs for some tasks | A skill |

- When the need isn't a skill, tell the user which feature fits and why, and stop unless they still want a skill.
- When the request holds several needs, split it: each need gets its own feature or skill.

Example: "a skill so Claude never edits `.env`" is a hook. "A skill with our release checklist" is a skill. "A skill that formats code after each edit" is a hook that runs the formatter, plus a skill only if fixing what the formatter reports needs judgment.

## The six types

A skill's type comes from three choices: what it holds, who invokes it, and where it runs.

| Type | Holds | Who invokes it | Where it runs | Frontmatter |
| :-- | :-- | :-- | :-- | :-- |
| Reference skill | Knowledge | The user and Claude | Inline | none |
| Task skill | A procedure for one action | The user and Claude | Inline | none |
| User-only task skill | A procedure with side effects | Only the user | Inline | `disable-model-invocation: true` |
| Background knowledge skill | Knowledge that isn't an action | Only Claude | Inline | `user-invocable: false` |
| Forked task skill | A self-contained procedure | The user and Claude | In a new subagent | `context: fork` |
| Preloaded knowledge skill | Knowledge for a subagent | A subagent, at its start | In that subagent | listed in the subagent's `skills` |

Choose the type by these criteria, in order:

1. Knowledge or procedure: knowledge Claude applies to the current work is reference content. Steps for one action are task content.
2. Who invokes it, by consequence: if Claude running the skill on its own could change something the user didn't approve, only the user invokes it.
3. Where it runs: a task whose intermediate work would fill the main conversation, and that needs none of its history, runs forked. Knowledge a custom subagent applies to every task it gets is preloaded.

## Reference skill

Conventions, patterns, style guides or domain rules that Claude applies alongside the conversation.

- Write the rules as standing guidance for any work they touch, not as steps.
- Set `paths` when the knowledge applies only to certain files, so the skill loads automatically only for them.

```yaml
---
name: invoice-conventions
description: Use when writing or reviewing code that creates invoices. Field names, rounding and tax rules for this codebase.
paths: src/billing/**
---

When code creates an invoice:
- Store amounts in cents as integers
- Round tax per line, then sum
- Name dates `issued_on` and `due_on`
```

## Task skill

Step-by-step instructions for one action that Claude may also start on its own, such as generating a report or summarizing changes.

- Open with the task, give the steps, and end with what the result is.
- Take the input through arguments: `$ARGUMENTS`, or the names declared in `arguments`. Set `argument-hint` to show the user what to pass.

```yaml
---
name: weekly-sales-summary
description: Use when the user asks for this week's sales numbers or the regional report. Builds the weekly summary from the CRM export.
argument-hint: <export-file>
---

Build the weekly sales summary from $ARGUMENTS:
1. Total the sales by region
2. Compare each region with last week
3. Return a table with the three regions that changed most
```

## User-only task skill

A procedure with side effects or timing the user must control, such as deploying, sending, publishing or paying.

- Set `disable-model-invocation: true`. The description then reaches no model: write it for the user who picks the command in the `/` menu.
- No other skill can load it, no subagent can preload it, and a session-scoped scheduled task can't run it. Use another type for a step that another skill or a subagent must run.
- Write the body as the procedure the command runs.

```yaml
---
name: publish-release
description: Publishes a tagged release to the package registry.
disable-model-invocation: true
argument-hint: <version>
---

Publish release $ARGUMENTS:
1. Run the test suite
2. Build the package
3. Push the tag and publish
4. Confirm the version on the registry
```

## Background knowledge skill

Knowledge Claude needs in some situations that isn't an action a user would type, such as how a legacy system works.

- Set `user-invocable: false`. The skill leaves the `/` menu, and Claude loads it from its description.
- The description is the only way it loads: name the situations and files where it applies.

```yaml
---
name: billing-legacy-context
description: How the 2019 billing system stores invoices and why its totals differ from the new one. Use when reading or migrating code under billing/legacy/.
user-invocable: false
---
```

## Forked task skill

A self-contained task that runs in a new subagent, whose work stays out of the main conversation and only its result returns.

- Set `context: fork`, and name the subagent type in `agent` (`general-purpose` by default).
- Fork only a task. A forked skill of guidelines alone gives the subagent nothing to do, and it returns nothing useful.

Works, because it holds a whole task:

```yaml
---
name: map-dependencies
description: Maps which modules import a given module and reports the call sites.
context: fork
agent: Explore
---

Map every importer of $ARGUMENTS:
1. Find the imports with Glob and Grep
2. Read each call site
3. Return a list of files and lines, grouped by module
```

Fails, because it holds guidelines and no task:

```yaml
---
name: api-style
context: fork
---

Use RESTful names. Return consistent errors.
```

Choose `agent`, `background`, the inputs the fork carries and its tools in the subagents file of Phase 2.

## Preloaded knowledge skill

Knowledge a custom subagent carries from its start. The subagent lists the skill in its `skills` field, and the skill's full content is injected beside the task the subagent was given.

- Write it as reference content that applies to any task the subagent gets, not to "the user's request" or to the conversation that spawned it.
- Leave out `disable-model-invocation: true`: a skill with it can't be preloaded.

| Approach | System prompt | Task | Also loads |
| :-- | :-- | :-- | :-- |
| Forked task skill | The agent type's | The `SKILL.md` content | CLAUDE.md, except for Explore and Plan |
| Preloaded knowledge skill | The subagent's body | Claude's delegation message | The preloaded skills and CLAUDE.md |

Choose the subagent's side in the subagents file of Phase 2.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Compare similar features](https://code.claude.com/docs/en/features-overview#compare-similar-features) when the need sits between a skill and another feature. It compares a skill with CLAUDE.md, rules, subagents, MCP, hooks and output styles, pair by pair, with the case each one fits.
- Read [How skill triggering works](https://agentskills.io/skill-creation/optimizing-descriptions#how-skill-triggering-works) when the task may be simple enough for Claude to do without the skill. It explains which tasks make an agent consult a skill and which it handles alone.
- Read [Types of skill content](https://code.claude.com/docs/en/skills#types-of-skill-content) when it isn't clear whether the content is knowledge or a procedure. It shows both kinds side by side and gives the conciseness test for the body.
- Read [Control who invokes a skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) when the skill is user-only or Claude-only. It tables who can invoke the skill and what loads into context for each field, and lists what each field prevents.
- Read [Run skills in a subagent](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent) when the skill runs forked. It covers the cases where Claude Code waits for the result even in the background, the narrower tool set of a background fork, its edits outside checkpoints, and the `agent` options.
- Read [Preload skills into subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents) when a subagent will carry the skill. It covers the limit of 32 names, which skills can't be preloaded, and how to stop a subagent from invoking skills.
- Read [Claude stops following a skill](https://code.claude.com/docs/en/skills#claude-stops-following-a-skill) when a rule in the skill must hold on every turn. It says when to move the rule into a hook in the skill's `hooks` frontmatter, and how to word guidance that applies to the whole task.
- Read [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) when you write `paths`, `arguments` or `argument-hint`. It gives each field's exact syntax and default.
- Read [Where Skills work](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#where-skills-work) when the skill must also work on claude.ai or the API. It says which surfaces offer pre-built skills and which take custom skills.
- Read [Restrict Claude's skill access](https://code.claude.com/docs/en/skills#restrict-claude%E2%80%99s-skill-access) when you tell users how to approve or block the skill. It gives the exact and prefix forms of `Skill(...)` rules, and what a deny rule also blocks.
- Read the [Claude Code changelog](https://code.claude.com/docs/en/changelog) when the skill runs in scheduled tasks or `/loop`. It records the prompt those runs show before a skill with `allowed-tools` or hooks, and any later change to it.
