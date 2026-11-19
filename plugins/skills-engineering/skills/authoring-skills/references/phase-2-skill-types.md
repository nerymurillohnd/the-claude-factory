# Phase 2: Skill types

The six types of skill, how to choose one, and what each type changes in the skill you write.

## Gotchas

- A skill with `disable-model-invocation: true` runs only when the user invokes it, and Claude never loads it on its own: leave the field out of a skill Claude must load proactively.
- A skill with `user-invocable: false` leaves the `/` menu and doesn't run when typed: only Claude loads it, from its description.
- A forked skill that holds guidelines and no task returns nothing useful: fork only a complete task.

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

Conventions, patterns, style guides or domain rules that Claude applies alongside the conversation. Write the rules as standing guidance for any work they touch, not as steps, and set `paths` when they apply only to certain files.

```markdown
<!-- Weak: knowledge as steps, so Claude runs it once instead of applying it to all billing work -->
1. Open the invoice code
2. Check the amounts are in cents

<!-- Strong: standing rules that apply to any work on invoices -->
When code creates an invoice:
- Store amounts in cents as integers
- Round tax per line, then sum
```

## Task skill

Step-by-step instructions for one action that Claude may also start on its own, such as generating a report.

## User-only task skill

A procedure with side effects or timing the user must control, such as deploying, sending, publishing or paying.

## Background knowledge skill

Knowledge Claude needs in some situations that isn't an action a user would type, such as how a legacy system works. The description is the only way it loads, so it names the situations and files where it applies.

## Forked task skill

A self-contained task that runs in a new subagent, whose work stays out of the main conversation and only its result returns.

```markdown
<!-- Weak: guidelines and no task, so the forked subagent returns nothing useful -->
---
name: api-style
context: fork
---

Use RESTful names. Return consistent errors.

<!-- Strong: a whole task, with its input and what to return -->
---
name: map-dependencies
description: Maps which modules import a given module and reports the call sites.
context: fork
agent: Explore
---

Map every importer of $ARGUMENTS and return the files and lines, grouped by module.
```

## Preloaded knowledge skill

Knowledge a custom subagent carries from its start, injected in full beside the task the subagent was given. Write it as reference content for any task the subagent gets, not for "the user's request" or the conversation that spawned it. The subagents file of Phase 2 covers both sides of a fork and a preload.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Types of skill content](https://code.claude.com/docs/en/skills#types-of-skill-content) when it isn't clear whether the content is knowledge or a procedure. It shows both kinds side by side.
- Read [Control who invokes a skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) when the skill is user-only or Claude-only. It tables who can invoke the skill and what loads into context for each field.
- Read [Run skills in a subagent](https://code.claude.com/docs/en/skills#run-skills-in-a-subagent) when the skill runs forked. It covers the `agent` options and how a fork runs.
- Read [Preload skills into subagents](https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents) when a subagent will carry the skill. It covers which skills can be preloaded.
