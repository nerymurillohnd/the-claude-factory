---
paths:
  - "plugins/*/evals/**"
  - ".github/workflows/evals.yml"
---

# Evals Policy

- Follow this policy for every plugin eval suite.
- Source: <https://code.claude.com/docs/en/plugin-evals>, verified 2026-10-12. Claude Code v2.1.283+ needs git 2.31+.

## Models

- Run the agent under test on Sonnet.
- Judge `llm` and `baseline` graders with Opus.
- Pass `--model sonnet --judge-model opus` locally.

## Case Selection

- Write each case from the user's side: what someone who installed the plugin asks, in their words, and what they need back.
- Add a case only when it proves at least one of these kinds:
  - Difference: without the plugin, Claude fails in a specific, predictable way; with it, it succeeds.
  - Trigger conflict: the plugin fires when it should and stays quiet when it should not (another skill, a nearby request).
  - Own risk: a failure here breaks the plugin itself (an agent not finding its input, a hook not firing).
  - Guardrail: the plugin does not over-report or invent. It may show Δ ≈ 0; score it `arm: with-only`.
- State the kind and the hypothesis in the case's `prompt.md` `description`.
- Never add obvious cases, duplicates of another case's hypothesis, or "test everything" suites.
- Do not write cases for mechanics already proven by unit tests or installed runs: agents launching, inventory, checker output.
- Dry-check every fixture before a paid run: build it in a temp folder and run the plugin's own scripts on it.
- Treat a fixture that trips the plugin as a plugin bug or a wrong fixture.
- Prefer free deterministic graders: `regex`, `tool_used`, `tool_order`, `file_exists`.
- Use an `llm` judge only where the result needs judgment. Each one costs 3 Opus calls per run.

## Trigger Rate

- Measure a skill's triggering as a rate.
- Write one case per realistic prompt: different wordings, no slash command, no skill name.
- Give each trigger case a `tool_used: Skill` grader.
- Add prompts that must not trigger the skill, graded `min: 0`, `max: 0`, `arm: both`. Docs: skills, Skill not triggering.
- Keep `max_turns` low on trigger cases. They only need the first tool call.
- Tag trigger cases `trigger`, and re-run `--tag trigger` after every description change.

## Local Smoke Test

- Run one arm and one run, with traces kept:

```bash
claude plugin eval plugins/<name> [--case <glob> | --tag <tag>] --runs 1 --ablation none \
  --model sonnet --judge-model opus --scaffold --no-publish --trust-plugin --keep-temp [--allow-tools …]
```

- Pass one glob per run to `--case`. Use `--tag` to group cases.
- Grant both arms what a real user's session has with `--allow-tools`: `Bash`, `Write`, and `WebFetch(domain:…)` for each source the plugin verifies against.
- A skill's own `allowed-tools` can't widen an eval's grants.
- Read `out/trace.jsonl` in the kept folder, then remove the folder. Subagent calls carry `parent_tool_use_id`.
- Read the raw WITH / W/OUT / Δ table:
  - Δ ≈ 0 on a non-guardrail case: remove or rewrite the case.
  - Fails in both arms: suspect the grader or the task before the plugin.
- Take Δ from the full CI run, never from the smoke test.
- Record the smoke test's printed cost. It sets the full-run cap in `.github/scripts/evals-config.json`.

## Full Run (CI, Capped)

- Evals are optional per plugin. Nery decides which plugins get a suite.
- Release a plugin that ships an eval suite only after its full run passes.
- Gate on the with-arm score against `--threshold`. Report Δ; never gate on it.
- Give graders that check the plugin's own steps `arm: both`: inventory, agent briefs, full reads, verification.
- A two-arm run drops `arm: with-only` and `tool_used: Skill` graders from the score, so the gate never sees them.
- The baseline arm fails the `arm: both` step graders by design. Read Δ per grader in the report.
- Prove a hook fires by its effect in the reply or the tool calls. The eval trace has no hook events or hook output.

## Hygiene

- Write fixture scripts only inside the run's workspace.
