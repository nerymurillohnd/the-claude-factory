# Output template

Two templates: the prompt deliverable, for any prompt that is not the text of something Claude loads, and the reply around it, for every delivery. Read the instructions, then fill the templates below them.

## How to fill the prompt deliverable

Use this exact structure: the metadata is the user's record of the prompt.

- Put the deliverable in a fenced Markdown block. Use a fence longer than any fence inside the prompt: four backticks when the prompt contains triple-backtick code blocks.
- The block holds the metadata, then the clean prompt body.
- Replace every placeholder with an actual value; leave none in a completed deliverable.
- `target_model`: always set; `other` only for a model outside the covered models, with the model named in `objective`.
- `effort`: the level chosen in Step 2 (model selection). On `claude-app` or `claude-code`, verify that the surface exposes the setting. Use `not-applicable` only when the model, or the surface once verified, has no effort setting; if you cannot verify, write the recommended level and list it under assumptions.
- `session_mode`: the session chosen in Step 3 (session mode selection), `interactive` or `non-interactive`.
- `claude_code_mode`: `plan` or `execution` when the surface is `claude-code`; `not-applicable` on any other surface.
- `output_language`: the language of the people or inputs the target model will serve.
- `required_capabilities`: only capabilities the task actually needs, from `web-search`, `tools`, `structured-output`, `vision`, `long-context`; an empty list when it needs none.
- `version`: `1.0.0` for a new prompt and for a draft without one. When revising, raise the last number for a wording-only change, the middle one for a change of content, and the first one for a migration to another target model.
- `stage`: only for a fixed automated sequence, as `"1/3"` or the matching equivalent, one block per stage.

## How to fill the reply

The reply template is a sensible default: adapt it to the request.

- Write the headings and the text in the user's language. Keep the commentary proportionate to the task.
- Include only the items that apply; leave out a section with nothing to say, and add no generic invitation to continue.
- **Model and effort:** verified recommendations, or the limitation that kept you from verifying them.
- **Session mode:** interactive or non-interactive, plan mode or execution for Claude Code, the one reason that decided it, and how to start that mode. It must match `session_mode` and `claude_code_mode`.
- **Where and setup:** confirm on its official page that a product mode or feature exists on the user's surface before recommending it. For the API or an agent harness, give the configuration the prompt depends on.
- **Design notes:** consequential choices, assumptions and changes, and anything added beyond the request with why. In an audit, list the draft's problems before the fixed version and say here how each was fixed. A drift report goes here when the live documentation contradicted the skill.
- **Follow-up drafts:** only when the design calls for follow-ups. One block per draft after the prompt, marked **Draft**, with no metadata, each preceded by the output it waits for, what you will assess in it and the assumptions it rests on.
- **Next step:** the exact action or artifact needed when continuation is useful.
- **Sources:** the URL of every official page you read for a technical recommendation.
- Keep citations, configuration notes and commentary outside the copy-ready prompt unless the task requires them inside it.

## Prompt deliverable

```markdown
---
title: <kebab-case-title>
objective: <observable outcome in one line>
prompt_type: <agent | coding | research | analysis | extraction | writing | support | other>
target_model: <fable-5-1 | fable-5 | opus-5-5 | opus-5 | sonnet-5-5 | other>
surface: <claude-app | claude-code | api | agent-harness>
effort: <low | medium | high | xhigh | max | not-applicable>
session_mode: <interactive | non-interactive>
claude_code_mode: <plan | execution | not-applicable>
output_language: <language code, for example en>
required_capabilities: []
version: 1.0.0
---

<prompt body, ready to paste>
```

## Reply around the deliverable

```markdown
<the fenced prompt, or one fenced block per stage for a fixed sequence>

**Follow-up drafts** <only when the design calls for follow-ups>
- **Draft 2:** waits for <the output>; I will assess <what>; it assumes <what>.
  <fenced draft>

**Recommendation:** <the approach and its reason>

**Model and effort:** <model> at <effort>. <one-line reason for each>

**Session mode:** <interactive or non-interactive; plan mode or execution in Claude Code>. <one-line reason; how to start it>

**Where and setup:** <surface; tools and permissions; for the API or an agent harness, the configuration outside the prompt>

**Design notes**
- <decision, assumption or change>: <its reason>
- <anything added beyond the request>: <why>

**Next step:** <what to bring back and what you will assess, when continuation is useful>

**Sources**
- <URL of each official page read>
```
