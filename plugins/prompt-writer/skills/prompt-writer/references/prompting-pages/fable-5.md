# Writing prompts for Claude Fable 5

Apply these patterns to Fable 5, and to Fable 5.1 except where the Fable 5.1 guidance gives its own version. Apply an item only when the prompt's use case calls for it. Use each sample as written, at its stated placement, and adapt it only where it is marked as an example or a starting point. Restate emphasis in a sample (MUST, NEVER, CRITICAL, capitals) in calm language with its reason; keep everything else as written.

## Contents

- Long turns and overplanning
- Effort
- Brief instructions steer
- Grounded progress claims
- Boundaries
- Parallel subagents
- Memory
- Early stopping
- Context-budget concern
- Giving the reason
- Readable final summaries
- Send-to-user tool
- Prompts and skills written for older models
- Reasoning in the response
- Settings that return errors
- Pages for the API setup

## Long turns and overplanning

Hard tasks at higher effort can run for many minutes, and autonomous runs for hours. In the reply's setup, recommend longer client timeouts, streaming, user-facing progress indicators, and checking runs asynchronously (for example through scheduled jobs) instead of blocking.

When the task is ambiguous, add this to keep the model from overplanning:

```text wrap
When you have enough information to act, act. Do not re-derive facts already established in the conversation, re-litigate a decision the user has already made, or narrate options you will not pursue in user-facing messages. If you are weighing a choice, give a recommendation, not an exhaustive survey. This does not apply to thinking blocks.
```

## Effort

- Recommend `high` for most tasks, `xhigh` for the most capability-sensitive work, and `medium` or `low` for routine work. Recommend lowering effort when a task completes but takes longer than it needs, or when the user wants a quicker, more interactive style.
- On routine work at higher effort, the model can gather context and deliberate beyond what the task needs; higher effort also often produces excellent verification, sophisticated reasoning and the most rigorous output, so weigh both. To prevent unrequested tidying or refactoring at higher effort, add:

```text wrap
Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup and a one-shot operation usually doesn't need a helper. Don't design for hypothetical future requirements: do the simplest thing that works well. Avoid premature abstraction and half-finished implementations. Don't add error handling, fallbacks, or validation for scenarios that cannot happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use feature flags or backwards-compatibility shims when you can just change the code.
```

## Brief instructions steer

A brief instruction steers most behaviors as well as listing each one: write the shortest instruction that names the behavior. Unsteered, especially at higher effort, the model can survey options it won't pursue, explain root causes at length, write heavily structured PR descriptions, or add comments that narrate the next line. For brevity, add:

```text wrap
Lead with the outcome. Your first sentence after finishing should answer "what happened" or "what did you find": the thing the user would ask for if they said "just give me the TLDR." Supporting detail and reasoning come after. Being readable and being concise are different things, and readability matters more.

The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next), not to compress the writing into fragments, abbreviations, arrow chains like A → B → fails, or jargon.
```

For checkpoints in long-running workflows, this is enough, with no list of cases:

```text wrap
Pause for the user only when the work genuinely requires them: a destructive or irreversible action, a real scope change, or input that only they can provide. If you hit one of these, ask and end the turn, rather than ending on a promise.
```

## Grounded progress claims

On long autonomous runs, add this; in Anthropic's testing it nearly eliminated fabricated status reports:

```text wrap
Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so explicitly. Report outcomes faithfully: if tests fail, say so with the output; if a step was skipped, say that; when something is done and verified, state it plainly without hedging.
```

## Boundaries

The model can occasionally take unrequested actions, such as drafting an email nobody asked for or creating defensive git-branch backups. State what it should and should not do:

```text wrap
When the user is describing a problem, asking a question, or thinking out loud rather than requesting a change, the deliverable is your assessment. Report your findings and stop. Don't apply a fix until they ask for one. Before running a command that changes system state (restarts, deletes, config edits), check that the evidence actually supports that specific action. A signal that pattern-matches to a known failure may have a different cause.
```

## Parallel subagents

The model dispatches parallel subagents readily. Tell it to use them, say when delegation fits, and prefer asynchronous coordination over blocking until each subagent returns. In the setup, recommend long-lived subagents that keep their context across subtasks: they save time and cost through cache reads. Add:

```text wrap
Delegate independent subtasks to subagents and keep working while they run. Intervene if a subagent goes off track or is missing relevant context.
```

## Memory

When the model works across sessions, give it a place to record lessons, as simple as a Markdown file, and add:

```text wrap
Store one lesson per file with a one-line summary at the top. Record corrections and confirmed approaches alike, including why they mattered. Don't save what the repo or chat history already records; update an existing note rather than creating a duplicate; delete notes that turn out to be wrong.
```

To build the memory from existing history, a prompt like this, with `[X]` replaced by the location:

```text wrap
Reflect on the previous sessions we've had together. Use subagents to identify core themes and lessons, and store them in [X]. Make sure you know to reference [X] for future use.
```

## Early stopping

Deep into a long session the model can occasionally end a turn by announcing a step without the tool call, or ask permission it doesn't need. In interactive use, "continue" suffices. To define when pausing fits, use the checkpoint instruction in "Brief instructions steer". For autonomous pipelines, also add this system reminder:

```text wrap
You are operating autonomously. The user is not watching in real time and cannot answer questions mid-task, so asking "Want me to…?" or "Shall I…?" will block the work. For reversible actions that follow from the original request, proceed without asking. Offering follow-ups after the task is done is fine; asking permission after already discussing with the user before doing the work is not. Before ending your turn, check your last paragraph. If it is a plan, an analysis, a question, a list of next steps, or a promise about work you have not done ("I'll…", "let me know when…"), do that work now with tool calls. End your turn only when the task is complete or you are blocked on input only the user can provide.
```

## Context-budget concern

In very long sessions the model can occasionally suggest a new session, offer to hand off, or trim its own work, most often when the harness shows a remaining-token countdown. Recommend not showing the countdown. When the harness must show it, add:

```text wrap
You have ample context remaining. Do not stop, summarize, or suggest a new session on account of context limits. Continue the work.
```

## Giving the reason

The model performs better when it knows why it is asked, especially in long-running agents drawing on several workstreams. Frame the request with its purpose:

```text wrap
I'm working on [the larger task] for [who it's for]. They need [what the output enables]. With that in mind: [request].
```

## Readable final summaries

In long agentic conversations the model can write hard-to-follow text: arrow-chain shorthand, deep implementation detail, references to thinking the user never saw. Add:

```text wrap
Terse shorthand is fine between tool calls. Your final summary is different: it's for a reader who didn't see any of that.

If you've been working for a while without the user watching (overnight, across many tool calls, since they last spoke), your final message is their first look at any of it. Write it as a re-grounding, not a continuation of your working thread: the outcome first, then the one or two things you need from them, each explained as if new. The vocabulary you built up while working is yours, not theirs; leave it behind unless you re-introduce it.

When you write the summary at the end, drop the working shorthand. Write complete sentences. Spell out terms. Don't use arrow chains, hyphen-stacked compounds, or labels you made up earlier. When you mention files, commits, flags, or other identifiers, give each one its own plain-language clause. Open with the outcome: one sentence on what happened or what you found. Then the supporting detail. If you have to choose between short and clear, choose clear.
```

## Send-to-user tool

When a long asynchronous agent must show the user something exactly as written without ending its turn (a deliverable, a progress update with specific numbers, a direct answer to a mid-loop question), recommend a client tool whose input the UI renders verbatim and acknowledges with a simple tool result. Tool inputs are never summarized. For agents that only narrate routine progress, the model's own summaries are usually enough. The tool definition:

```json
{
  "name": "send_to_user",
  "description": "Display a message directly to the user. Use this for progress updates, partial results, or content the user must see exactly as written before the task finishes.",
  "input_schema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The content to display to the user."
      }
    },
    "required": ["message"]
  }
}
```

The model rarely calls it without a system-prompt instruction. Pair the tool with:

```text wrap
Between tool calls, when you have content the user must read verbatim (a partial deliverable, a direct answer to their question), call the send_to_user tool with that content. Use send_to_user only for user-facing content, not for narration or reasoning.
```

## Prompts and skills written for older models

- They are often too prescriptive for this model and can degrade its output. When refining, auditing or migrating, review older instructions and consider removing them where default performance is better.
- For long-running tasks, verification works best through separate, fresh-context verifier subagents rather than self-critique. Add, with `[X]` replaced:

```text wrap
Establish a method for checking your own work at an interval of [X] as you build. Run this every [X interval], verifying your work with subagents against the specification.
```

## Reasoning in the response

Never write a prompt, skill or harness instruction that tells the model to echo, transcribe or explain its internal reasoning in the response: it may be declined as `reasoning_extraction`, and server-side fallback with `fallbacks: "default"` does not retry that category. When refining or migrating, find and remove reflection or show-your-thinking instructions. A short explanation of the answer, or a summary of the actions taken, is fine. When the application needs the reasoning, recommend reading the thinking blocks in the setup, and a send-to-user tool for progress during long runs.

The classifiers target offensive cybersecurity techniques, biology and life sciences content, and extraction of the model's summarized thinking; benign security and life sciences work can trigger them too.

## Settings that return errors

- Return a 400 error: prefill, non-default `temperature`, `top_p` or `top_k`, `budget_tokens`, and `thinking: {"type": "disabled"}`.
- Forced `tool_choice` (`any` or `tool`) is accepted on Fable 5; Fable 5.1 rejects it.
- Model ID `claude-fable-5`. Adaptive thinking is always on; `thinking.display` defaults to `"omitted"`, and `"summarized"` is available.
- Effort is request-level: changing it between requests drops the cached prefix.
- Fable 5 does not run the history prefix check; an append-only history still keeps the prompt cache warm.

## Pages for the API setup

When the prompt runs on the API or an agent harness, read live:

| Page | Size | Read |
| :-- | :-- | :-- |
| <https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1> | about 28,000 characters without SDK code; whole | "Unchanged from Claude Fable 5" under "Behavior differences", for the settings Fable 5 rejects |
