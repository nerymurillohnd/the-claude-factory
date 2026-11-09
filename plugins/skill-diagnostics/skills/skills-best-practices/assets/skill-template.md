---
name: <skill-name, the same as the folder name>
description: <What the skill does, in the third person, main use case first. Use when <the requests and contexts, in the words users type>, even if they don't name <the domain>. Not for <the kind of request where it ends>.>
---

# <Skill title>

<Purpose: one or two sentences on what the skill produces.>

Inputs: <each input and where it comes from>.
Done when: <the condition that ends the work>.

## Standing rules

- <A default or rule that holds for the whole task.>
- <What running the skill authorizes, and what still needs the user, when it has side effects.>

## Gotchas

- <A concrete, environment-specific fact that defies a reasonable assumption.>

## Workflow

Copy this checklist and tick each item as you complete it:

```
Task Progress:
- [ ] Step 1: <action> (<file to edit or script to run>)
- [ ] Step 2: <action> (<file to edit or script to run>)
- [ ] Step 3: Validate <the output> (<validator>)
```

**Step 1: <action>.** <The exact action, the command or file, and what the step produces.>

**Step 2: <action>.** <The exact action. When it needs a reference: Read `[references/<file>.md](references/<file>.md)`.>

**Step 3: Validate <the output>.** <See Validation loop.>

If Step 3 fails, return to Step <n>.

## Validation loop

1. Validate: `python3 ${CLAUDE_SKILL_DIR}/scripts/<validator>.py <output>`, or check against each rule in `[references/<file>.md](references/<file>.md)`.
2. If validation fails, read the error or note each rule broken, fix, and validate again.
3. Proceed only when validation passes: <what passing means>.

## Output

<The output template, strict or flexible, and one input/output example.>

## Files

- `[references/<file>.md](references/<file>.md)`: read when <condition>.
- `[assets/<file>](assets/<file>)`: use when <condition>.
- `scripts/<file>`: run as `python3 ${CLAUDE_SKILL_DIR}/scripts/<file> <arguments>` when <condition>.

## Old patterns

<Legacy material, collapsed, or delete this section.>
