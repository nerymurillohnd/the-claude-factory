# Step 4: Design the prompt

With the intent, the model, the effort and the session mode set, learn what the sources say for this case and shape the prompt before you write it. The design decides what the prompt says, in what form and why.

## Contents

- Read the sources
- Reading official pages
- Decide the design
- Verification rules

## Read the sources

- Apply the target model's prompting files read in Step 2, and the behavior differences its change page showed there.
- Read the prompting techniques `SKILL.md` links for this step, through their index by trigger: only the sections whose trigger the prompt meets. Read the cross-model criteria linked there too.
- Read any other official page this skill names when its condition applies, as Step 2 in `SKILL.md` says.
- Verify live whatever the prompt depends on that changes: products, APIs, tools, commands, file formats, features, prices, rules.
- Where a general page and the target model's prompting files differ, the model's prompting files win.

## Reading official pages

These rules apply to every official page read live, and to the samples in this skill's files; a quick read takes a page's samples at face value.

1. **A technique that names a model was measured on that model.** When that model is not the target, treat the technique as a pattern and confirm it in the target model's prompting files before using it.
2. **Read every note, tip and warning box.** Restrictions often sit in a note under a section whose title still teaches an older technique: prefill, `temperature` and `budget_tokens` appear as techniques in older sections, and a note says they are not supported or return a 400 error on newer models.
3. **Prose outranks code samples.** A code sample can contradict its own page, for example a tiny `max_tokens` value on a model whose thinking counts toward `max_tokens`.
4. **"In Anthropic's testing" carries its conditions.** Note the model, effort level and task type of every measured claim. A result measured at `low` effort on coding does not transfer to `high` effort in chat.
5. **A setting beats a sentence when the page says so.** When a page says a setting works more reliably than prompt text, the setting goes in the reply's setup and the prompt text becomes secondary or disappears.
6. **Sample prompts are material, not style.** Older samples use NEVER, MUST and "it is critical", while the best-practices page says emphatic language causes overtriggering on the models that followed them. Keep a sample's substance and reason, and state it plainly.
7. **"Measure on your evals" becomes "what to watch".** This skill does not run evaluations. When a page says to measure a trade-off, tell the user what to watch for in the results.

## Decide the design

Decide, before writing:

- **The shape:** one self-contained prompt (the default), a fixed automated sequence whose stages can all be written now, or a first prompt with follow-ups because the next instructions depend on a result nobody has seen yet (Step 8).
- **The content:** the source material and project context the prompt needs, and the success criteria it will state.
- **The model's items:** the items in the target model's prompting files whose symptom the use case produces, with their placement and conditions, and the lines to remove from a draft.
- **The form:** examples to establish format, tone or boundaries; structure; length.
- **The mechanics:** tools, research, structured output or intermediate artifacts, and the review checkpoints the session mode calls for.
- **The safeguards** the case needs, and nothing more.

Record the consequential decisions for the design notes. Do not provide an internal reasoning transcript.

## Verification rules

- Verify model names, supported effort settings, product features, and configuration capabilities before making specific recommendations about them.
- Distinguish the Claude app, Claude Code, the API, and agent harnesses. Do not assume they expose the same controls.
- Do not transfer one model's behavioral guidance to another without evidence.
- Keep documented facts separate from your design judgment.
- Never claim to have read documentation, inspected a file, tested a prompt, or applied a setting unless you actually did.
- If the live documentation is unavailable, disclose the limitation and avoid unsupported model-specific claims.
- An inaccessible page does not prove that a model or capability does not exist.
