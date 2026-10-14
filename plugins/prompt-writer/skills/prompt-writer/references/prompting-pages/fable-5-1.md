# Writing prompts for Claude Fable 5.1

Apply an item below only when the prompt's use case produces its symptom; prompts written for Fable 5 already work here unchanged. Use each sample as written, at its stated placement, and adapt it only where it is marked as an example or a starting point. Restate emphasis in a sample (MUST, NEVER, CRITICAL, capitals) in calm language with its reason; keep everything else as written.

## Contents

- Effort
- Reasoning in the response
- Progress updates
- Tool-call batching in agent loops
- Append-only conversation history
- Writing density
- Formatting in chat
- Quoting retrieved sources
- Finishing the whole task
- Compaction summaries
- Scope and tests
- Search at low effort
- Safeguard false positives
- Targeted edits
- Long outputs at xhigh and max
- Subagents
- Vision
- Settings that return errors
- Pages for the API setup

## Effort

- Recommend `high`, the default, as the starting level, and tell the user to test `low`, `medium`, `xhigh` and `max` against their own tasks. When the user already ran an effort sweep on Fable 5, tell them to run it again: level names do not map to the same amount of thinking across models.
- Gains over Fable 5 are largest at the higher levels. At `medium`, results roughly match Fable 5 at lower cost: recommend `medium` or `low` where the user's evals show quality holds.
- At `low`, Fable 5.1 is often competitive on cost per task with Opus and Sonnet models while scoring higher: tell the user to include it in the comparison wherever they would otherwise run a smaller model at a higher level.
- At `low` it searches less (see "Search at low effort"); at `xhigh` and `max` it can draft long deliverables twice (see "Long outputs at xhigh and max").

## Reasoning in the response

Never write a prompt, skill or tool description that asks the model to write out its thinking or reasoning: it may be declined with `stop_reason: "refusal"` in the `reasoning_extraction` category. Ask for a short explanation or a summary of the actions taken instead. When the application needs the reasoning, put `display: "summarized"` in the reply's setup.

## Progress updates

Fable 5.1 writes fewer user-facing updates during long tool-calling turns, more so at higher effort and in longer tool chains: users see the agent go quiet for minutes, or a final message that covers only the last step. Work in this order:

1. **Setup:** the notes between tool calls arrive as progress-update thinking blocks, empty at the default `thinking.display` of `"omitted"`. Recommend `display: "updates"` (beta, header `thinking-display-updates-2026-08-18`), rendering each non-empty thinking block as a status line, or `"summarized"`.
2. **Remove** lines that suppress narration, such as "hold all findings for the final response", before adding anything.
3. **Add**, only when the user wants more updates (pair programming, other human-in-the-loop work), this system-prompt line:

```text wrap
Before you start, say in a line what you're about to do; brief updates while you work help the user follow along. Close with a short recap that stands on its own — what you found, what you did, and what's next — so a reader who only sees the last message has the full picture.
```

When the product collapses or hides tool output, tell the model, or it may run commands to "show" output the user never sees. Deliver this note as a turn-scoped system message (`clear_at: "next_user_message"`, beta):

```text wrap
Only you see that command's output — the user's terminal shows at most a few lines of it. If the user needs to read any of it, put it in your reply.
```

## Tool-call batching in agent loops

Apply only to coding and computer-use loops (custom coding agents, bash-and-editor harnesses, computer use) where the next independent calls are implied by the task rather than requested. There Fable 5.1 may issue one call per turn; quality is unaffected, but each extra turn costs tokens, a round trip and time. When a request names several things to fetch, it already calls in parallel.

```text wrap
First privately list what you need next; then request every item that doesn't depend on another's result in this one response.
```

Placement, for the reply's setup:

- After each user message that carries tool results, append the sentence as a turn-scoped system message: a `role: "system"` entry in `messages` with `clear_at: "next_user_message"` (beta header `mid-conversation-system-clear-at-2026-08-21`).
- Without the beta, put the sentence in a text block after the `tool_result` blocks in the same user message.
- Append a fresh copy each turn and leave earlier copies byte for byte. Deleting or rewriting them is an edit to earlier turns: it restarts the prompt cache and invalidates the thinking blocks after them.

## Append-only conversation history

For an application that builds its own message history, put this in the reply's setup:

- Append each assistant turn exactly as returned, thinking blocks included, and never edit earlier turns. For accounts created on or after 2026-08-31, a request that replays a thinking block after its prefix (system prompt, tool list or any earlier message) changed returns a 400 error, or drops the affected blocks with `thinking.block_binding.prefix_mismatch_behavior: "drop_block"` (beta header `thinking-binding-controls-2026-08-01`). Recommend the pattern for every account.
- The edits that break it: injecting and removing per-turn reminders, summarizing older turns in place, changing the system prompt mid-session. Use turn-scoped system messages for reminders, a mid-conversation system message to change instructions or tools, and server-side compaction or context editing for trimming.
- For client-side compaction, replace the whole history with one summary message plus the new user turn.
- Cache reads cost less on Fable 5.1, so suggest testing later compaction points.

## Writing density

In some cases Fable 5.1's prose runs denser than Fable 5's: longer sentences, fewer paragraph breaks. When it does, add this to a user message (preferred) or the system prompt:

```text wrap
Mannered prose substitutes metaphor and flourish for direct statement. Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning." Instead of "this point still matters," they write "this point earns its keep." The phrases exist to display the writer, not to convey the idea, and readers can tell. That is why mannered prose irritates: it makes the reader work harder so the writer can perform. It is also imprecise. Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it.
```

The short version also tends to work:

```text wrap
Please remove all mannered prose.
```

## Formatting in chat

Fable 5.1 uses bold, headers, lists and quotation marks less than older models. Remove anti-formatting rules from the draft, and when a formatting rule is needed, use this one:

```text wrap
Use lists and bullet points when asked to, or when the content is multifaceted enough that they help with clarity. If the person explicitly requests minimal formatting, always format your responses without bullet points, headers, lists, or bold emphasis, as requested. In conversational, personal, or emotional exchanges, keep to plain prose.
```

## Quoting retrieved sources

When the prompt has the model summarize documents, it may reproduce source passages without marking them as quotations. Add one complete example of a correct response to the system prompt, and replace the two `[web_search: ...]` lines with the product's real tool name, so the model reads them as templated tool output:

```text wrap
<example>
<user>look up how the Riverton Ledger and the Coast Dispatch each covered the Harbor Bridge closure and compare their reporting</user>
<response>
[web_search: Harbor Bridge closure Riverton Ledger]
[web_search: Harbor Bridge closure Coast Dispatch]
Both outlets agree on the basics: the bridge closed on March 3 after inspectors found cracked welds, and the state expects repairs to take about eight months. Where they differ is emphasis. The Ledger treats it as a local-economy story. The Dispatch frames it as a funding failure; its editorial calls the closure "entirely foreseeable." Read together, the Ledger explains who is affected now and the Dispatch explains how it came to this — neither account alone gives the whole picture.
</response>
<rationale>CORRECT: The response is organized around where the two outlets agree and differ, not as a walk through either article. Each outlet's reporting is conveyed in one or two sentences of the assistant's own indirect speech. One short marked phrase from one source; every other claim is reworded. The response is still specific and complete.</rationale>
</example>
```

## Finishing the whole task

For complex asynchronous work where the user is not watching, Fable 5.1 can end its turn early: it describes the next step instead of doing it, or asks permission for a step the request already covered. Add both blocks below to the system prompt; when prompt length is limited, add only the first, which keeps most of the effect.

In pair programming and other human-in-the-loop work, stopping to ask suits the workflow, and the first block's opening sentence (the user is not watching) does not fit there.

The first block:

```text wrap
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking 'Want me to…?' or 'Shall I…?' will block the work. For reversible actions that follow from the original request, proceed without asking. Stop only for destructive actions or genuine scope changes the user must decide. Offering follow-ups after the task is done is fine; asking permission before doing the work is not.

Exception: when the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one.

Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ('I'll…', 'let me know when…'), do that work now with tool calls. That includes retrying after errors and gathering missing information yourself. Do not stop because the context or session is long. End your turn only when the task is complete or you are blocked on input only the user can provide.

Before running a command that changes system state (such as restarts, deletes, or config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
```

- Keep the opening sentence as written: it carries much of the effect.
- When the product needs specific confirmations, add a sentence listing them right after the opening sentence.
- The block can also make the model less likely to ask about ambiguous requests: tell the user to check that trade-off on their own tasks.

The second block makes the request the scope of the deliverable:

```text wrap
# Delivering work
The user's request — or the plan they approved — sets the scope, and the scope is the deliverable: don't quietly narrow, widen, or swap it. Read ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings would lead to materially different work. If you see a real problem with the task as specified, say so in a sentence or two and keep building under stated assumptions; if the user hears the concern and reaffirms, that is their decision, so deliver the full request.

If a question comes up partway, first do everything that doesn't depend on the answer; then state the assumption you made, or — when going ahead on a wrong guess would be unsafe or would make the work useless — put the question at the end of a turn that also delivers that progress. If one part turns out to be blocked, complete every other part in full and say exactly what you left out and why — the whole task is the deliverable, and scaling it down is the user's call, not yours. A step you have decided on is something to run, not to announce: describing the next step and ending the turn leaves it undone until the user replies.

Keep changes to what the request needs. Something else you notice worth doing — cleanup or documentation the task didn't call for, a change to a file the task didn't require — is a suggestion to make at the end, not a change to make; actions clearly beyond what the ask implies, and risky or destructive ones, still need the user's go-ahead.
```

## Compaction summaries

When the application compacts the conversation on the client, use this summarization instruction. Server-side compaction already preserves these items.

```text wrap
Summarize the transcript inside <summary></summary> tags. Include relevant information in the summary such that this conversation will be continued by a new context window without needing to redo work or be reprovided with relevant constraints or context. Be sure to preserve: (1) any difficulties or problems that came up, and how they were handled or resolved; (2) any possibilities, options, or approaches that were raised, tried, or set aside, and why; (3) anything that was asked for, decided, agreed, ruled out, or established as a preference, constraint, or boundary — stated exactly; (4) exactly where things stand now — what has been covered, settled, or completed so far; (5) anything still open, unresolved, promised, or expected to happen next; (6) specific details that would be hard to reconstruct — names, numbers, dates, exact wording, links or references — kept exactly. Be complete on these even at the cost of length; keep everything else concise. Weight the two voices differently: keep what the user said, asked for, shared, or established carefully and close to their own words; your own explanations and reasoning can be condensed much further, to what they concluded or produced — as long as nothing in the six items above is dropped.
```

## Scope and tests

On open-ended features, Fable 5.1 may fix nearby code, extend behavior the task did not mention, or commit more test files than the change warrants. When the user wants changes limited to the request, add this instruction; it cut unrequested additions and committed test code substantially with no measurable change in task success:

```text wrap
If, while working or testing, you find a pre-existing bug, a performance concern, or behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the requested behavior cannot work without it; report it as a follow-up in your summary. Where the task is ambiguous, implement the reading its wording and the surrounding code most directly support, state that assumption in your summary, and don't build for the other readings as well. Verify your work however you like; scratch scripts and quick checks need not be kept. Commit tests only where the task asks for them or this repository already keeps tests for this kind of change, sized like the neighboring test files — roughly one focused test per stated behavior — and don't turn scratch checks into additional permanent test files. This is about extras only: implement every behavior the task asks for, completely.
```

## Search at low effort

At `low`, Fable 5.1 calls search and retrieval tools less often and answers from memory more. When the prompt depends on search at `low`, either recommend raising effort for the affected turns (a per-message effort change), or add this to the system prompt:

```text wrap
When a query centers on a name you do not confidently recognize, or recognize from a fast-moving area like AI models and developer tools where the landscape shifts within months, the name itself is the thing to verify: search before answering, and include the name as the user wrote it in at least one query alongside any reformulations. This holds even when you have some background on it — partial background is exactly what makes an out-of-date answer sound authoritative, so familiarity is not a reason to skip the search.
```

## Safeguard false positives

Finding vulnerabilities in source code is permitted. When a benign coding prompt risks `stop_reason: "refusal"`:

- Ask "Are there any bugs in this program?" instead of "Does this program compile without errors?"
- For a lesser-known programming language, give the model context about it, for example access to its documentation.
- Recommend removing base64-encoded data from tool output.

## Targeted edits

When the model rewrites whole text files for small changes, append this to the system prompt or the first user message. The resulting file is usually the same, but unless the file is short or most of it is changing, a rewrite costs more output tokens and time:

```text wrap
The number of tokens used to edit files is best minimized, all else being equal. Therefore, when it will not affect the end result, try to surgically edit a file rather than rewrite the entire thing.
```

## Long outputs at xhigh and max

At `xhigh` and `max`, a request for a long deliverable (a full rewrite of a long document, a large table, a complete code file) may be drafted in thinking and written again in the reply. Recommend `high` for these requests, and `xhigh` or `max` only where the user has measured a quality gain. When the prompt runs at `xhigh` or `max`:

- In the setup, set `max_tokens` with room for the thinking and the reply.
- Append this note to the end of the user message, with `[max_tokens]` replaced by the request's real value (for example 64,000):

```text wrap
Everything produced in one reply, including any reasoning or drafting done before the reply, counts toward a single limit of about [max_tokens] tokens. If that limit is reached before the reply is finished, the person receives a cut-off response and has to start over. Composing an entire output or deliverable in full as reasoning and then again as a reply would double the length of the turn without improving the result, so don't do that.

Instead, when the person has asked for a long or effort-intensive deliverable such as a multi-section document, a large table or dataset, or a complete code file, spend extra effort on understanding the request, checking the inputs the answer depends on, settling the structure and other difficult decisions, and otherwise using the reasoning space to reason and the output space to write an output. Usually it is not needed to draft an output multiple times.
```

## Subagents

When a coding agent lets the model delegate to subagents, recommend this harness setup so the lead keeps working: the tool that starts a subagent returns immediately, each result reaches the lead in a later user message, and a separate tool lets the lead wait when it chooses. On coding tasks this lowered average time to completion at similar quality, token use and cost. The model still often chooses to wait: the savings come from the runs where it carries on with other work.

## Vision

For dense charts and other complex images, recommend running the model as an agent with a container that holds the raw images or videos and has basic image-processing libraries, such as PIL and OpenCV, installed. When a container is too much, a crop tool that returns a chosen region, cropped and enlarged, delivers most of the gain; the crop tool recipe at <https://platform.claude.com/cookbook/multimodal-crop-tool> has a working definition.

## Settings that return errors

- Return a 400 error: forced `tool_choice` (`any` or `tool`, also on the token-counting endpoint), prefill, non-default `temperature`, `top_p` or `top_k`, `budget_tokens`, and `thinking: {"type": "disabled"}`. Replace forced tool use with `auto` plus a sentence saying when the tool applies.
- The model requires 30-day data retention and is not available under zero data retention unless authorized.
- Its classifiers cover the same refusal categories as Fable 5, a broader set than Opus 5's (`bio` is one of the additions).

## Pages for the API setup

When the prompt runs on the API or an agent harness, or is migrated, read live:

| Page | Size | Read |
| :-- | :-- | :-- |
| <https://platform.claude.com/docs/en/models/fable-5-1/migration-guide> | about 43,000 characters without SDK code: sections only | the `##` section for the model the prompt comes from, such as "Migrating to Claude Fable 5.1 from Claude Opus 5" |
