# Writing prompts for Claude Sonnet 5.5: patterns from Sonnet 5

Apply these Sonnet 5 patterns when the target is Sonnet 5.5, except where the Sonnet 5.5 guidance says otherwise; Sonnet 5 itself is never a target. Apply an item only when the prompt's use case calls for it. Use each sample as written, at its stated placement, and adapt it only where it is marked as an example or a starting point. Restate emphasis in a sample (MUST, NEVER, CRITICAL, capitals) in calm language with its reason; keep everything else as written.

## Contents

- Response length
- Tool use
- Progress updates
- Literal instruction following
- Tone and writing style
- Design and frontend defaults
- Interactive coding
- Code review

## Response length

The model fits response length to the task: short on simple lookups, longer on open-ended analysis. When the product needs a particular verbosity, prompt for it. To decrease verbosity, for example:

```text wrap
Provide concise, focused responses. Skip non-essential context, and keep examples minimal.
```

For a specific kind of verbosity (over-explaining), add an instruction against it; positive examples of the wanted concision work better than negative examples or prohibitions.

## Tool use

The model reaches for tools and runs self-verification loops readily, and higher effort means substantially more tool use in agentic search and coding. When the model under-uses a tool (a web search tool, for example), say in the prompt why and when to use it.

## Progress updates

The model gives regular updates on long agentic work. Remove scaffolding that forces interim status messages ("After every 3 tool calls, summarize progress"). When the updates don't fit the use case, describe what they should look like and give examples.

## Literal instruction following

The model reads prompts literally, particularly at lower effort: it does not generalize an instruction from one item to another, and does not infer requests that weren't made. This favors API use with carefully tuned prompts, structured extraction and predictable pipelines. When an instruction should apply broadly, state its scope, for example "Apply this formatting to every section, not just the first one".

## Tone and writing style

When the product relies on a specific voice, re-check style prompts against the model's output. For a warmer, more conversational voice, add:

```text wrap
Use a warm, collaborative tone. Acknowledge the user's framing before answering.
```

Non-default `temperature`, `top_p` or `top_k` returns a 400 error: get stylistic variety from system-prompt instructions instead.

## Design and frontend defaults

On open-ended frontend and design briefs the model can settle into one default visual style, which fits poorly in dashboards, developer tools, fintech, healthcare or enterprise apps. Generic instructions ("don't use that color", "make it clean and minimal") shift it to another fixed palette. Two approaches work:

1. **Specify a concrete alternative.** The model follows explicit specs precisely: give it a concrete visual specification (palette, typography, layout, corner radius, motion) instead of a generic instruction.
2. **Have the model propose options before building.** This gives the user control, and since non-default `temperature` is not accepted, it is the recommended way to get meaningfully different design directions across runs:

```text wrap
Before building, propose 4 distinct visual directions tailored to this brief (each as: bg hex / accent hex / typeface, plus a one-line rationale). Ask the user to pick one, then implement only that direction.
```

Optionally add this short directive against generic patterns to the system prompt, alongside either approach:

```text wrap
<frontend_aesthetics>
NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white or dark backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character. Use unique fonts, cohesive colors and themes, and animations for effects and micro-interactions.
</frontend_aesthetics>
```

## Interactive coding

Token use and behavior differ between autonomous coding agents with a single user turn and interactive agents with many. In interactive coding products the user builds, recommend autonomous features such as an auto mode and fewer required user interactions (in Claude Code, the permission mode stays the user's choice), and put the task, intent and relevant constraints in the first user turn: ambiguous or underspecified specs spread over several turns tend to cost tokens and sometimes quality.

## Code review

A review prompt with "only report high-severity issues", "be conservative" or "don't nitpick" may be followed faithfully, especially in a review harness tuned for an older model: the model may investigate as deeply but report fewer findings, so precision typically rises and measured recall can fall. For a finding stage, add:

```text wrap
Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage - a separate verification step will do that. Your goal here is coverage: it is better to surface a finding that later gets filtered out than to silently drop a real bug. For each finding, include your confidence level and an estimated severity so a downstream filter can rank them.
```

This works without a real second step, but moving the confidence filter to a separate stage often helps; when the harness has a verification, deduplication or ranking stage, tell the model its job at the finding stage is coverage. When the model must filter in a single pass, define the bar concretely instead of with words like "important", for example: "report any bugs that could cause incorrect behavior, a test failure, or a misleading result; only omit nits like pure style or naming preferences." Tell the user to check recall on a sample of their own test cases.
