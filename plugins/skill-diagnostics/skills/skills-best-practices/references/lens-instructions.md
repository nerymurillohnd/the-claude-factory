# Instructions lens

What the instructions reviewer checks: whether the body and its workflows tell the agent what it lacks, in the right order, with the patterns the skill's profile requires.

## Contents

- [Items](#items)
- [Method](#method)

## Items

Each line names the checklist item from [checklist.md](checklist.md), then the area file and heading that hold the rule, then the rule's bold lead-in. Read the rule there; it is not repeated here.

- `BS-2` · [body-and-structure.md#structure-and-supporting-files](body-and-structure.md#structure-and-supporting-files) · **Say when to load each file.**
- `BS-2` · [body-and-structure.md#structure-and-supporting-files](body-and-structure.md#structure-and-supporting-files) · **Three organizing patterns**
- `BS-2` · [body-and-structure.md#structure-and-supporting-files](body-and-structure.md#structure-and-supporting-files) · **Descriptive file names**
- `BS-2` · [body-and-structure.md#structure-and-supporting-files](body-and-structure.md#structure-and-supporting-files) · **Keep reference files focused**
- `BS-2` · [body-and-structure.md#paths-and-placeholders](body-and-structure.md#paths-and-placeholders) · **Paths that work on every surface.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Start from real expertise.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Add what the agent lacks, omit what it knows.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Explain why only where it changes behavior.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Prefer a reason to emphatic wording.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Design a coherent unit.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Aim for moderate detail.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Match specificity to fragility.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Give defaults, not menus.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Teach procedures, not answers.**
- `BS-5` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Write a Gotchas section.**
- `BS-6` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Use one term per concept**
- `BS-6` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Avoid time-sensitive text.**
- `BS-6` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Name MCP tools in the form of the surface you ship to.**
- `BS-7` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Provide templates and examples for output.**
- `BS-8` · [workflows.md#when-to-use-these-patterns](workflows.md#when-to-use-these-patterns)
- `BS-8` · [workflows.md#checklist-for-a-multi-step-workflow](workflows.md#checklist-for-a-multi-step-workflow)
- `BS-8` · [workflows.md#validation-loop](workflows.md#validation-loop)
- `BS-8` · [workflows.md#plan-validate-execute](workflows.md#plan-validate-execute)
- `BS-8` · [workflows.md#fit-each-pattern-to-the-skill](workflows.md#fit-each-pattern-to-the-skill)
- `BS-8` · [workflows.md#conditional-workflow](workflows.md#conditional-workflow)
- `BS-8` · [workflows.md#say-when-the-work-is-done](workflows.md#say-when-the-work-is-done)
- `BS-10` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Write standing instructions.**
- `BS-12` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **State what running the skill authorizes.**
- `BS-12` · [body-and-structure.md#writing-the-body](body-and-structure.md#writing-the-body) · **Give a forked or preloaded skill a closed contract.**
- `BS-13` · [body-and-structure.md#order-of-blocks-in-skillmd](body-and-structure.md#order-of-blocks-in-skillmd)

## Method

1. Read the area file each pointer names at the step that uses it.
2. Passage by passage through `SKILL.md` and every reference: would the agent get this wrong without it? Mark each passage that only says what the agent already knows.
3. For each part, name its fragility (many valid approaches, a preferred pattern, or a fragile operation) and check that the level of control matches it.
4. At each choice the skill offers, check for one default with an escape hatch, not a menu.
5. Take the profile from the brief. For each pattern it makes required, check that the pattern is present and fits the skill's own steps; for each pattern it makes unnecessary, check that the skill doesn't carry it.
6. Read `SKILL.md` top to bottom and note where each rule first appears; a rule that first appears after the step it governs is a finding.
7. For each rule written in prose as one that must always hold, check whether it should be a hook.
8. Track the terms the skill uses for each concept across all files; a concept with two names is a finding.
