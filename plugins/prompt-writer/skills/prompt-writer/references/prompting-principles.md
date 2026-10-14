# Prompting principles (all current models)

Read for every prompt. Only the non-obvious, documented points are here; general prompt craft (clarity, XML tags, roles, numbered steps) is assumed. Model-specific files override this one. Where a technique was measured on one model, re-check it before relying on it for another.

## Instructions

- Ambition is not inferred. If above-baseline work is wanted, ask for it explicitly ("include as many relevant features as possible; go beyond the basics"), and request specific features (animations, interactivity) by name.
- Give the reason behind non-obvious rules; the model generalizes from the reason to cases the rule does not list.
- Wording is taken literally. "Can you suggest changes?" yields suggestions; "Change this function to..." yields edits.
- Positive examples of the desired style steer better than lists of what to avoid. Three to five relevant, diverse examples in `<example>` tags is the documented sweet spot; worked examples (problem, method, answer) also shape how the model reasons.
- Drop CRITICAL/MUST emphasis written for older models. Since Opus 4.5 and 4.6, models respond more strongly to the system prompt, so emphasis that once fixed undertriggering now causes overtriggering. When a tool undertriggers, explain when and why to use it.

## Long context (roughly 20k+ tokens)

- Put long documents above instructions and the query. Placing the question last measured up to a 30 percent quality gain in testing, most with several documents.
- Wrap each document as `<document index="n">` with `<source>` and `<document_content>` inside `<documents>`.
- Ask for relevant quotes first, then the task based on those quotes.

## Output and formatting

- Describe the desired format positively ("flowing prose paragraphs") rather than banning one ("no markdown"); match the prompt's own formatting to the output wanted.
- Fable 5.1 already formats sparingly; heavy anti-formatting blocks from older prompts suppress structure the content needs. State when formatting fits instead.
- Current models default to LaTeX for math; ask for plain text explicitly when needed.
- Ask for sentence or paragraph counts, not word counts.
- Current models may skip summaries after tool calls; ask for one if wanted.
- Use structured outputs, not prompt instructions, when JSON schema conformance must be guaranteed.

## Thinking

- Thinking is adaptive on current models and effort is the primary control. Lowering effort reduces thinking more reliably than prompt instructions.
- Prefer a general instruction ("think thoroughly about X") over a hand-written reasoning plan.
- Useful steering: reflect on tool results before the next action; commit to an approach and revisit only on contradicting evidence.
- Never ask the model to write its reasoning into the response (for example in `<thinking>` tags): all four target models may decline with `reasoning_extraction`. Request a brief rationale or a recap of actions; if the application needs the reasoning, set `thinking.display: "summarized"`.
- A self-check line ("before finishing, verify against [criteria]") helps most models; Opus 5 over-verifies with it.

## Chaining

Adaptive thinking and subagents cover most multistep work in one call. Chain separate calls only to inspect, log, or branch intermediate outputs, or to enforce a pipeline; the most useful chain is draft → review against criteria → refine.

## Migrating older prompts

- Remove prefill, `budget_tokens`, and non-default sampling parameters (the per-model status is in `model-selection-and-config.md`); use structured outputs, instructions, and effort.
- Dial back anti-laziness and "always use tools" language.
- Remove instructions that force visible reasoning.
- Remove scaffolding that forced interim status messages where the model already updates well; describe the cadence instead.
- Trim instructions written for prior models that default behavior now covers; they are often too prescriptive for Fable-class models.
- Then apply the target model's adjustments.
