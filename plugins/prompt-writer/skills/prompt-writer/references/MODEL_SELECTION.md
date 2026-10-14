# Step 2: Select the model

Recommend exactly one target model, an effort level and the session settings before you write the prompt. Scope: Claude Fable 5.1, Claude Fable 5, Claude Opus 5.5, Claude Opus 5, Claude Sonnet 5.5. Never leave the target open: the covered models' prompting pages give opposite instructions for the same technique.

## Contents

- Steps
- Decision rules
- Effort table
- Applies to every covered model
- Setup to recommend
- API and agent-harness configuration
- A model outside the scope

## Steps

1. **Classify the task** on four axes:
   - **Difficulty:** routine, moderate, hard, or frontier (open, ambiguous, unsolved).
   - **Horizon:** single reply, short multistep, or long-running agentic (hours or more, subagents).
   - **Constraints:** latency-sensitive, cost-sensitive, or quality-first.
   - **Domain risk:** offensive security, biology or life sciences, or requests to reveal reasoning.
2. **Check availability.** Respect the user's selected model and environment when workable. If the user is pinned to a model (platform, plan, existing pipeline), write for that model and skip to step 4. Rule out a model the user's surface or plan cannot run, and Fable 5.1 when the organization lacks 30-day data retention. When the surface, plan, platform or retention is unknown and would change the pick, it belongs in the Step 1 round; when it surfaces only now, ask it as that round's one follow-up; otherwise state the assumption.
3. **Pick the model** using the decision rules below. Prefer Fable 5.1, Opus 5.5 or Sonnet 5.5. Pick Fable 5 or Opus 5 only when the user is pinned to it or is migrating a prompt already tuned for it. Tune effort before switching models: it is often the better lever. Latency and cost often improve more by choosing a different model than by rewording the prompt. State the choice and the one reason that decided it.
4. **Check for changes.** Before setting effort and setup, read the target's change page live and whole, as Step 2 in `SKILL.md` says. Follow any model ID, default, effort level, breaking change, refusal or fallback rule, or setting that returns an error that differs from this file, and report it in the design notes. Keep the page's behavior differences for Step 4.
   - Claude Fable 5.1: <https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1>
   - Claude Fable 5: <https://platform.claude.com/docs/en/models/fable-5/overview>
   - Claude Opus 5.5: <https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5>
   - Claude Opus 5: <https://platform.claude.com/docs/en/models/opus-5/overview>
   - Claude Sonnet 5.5: <https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5>

   Fable 5 and Opus 5 have no what's-new page of their own: their change page is their overview. The successor's what's-new page their prompting files list is an API setup page, read only when the API setup applies.
5. **Pick the effort** from the effort table. Never carry an effort value across models: effort names map to different amounts of thinking on each model.
6. **Set the rest of the setup** (see "Setup to recommend").
7. **Record the recommendation** for the reply around the deliverable; the session mode, the design and the prompt come next.

## Decision rules

The default row holds unless the user's stated priority or situation matches another row; when two rows match, the user's stated priority decides.

| Situation | Recommend |
|---|---|
| Default for most workloads: agentic coding in real repos, code review, knowledge work, document and chart reading, computer use | **Opus 5.5** |
| Hardest reasoning, frontier problems, long-horizon autonomous work, or Opus 5.5 at higher effort still falls short | **Fable 5.1** |
| Speed matters most: chat, well-specified coding, multistep tool use, high volume | **Sonnet 5.5** |
| Pinned to the previous generation | **Fable 5** or **Opus 5**, matching the tier above |
| Offensive security or biology or life sciences | Not Fable. Warn that safety classifiers on every model in scope can return `stop_reason: "refusal"` |
| Cost-sensitive but quality-first | **Fable 5.1 at `low`**: it is often competitive on cost per task with Opus 5.5 or Sonnet 5.5 at higher effort while scoring higher; name that alternative as the one to compare against |

## Effort table

| Model | Default | Start here | Raise to |
|---|---|---|---|
| Fable 5.1 | `high` | `high`; `medium` for routine work (matches Fable 5 quality at lower cost) | `xhigh`/`max` only after a measured gain |
| Fable 5 | `high` | `high`; `medium`/`low` for routine or interactive work | `xhigh` for the most capability-sensitive work |
| Opus 5.5 | `medium` | `medium` (matches or beats Opus 5 at `high`); `low` for cost-sensitive coding | `xhigh`/`max` only after a measured gain |
| Opus 5 | `high` | `high`; `low`/`medium` wherever quality holds | `xhigh` for demanding coding and agentic work |
| Sonnet 5.5 | `high` | `high` for most work; `medium` for well-specified agentic coding and multistep tool use; `medium` or `low` for chat and other latency-sensitive work | `high` for harder or longer tasks; `xhigh`/`max` only after a measured gain |

- Effort is soft: it guides thinking and also tool behavior, and lower effort makes fewer and terser tool calls. `max_tokens` is the hard ceiling.
- Effort affects all output tokens, text included, except on Opus 5, where it does not reliably shorten responses: prompt for length there.
- A top-level effort change between requests restarts the prompt cache. To change it mid-conversation, recommend the per-message form (beta) where the model supports it. `adaptive` is a thinking mode, not an effort value.
- The effort documentation describes the API. Before recommending a level for the Claude app or Claude Code, confirm that surface exposes the setting.

## Applies to every covered model

- Never ask the model to write out its reasoning in the response; it can trigger `reasoning_extraction` refusals. Ask for a short summary instead.
- Size `max_tokens` for thinking plus the reply.
- Lower effort is the most reliable lever for cost and latency, more reliable than prompt instructions.

## Setup to recommend

Give each of these separately in the reply, and only when it applies:

- The recommended model.
- The recommended effort, if the surface supports it.
- The execution surface. The session mode is chosen in Step 3.
- The tools and permissions the prompt needs.
- Configuration outside the prompt text. For the API or an agent harness, give the configuration the prompt depends on (see "API and agent-harness configuration"): much of what makes a prompt work there lives in that configuration, not in the text.

Never fabricate parameter values, command syntax, product modes or available permissions. Never imply that a recommendation has changed the user's configuration. When an exact value cannot be verified, write the recommended value and state what remains unconfirmed. Product modes and features (Claude Code permission modes, effort settings in the app, Claude app features, skills to pair with the prompt) change: confirm on its official page that each exists, and how it is named, before recommending it:

| Product fact | Page | Size and sections |
| :-- | :-- | :-- |
| Claude Code model selection and effort (`/model`, `/effort`) | <https://code.claude.com/docs/en/model-config> | about 116,000 characters: subsections only, "### Setting your model" and "### Adjust effort level" (about 12,000 to 13,000 each) |
| Claude Code permission modes and plan mode | <https://code.claude.com/docs/en/permission-modes> | about 90,000 characters: sections only, "## Switch permission modes" (about 9,700) |
| Claude Code skills and slash commands | <https://code.claude.com/docs/en/skills> | about 100,000 characters: subsections only, "### Frontmatter reference" and "### Pass arguments to skills" |

## API and agent-harness configuration

Check what the prompt depends on outside its text, in this order, and give it in the reply's setup:

1. **Platform first.** Features differ by platform (Claude API, Amazon Bedrock, Google Cloud, Microsoft Foundry): confirm the user's platform before recommending structured outputs, strict tools, per-message effort, server-side fallback or fast mode.
2. **Effort**, set explicitly.
3. **`max_tokens`**, sized for thinking plus the reply: thinking counts toward it even when hidden. Above 21,333 the SDK requires streaming.
4. **Thinking display.** `display` defaults to `"omitted"`. Use `"updates"` (beta) when users must see the progress notes the model writes between tool calls, and `"summarized"` when someone must read the reasoning.
5. **Remove what returns a 400 error,** from the target model's prompting files and its what's-new page: sampling parameters, prefill, `budget_tokens`, forced `tool_choice` and disabled thinking where the model rejects them. Replace forced tool use with `auto` plus a sentence saying when the tool applies; when the application requires the call on this turn, append a mid-conversation system message after the latest user turn that names the tool and says to open with it. Use strict tools where available.
6. **Keep the conversation append-only.** Freeze `system` and `tools` at session start and put changing values (the date, a mode) in mid-conversation system messages. Send per-turn reminders as turn-scoped system messages and leave them in the history. Add or remove tools with tool-change blocks. Echo assistant turns exactly, thinking blocks included. For client-side compaction, replace the whole history with one summary. An account created before enforcement began won't see the errors a newer account gets, so the pattern matters even when tests pass.
7. **Handle refusals.** A refusal is HTTP 200 with `stop_reason: "refusal"`: branch on it, and discard any partial output that came before a mid-stream refusal. Fallback has no recommended model for `reasoning_extraction`; the fix for that category is the prompt.
8. **Structured outputs** when the format must be guaranteed. Put no reasoning field in the schema; ask for a short explanation instead. Check `stop_reason` before parsing.

When an item needs more than this list, read its page live:

| Page | Size | Read |
| :-- | :-- | :-- |
| <https://platform.claude.com/docs/en/about-claude/models/choosing-a-model> | about 9,000 characters; whole | "Choose the best model to start with", "Model selection matrix" |
| <https://platform.claude.com/docs/en/models/overview> | about 20,000 characters; whole | "Compare models", for model IDs and availability |
| <https://platform.claude.com/docs/en/build-with-claude/effort> | about 28,000 characters without SDK code; whole | "Best practices"; "Effort with tool use" and "Effort with thinking" when they apply; "Change effort mid-conversation" for multi-turn API work |
| <https://platform.claude.com/docs/en/build-with-claude/thinking> | about 67,000 characters without SDK code: sections only | "Configuring thinking"; "Reading thinking output"; "Thinking with tool use"; "Limits and feature compatibility" |
| <https://platform.claude.com/docs/en/build-with-claude/preserved-thinking> | about 82,000 characters without SDK code: sections only | "Who needs to change anything" first; then "Keeping the prefix unchanged" and "Make changes without editing the prefix" when the application builds its own message history; "Switching models mid-conversation" when it routes or falls back between models |
| <https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages> | about 37,000 characters without SDK code: sections only | "When to use a mid-conversation system message", "How it works"; "Mid-conversation tool changes" when tools change during a session |
| <https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback> | about 38,000 characters without SDK code: sections only | "What a refusal looks like", "How refusals are billed", "Picking a fallback approach", "Common pitfalls" |
| <https://platform.claude.com/docs/en/build-with-claude/structured-outputs> | about 36,000 characters without SDK code: sections only | "Why use structured outputs", "Important considerations", "Feature compatibility" |

## A model outside the scope

Say this guidance covers only the models in scope, and recommend the closest covered one and why. If the user keeps the other model, set `target_model: other`, name the model in `objective`, write from the general pages, and verify its effort setting and the parameters it rejects on its official page.
