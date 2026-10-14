# Claude Opus 5

Anthropic lists Opus 5 as a legacy model that is still available and recommends migrating to Opus 5.5; suggest Opus 5.5 for new work unless the user needs Opus 5. Opus 4.8 prompts work on Opus 5 out of the box. Apply the items below that match the use case.

## Contents

- Strengths relevant to prompting
- Effort
- Response length and verbosity
- Progress updates
- Written deliverable length
- Verification and scope
- Code review
- Subagents
- Self-correction
- Running with thinking disabled
- Reasoning in the response

## Strengths relevant to prompting

- Hard agentic coding (multi-file features, large refactors, end-to-end work); completes tasks rather than leaving stubs. Performs best with the full specification up front, then left to run.
- Code review with high precision and recall, holding at lower effort.
- Charts, documents, diagrams, UI replication; tools for crop and verify help more than extra thinking.
- 1M-token context window (default and maximum) with consistent instruction following throughout.
- Complex multi-sheet spreadsheets and well-structured decks; give it any required styles or templates.
- Multi-agent coordination with effective writer-verifier patterns.

## Effort

Default `high`. Use `low` and `medium` liberally as the main cost and latency control where quality holds; `xhigh` for demanding coding and agentic work. Effort controls thinking, not visible response length.

## Response length and verbosity

Default responses run longer than older Opus models, and lowering effort does not reliably shorten them. Prompt for concision explicitly: focused, brief answers; short caveats; high-level explanations unless depth is requested. In a long system prompt, add a short concision reminder near the end as well.

## Progress updates

It narrates readily during agentic work. Describe the cadence you want: one sentence before the first tool call, updates only on important findings or a change of direction, and a final message that opens with the outcome. To get more narration, describe it and give positive examples.

## Written deliverable length

Files it writes (reports, Markdown documents, summaries) run long. Ask it to match document length to what the task needs, without filler sections, redundant summaries, or boilerplate.

## Verification and scope

- It verifies its own work unprompted. Remove explicit verification instructions ("add a final verification step", "use a subagent to verify") and legacy verification scaffolding; they cause over-verification with no quality gain. A separate verifier role in a multi-agent writer-verifier design is fine; the removal applies to asking the model to check its own work.
- It can expand scope. For narrow tasks, instruct: deliver what was asked at the intended scope; make routine judgment calls and check in only when readings lead to materially different work; flag a mistaken request or better approach in a sentence, then continue as asked; finish the whole task and stop short of actions beyond the ask.

## Code review

"Only report high-severity issues" or "be conservative" may be followed literally and lowers what it reports. Ask it to report everything and filter in a separate pass. (Sonnet 5 and Opus 4.8 guidance adds detail that applies by analogy: include confidence and severity per finding; if filtering in one pass, define the bar concretely, such as anything that could cause incorrect behavior, a test failure, or a misleading result.)

## Subagents

It delegates readily, which multiplies cost on small tasks. Instruct: delegate only large, independent, parallelizable work; do not delegate what a handful of tool calls can finish; do not use subagents to double-check its own work; keep spawn counts low. In Claude Code or the Agent SDK, hard caps exist (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, SDK `max_budget_usd`; Claude Code 2.1.217 or later). Claude Code adds its own delegation instruction only with the `claude_code` system prompt preset; with a custom prompt, add one.

## Self-correction

It catches and fixes its own mistakes. Do not add "double-check your answer" instructions. To limit narration of corrections in user-facing products: flag an earlier mistake only if it alters the user's code, conclusions, or decisions; keep such corrections short and plain; fix inconsequential slips silently.

## Running with thinking disabled

Thinking is on by default and can be disabled only at effort `high` or lower. Prefer thinking on at `low` effort over thinking off. With thinking off, two artifacts can appear: tool calls written as text instead of `tool_use` blocks, and internal XML tags in visible output. Remove any rule telling it not to think. If thinking must stay off, add one combined instruction: it may say a brief sentence before a tool call; if no tool fits, say so instead of guessing; do not include internal or system XML tags in the response. Do not name thinking tags specifically; the general form works better.

## Reasoning in the response

Instructions to write out its reasoning, verbatim or in a fixed format, may be declined as `reasoning_extraction`. Ask for a short explanation or a summary of actions; read summarized thinking if reasoning is needed.
