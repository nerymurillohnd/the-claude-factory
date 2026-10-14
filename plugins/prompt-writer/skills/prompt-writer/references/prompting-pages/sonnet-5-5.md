# Writing prompts for Claude Sonnet 5.5

Start from the Sonnet 5 patterns, and recommend an Opus model instead for the hardest long-horizon work. Apply an item below only when the prompt's use case produces its symptom. Use each sample as written, at its stated placement, and adapt it only where it is marked as an example or a starting point.

## Contents

- Effort
- Initiative and scope
- Running without up-front thinking
- Reasoning tasks with JSON output
- Progress updates
- Tool use in chat and knowledge work
- Mid-turn user messages
- Verification on coding tasks
- Tolerant tool-call handling
- Visual inputs
- Safeguard refusals and reasoning in the response
- Settings that return errors
- Pages for the API setup

## Effort

- Levels are recalibrated from Sonnet 5: never carry a level over; tell the user to run a fresh effort sweep on their own tasks. Recommend `high`, the Claude API default, for most work; `medium` for well-specified agentic coding and multistep tool use, `high` for harder or longer agentic tasks; `medium` or `low` for chat and other latency-sensitive work, since higher effort delays the start of the reply. Raise effort when quality needs it.
- Lower effort changes how it finishes agentic work: at `low` it keeps thinking short and can skip verifying a change; at `low` and `medium`, on long agentic tasks, it is more likely to stop and check in before finishing.
- From `medium` up it thinks briefly before almost every reply, even a greeting. Asking in the prompt for less thinking doesn't reliably reduce it: lower effort instead. At `low` it skips thinking on most simple requests.
- In the setup: `max_tokens` with room for thinking and the reply (thinking counts even when not returned); for agentic coding, 128,000, the model's maximum, with streaming.
- Reserve `xhigh` and `max` for work with a measured gain: thinking and replies get much longer, and `between_tools` is not accepted there.
- Changing the top-level `effort` between requests invalidates the prompt cache. Recommend a per-message effort change (beta), which keeps the cache and holds until the next change, for example raising to `high` before a hard question in a `low` session and back afterwards. It needs adaptive thinking: with `between_tools` it returns a 400 error.

## Initiative and scope

**Carrying work through.** On agentic coding at `low` and `medium`, the model sometimes checks in before the work is done. Recommend a higher effort first. To keep it working without changing effort, add both paragraphs to the system prompt:

```text wrap
Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.

When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.
```

Sessions at `low` and `medium` then run longer and cost more. Keep the application's own rules for risky or irreversible actions in the system prompt: this does not replace them.

**Unrequested additions when coding.** The model adds tests, documentation and small supporting files that fit the repository's conventions, at every effort level and more at higher effort; the requested change itself stays close to what was asked. Most teams welcome this. Only when the user wants changes limited to the request, add the second paragraph alone, the one that starts "When the work the user asked for is done"; at `xhigh` and `max` it also makes changes smaller overall.

**Thoroughness at `xhigh` and `max`.** The model can start its own rounds of review and verification after finishing, sometimes with subagents when the harness provides them, and make related fixes. Recommend `high` or below for routine work. When the user wants that thoroughness focused on the task, add:

```text wrap
When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own, and don't launch reviewer sub-agents unless the user asked for a review. If you think a deeper review is worth doing, say so at the end.
```

At `max` on coding tasks this stopped reviewer subagents and cut session cost by about a third with no change in quality; self-started review rounds by the main agent become less frequent but don't disappear.

**Open-ended requests.** A request like "show me what you can do with this" can start a full build (a presentation, report or video) when the user wanted ideas. When ideas or a plan should come first, say so in the request, or add:

```text wrap
When the user asks for ideas, options or a plan, give them that and stop. Don't start building or changing anything until they say to go ahead.
```

## Running without up-front thinking

For an integration that ran with thinking off, recommend `thinking: {"type": "between_tools"}`, the lowest setting, accepted at `high` effort or below. In the setup and the prompt:

- `between_tools` at `xhigh` or `max` returns a 400 error, and so does a per-message effort change that differs from the level in effect. To vary effort per turn, use adaptive thinking.
- Remove any instruction telling the model not to think: it makes internal XML tags in visible output more likely.
- Read response content by block type: with adaptive thinking, a response can begin with a thinking block (empty under the default `display: "omitted"`); under `between_tools`, with a progress-update thinking block.
- Pass thinking blocks back unchanged with the rest of the assistant turn.
- In a request without tools, `between_tools` means no thinking at all: use adaptive thinking for tasks that need working out.

## Reasoning tasks with JSON output

When the prompt asks for a JSON answer that needs a few steps of working out (totaling figures, applying a rule, ranking items), the model often answers without thinking first, particularly at `low` and `medium`.

With structured outputs (recommend them where available), the response holds only the JSON, so the model can work the problem out only in its thinking:

- With adaptive thinking, add this line to the end of the system prompt. At `high` it brings accuracy close to `xhigh` for a modest increase in output tokens; at `low` and `medium` it raises accuracy, though not to `high`, for a larger increase:

```text wrap
Think the problem through before you answer.
```

- Or recommend `xhigh` with adaptive thinking, which gives the highest accuracy even without the line, at more output tokens than `high`.
- Never use `between_tools` for these requests: in a request without tools the model doesn't think before answering, and the line has no effect.
- In the setup: at `low` and `medium` the model occasionally thinks until `max_tokens`. Treat any `stop_reason: "max_tokens"` as failed even when the text holds valid JSON, and retry; set `max_tokens` high enough for thinking and JSON, but no higher than one attempt is worth.

Without structured outputs, the model often works the problem out in the text and writes the JSON at the end. In the setup:

- Read only the `text` blocks, treat `stop_reason: "max_tokens"` as failed, and parse the last JSON value: starting at each `{` or `[`, try to parse a value; when one parses, continue from its end so nested values aren't counted on their own; keep the last value found. Never take the span from the first `{` to the last `}`: the model sometimes writes a draft before its final JSON. For several values in a row (one record per line), keep the last run separated only by spaces, commas or line breaks. Check the expected fields and retry once if they are missing.
- Or recommend `xhigh` with adaptive thinking: the model then works in its thinking and nearly always returns the JSON alone, at about the same total output.

## Progress updates

Notes longer than a sentence or two between tool calls arrive as progress-update thinking blocks, empty at the default `thinking.display`; shorter remarks stay text. In the setup and the prompt, in order:

1. Recommend `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`). With `between_tools` the notes already carry their summary and no `display` field is needed; `between_tools` takes no other field, and `display`, `budget_tokens` or `block_binding` sent with it returns a 400 error.
2. When the model must show exact text mid-turn (a code snippet, a question it needs answered), give it a tool for sending the user a message, reserved for that content, declared in the first request of the session.
3. Remove older instructions such as "hold all findings for the final response".
4. For updates at predictable points (a line before the first tool call, a short recap at the end), say so in the system prompt; this helps most in human-in-the-loop work.
5. When turns still go quiet, the harness counts consecutive tool-calling steps with no text or progress update; after several (five, for example), it appends this reminder after the latest tool results as a turn-scoped system message (beta), leaves it in `messages`, and stops after the second or third reminder:

```text wrap
The user hasn't heard from you in a while — say in a few words what you're doing, then continue.
```

Frequent harness text after tool results can make the model suspect prompt injection: keep reminders rare.

## Tool use in chat and knowledge work

On chat and knowledge-work tasks, the model sometimes answers from training knowledge when a search would catch changed details (what is allowed, required or charged). First remove language that discourages tool use, such as "only use tools when strictly necessary" or "minimize tool calls". Then, only when the product gives the model a search tool, add:

```text wrap
Use the search tool to check specifics that may have changed since your training, such as what is allowed, required or charged, even when you feel confident. For researched work such as a report or a comparison, gather current sources rather than writing from your training knowledge.
```

This matters most in research and support products.

## Mid-turn user messages

The model can misread a genuine user message as prompt injection when it arrives right after tool results: it may tell the user the tool result contained text posing as them, and ignore it or ask for confirmation. Causes include a token countdown after every tool result, users typing while the model is mid-turn, and harness text after tool results on every step. For the setup:

- Never put user text inside a `tool_result` block.
- Deliver mid-turn user input as a text block in the user message that carries the `tool_result` blocks, after the last `tool_result`.
- Put harness notices (reminders) in a separate mid-conversation system message after the user's words, never in the same block.
- In interactive sessions where users can type mid-turn, don't add a custom token or budget countdown after tool results. If the misread appears while a task budget is set, try without one.

## Verification on coding tasks

At `low` effort the model may report a change as done without running a check that exercises it, for example skipping tests because dependencies aren't installed. When the transcript shows changes reported complete without test or build output, add this paragraph, or one like it, to the system prompt; at `low` it makes skipped or superficial checks rare, with no measurable change in quality and a slightly higher cost per task:

```text wrap
When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.
```

## Tolerant tool-call handling

The model occasionally calls a declared tool with different letter case (`bash` for `Bash`) or passes a parameter under a slightly different name. For an API integration, recommend that the harness accept unambiguous case mismatches, or return a `tool_result` with `is_error: true` that states the exact expected name; the model usually corrects the call on its next turn.

## Visual inputs

For dense charts and technical drawings, recommend a tool to crop, zoom or run code on the image (the crop tool recipe at <https://platform.claude.com/cookbook/multimodal-crop-tool>). On charts, tools help at every effort level, and with tools at `high` the model read charts more accurately than without tools at `max`, at a fraction of the cost. On technical drawings, tools help only from `high` up, most at `xhigh` and `max`.

## Safeguard refusals and reasoning in the response

A decline arrives as a normal response with `stop_reason: "refusal"` and `stop_details.category`:

- `cyber`: could enable cyber harm. Finding vulnerabilities in source code is allowed; high-risk dual-use work is not. The Cyber Verification Program exists for blocked legitimate security work.
- `bio`: could enable biological harm. Everyday health and educational questions are unaffected. The Life Sciences Verification Program exists for blocked legitimate life sciences work.
- `frontier_llm`: could assist the development of competing AI models.
- `reasoning_extraction`: asks the model to reproduce its internal reasoning in the response.
- `general_harms`: another usage-policy area; benign work can trigger it.

When server-side fallback (beta) is turned on, it retries `cyber` and `frontier_llm` declines on Sonnet 5, and does not retry `bio`, `reasoning_extraction` or `general_harms`.

Never write a prompt that asks the model to include its reasoning in the response. Remove such instructions; with adaptive thinking, recommend reading summarized thinking (`display: "summarized"`). A short explanation of the answer or a summary of the actions taken is fine.

## Settings that return errors

- Return a 400 error: forced `tool_choice`; `thinking: {"type": "disabled"}` (use `between_tools`); `between_tools` at `xhigh` or `max`, or with `display`, `budget_tokens` or `block_binding`; prefill; non-default `temperature`, `top_p` or `top_k`; `budget_tokens`.

## Pages for the API setup

When the prompt runs on the API or an agent harness, or is migrated, read live:

| Page | Size | Read |
| :-- | :-- | :-- |
| <https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide> | about 30,000 characters without SDK code: whole only through the filter, otherwise sections | "Send a request to Claude Sonnet 5.5" for what a request must satisfy; "Migrating to Claude Sonnet 5.5 from Claude Sonnet 5" when migrating a prompt |
