# Name and description

How to choose a skill's name and write its description, and how to test that the description triggers the skill when it should and only then. The description decides whether the skill is ever used: at startup the model sees only each skill's name and description, and picks from those alone.

## Contents

- Choose the name
- What the description must carry
- Point of view and phrasing
- Length by surface
- when_to_use
- Placeholders and characters
- Correct and incorrect descriptions
- Test the triggering

## Choose the name

Rules the specification and uploads to claude.ai and the Skills API enforce. Follow them for every skill, so it can leave Claude Code later; a plugin-root `SKILL.md` is the one exception to the folder match, because its folder is the plugin's:

- 1-64 characters, lowercase letters, digits and hyphens; no leading, trailing or doubled hyphen.
- Matches the folder name exactly.
- For uploads: no XML tags, and neither `anthropic` nor `claude` anywhere in it.

Choosing among valid names:

1. Name the activity or capability the skill gives, so the name alone tells the model and its users what it is for. Prefer the gerund form, such as `exporting-invoices` or `writing-release-notes`. A noun phrase (`invoice-export`) or an action form (`export-invoices`) is acceptable.
2. Follow the pattern of the sibling skills in the same plugin or folder, even when it isn't the gerund: a consistent set is easier to reference and search.
3. Avoid names that say nothing about the task (`helper`, `utils`, `tools`) or cover too much (`documents`, `data`, `files`).
4. Don't repeat the plugin name inside a plugin skill's name: the command is already `/<plugin>:<name>`.
5. Check the name isn't taken by a bundled skill, a built-in command, or a skill at a higher-precedence location, unless replacing it is the intent. Read [skill-types.md](skill-types.md) for the names Claude Code reserves.

Propose the name with its reason and alternatives; the requester decides. Changing an existing skill's name breaks every place that invokes it, so keep it unless the requester asks.

## What the description must carry

The description is what the model compares the user's request against. It must let the model answer two questions without opening the skill: what does this do, and is this request one of its cases?

Put in it:

1. **What the skill does in its key use case**, in terms of the outcome, not the mechanism. It comes first: Claude Code truncates long descriptions in its listing, so the end is lost first.
2. **When to use it**, as the situations and requests that call for it, in the words its users actually say.
3. **Requests that never name the domain**, when those are common: "even if they don't say 'invoice'". Models tend to skip skills for tasks they think they can do alone, so a description that is slightly insistent about its cases triggers better.
4. **The boundary**, when a near-miss request or a sibling skill shares its keywords: "Not for X, which [sibling] does." Name what it is not for only where confusion is likely.

Leave out:

- A summary of the skill's steps. The model may follow the summary instead of reading the body.
- How the skill is built (its files, scripts, phases).
- Claims about quality ("expert", "comprehensive", "best practices").

## Point of view and phrasing

- Write in the third person: the description is injected into the system prompt, and "I can help you" or "You can use this" confuses who is speaking.
- Open with what it does as a verb in the third person ("Generates", "Reviews", "Converts"), then "Use when ..." for the triggers.
- Use the domain's concrete nouns: file types (`.xlsx`), tools (`BigQuery`), artifacts (`commit message`), and the phrases users type.
- Write one description per skill, never one that tries to serve two unrelated skills: split the skill instead.

## Length by surface

- **Spec, claude.ai and Skills API**: at most 1,024 characters, non-empty, no XML tags. Above the limit the upload fails.
- **Claude Code**: doesn't reject a longer `description`, but its listing cuts `description` plus `when_to_use` at 1,536 characters by default (configurable with `skillListingMaxDescChars`). Text past the cut never reaches the model. The whole listing also has a budget, 1% of the context window by default (`skillListingBudgetFraction`); when it overflows, Claude Code drops the descriptions of the least-used skills first.
- A description within its surface's limit is not too long. Cut it only for a reason: a duplicate, a workflow summary, or words that don't help the model choose.
- A description far shorter than its cases need is a defect: "Handles invoices" triggers on everything or nothing.

For a skill that runs on several surfaces, keep under 1,024 characters.

## when_to_use

A Claude Code-only field appended to the description in the listing and counted in the same 1,536-character cut. Use it when a Claude Code-only skill has many trigger phrases or example requests that would crowd the description. Never set it on a skill that is uploaded to claude.ai or the API: the upload fails on the unknown key.

## Placeholders and characters

- Claude Code shows `<` and `>` in `description` and `when_to_use` as `&lt;` and `&gt;`, and the platform refuses XML tags. Write placeholders in square brackets, `[branch]`, or move them to `argument-hint`.
- A YAML value containing `: ` (colon and space) or starting with a quote or special character must be quoted, or the YAML fails to parse and the skill loads with no description. Prefer wording that needs no quotes.

## Correct and incorrect descriptions

Vague:

```yaml
description: Handles invoices.
```

Specific about what and when:

```yaml
description: Extracts line items, totals and tax from supplier invoices in PDF or image form and exports them to CSV. Use when the user shares an invoice, asks to digitize receipts, or needs invoice data in a spreadsheet.
```

Missing triggers:

```yaml
description: Writes changelog entries.
```

With the requests that should load it:

```yaml
description: Writes changelog entries from merged pull requests in Keep a Changelog format. Use when the user asks for release notes, a changelog update, or what changed since the last tag.
```

Mechanics instead of intent:

```yaml
description: Runs parse_csv.py, then aggregate.py, then renders report.md from the template.
```

Intent, in the users' words:

```yaml
description: Builds the weekly sales report from the CRM export. Use when the user asks for this week's sales numbers, a sales summary or the regional report, even if they only paste a CSV.
```

Overlapping a sibling skill with no boundary:

```yaml
description: Works with pull requests.
```

With the boundary that separates it from its sibling:

```yaml
description: Reviews a pull request's code for bugs and style. Use when the user asks to review, check or comment on a PR. Not for merging or fixing CI, which pr-lifecycle does.
```

## Test the triggering

Test when the model invokes the skill on its own and other skills or general knowledge compete for the same requests. Skip it for a skill only users invoke.

1. Write about 20 realistic requests: 8-10 that should load the skill and 8-10 that should not.
   - Should-trigger: vary the phrasing (formal, casual, with typos), how explicit it is, and how much detail it carries, including requests that never name the domain.
   - Should-not-trigger: near-misses that share keywords but need something else, not obviously unrelated requests.
   - Make them concrete, as users write them: file paths, column names, personal context, a pasted error.
2. Run each request about three times in a fresh session with the skill installed, and record how often the skill loads. A request passes when its rate is above 0.5 for should-trigger, and below it for should-not-trigger.
3. Split the set about 60/40 into a set you tune against and a set you only check. Change the description from the patterns of failures in the first set, never by pasting keywords from a failed request.
4. Stop when the held-out set passes or after about five rounds. Keep the version that scored best on the held-out set, not the last one.

Run the same requests against the old description when changing an existing one, and keep the change only if it scores higher. Read [validation.md](validation.md) for running the runs with `claude plugin eval` in a plugin.
