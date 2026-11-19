# Design proposal: [skill name]

Version [n], [YYYY-MM-DD]. [What changed since the last version, or "First version"]

## Understanding

[What you understood the user wants, in their terms, and what lies behind the request]

## Goal

[The goal the skill must meet, in one sentence]. Success: [what its users get when it works]

## Use cases

[Each request the skill must serve, in the words a user would write, and its expected result]

## Its users

[Who will run the skill, and how they invoke it: the user, Claude, a subagent, a scheduled task]

## Environment

- Where you work: [surface, machine, project; "same as below" when the skill runs where you work]
- Where the skill runs and is served from: [location and surfaces, with the reason]
- What already loads there: [each overlap or friction found and where it lives; its decision goes under Decisions taken]

## Domain sources

[Each area and technology the skill draws on, with its version or edition, each source you read with its URL and date, and the facts from it that shape the skill]

## Skill type

[One of the six types, with the reason]

## Base architecture

Not final: the plan settles each file.

- Components: [each one the skill needs, such as references, scripts, assets, hooks, injected commands, subagents, MCP tools or other skills, with the failure it prevents]
- Folders: [a sketch of the skill's folder tree]
- Content split: [what stays in SKILL.md, and what goes to which file behind which condition]

## Frontmatter

[Each field and its value, with the reason]

## Name and description

- Name: [proposed name], because [reason]. Alternatives: [one or two names]
- Description: [the draft text]

## Decisions taken

[Each choice made with the user during phases 1 and 2, including each overlap or friction, and its reason]

## Open questions

[What the user still decides, each with your recommendation. Settle each one before the design is approved; "None" when nothing is open]
