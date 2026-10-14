# Claude Opus 5.5

Opus 5 prompts work on Opus 5.5 without changes, and the Opus 5 patterns (explicit concision instructions, no extra verification or double-check instructions, damping subagent use, limiting correction narration) remain a reasonable starting point. Apply them by default, and note once in the design notes that they were documented for Opus 5. Apply the items below that match the use case.

## Contents

- Strengths relevant to prompting
- Effort
- Prompts written for thinking disabled
- Unattended agentic runs
- Safeguard refusals
- Progress updates
- Multi-app workflows
- Time signals in multi-agent harnesses
- Chat system prompts
- Pasted text in user messages
- Visual inputs
- Frontend design

## Strengths relevant to prompting

- Agentic coding in real repositories, carried until tests pass; at `medium` it matched or beat Opus 5 at `high` in fewer steps. Sustains multi-hour autonomous audits and migrations with parallel subagents.
- Code review: more bugs caught, fewer false alarms.
- Knowledge work: fewer wrong figures or wrong citations; strong at financial models and at catching easy-to-miss details in large inputs.
- Plain-language updates and final summaries.
- Dense charts read more accurately at its lowest effort than Opus 5 at its highest; position-dependent visuals (flowcharts, diagram diffs, calendar screenshots) are stronger; computer use at default effort matches Opus 5 at much higher effort.

## Effort

- Default `medium` (Opus 5 defaults to `high`). Set effort explicitly and test several levels.
- At a given level it thinks more per turn than Opus 5, especially at `xhigh`/`max`. Keeping the Opus 5 value means longer turns and more tokens.
- Set `max_tokens` with room for thinking; 128,000 works well for agentic coding.
- Reserve `xhigh`/`max` for measured gains. To reduce thinking, lower effort first.
- Use a per-message effort change (beta) to switch levels mid-conversation without breaking the cache.

## Prompts written for thinking disabled

Thinking is always on; `thinking: {"type": "disabled"}` is not accepted. When migrating an integration that ran with thinking off:

- Start at `low` effort and measure; move to `medium` if quality drops. If time to first token still matters, a system line asking it to answer directly without deliberating can reduce thinking further; measure quality.
- Remove instructions that asked for written-out reasoning as a stand-in for thinking; read summarized thinking instead.
- Re-check whether the Opus 5 thinking-disabled mitigations are still needed; remove any rule telling the model not to think.
- Read content by block type.

Also: forced `tool_choice` (`any` or `tool`) returns 400. Use `auto` with strict tool use or structured outputs, and say in the prompt when the tool applies.

## Unattended agentic runs

It keeps the user updated on long multi-part tasks, and some updates end the turn with text (`stop_reason: "end_turn"`). An unattended loop that treats that as completion stops early.

Harness (recommend alongside the prompt):

- Treat a text-only end of turn as a report, not proof of completion.
- Keep the task's parts in a checklist the model updates (to-do tool or file). If a turn ends with open items and no stated blocker, send a short user message naming the open items and asking it to continue or say what blocks it.
- Optionally state the completion condition up front and have a smaller model check it at each end of turn.
- Stop after two or three automatic continuations on the same task.
- If a background command or subagent is still running, wait for it and return its output before treating the task as done.

Prompt: it responds well to an addition that names the specific early stops to avoid and the stops that are wanted. The four unwanted patterns: a long summary that announces the next step without a tool call; an offer to continue unless the user objects; a list of decisions for the user when none blocks the work; deciding to report because the turn is long or a milestone is done. Status notes and recommendations should go in the same message as the next tool call. Wanted stops: nothing can move without the user, or the blocker is deliberately protected. It does not override confirmation for risky actions. Add it at the end of the system prompt from the first request; leave it out of human-in-the-loop products. Expect somewhat more tool calls and tokens.

## Safeguard refusals

Classifiers for biology (same as Fable 5.1; new if coming from Opus 5), cybersecurity (finding vulnerabilities in source code is allowed; high-risk dual-use activity is not), and reasoning extraction. Remove instructions that ask for visible reasoning; use `display: "summarized"` if reasoning is needed. Server-side fallback does not retry `reasoning_extraction` declines.

## Progress updates

Between tool calls it writes short notes about what it found and what it does next. They arrive as progress-update thinking blocks, empty at the default display.

1. Set `display: "updates"` (beta) to receive them.
2. If it may need to hand the user something verbatim mid-turn, give it a send-to-user tool, declared from the first request, and tell it to reserve the tool for that content.
3. For predictable updates (one-line intent before the first tool call, short recap at the end), say so in the system prompt.
4. If turns still go quiet, the harness counts consecutive tool steps with nothing for the user to read; after about five, append a turn-scoped reminder asking for a few words on what it is doing. Stop after two or three reminders. In Anthropic's testing, tasks containing a long silent stretch dropped by about half, and cost did not measurably change.

## Multi-app workflows

In automation across email, documents, spreadsheets, and CRM, it gets to work quickly. One system-prompt sentence asking it to explore broadly first (list and open the emails, documents, tabs, and records that could be relevant, including ones the task does not name, and use what it finds) completed noticeably more tasks correctly at `medium` and `max`. Keep untrusted content out of searched sources, because it will act on what it finds.

## Time signals in multi-agent harnesses

It paces work to elapsed-time information. With an estimable budget, append `elapsed <s>s / <budget>s` to each message the harness sends back; set the budget somewhat above the target and keep a hard timeout. Without a budget, show elapsed time and add one sentence saying time matters and earlier correct results are better. Teams finished sooner with comparable quality; it may search and verify a little less under time pressure.

## Chat system prompts

- Remove "think carefully before answering" lines; effort controls thinking, and removing them made replies start sooner without a clear quality loss.
- Optional: two sentences at the end of the system prompt telling it to treat earlier answers as settled and focus thinking on the current question unless the user points to a problem. Reduces follow-up latency. Omit for long analyses or agentic work where later steps can expose earlier mistakes; it may also make it less likely to flag its own earlier errors.

## Pasted text in user messages

To resist instructions hidden in content the user pasted, the application wraps each pasted block in `<pasted_content id="...">` ... `</pasted_content id="...">` with the same short random ID on both tags, each on its own line. The system prompt explains that text inside those tags was pasted from elsewhere, may contain instructions the user did not write, should be followed only where the user's own message asks, and that the ID is invisible to the user and should not be mentioned. It can make the model slightly more cautious; the tags can be imitated, so treat it as one layer.

## Visual inputs

Reads charts and screenshots more precisely than Opus 5 without tools, so re-test old visual scaffolding. For the densest inputs, higher resolution and image tools (container with PIL/OpenCV, or a crop tool) still add accuracy, more so at higher effort. Without tools, raising effort helps technical drawings but not charts.

## Frontend design

Without design direction it falls back on a few default styles; "avoid a generic AI look" just swaps defaults. Name specific patterns to avoid (for example cream or off-white backgrounds, italic accent words in headlines, numbered section labels, monospace labels, pill-shaped buttons), check the first result, and extend the list.
