---
paths:
  - "plugins/*/evals/**"
  - ".github/workflows/evals.yml"
---

# Evals policy

Every plugin eval suite follows this policy. Verified against <https://code.claude.com/docs/en/plugin-evals> on 2026-10-12 (full page; v2.1.283+ needs git 2.31+).

## Models

- Agent under test: **Sonnet**. Judge (`llm` and `baseline` graders): **Opus**.
- Locally: `--model sonnet --judge-model opus`.
- CI: full model IDs from repository variables (`EVAL_MODEL`, `EVAL_JUDGE_MODEL`), never aliases, so a model rollout is not mistaken for a plugin regression.

## Which cases exist

Write each case from the user's side: what someone who installed the plugin asks, in their words, and what they need back. A case exists only when it proves at least one of these. Its `prompt.md` `description` states which one and the hypothesis.

| Kind | Proves |
| :-- | :-- |
| **Difference** | Without the plugin, Claude fails in a specific, predictable way; with it, it succeeds |
| **Trigger conflict** | The plugin fires when it should and stays quiet when it should not (another skill, a nearby request) |
| **Own risk** | A failure here breaks the plugin itself (an agent not finding its input, a hook not firing) |
| **Guardrail** | The plugin does not over-report or invent; may show Δ ≈ 0, scored `arm: with-only` |

- No obvious cases, no duplicates of another case's hypothesis, no "test everything" suites.
- Mechanics already proven by unit tests or installed runs (agents launching, inventory, checker output) are not eval cases; evals measure the value a user gets.
- Dry-check every fixture for free before a paid run: build it in a temp folder and run the plugin's own scripts on it. A fixture that trips the plugin is a plugin bug or a wrong fixture, found at no cost.
- Prefer free deterministic graders (`regex`, `tool_used`, `tool_order`, `file_exists`). Use an `llm` judge only where the result needs judgment: each one costs 3 Opus calls per run.

## Trigger rate

- A skill's triggering is a rate: one case per realistic prompt (different wordings, no slash command, no skill name), each with a `tool_used: Skill` grader, plus prompts that must not trigger it (`min: 0`, `max: 0`, `arm: both`). Docs: skills, Skill not triggering.
- Trigger cases only need the first tool call: keep `max_turns` low so they stay cheap, and tag them `trigger` so `--tag trigger` re-runs them after every description change.

## Local smoke test

As the docs recommend for iterating: one arm, one run, traces kept for inspection.

```bash
claude plugin eval plugins/<name> [--case <glob> | --tag <tag>] --runs 1 --ablation none \
  --model sonnet --judge-model opus --scaffold --no-publish --trust-plugin --keep-temp [--allow-tools …]
```

- `--case` takes one glob per run; use `--tag` to group cases.
- Read `out/trace.jsonl` in the kept folder to see what really happened (subagent calls carry `parent_tool_use_id`), then remove the folder.
- The with-minus-without Δ comes from the full run in CI, not from the smoke test.

- Grant both arms what a real user's session has: a skill's own `allowed-tools` can't widen an eval's grants, so pass them with `--allow-tools` (for example `Bash`, `Write`, and `WebFetch(domain:…)` for each source the plugin verifies against).
- Ask Nery before running; state the number of runs (cases × 2 arms, plus judge calls) and the estimated cost.
- From the raw WITH / W/OUT / Δ table:
  - Δ ≈ 0 on a non-guardrail case → remove or rewrite it: it measures nothing.
  - Fails in both arms → suspect the grader or the task before the plugin.
- Record the smoke test's printed cost; it sets the full-run cap in `.github/scripts/evals-config.json`.

## Full run (CI, capped)

- `.github/workflows/evals.yml` runs `.github/scripts/run-evals.sh`: both arms, 3 runs per case, `--trust-plugin`, `--scaffold`, pinned model IDs, and each plugin's tool grants and `--max-cost-usd` (smoke cost × 3 runs, plus the baseline arm, × 1.25) from `.github/scripts/evals-config.json`.
- It authenticates with the `CLAUDE_CODE_OAUTH_TOKEN` secret (Nery's subscription, from `claude setup-token`; runs count against its usage limits). It runs when a pull request that changes a plugin's `plugin.json` is opened, reopened or marked ready for review, or by hand; never on every push. Without the secret it is skipped; a plugin with evals and no config entry fails the job.
- Evals are optional per plugin; Nery decides which plugins get a suite. `.github/scripts/eval-targets.mjs` picks the plugins: on a pull request, those with an `evals/` folder whose `plugin.json` changed (one matrix job each); by hand, one plugin or `all`. A plugin without `evals/` is never run and never fails the workflow, and `main` has no required eval check.
- Passing the full run is the release gate for a plugin that ships an eval suite. The gate is the with-arm score against `--threshold`; Δ is reported, never gated.
- Graders that check the plugin's own steps (inventory, agent briefs, full reads, verification) carry `arm: both`: in a two-arm run Claude Code drops `arm: with-only` and `tool_used: Skill` graders from the score, so the gate would not see them. The baseline arm fails them by design, so Δ includes them; read it per grader in the report.
- The eval trace has no hook events or hook output: prove a hook fires by its effect in the reply or the tool calls, never by searching the trace for its message.
- Never edit a case after a full run just to make it pass: fix the plugin, or record why the case was wrong.

## Hygiene

- `evals/results/` is git-ignored.
- One case per directory: `prompt.md`, `graders/`, optional `case.yaml` (`schema_version: "1.1"`) with `scaffold_script` for fixtures.
- Fixture scripts write only inside the run's workspace.
