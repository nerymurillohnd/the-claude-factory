# Prompting techniques for every covered model

These techniques come from the official prompting best-practices page and apply to every covered model; where the target model's prompting files say otherwise, they win. Apply a technique only when its trigger holds: an unneeded technique adds length and noise. Use each sample as written, except that emphasis (MUST, NEVER, CRITICAL, capitals) is restated in calm language with its reason; adapt it only where it is marked as an example, and when a technique names the model it was measured on, re-check it before applying it to another.

## Contents

- Index by trigger
- Core rules
- Examples
- Structure and role
- Long inputs
- Model self-knowledge
- Output and formatting
- Migrating away from prefill
- Tool use and action
- Parallel tool calls
- Thinking
- Long-horizon and multi-window work
- Autonomy and reversibility
- Research
- Subagents
- Prompt chains
- Agentic coding
- Vision
- Frontend design
- Prompts from older models

## Index by trigger

| When the prompt… | Read |
| :-- | :-- |
| is any prompt | Core rules |
| must keep a format, tone or structure | Examples, Output and formatting |
| mixes instructions, context, examples and inputs, or is a system prompt | Structure and role |
| carries documents of about 20,000 tokens or more | Long inputs |
| belongs to an app that must state its model or pick a model string | Model self-knowledge |
| controls format, preamble, math notation, summaries or visual documents | Output and formatting |
| comes from a draft that used prefill | Migrating away from prefill |
| gives the model tools, or should act or only advise | Tool use and action, Parallel tool calls |
| depends on how much or how the model thinks | Thinking |
| runs long, compacts context or spans several context windows | Long-horizon and multi-window work |
| can take risky or irreversible actions | Autonomy and reversibility |
| asks for research across sources | Research |
| runs where subagents are available | Subagents |
| needs intermediate outputs inspected | Prompt chains |
| drives a coding agent | Agentic coding |
| processes images or extracts data from them | Vision |
| builds a frontend | Frontend design |
| is migrated from an older model | Prompts from older models |

## Core rules

- **Be clear and direct.** State the output format and the constraints exactly. Run the golden rule on the finished prompt: a colleague with minimal context on the task should be able to follow it without being confused.
- **Number the steps** when their order or completeness matters.
- **Ask for above-and-beyond work explicitly** when it is wanted, and name the wanted features (animations, interactivity): the model does not infer extra ambition from a vague prompt. Example:

```text
Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.
```

- **Give the reason** behind each important constraint: the model generalizes from it. Example, instead of "NEVER use ellipses":

```text
Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them.
```

- **Use calm, targeted language.** Write "Use this tool when…" instead of "CRITICAL: You MUST use this tool when…": prompts written to fix undertriggering on older models may overtrigger on the models that followed them, and "If in doubt, use [tool]" can cause overtriggering. Confirm in the target model's prompting files.

## Examples

When format, tone or structure must be consistent, include three to five examples that are relevant (mirror the use case), diverse (cover edge cases, so no unintended pattern is copied) and structured (each in `<example>` tags, all inside `<examples>`). Claude can evaluate examples for relevance and diversity, or generate more from an initial set.

## Structure and role

- When the prompt mixes instructions, context, examples and variable inputs, wrap each kind in its own XML tag (`<instructions>`, `<context>`, `<input>`). Use consistent, descriptive tag names, and nest tags when content has a hierarchy (documents inside `<documents>`, each inside `<document index="n">`).
- For a system prompt, set a role tied to the use case; even a single sentence makes a difference.

## Long inputs

For documents or data of about 20,000 tokens or more:

- Put the long inputs at the top, above the query, instructions and examples. Queries at the end can improve response quality by up to 30 percent in tests, especially with complex, multi-document inputs.
- With several documents, wrap each in `<document>` tags with `<document_content>` and `<source>` (and other metadata) subtags, inside `<documents>`.
- Ask for the relevant quotes first, in `<quotes>` tags, then for the task based on those quotes.

## Model self-knowledge

When an app must state which model it runs, or when the model must pick a model string for an LLM it calls, use these, with the target model's name and string:

```text
The assistant is Claude, created by Anthropic. The current model is Claude Opus 5.5.
```

```text
When an LLM is needed, please default to Claude Opus 5.5 unless the user requests
otherwise. The exact model string for Claude Opus 5.5 is claude-opus-5-5.
```

## Output and formatting

- **Summaries after tool use.** The models may skip a summary after tool calls and go straight to the next action. When the user wants visibility, add:

```text
After completing a task that involves tool use, provide a quick summary of the work you've done.
```

- **Opus 5 length.** Opus 5 is the exception on length: its responses run long, and effort does not reliably change their length; prompt for concision instead.
- **Fable 5.1 progress text.** Fable 5.1 has the opposite tendency during agentic work: it writes fewer user-facing updates between tool calls. Ask for progress text explicitly, and remove any instruction telling it to keep that text brief.
- **Format control:** say what to do instead of what not to do ("Your response should be composed of smoothly flowing prose paragraphs." instead of "Do not use markdown in your response"); use XML format indicators ("Write the prose sections of your response in <smoothly_flowing_prose_paragraphs> tags."); match the prompt's own style to the output wanted (less markdown in the prompt, less in the output); for strict control, a detailed format block. A long minimize-markdown block can suppress structure Fable 5.1 needs: for Fable 5.1, leave it out or use the shorter formatting rule in its prompting files.
- **No preamble.** When the output must start with the content itself, use a system-prompt instruction: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc." Alternatives: output inside XML tags, structured outputs or a tool call. If an occasional preamble slips through, strip it in post-processing.
- **Plain-text math.** The models default to LaTeX for math. When plain text is needed, add:

```text
Format your response in plain text only. Do not use LaTeX, MathJax, or any markup
notation such as \( \), $, or \frac{}{}. Write all math expressions using standard text
characters (e.g., "/" for division, "*" for multiplication, and "^" for exponents).
```

- **Presentations and visual documents.** Ask for design explicitly. Example:

```text
Create a professional presentation on [topic]. Include thoughtful design elements,
visual hierarchy, and engaging animations where appropriate.
```

## Migrating away from prefill

A prefilled last assistant turn returns a 400 error on every covered model. Replace each old use:

- **Output format** (JSON, YAML, classification): structured outputs, or ask the model to conform to the structure, best with retries; for classification, a tool with an enum field.
- **Preamble:** the no-preamble instruction in "Output and formatting".
- **Refusals the prefill steered around:** clear prompting in the user message, without prefill.
- **Continuations:** move the continuation to the user message with the interrupted text: "Your previous response was interrupted and ended with \`[previous_response]\`. Continue from where you left off." When the continuation is part of error or incomplete-response handling and there is no UX penalty, retry the request instead.
- **Context hydration** in very long conversations: inject the reminders into the user turn; in a more complex agentic system, consider hydrating through tools or during context compaction.

## Tool use and action

- Wording is taken literally: "Can you suggest some changes to improve this function?" yields suggestions; "Change this function to improve its performance." yields edits.
- When the agent should act by default, add to the system prompt:

```text
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is
unclear, infer the most useful likely action and proceed, using tools to discover any
missing details instead of guessing. Try to infer the user's intent about whether a tool
call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>
```

- When the agent should only advise until told to act:

```text
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed to make
changes. When the user's intent is ambiguous, default to providing information, doing
research, and providing recommendations rather than taking action. Only proceed with
edits, modifications, or implementations when the user explicitly requests them.
</do_not_act_before_instructions>
```

- Choose between them from whether the user wants the agent to act or to advise by default.

## Parallel tool calls

The models already run independent tool calls in parallel. To push this toward always:

```text
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool
calls, make all of the independent tool calls in parallel. Prioritize calling tools
simultaneously whenever the actions can be done in parallel rather than sequentially.
For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into
context at the same time. Maximize use of parallel tool calls where possible to increase
speed and efficiency. However, if some tool calls depend on previous calls to inform
dependent values like the parameters, do NOT call these tools in parallel and instead
call them sequentially. Never use placeholders or guess missing parameters in tool
calls.
</use_parallel_tool_calls>
```

To reduce parallel execution for system stability:

```text
Execute operations sequentially with brief pauses between each step to ensure stability.
```

On Fable 5.1 in long agent loops, send the parallel-calls instruction as a turn-scoped system message after each round of tool results.

## Thinking

- **Prefer general instructions over prescriptive steps:** "think thoroughly" often produces better reasoning than a hand-written step-by-step plan.
- **Worked examples shape thinking:** present each as a problem, the method to apply, and the expected answer.
- **Never use manual chain-of-thought** on the covered models: rely on thinking instead, at a lower effort if cost or latency matters. A prompt that asks the model to write out its reasoning, for example in `<thinking>` tags, may be declined.
- **Self-check:** append something like "Before you finish, verify your answer against [test criteria]." It catches errors, especially in coding and math. Never add it for Opus 5 or Opus 5.5, which verify on their own and over-verify with it.
- **Reflection after tool results:**

```text
After receiving tool results, carefully reflect on their quality and determine optimal
next steps before proceeding. Use your thinking to plan and iterate based on this new
information, and then take the best next action.
```

- **Too much thinking.** When the model thinks more often than wanted (large or complex system prompts can cause it), add this instruction, or lower effort:

```text
Thinking adds latency and should only be used when it will meaningfully improve
answer quality - typically for problems that require multistep reasoning. When in
doubt, respond directly.
```

- **Overthinking** was measured on an older model; confirm it on the target before applying: replace blanket defaults ("Default to using [tool]") with targeted ones ("Use [tool] when it would enhance your understanding of the problem"), and when the model keeps revisiting its approach, add:

```text
When you're deciding how to approach a problem, choose an approach and commit to it.
Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. If you're weighing two approaches, pick one and see it
through. You can always course-correct later if the chosen approach fails.
```

## Long-horizon and multi-window work

- **Compaction notice.** Only when the harness really compacts context or saves it to external files, add this; otherwise the model may wrap up as it nears the limit:

```text
Your context window will be automatically compacted as it approaches its limit, allowing
you to continue working indefinitely from where you left off. Therefore, do not stop
tasks early due to token budget concerns. As you approach your token budget limit, save
your current progress and state to memory before the context window refreshes. Always be
as persistent and autonomous as possible and complete tasks fully, even if the end of
your budget is approaching. Never artificially stop any task early regardless of the
context remaining.
```

- **Several context windows:**
  1. Use a different prompt for the first window, to set up the framework (tests, setup scripts); later windows iterate on a to-do list.
  2. Have the model write tests in a structured file (for example `tests.json`), and state: "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."
  3. Encourage setup scripts (for example `init.sh`) that start servers, test suites and linters.
  4. To start a fresh window rather than compact, be prescriptive: "Call pwd; you can only read and write files in this directory." "Review progress.txt, tests.json, and the git logs." "Manually run through a fundamental integration test before moving on to implementing new features."
  5. Provide verification tools for UI work: computer use, browser use, or a browser automation MCP server.
  6. Encourage complete use of the context:

```text
This is a very long task, so it may be beneficial to plan out your work clearly. It's
encouraged to spend your entire output context working on the task - just make sure you
don't run out of context with significant uncommitted work. Continue working
systematically until you have completed this task.
```

- **State:** JSON or another structured format for structured state (test results, task status); free-text progress notes for general progress; git for history and restorable checkpoints. Ask the model to track its progress and work incrementally.

## Autonomy and reversibility

When the agent can take actions that are hard to reverse or affect shared systems (measured on an older model; confirm it in the target model's prompting files), add:

```text
Consider the reversibility and potential impact of your actions. You are encouraged to
take local, reversible actions like editing files or running tests, but for actions that
are hard to reverse, affect shared systems, or could be destructive, ask the user before
proceeding.

Examples of actions that warrant confirmation:
- Destructive operations: deleting files or branches, dropping database tables, rm -rf
- Hard to reverse operations: git push --force, git reset --hard, amending published commits
- Operations visible to others: pushing code, commenting on PRs/issues, sending
messages, modifying shared infrastructure

When encountering obstacles, do not use destructive actions as a shortcut. For example,
don't bypass safety checks (e.g. --no-verify) or discard unfamiliar files that may be
in-progress work.
```

## Research

Define what a successful answer is, and ask the model to verify information across several sources. For complex research, add:

```text
Search for this information in a structured way. As you gather data, develop several
competing hypotheses. Track your confidence levels in your progress notes to improve
calibration. Regularly self-critique your approach and plan. Update a hypothesis tree or
research notes file to persist information and provide transparency. Break down this
complex research task systematically.
```

## Subagents

Describe the subagent tools well and let the model delegate on its own. Opus 5 delegates more readily than older models: for it, use the delegation guidance in its prompting files. When a model delegates more than it should, add:

```text
Use subagents when tasks can run in parallel, require isolated context, or involve
independent workstreams that don't need to share state. For simple tasks, sequential
operations, single-file edits, or tasks where you need to maintain context across steps,
work directly rather than delegating.
```

## Prompt chains

Thinking and subagents handle most multistep work in one call. Recommend separate calls only when intermediate outputs must be inspected or a pipeline enforced; the most common chain is self-correction: draft → review against criteria → refine.

## Agentic coding

- **Temporary files.** Temporary files can improve agentic coding results; when the user prefers no net-new files, add:

```text
If you create any temporary new files, scripts, or helper files for iteration, clean up
these files by removing them at the end of the task.
```

- **Overengineering** (measured on older models; confirm it in the target model's prompting files). When the model adds files, abstractions or flexibility nobody asked for, add:

```text
Avoid over-engineering. Only make changes that are directly requested or clearly
necessary. Keep solutions simple and focused:

- Scope: Don't add features, refactor code, or make "improvements" beyond what was
asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need
extra configurability.

- Documentation: Don't add docstrings, comments, or type annotations to code you didn't
change. Only add comments where the logic isn't self-evident.

- Defensive coding: Don't add error handling, fallbacks, or validation for scenarios
that can't happen. Trust internal code and framework guarantees. Only validate at system
boundaries (user input, external APIs).

- Abstractions: Don't create helpers, utilities, or abstractions for one-time
operations. Don't design for hypothetical future requirements. The right amount of
complexity is the minimum needed for the current task.
```

- **Tests as targets.** When the model may focus on passing tests or use workarounds, add:

```text
Please write a high-quality, general-purpose solution using the standard tools
available. Do not create helper scripts or workarounds to accomplish the task more
efficiently. Implement a solution that works correctly for all valid inputs, not just
the test cases. Do not hard-code values or create solutions that only work for specific
test inputs. Instead, implement the actual logic that solves the problem generally.

Focus on understanding the problem requirements and implementing the correct algorithm.
Tests are there to verify correctness, not to define the solution. Provide a principled
implementation that follows best practices and software design principles.

If the task is unreasonable or infeasible, or if any of the tests are incorrect, please
inform me rather than working around them. The solution should be robust, maintainable,
and extendable.
```

- **Grounded answers about code.** To minimize hallucinations, add:

```text
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file,
you MUST read the file before answering. Make sure to investigate and read relevant
files BEFORE answering questions about the codebase. Never make any claims about code
before investigating unless you are certain of the correct answer - give grounded and
hallucination-free answers.
</investigate_before_answering>
```

## Vision

For image processing and data extraction, especially with several images, give the model a crop tool or an agent skill so it can zoom into relevant regions; the recipe at <https://platform.claude.com/cookbook/multimodal-crop-tool> has a working definition. These vision gains were measured on older models.

## Frontend design

Without guidance, the models default to generic patterns. For frontend work, use this system-prompt snippet:

```text
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this
creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive
frontends that surprise and delight.

Focus on:
- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic
fonts like Arial and Inter; opt instead for distinctive choices that elevate the
frontend's aesthetics.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency.
Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw
from IDE themes and cultural aesthetics for inspiration.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only
solutions for HTML. Use Motion library for React when available. Focus on high-impact
moments: one well-orchestrated page load with staggered reveals (animation-delay)
creates more delight than scattered micro-interactions.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer
CSS gradients, use geometric patterns, or add contextual effects that match the overall
aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the
context. Vary between light and dark themes, different fonts, different aesthetics. You
still tend to converge on common choices (Space Grotesk, for example) across
generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>
```

## Prompts from older models

When migrating a prompt written for an older model:

- Describe the wanted output exactly, and request features such as animations and interactive elements explicitly.
- Frame instructions with modifiers that encourage more quality and detail ("Go beyond the basics…").
- Replace manual thinking (`budget_tokens`, which returns a 400 error) with adaptive thinking and effort.
- Migrate away from prefill (see "Migrating away from prefill").
- Dial back anti-laziness and "use tools aggressively" guidance written for older models.
- Append each assistant turn exactly as the API returned it, thinking blocks included, and keep the history append-only. On Fable 5.1, Opus 5.5 and Sonnet 5.5, for accounts created on or after 2026-08-31, modifying the conversation before a thinking block returns an error; keep the pattern for every account: move such changes to mid-conversation system messages and server-side context management.
