# Phase 2: Name and description

Decide the skill's name and write its description, from everything decided before. This file covers:

- name rules
- how a name becomes a command, and name clashes
- description rules
- examples of descriptions

## Name rules

- At most 64 characters, in lowercase letters, digits and hyphens. No hyphen at the start or the end, and no two in a row.
- It matches the skill's folder name.
- No XML tags, and no `anthropic` or `claude`.
- Name the activity the skill gives, in the gerund form when siblings don't follow another pattern: `exporting-invoices`. Avoid names that say nothing (`helper`, `utils`) or cover too much (`data`).
- In a plugin skill, write the bare name. Claude Code adds the plugin prefix.
- Don't name a folder `synced`, in any capitalization: Claude Code skips it. Outside a plugin, a name that is or starts with `anthropic-skills` doesn't load.
- Claude Code refuses a name that has a zero-width space or other control character, a private-use or unassigned character, a text-direction character, a blank other than one plain space between words, or `<` or `>`.
- Propose the name with alternatives and the reason.

## From name to command

- Personal or project skill: the command is `name`, or the folder name when `name` is missing.
- Plugin skill: `/plugin-name:name`. `name` replaces the folder's name in the last segment.
- Single skill at a plugin root: `name` is the whole last segment. Always set it.
- Skill in an added directory: it gets the directory's folder name as a prefix, such as `/cli:verify`, when its name clashes with another skill (Claude Code 2.1.309 and later).

## Name clashes

Check the names found in the user's environment before you choose one.

- Enterprise beats personal, and personal beats project. A skill of any of them replaces a bundled or built-in command of the same name, but not that command's aliases.
- A plugin skill never clashes: both load, because its name has the plugin prefix.
- A synced claude.ai skill loses its short name to any other skill or command and runs under its full name.

Read [Resolve skills that share a name](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name) when the name may clash.

Read [How a skill gets its command name](https://code.claude.com/docs/en/skills#how-a-skill-gets-its-command-name) when the location is not a plain skill folder.

## Description rules

The model reads only the description when it decides whether to load the skill, and it matches it against the user's request.

- Say when to use the skill and what it does. Open with a "Use…" clause when the trigger is what tells the skill apart: "Use when…", "Use only when…", "Use every time…", "Use for…". When what the skill does is what tells it apart, open with that. Never bury the key use case behind long lists.
- Describe what the user is trying to achieve, in the words users say, not the skill's mechanics.
- List the contexts where it applies, most likely first, including requests that never name the domain. Models tend to skip a skill for a task they think they can handle alone.
- Name the boundary with any sibling skill that shares its keywords.
- Write in the third person. The "Use…" opening is the one imperative.
- Keep it to a few sentences or a short paragraph, at most 1,024 characters. Claude Code cuts the description and `when_to_use` together at 1,536 characters, and the end is lost first.
- Write placeholders in square brackets: angle brackets show as escaped text. No XML tags.
- For a skill only users invoke, the description reaches no model. Write it for the user who picks the command.

Before you settle it, list the requests that should load the skill and the near-misses that shouldn't, and check the description picks right for each.

Read [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) when you need to test whether a description triggers.

Read [Writing effective descriptions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions) when you need more examples.

## Examples

Vague, so it triggers on everything or nothing:

```yaml
description: Handles invoices.
```

Specific about when to use it and what it does:

```yaml
description: Use when the user shares a supplier invoice, asks to digitize receipts, or needs invoice data in a spreadsheet, even if they never say "invoice". Extracts line items, totals and tax from PDF or image invoices into CSV.
```

Mechanics instead of intent, so it matches no request a user would type:

```yaml
description: Runs parse_csv.py, then aggregate.py, then renders report.md from the template.
```

Intent, in the users' words:

```yaml
description: Use when the user asks for this week's sales numbers, a sales summary or the regional report, even if they only paste a CSV. Builds the weekly sales report from the CRM export.
```

Overlapping a sibling skill, so the model picks either one:

```yaml
description: Works with pull requests.
```

With the boundary that separates it:

```yaml
description: Use when the user asks to review, check or comment on a pull request's code. Reviews it for bugs and style. Not for merging or fixing CI, which pr-lifecycle does.
```
