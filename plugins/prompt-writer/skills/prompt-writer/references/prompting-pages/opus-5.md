# Writing prompts for Claude Opus 5

Apply these patterns to Opus 5, and use them as the starting point for Opus 5.5. Apply an item only when the prompt's use case calls for it. Use each sample as written, at its stated placement, and adapt it only where it is marked as an example or a starting point.

## Contents

- Effort
- Response length
- Progress updates
- Written deliverable length
- Verification and scope
- Code review
- Subagents
- Self-correction
- Reasoning in the response
- Settings that return errors
- Pages for the API setup

## Effort

Recommend starting at the default `high` and adjusting on the user's own tasks: `low` and `medium` freely as the main control for cost and latency wherever quality holds, and `xhigh` for demanding coding and agentic work. When a level was carried over from an older model, recommend re-running an effort sweep.

## Response length

Opus 5's user-facing responses run long, and effort controls thinking, not visible length: lowering effort does not reliably shorten them. Prompt for length explicitly. For a user-facing multi-turn product:

```text wrap
Keep responses focused, brief, and concise. Keep disclaimers and caveats short, and spend most of the response on the main answer. When asked to explain something, give a high-level summary unless an in-depth explanation is specifically requested.
```

In a long system prompt, also add a short reminder near the end:

```text wrap
<tone_preference>
Keep outputs reasonably concise.
</tone_preference>
```

## Progress updates

Opus 5 narrates readily during agentic work. To tune narration down, describe the cadence and shape wanted:

```text wrap
Before your first tool call, say in one sentence what you're about to do. While working, give a brief update only when you find something important or change direction. When you finish, lead with the outcome: your first sentence should answer "what happened" or "what did you find," with supporting detail after it for readers who want it.
```

To tune narration up or change its style, describe the updates wanted and give examples: positive examples work better than instructions about what not to do.

## Written deliverable length

Files it writes to disk (reports, Markdown documents, summaries) also run long. When the prompt produces documents, add:

```text wrap
Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate.
```

## Verification and scope

- Opus 5 verifies its own work unprompted. Remove explicit verification instructions ("include a final verification step for any non-trivial task", "use a subagent to verify") and recommend removing legacy harness scaffolding that adds separate verification steps: they cause over-verification, and removing them saves tokens with no quality loss.
- It can expand a task's scope. For narrow tasks, add:

```text wrap
Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole task, and stop short of actions that are clearly beyond what was asked.
```

## Code review

A review prompt that says "only report high-severity issues" or "be conservative" may be followed literally, so the model reports less. Ask it to report everything, and filter in a separate pass.

## Subagents

Opus 5 delegates readily, which multiplies cost and time on small tasks. When the harness supports subagents, say when delegation fits, or set caps. For example:

```text wrap
Delegate to a subagent only for large tasks that are genuinely independent and parallelizable, such as a wide multi-file investigation. Do not delegate work you can finish yourself in a handful of tool calls, and do not use subagents to verify or double-check your own work. If one subagent can complete the task, use one rather than several, and keep spawn counts low.
```

For the setup in Claude Code or the Claude Agent SDK: the caps are the `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` environment variables and the SDK's `max_budget_usd` option (`maxBudgetUsd` in TypeScript), which need Claude Code 2.1.217 or later: update a pinned SDK before pointing it at Opus 5. Claude Code adds its own delegation instruction only with its `claude_code` system prompt preset; with a custom or omitted system prompt, the prompt must include one.

## Self-correction

Opus 5 catches and fixes its own mistakes. Never add re-check instructions ("double-check your answer", "re-verify before responding"): they add cost without improving results. It also narrates corrections to its earlier statements. In user-facing products, limit that with:

```text wrap
Only correct an earlier statement when the error would change the user's code, conclusions, or decisions. State corrections plainly and briefly, then continue the task. For slips that change nothing for the user, make the fix and move on without noting it.
```

## Reasoning in the response

Never write a prompt, skill or tool description that asks the model to write out its thinking or reasoning, verbatim or in a fixed format: it may be declined in the `reasoning_extraction` refusal category. Ask for a short explanation of the answer or a summary of the actions taken. When the application needs the reasoning, recommend keeping thinking on and reading summarized thinking (`display: "summarized"`).

## Settings that return errors

- Return a 400 error: prefill, non-default `temperature`, `top_p` or `top_k`, and `budget_tokens`.
- Forced `tool_choice` is accepted.

## Pages for the API setup

When the prompt runs on the API or an agent harness, read live:

| Page | Size | Read |
| :-- | :-- | :-- |
| <https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5> | about 21,000 characters without SDK code; whole | the Opus 5 API facts it states by contrast |
