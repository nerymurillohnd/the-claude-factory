# Cross-guide criteria

The findings that only appear when the official pages are read side by side. Each one gives the guidance, the criterion behind it, how to apply it, and the official page and section that confirm it. Confirm before relying on a detail: the pages change, the criteria hold.

## 1. The target model is not optional

- **Guidance:** the covered models' prompting pages give opposite instructions for the same technique. Explicit verification steps cause over-verification on Opus 5, and Opus 5.5 inherits that pattern by default; Sonnet 5.5 at lower effort may report a change done without checking it, so it needs a real-check instruction. Anti-formatting rules written for older models suppress structure Fable 5.1 needs.
- **Criterion:** a technique is right or wrong only relative to a model. A prompt written for no model in particular applies some instruction that backfires on at least one.
- **Apply:** choose the target before writing; take each technique from the general pages, then check the target model's prompting page for the same topic; where they differ, the model's prompting page wins. The instructions that differ most:

  | Instruction | Where it differs |
  | :-- | :-- |
  | Verify or double-check your work | Remove on Opus 5, and on Opus 5.5, whose prompting page takes the Opus 5 patterns as its starting point. Add on Sonnet 5.5 when changes are reported done without a check (seen at `low` effort). Fable 5: fresh-context verifier subagents on long runs. |
  | Think carefully before answering | Consider removing from chat system prompts on Opus 5.5. On Sonnet 5.5, a think-it-through line helps JSON answers to reasoning tasks. |
  | Think less, answer directly | Lower effort instead: prompt text does not reliably reduce thinking on Sonnet 5.5, and on Opus 5.5 an answer-directly line comes only after effort is already `low`. |
  | Progress narration | Fable 5.1 writes fewer updates: ask for them. Opus 5 narrates readily: describe the cadence wanted. Sonnet 5.5: remove "hold all findings" lines. |
  | Anti-formatting rules | Remove, or make conditional, on Fable 5.1. |
  | Brief rule or named cases | A brief rule steers Fable 5 (Fable 5 page; the Fable 5.1 page keeps Fable 5 prompts working). Opus 5.5 needs the specific cases named. |
  | Scope limits | Fable 5.1 may fix nearby code and commit extra tests. Opus 5 expands scope. Sonnet 5.5 adds tests and docs, which most teams welcome. Sonnet 5 follows instructions literally, a pattern the Sonnet 5.5 page keeps as its starting point: state the scope it should generalize to. |
  | Subagents | Damp on Opus 5 and Opus 5.5. Use often and asynchronously on Fable 5 and Fable 5.1. Sonnet 5.5 at `xhigh` or `max` can start its own review rounds, sometimes with subagents. |
  | "Only report high-severity issues" | May be followed literally on Opus 5 and Opus 5.5, and on Sonnet 5, whose patterns the Sonnet 5.5 page keeps as its starting point: ask for every finding and filter in a separate pass. |

- **Confirm in:** the Opus 5 prompting file ("Verification and scope"), the Opus 5.5 prompting page, the Sonnet 5.5 prompting page ("Verification on coding tasks"), the Fable 5.1 prompting page ("Formatting in chat"), the Fable 5 prompting page.

## 2. Some anti-patterns break requests

- **Guidance:** assistant prefill returns a 400 error on the covered models; non-default `temperature`, `top_p` or `top_k` and manual `budget_tokens` return a 400 error on the covered models; each model adds its own rejected settings (thinking modes, forced `tool_choice`).
- **Criterion:** these are not style problems: the request fails before the prompt is read. Prompts and integrations written for older models carry them, so a migrated or audited prompt often does.
- **Apply:** remove them from any draft and its setup, and give the replacement the documentation names (structured outputs, instructions, effort). Read the model's "what a request must satisfy" list rather than recalling it.
- **Confirm in:** <https://platform.claude.com/docs/en/models/opus-5-5/migration-guide> ("What every request to Claude Opus 5.5 must satisfy"), <https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide> ("Send a request to Claude Sonnet 5.5"), <https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1> ("Behavior differences").

## 3. Visible reasoning can be declined

- **Guidance:** asking the target model to write its reasoning into the response (for example in `<thinking>` tags) may be declined as `reasoning_extraction` on the covered models. The same holds for a reasoning, thinking or trace field in a JSON schema or tool input. The category has no recommended fallback model, and a decline in it is billed, so the fix is the prompt.
- **Criterion:** chain-of-thought prompting written for older models risks a refusal with no automatic recovery on the covered models; their thinking is adaptive and controlled by effort instead.
- **Apply:** ask for a brief rationale or a recap of actions; when an application needs the reasoning, recommend the summarized thinking display in the setup.
- **Confirm in:** "Reasoning in the response" in the Fable 5.1 prompting file, "Safeguard refusals and reasoning in the response" in the Opus 5.5 and Sonnet 5.5 prompting files, "Reasoning in the response" on the Opus 5 prompting page, and <https://platform.claude.com/docs/en/build-with-claude/thinking> and <https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback>.

## 4. Many fixes live in the harness, not the prompt

- **Guidance:** effort, `max_tokens`, `thinking.display: "updates"`, turn-scoped system messages, an append-only history and structured outputs each solve problems that no wording solves.
- **Criterion:** for the API and agent harnesses, a prompt delivered without its configuration is half a solution, and an instruction that tries to do a setting's job (asking the model to think less, to emit valid JSON) is less reliable than the setting.
- **Apply:** when the documentation names a setting for the problem, put it in the reply's setup and keep the prompt for what only text can do.
- **Confirm in:** <https://platform.claude.com/docs/en/build-with-claude/effort> and <https://platform.claude.com/docs/en/build-with-claude/structured-outputs>, and the harness items on each covered model's prompting page.

## 5. Aggressive language hurts

- **Guidance:** CRITICAL, MUST and all-caps emphasis, which fixed under-triggering on older models, can make the models that followed them over-apply the instruction and over-use tools. The covered models' prompting pages do not restate it, so treat it as a pattern and confirm on the target model's page.
- **Criterion:** a reason generalizes better than emphasis.
- **Apply:** state each instruction plainly with its reason; when a tool is under-used, say when and why to use it.
- **Confirm in:** the best-practices page, kept in this skill rewritten as instructions ("General principles", "Tool use").

## 6. Prompt engineering has prerequisites

- **Guidance:** before prompt engineering, the documentation asks for success criteria, a way to test against them, and a first draft.
- **Criterion:** without criteria and a test, nobody can tell whether a prompt improved; some goals (latency, cost) are reached faster by changing the model than the prompt.
- **Apply:** collect the criteria and the test in the clarify round, in the user's terms; write them into the prompt as observable criteria; recommend a model change when it serves the goal better.
- **Confirm in:** <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview> ("Before prompt engineering"; about 2,800 characters, whole), <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests> ("Define your success criteria").

## 7. General pages can lag behind the models

- **Guidance:** some general pages describe techniques the covered models reject; the consistency page, for example, has a section on prefilling Claude's response.
- **Criterion:** a general page states a goal that holds and a mechanism that may not.
- **Apply:** keep the goal, and reach it with the mechanism the target model's prompting page gives.
- **Confirm in:** the guardrail pages under <https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/>, against the target model's prompting page.

## 8. Surfaces differ

- **Guidance:** effort defaults and parameters in the API documentation are the API's; the Claude app and Claude Code may not expose the same setting. In Claude Code, slash commands are skills, and a skill or slash command with no argument placeholder gets the user's typed text appended at its end, where it reads as a fresh instruction.
- **Criterion:** a recommendation is only useful on the surface where the user will run the prompt.
- **Apply:** confirm the setting exists on the user's surface before recommending it; for Claude Code skills and commands, place the argument placeholder where the input belongs.
- **Confirm in:** <https://platform.claude.com/docs/en/build-with-claude/effort>, <https://code.claude.com/docs/en/skills> ("### Pass arguments to skills", about 2,700 characters).

## 9. Few examples teach unintended patterns

- **Guidance:** examples work when they are relevant, diverse and structured; diverse means they cover edge cases and vary enough that Claude doesn't pick up unintended patterns. This skill has two delivery examples, too few to vary every value.
- **Criterion:** what repeats across the examples, or appears in only one, reads as a rule unless the text says otherwise.
- **Apply:** use the examples for the shape and the level of detail of a delivery; take the number of questions, the model, the effort, the session mode and the wording from the request, the target model's prompting files and the pages you read.
- **Confirm in:** the best-practices page, kept in this skill rewritten as instructions ("Use examples effectively").
