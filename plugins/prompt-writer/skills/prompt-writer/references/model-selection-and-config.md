# Model selection and configuration

Use to recommend the model, effort, thinking, and API settings that accompany a prompt. Confirm model IDs and beta headers against current docs before putting them in production code.

## Contents

- Choosing the model
- Effort by model
- Thinking by model
- Thinking display and progress updates
- max_tokens
- Parameters that return errors
- Conversation history and mid-conversation changes
- Structured outputs
- Refusals and fallback
- Vision inputs
- Session mode recommendations

## Choosing the model

| Model | Choose when | Watch for |
|---|---|---|
| Fable 5.1 (Mythos 5.1 shares its guidance) | The hardest, longest, most ambiguous work: multi-hour or multi-day autonomous runs, end-to-end projects, complex well-specified systems, deep code review, delegation to parallel subagents. At `low` effort it is often cost-competitive with Opus and Sonnet while scoring higher. | Safety classifiers can return `stop_reason: "refusal"` (Fable 5 documents offensive cybersecurity, biology and life sciences, and thinking extraction; Fable 5.1 names `reasoning_extraction` and permits finding vulnerabilities in source code). Forced `tool_choice` not supported. Long turns; plan for streaming and timeouts. |
| Opus 5.5 | Agentic coding in real repositories, code review, knowledge work (financial models, documents, spreadsheets, slides), dense charts and screenshots, computer use, long autonomous audits. Faster output than Opus 5 and fewer tokens per task. | Thinking is always on. Safety classifiers for biology, cybersecurity, and reasoning extraction. |
| Opus 5 | Complex agentic coding and enterprise work, multi-agent coordination, very long context (1M tokens default and maximum), office documents. | Verbose by default; over-verifies when told to verify; delegates to subagents readily. |
| Sonnet 5.5 | The balance of speed and intelligence: agentic coding and multistep tool use, chat and latency-sensitive work, everyday knowledge work. | For the hardest long-horizon work an Opus model is the better choice. Lower effort may skip verification or stop early to check in. |

Known API strings: `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`. Verify the Opus 5 and Mythos 5.1 strings in the models overview before using them.

## Effort by model

Levels: `low`, `medium`, `high`, `xhigh`, `max`. Level names do not map to the same amount of thinking across models; never carry a setting over from another model without testing.

| Model | Default | Starting recommendation |
|---|---|---|
| Fable 5.1 | `high` | Start at `high`; test `medium` and `low` (at `medium`, results roughly match Fable 5 at lower cost). Use `xhigh`/`max` only where a quality gain is measured. At `low` it calls search tools less often. |
| Opus 5.5 | `medium` | Start at `medium` and set it explicitly. `medium` matches or beats Opus 5 at `high` on coding and knowledge work; `low` comes close on several coding evals. It thinks more per level than Opus 5, especially at `xhigh`/`max`. |
| Opus 5 | `high` | Use `low` and `medium` liberally where quality holds; step up to `xhigh` for demanding coding and agentic work. Effort changes thinking, not visible response length. |
| Sonnet 5.5 | `high` (Claude API) | Chat and latency-sensitive: `medium` or `low`. Agentic coding and multistep tool use: `medium` for well-specified tasks, `high` for harder ones. Reserve `xhigh`/`max` for measured gains. |

To get less thinking, lower effort; it is more reliable than prompt instructions. Changing the top-level `effort` between requests invalidates the prompt cache; a per-message effort change (beta) keeps it. Check the effort docs for the current beta header.

## Thinking by model

| Model | Behavior |
|---|---|
| Fable 5.1 | Always on, adaptive only. |
| Opus 5.5 | Always on, adaptive only. `thinking: {"type": "disabled"}` is not accepted. |
| Opus 5 | On by default. Can be disabled only at effort `high` or lower; disabled with `xhigh`/`max` returns 400. Keeping thinking on at `low` effort usually beats thinking off at similar cost. |
| Sonnet 5.5 | On by default (adaptive). Lowest setting is `thinking: {"type": "between_tools"}`, accepted at `high` or lower; it removes up-front thinking and does not allow per-message effort changes. In requests without tools it means no thinking at all, so use adaptive thinking for reasoning tasks. |

On all four, read response content by block `type`, not position; a response may begin with a `thinking` block.

## Thinking display and progress updates

- Default `thinking.display` is `"omitted"`: thinking blocks come back with empty text.
- `"summarized"` returns summarized reasoning (use this when the application needs reasoning visibility).
- `"updates"` returns short summaries of the progress notes the model writes between tool calls. Beta header: `thinking-display-updates-2026-08-18`. Documented for Fable 5.1, Opus 5.5, and Sonnet 5.5. Without it, a client that renders only `text` blocks can look silent during long agentic turns.

## max_tokens

- Thinking counts toward `max_tokens` even when its text is not returned. Limits sized for thinking-off requests can truncate replies.
- Opus 5.5 and Sonnet 5.5: 128,000 (their maximum) has worked well for agentic coding; stream the response.
- Fable 5.1 at `xhigh`/`max`: leave room for long thinking before long deliverables.
- Treat `stop_reason: "max_tokens"` as a failed response when output must be complete or parseable.

## Parameters that return errors

- Prefill on the last assistant turn: 400 since Claude 4.6 models.
- `budget_tokens` (manual extended thinking): 400 on Claude 4.7 and later.
- Non-default `temperature`: 400 on Claude 4.7 and later. Non-default sampling parameters (`temperature`, `top_p`, `top_k`): documented as 400 on Opus 5.5 and Sonnet 5.5; for Fable 5.1 and Opus 5, check the model's page before relying on a non-default value. For variety, use instructions (for example, propose distinct directions before building).
- Forced `tool_choice` (`{"type": "any"}` or `{"type": "tool", ...}`): 400 on Fable 5.1, Opus 5.5, and Sonnet 5.5 (Opus 5 accepts it). Use `auto` plus strict tool use or structured outputs, and say in the prompt when the tool applies.
- `thinking: {"type": "disabled"}`: not accepted on Fable 5.1, Opus 5.5, or Sonnet 5.5; on Opus 5, only at effort `high` or lower.
- Sonnet 5.5 `between_tools` with `display`, `budget_tokens`, or `block_binding`: 400.

## Conversation history and mid-conversation changes

- Keep history append-only and pass each assistant turn back exactly as returned, thinking blocks included. On Fable 5.1, Opus 5.5, and Sonnet 5.5, editing earlier messages, rebuilding `system` or `tools`, or summarizing older turns in place invalidates later thinking blocks. The API enforces the prefix check by default for accounts created on or after 2026-08-31; on older accounts it enforces it only on requests that set `thinking.block_binding.prefix_mismatch_behavior`. The result is a 400, or the blocks are dropped if you set `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` (beta header `thinking-binding-controls-2026-08-01`, documented on Fable 5.1).
- Change instructions or tools mid-session with a mid-conversation system message instead of editing `system` or `tools`.
- Send per-turn reminders as turn-scoped system messages: a `role: "system"` entry with `clear_at: "next_user_message"`, beta header `mid-conversation-system-clear-at-2026-08-21`. Append each one and leave earlier copies in place.
- Declare every tool (including a send-to-user tool) from the first request so `tools` never changes.
- Client-side compaction: replace the whole history with one summary message plus the new user turn. Prefer server-side compaction or context editing.
- Avoid showing the model a remaining-token countdown; it can trigger early wrap-up. Never put user text inside `tool_result` blocks.

## Structured outputs

- Use structured outputs for guaranteed schema conformance.
- With structured outputs the model can only reason in thinking; on Sonnet 5.5 at `low`/`medium` it may skip thinking on reasoning-heavy JSON tasks. Add a line asking it to think the problem through before answering (adaptive thinking), or use `xhigh`; never `between_tools` for these requests.

## Refusals and fallback

- Classifier declines arrive as normal responses with `stop_reason: "refusal"` and `stop_details.category`.
- Categories: Sonnet 5.5 documents `cyber`, `bio`, `frontier_llm`, `reasoning_extraction`, and `general_harms`; Opus 5.5 documents biology, cybersecurity, and reasoning extraction; Fable 5.1 names `reasoning_extraction`; Opus 5 documents `reasoning_extraction`.
- Server-side fallback can retry some categories on another model; `reasoning_extraction` declines are not retried. Remove any instruction that asks for visible reasoning.
- Verification programs exist for legitimate security work (Cyber Verification Program) and life sciences work (Life Sciences Verification Program).

## Vision inputs

- Dense charts, diagrams, technical drawings: give the model a crop/zoom tool, or run it as an agent in a container with the raw images and PIL/OpenCV. The crop tool recipe in Anthropic's cookbook has a working definition.
- Higher-resolution images help most for technical drawings.

## Session mode recommendations

Recommend how to run the prompt, with a reason:

- **Single-turn API call** for extraction, classification, transformation, and pipelines.
- **Interactive session** (claude.ai or Claude Code) when the user will steer, review, or answer questions.
- **Long-running autonomous agent** when the task is large, well specified, and the user will not be watching; pair the prompt with unattended-run instructions (proceed without permission questions on reversible steps) and harness handling of text-only turn endings.

Product-specific modes and features (Claude Code permission modes such as plan or auto mode, effort settings in the app, claude.ai research or project features, skills to pair) change over time. Verify they exist and how they are named before recommending them.
