# Output template

Two templates: the prompt deliverable, for any prompt that is not the text of something Claude loads, and the reply around it, for every delivery.

## Prompt deliverable

This frontmatter plus the clean prompt body:

```markdown
---
title: <kebab-case-title>
objective: <observable outcome>
prompt_type: <agent | coding | research | analysis | extraction | writing | support | other>
target_model: <fable-5-1 | mythos-5-1 | opus-5-5 | opus-5 | sonnet-5-5 | other>
surface: <claude-app | claude-code | api | agent-harness>
effort: <low | medium | high | xhigh | max | not-applicable>
output_language: <language code, for example en>
required_capabilities:
  - <none | web-search | tools | structured-output | vision | long-context>
version: 1.0.0
---

<prompt body, ready to paste>
```

### Field rules

- `target_model`: from the list in "References" in `SKILL.md`.
- `effort`: the level chosen at step 4. On `claude-app` or `claude-code`, verify that the surface exposes the setting (see "Gotchas" in `SKILL.md`). Use `not-applicable` only when the model, or the surface once verified, has no effort setting; if you cannot verify, write the recommended level and list it under assumptions.
- `output_language`: the language of the people or inputs the target model will serve; ask only when that is unclear and it matters, as one of the questions of the clarify round. Since the frontmatter is not pasted, the body states the language when it matters. Write the prompt body itself in English unless the user asks otherwise.
- `required_capabilities`: only what the prompt needs; `none` when it needs nothing.
- `stage`: only for a fixed automated chain.
- `version`: `1.0.0` for a new prompt and for a draft without one. When revising, raise the last number for a wording-only change, the middle one for a change of content, and the first one for a migration to another target model.

## Reply around the deliverable

Write the headings and the text in the user's language and in plain words; the prompt body stays in English unless they asked otherwise. Drop a line or section whose condition does not hold.

```markdown
<the fenced prompt, or one fenced block per stage for a fixed chain>

**How to run it**
- **Model and effort:** <model> at <effort>. <one-line reason for each>
- **Where:** <session mode and surface>. <reason>
- **Configuration:** <API or agent harness only: the settings the prompt depends on>
- **Skills:** <the skills the prompt relies on>

**Follow-up:** <first of several prompts, or a result to review before acting: what to bring back and what you will assess in it; for a fixed chain, what each stage receives>

**Design notes**
- <key decision>: <the reference, or the live page with its URL>
- <anything added beyond the request>: <why>

**Assumptions and limitations**
- <only the unavoidable ones>

<one line inviting the user back if the result misses the goal; skip it when Follow-up already asks for the output>
```
