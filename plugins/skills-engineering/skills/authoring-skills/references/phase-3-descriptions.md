# Phase 3: Descriptions

How to write the skill's description: when to use it and what it does, in the words its users say, and the boundary with its sibling skills, with correct and incorrect pairs and the reason each difference matters.

## Descriptions

The model reads only the description when it decides whether to load the skill, matching it against the user's request. Write it to that end:

- Write the condition of use as an imperative "Use…" clause: the model is deciding whether to act, so tell it when to act. Fit its form to the skill: "Use when…" for a skill picked by the request, "Use only when…" for narrow cases, "Use every time…" for a step that must always run, "Use for…" for a base skill. The words "this skill" are not needed.
- Decide where the clause goes. For a skill served by Claude Code, open with it when the trigger is what tells the skill apart: the Claude Code docs ask to put the key use case first and lead with words a request would contain. When what the skill does is what tells it apart, open with that, as Anthropic's guide to building skills shows. Never bury the key use case behind long lists.
- A skill with `disable-model-invocation: true` is read by the user picking the command, not by the model: write its description for that reader.
- Say both when to use the skill and what it does: Claude Code's listing truncates long descriptions, and the end is lost first.
- Describe what the user is trying to achieve, in the words users actually say, not the skill's internal mechanics: the model matches against the request, not against how the skill works.
- Be insistent about its cases. List the contexts where it applies, including requests that never name the domain ("even if they don't mention 'invoice'"): models tend to skip a skill for a task they think they can handle alone.
- Name the boundary with any sibling skill that shares its keywords.
- Write in the third person, never "I can" or "you can": the description goes into the system prompt.
- Keep it concise: a few sentences to a short paragraph, at most 1,024 characters for a skill that may leave Claude Code. Claude Code's listing cuts the description at 1,536.
- Write placeholders in square brackets: angle brackets show as escaped text.

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
