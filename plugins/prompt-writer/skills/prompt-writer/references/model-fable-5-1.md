# Claude Fable 5.1 (and Claude Mythos 5.1)

Fable 5 prompts work on Fable 5.1 without changes. Apply the items below that match the prompt's use case. Fable 5 guidance that still applies is included at the end.

## Contents

- Effort
- Refusals and reasoning in the response
- Progress updates
- Tool-call batching in agent loops
- Conversation history
- Writing density
- Formatting in chat
- Quoting retrieved sources
- Finishing the whole task
- Compaction summaries
- Scope and tests
- Search at low effort
- Safeguard false positives
- File edits
- Long outputs at xhigh and max
- Subagents
- Vision
- Inherited from Fable 5

## Effort

Default `high`. Test `low`, `medium`, `xhigh`, `max` against real tasks. Gains over Fable 5 are largest at higher settings; `medium` roughly matches Fable 5 at lower cost; `low` is often cost-competitive with Opus and Sonnet while scoring higher.

## Refusals and reasoning in the response

Safety classifiers can return `stop_reason: "refusal"`; finding vulnerabilities in source code is permitted. Prompts, skills, or tool descriptions that tell it to write out its thinking may be declined as `reasoning_extraction`, and server-side fallback does not retry that category. Request a brief rationale or a recap of actions instead, or read summarized thinking (`display: "summarized"`).

## Progress updates

Fable 5.1 writes fewer user-facing updates during long tool-calling turns, more so at higher effort.

1. Configuration: set `thinking.display: "updates"` (beta) so progress notes reach the client.
2. Remove lines that suppress narration ("hold all findings for the final response").
3. If more updates are wanted (pair programming, human-in-the-loop), add a short instruction: state in one line what you are about to do before starting, give brief updates while working, and end with a self-contained recap of what was found, what was done, and what comes next.
4. If the product hides tool output, tell the model (turn-scoped system message) that only it sees command output and that anything the user needs must go in its reply.

## Tool-call batching in agent loops

In coding and computer-use loops where the next independent calls are implied rather than requested, it may issue one call per turn. Fix: after each round of tool results, append a turn-scoped system message telling it to list privately what it needs next and request every item that does not depend on another result in one response. Without the beta, put the sentence in a text block after the `tool_result` blocks.

## Conversation history

Keep history append-only and pass thinking blocks back unchanged. For accounts created on or after 2026-08-31, a replayed thinking block whose prefix (system prompt, tools, earlier messages) changed returns 400, or is dropped with `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` (beta header `thinking-binding-controls-2026-08-01`). Build for append-only regardless. Cache reads are cheaper on Fable 5.1, so later compaction points may be the better trade-off.

## Writing density

Prose can run dense (long sentences, few paragraph breaks). Add, preferably in a user message, an instruction that defines mannered prose (metaphor and flourish substituted for direct statement) and asks for literal phrasing whenever it is available. A one-line "remove all mannered prose" also tends to work.

## Formatting in chat

Fable 5.1 uses less bold, fewer headers, lists, and quotation marks than older models. Remove anti-formatting blocks written for them; they suppress structure the content needs. Replace them with a rule that says when formatting is appropriate: lists when asked or when content is multifaceted; no lists, headers, or bold when the user asks for minimal formatting; plain prose in conversational, personal, or emotional exchanges.

## Quoting retrieved sources

When summarizing documents it more often reproduces source passages without marking them as quotations. Fix: put one complete example in the system prompt (user request, correct response, one-sentence rationale) showing a response written in its own words with at most one short marked quote. Use the product's real tool name in any templated tool lines.

## Finishing the whole task

On complex asynchronous work it may describe the next step instead of doing it, or ask permission for work already requested. For autonomous runs add two blocks:

1. **Autonomy block.** The user is not watching and cannot answer mid-task, so permission questions block the work. Proceed with reversible actions that follow from the request; stop only for destructive actions or real scope changes. Exception: when the user is describing a problem or asking a question, the deliverable is the assessment, not a fix. Before ending the turn, check the last paragraph: if it is a plan, a list of next steps, a question, or a promise about undone work, do that work now. Do not stop because the session is long. Before state-changing commands, confirm the evidence supports that specific action. The opening sentence (the user is not watching) carries much of the effect; keep it.
2. **Scope block.** The request or approved plan is the deliverable; do not narrow, widen, or swap it. Make routine judgment calls; check in only when readings lead to materially different work. Voice real concerns briefly and keep building under stated assumptions. When a question arises mid-task, finish everything independent of it first. If one part is blocked, complete the rest and state exactly what was left out. Extra cleanup or changes the task did not require are suggestions for the end, not actions.

If prompt length is limited, keep the autonomy block. It can make the model ask less on ambiguous requests; weigh that trade-off. In pair programming and other human-in-the-loop work, stopping to ask suits the workflow, so these blocks are usually unnecessary there (inference; Opus 5.5 documents the same advice for its equivalent addition).

## Compaction summaries

For client-side compaction, instruct the summarizer to keep, exactly: problems and how they were handled; options raised, tried, or set aside and why; everything requested, decided, ruled out, or set as a preference or constraint; current status; open items and promises; hard-to-reconstruct details (names, numbers, dates, exact wording, links). Keep the user's words close to verbatim; condense the assistant's own reasoning to its conclusions.

## Scope and tests

On open-ended features it may fix nearby code, extend behavior, or commit extra test files. Instruct: report pre-existing bugs or unmentioned behavior as follow-ups instead of fixing them unless the requested behavior depends on it; pick the reading of ambiguous wording the code most directly supports and state it; scratch checks need not be kept; commit tests only where asked or where the repository already keeps tests for that kind of change, sized like neighboring tests; implement every requested behavior completely.

## Search at low effort

At `low` it answers from memory more often. Either raise effort for those turns or add a system prompt rule: when a query centers on a name the model does not confidently recognize, or one from a fast-moving field, search before answering and include the name exactly as written; partial familiarity is not a reason to skip the search.

## Safeguard false positives

Fewer than Fable 5, and finding vulnerabilities in source code is allowed. More likely with: compile-check phrasing (ask "are there any bugs in this program?" rather than "does this compile?"), lesser-known programming languages (give the model documentation or context), and base64 data in tool output (remove it).

## File edits

If it rewrites whole files for small changes, add: minimize tokens spent editing; when it will not change the result, edit surgically instead of rewriting.

## Long outputs at xhigh and max

At `xhigh`/`max` it may draft a long deliverable in thinking and again in the reply. Prefer `high` for these requests. If running higher: set `max_tokens` with room for thinking and reply, and append a note to the user message stating the single token limit (use the real value), that drafting the whole deliverable twice wastes it and risks a cut-off reply, and that reasoning should go to understanding the request, checking inputs, and settling structure.

## Subagents

Do not force the lead agent to wait for each subagent: the start-subagent tool returns immediately, results arrive in a later user message, and a separate tool lets the lead wait when it chooses.

## Vision

Best on dense images with iterative crop and verify: a container with raw images and PIL/OpenCV, or at least a crop tool.

## Inherited from Fable 5

- **Long turns.** Hard tasks at higher effort can run many minutes; autonomous runs, hours. Plan streaming, timeouts, and async check-ins.
- **Overplanning on ambiguous tasks.** Instruct: act once there is enough information; do not re-derive established facts or re-litigate decisions; recommend rather than survey options. (Does not apply to thinking.)
- **Strong instruction following.** A short instruction steers as well as an enumerated list. For brevity: lead with the outcome; keep output short by selecting what to include, not by compressing into fragments, arrow chains, or jargon.
- **Checkpoints.** Pause only for destructive or irreversible actions, real scope changes, or input only the user can provide; ask and end the turn instead of ending on a promise.
- **Grounded progress claims.** On long runs, audit each progress claim against a tool result from the session; report failures and skipped steps plainly.
- **Boundaries.** When the user describes a problem or asks a question, report findings and stop; check that evidence supports any state-changing command.
- **Memory.** It benefits from a place to write lessons (one lesson per file with a one-line summary; record corrections and confirmed approaches; update rather than duplicate; delete wrong notes).
- **Context-budget concern.** Avoid showing token countdowns; if unavoidable, reassure it that context is ample and it should not stop or suggest a new session.
- **Give the reason.** State the larger task, who it is for, and what the output enables.
- **Readable final summaries.** Shorthand is fine between tool calls; the final message is for a reader who saw none of it: outcome first, then what is needed from the user, complete sentences, no invented labels or arrow chains, clear over short.
- **Send-to-user tool.** For long async agents, a client tool whose input is rendered verbatim lets the agent deliver content mid-task. It is rarely called without an instruction saying to use it only for user-facing content.
- **Self-verification on long runs.** Fresh-context verifier subagents checking against the spec at intervals outperform self-critique.
- **Refactor old skills and prompts.** Instructions written for older models are often too prescriptive and can degrade output.
