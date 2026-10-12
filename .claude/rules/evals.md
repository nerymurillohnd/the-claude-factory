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

## Pilot (local, no cost cap)

```bash
claude plugin eval plugins/<name> --runs 1 --model sonnet --judge-model opus --scaffold --no-publish [--allow-tools …]
```

- Grant both arms what a real user's session has: a skill's own `allowed-tools` can't widen an eval's grants, so pass them with `--allow-tools` (for example `Bash`, `Write`, and `WebFetch(domain:…)` for each source the plugin verifies against).
- Ask Nery before running; state the number of runs (cases × 2 arms, plus judge calls) and the estimated cost.
- From the raw WITH / W/OUT / Δ table:
  - Δ ≈ 0 on a non-guardrail case → remove or rewrite it: it measures nothing.
  - Fails in both arms → suspect the grader or the task before the plugin.
- Record the pilot's printed cost; it sets the full-run cap.

## Full run (CI, capped)

- 3 runs per case (default), `--max-cost-usd` = pilot cost × 3 × 1.25, `--trust-plugin`, `--scaffold`, pinned model IDs.
- Passing the full run is the release gate for a plugin that ships an eval suite.
- Never edit a case after a full run just to make it pass: fix the plugin, or record why the case was wrong.

## Hygiene

- `evals/results/` is git-ignored.
- One case per directory: `prompt.md`, `graders/`, optional `case.yaml` (`schema_version: "1.1"`) with `scaffold_script` for fixtures.
- Fixture scripts write only inside the run's workspace.
