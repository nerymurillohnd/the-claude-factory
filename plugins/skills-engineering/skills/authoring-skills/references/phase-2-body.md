# Phase 2: Body

What the body of the skill must carry, and how to build its task: workflows, checklists, validation loops, plan-validate-execute, output templates and gotchas.

## Contents

- [Gotchas](#gotchas)
- [What the body must carry](#what-the-body-must-carry)
- [The form fits the failure](#the-form-fits-the-failure)
- [Workflows](#workflows)
- [Checklists](#checklists)
- [Validation loops](#validation-loops)
- [Plan, validate, execute](#plan-validate-execute)
- [Output templates](#output-templates)
- [Write the skill's gotchas](#write-the-skills-gotchas)
- [Official sources](#official-sources)

## Gotchas

- Once the skill loads, its content stays in the conversation and Claude Code doesn't read the file again. After compaction it keeps only the first 5,000 tokens of each skill invoked, within 25,000 tokens shared by all of them. Put the guidance for the whole task near the top, as standing instructions such as "after every edit".
- The task tools, such as `TaskCreate`, aren't available in every session. A skill that tracks its progress with them can fail silently: give it a checklist Claude copies into its reply instead.
- A confirmation needs someone to answer. In a subagent or an unattended run nobody can, so a skill that asks before acting needs a default to take and a report to return.

## What the body must carry

- Name the kind of work the skill serves and the disciplines that govern it, and derive from them the knowledge, methods, tools, failure modes and quality criteria the skill must carry.
- Ask of each line whether Claude would do this differently, or not know how, without it. Keep the domain's procedure and its reasons, conventions, facts that defy assumptions, exact tools and commands, and the corrections the user keeps making. Cut what any capable model knows, and point to a page for the rest.
- The costlier an error in the domain, the more evidence, verification and human control the skill requires.
- Use only the mechanisms below the task needs: each costs attention.

## The form fits the failure

| The failure | The form |
| :-- | :-- |
| Output in the wrong shape | A template, or input and output examples |
| An element Claude can't infer | The fact where it applies, or a gotcha |
| An action that depends on a condition | The condition and both branches |
| A judgment made inconsistently | The criterion and its reason |
| A rule skipped under pressure | The rule, each shortcut around it closed, and a hook if it must always hold |
| Code rewritten on every run | A script |

## Workflows

- Write numbered steps when the order matters: a step uses what an earlier one produced, or skipping one breaks a later one. Write goals and criteria when the order depends on what Claude finds, as in a review.
- Give each step one action, with its input, its command or method, and its output.
- Add only the controls a step needs:
  - Gate: a check that must pass before the next step starts.
  - Decision point: where the path forks, with a condition Claude can check and where each branch goes.
  - Exit condition: what must be true before a long workflow moves on.
  - Loop back: when a later step can reveal a gap, a return to an earlier step, with a limit on the rounds.
- Move a long branch or variant to its own file, and point to it from the decision point, so Claude reads only the branch it takes.

## Checklists

- Progress checklist: Claude copies it into its reply and ticks each item as it works. Use it for a long workflow with dependencies or gates, where Claude would lose its place.
- Verification checklist: Claude checks its finished output against it. Use it when the output can be wrong in ways Claude doesn't notice while producing it. Each item names something observable and fails on a bad output.

```text
# Weak: an item that passes whatever the output
- [ ] All requirements are met.
# Strong: an item that fails on a bad output
- [ ] The journal's debits equal its credits, to the cent.
```

## Validation loops

Do the work, run a validator, fix what it reports, and repeat until it passes. Use a loop where a step's errors are common and cheap to detect, so they are caught at the step that made them.

- Script: when the check is mechanical, such as a schema, a format or a cross-reference. Its errors name what to fix.
- Document: when the check is against written rules, such as a style guide.
- Self-check against stated criteria: when only judgment can check it. "Review your work" alone checks nothing.

Give the loop its stop: a number of rounds, or no gain over the last round. When the same error returns after a fix, stop and report it.

## Plan, validate, execute

For batch, destructive or costly work, Claude writes the intended changes to a changes file, such as `changes.json`, validates it, and only then applies it:

1. Analyze the input.
2. Write the changes to the changes file.
3. Validate it: every target exists, nothing conflicts, nothing required is missing.
4. Show the changes file to the user when they must approve, and wait.
5. Apply the changes.
6. Verify the result.

The changes file can be fixed and checked again without touching the originals.

## Output templates

Give a template when the output has a fixed shape, strict or flexible, inline or in `assets/`, as the embedding file of Phase 2 shows.

## Write the skill's gotchas

A gotcha is a fact of the environment or domain that defies a reasonable assumption, so Claude gets it wrong unless told: the export whose amounts are in cents, the sandbox API that accepts any key but never sends email. Leave out general advice: it isn't a gotcha unless a capable model would get it wrong.

- Put the gotchas in `SKILL.md`, before the steps they affect: Claude must know them before it reaches the situation.
- Put a gotcha that affects only one variant in that variant's file, before the steps it affects, and give the pointer to that file a condition Claude can recognize: for a non-obvious trap, Claude may not see that the file applies.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Skill content lifecycle](https://code.claude.com/docs/en/skills#skill-content-lifecycle) when the skill guides a long task. It says how content stays in the conversation and what survives compaction.
- Read [Task tool availability](https://code.claude.com/docs/en/tools-reference#task-tool-availability) when the skill tracks progress. It says which sessions offer the task tools.
- Read [Workflows and feedback loops](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#workflows-and-feedback-loops) when the task has many steps or a loop. It shows a copied checklist and a validator loop in a skill.
- Read [Checklists for multi-step workflows](https://agentskills.io/skill-creation/best-practices#checklists-for-multi-step-workflows), [Validation loops](https://agentskills.io/skill-creation/best-practices#validation-loops) and [Plan-validate-execute](https://agentskills.io/skill-creation/best-practices#plan-validate-execute) when you build one of those mechanisms. They show each with a worked example.
- Read [Gotchas sections](https://agentskills.io/skill-creation/best-practices#gotchas-sections) when you write the skill's gotchas. It says what a gotcha is and why it belongs before the situation.
- Read [Calibrating control](https://agentskills.io/skill-creation/best-practices#calibrating-control) when you decide how strict a step is. It matches specificity to fragility.
