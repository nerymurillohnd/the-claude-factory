# Claude Sonnet 5.5

Sonnet 5 prompts work on Sonnet 5.5 without changes. For the hardest long-horizon work, recommend an Opus model instead. Apply the items below that match the use case.

## Contents

- Effort
- Initiative and scope
- Running without up-front thinking
- Reasoning tasks with JSON output
- Progress updates
- Tool use in chat and knowledge work
- Mid-turn user messages
- Verification on coding tasks
- Tool-call handling
- Visual inputs
- Safeguard refusals
- Inherited from Sonnet 5

## Effort

- Levels are recalibrated versus Sonnet 5; re-test.
- Default `high` on the Claude API. Agentic coding and multistep tools: `medium` for well-specified tasks, `high` for harder or longer ones. Chat and latency-sensitive work: `medium` or `low`.
- At `low` it keeps thinking short and can skip verifying changes. At `low` and `medium`, on long agentic tasks, it is more likely to stop and check in early.
- From `medium` up it thinks briefly before almost every reply. Asking it in the prompt to think less does not reliably work; lower effort instead.
- `max_tokens`: leave room for thinking; 128,000 and streaming for agentic coding.
- Reserve `xhigh`/`max` for measured gains; `between_tools` is not accepted there.

## Initiative and scope

- **Stops before finishing (low/medium, agentic coding).** Try higher effort first. Or add: keep working until everything requested is done; stop to ask only when blocked on the user or before a risky step. Pair it with: when the work is done and checked, stop and report; do not add unrequested features, tests, files, docs, or refactors; mention useful extras at the end. Sessions at low/medium then run longer. Keep separate rules for risky or irreversible actions.
- **Unrequested additions.** It tends to add tests, docs, and small files matching repository conventions, more at higher effort. Most teams welcome it. To limit changes to what was asked, add only the "stop and report" paragraph.
- **Extra review rounds at `xhigh`/`max`.** It may start its own review and verification passes, sometimes with subagents. For routine work use `high` or below. To keep the thoroughness but focus it: once the work is done and checks pass, stop and report; no self-started review or hardening rounds or reviewer subagents unless a review was requested; suggest a deeper review at the end if warranted. At `max` this cut session cost about a third with no quality change.
- **Open-ended requests.** It may start building when ideas were wanted. Say in the request that ideas or a plan come first, or add a rule: when asked for ideas, options, or a plan, deliver that and wait for a go-ahead.

## Running without up-front thinking

`thinking: {"type": "between_tools"}` is the lowest setting, accepted at `high` or below. `thinking: {"type": "disabled"}` returns 400. Forced `tool_choice` (`any` or `tool`) also returns 400; use `auto` with strict tool use or structured outputs and say in the prompt when the tool applies.

- At `xhigh`/`max` it returns 400. Per-message effort changes are not allowed with it.
- Remove instructions telling the model not to think; they increase internal XML tags in visible output.
- Notes between tool calls still come back as thinking blocks with summaries; pass them back unchanged.
- In requests without tools it answers without thinking, so use adaptive thinking for reasoning tasks.

## Reasoning tasks with JSON output

Applies when a JSON answer requires working out (totals, applying rules, ranking). At `low`/`medium` it often answers without thinking.

- Prefer structured outputs. With adaptive thinking, end the system prompt with a line asking it to think the problem through before answering; at `high` this brings accuracy close to `xhigh`. Alternatively use `xhigh`, which is most accurate even without the line.
- Do not use `between_tools` for these requests.
- At `low`/`medium` with structured outputs it occasionally thinks until `max_tokens`: treat any `stop_reason: "max_tokens"` as failed, even if the JSON looks valid, and retry.
- Without structured outputs it often reasons in the text and writes JSON at the end. Parse the last complete JSON value in the text blocks (not the span from the first `{` to the last `}`), validate the expected fields, and retry once if missing. Or use `xhigh` with adaptive thinking, which nearly always returns JSON alone.

## Progress updates

- Notes longer than a sentence or two between tool calls arrive as progress-update thinking blocks, empty at the default display. Set `display: "updates"` (beta). With `between_tools` the summaries come back without a `display` field; sending `display`, `budget_tokens`, or `block_binding` with `between_tools` returns 400.
- For exact text mid-turn (a snippet, a question it needs answered), give a send-to-user tool declared in the first request, reserved for that content.
- Remove old "hold all findings for the final response" lines; describe the cadence wanted if needed.
- Harness reminder after several silent tool steps (turn-scoped, stop after two or three). Frequent harness text after tool results can make it suspect prompt injection.

## Tool use in chat and knowledge work

It sometimes answers from training knowledge when a search would catch changed details (what is allowed, required, or charged). Remove tool-discouraging language ("only when strictly necessary", "minimize tool calls"). With a search tool, add: check specifics that may have changed since training even when confident; for researched work such as reports or comparisons, gather current sources.

## Mid-turn user messages

It can misread a genuine user message as prompt injection when it arrives right after tool results. Never put user text inside `tool_result`. Put mid-turn user input in the same user message as the tool results, as a text block placed after them. Harness notices go in their own system message, after the user's words. In interactive sessions, avoid custom token countdowns after tool results.

## Verification on coding tasks

At `low` it may report a change done without running a check. Add: when changing runnable, buildable, or type-checkable code, run a real check that exercises the change (tests, type-checker, build, or the command itself); a syntax-only check or a check that failed to start does not count; install missing declared dependencies with the project's own package manager and lockfile, never sudo or the system package manager, unless told not to; if no real check can run, say which one was not run and why.

## Tool-call handling

It occasionally calls a tool with wrong letter case or a slightly different parameter name. The harness should accept unambiguous case mismatches or return `is_error: true` with the exact expected name; it usually corrects on the next turn.

## Visual inputs

For dense charts and technical drawings, give it crop, zoom, or code tools. On charts, tools at `high` beat no tools at `max` at a fraction of the cost. On drawings, tools help from `high` up.

## Safeguard refusals

Categories: `cyber` (finding vulnerabilities in source code is allowed), `bio`, `frontier_llm`, `reasoning_extraction`, `general_harms`. Server-side fallback (beta) retries `cyber` and `frontier_llm` on Sonnet 5, not the others. Remove instructions asking for reasoning in the response.

## Inherited from Sonnet 5

- **Literal instruction following,** especially at lower effort: it does not generalize an instruction from one item to others. State scope explicitly ("apply this to every section").
- **Tone:** re-check voice prompts; for a warmer voice, ask for a warm, collaborative tone that acknowledges the user's framing.
- **Design defaults:** generic "don't use that color" swaps one default for another. Give a concrete visual spec, or have it propose four distinct directions (background, accent, typeface, rationale) and implement the chosen one.
- **Code review:** ask for every issue with confidence and severity; filter separately.
- **Interactive coding:** specify task, intent, and constraints in the first turn rather than progressively.
