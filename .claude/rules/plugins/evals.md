---
paths:
  - "plugins/*/evals/**"
  - "plugins/*/evals-*/**"
  - "/.github/eval*.json"
  - ".github/workflows/**"
---

# Plugin evals

- Write an eval case only after discussing it with the owner: every case and judge grader is a model call billed to the owner.
- Pin every case to Sonnet 5.5 with `model: claude-sonnet-5-5` in its `prompt.md` frontmatter or under `execution:` in its `case.yaml`.
- Tag each case by the work it asks for: `effort-low` for a lookup or a trigger check answered in a few turns, `effort-medium` for a diagnosis or a single record or file written, `effort-high` for a long task across several files. Run each group with `CLAUDE_CODE_EFFORT_LEVEL=<level> claude plugin eval <plugin-dir> --tag effort-<level>`. `npm run check:consistency` (PC-14) fails on a case without exactly one of the three tags, which no CI group would run.
- Judge every `llm` and `baseline` grader with `--judge-model claude-opus-5-5`.
- Run a local smoke suite only with the owner's approval: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`, plus the flags `.github/evals.json` gives the plugin, which its cases need.
- Run the full suites in CI and keep local runs to the smoke run above: `.github/workflows/evals.yml` starts only for a pull request that adds a suite or changes a plugin that has one, and any other pull request skips it.
- When a plugin gets its first suite, add `plugins/<plugin>/**` to the `paths` of `evals.yml` in the same change; `npm run check:consistency` (PC-12) fails until it is there. Dispatch `evals.yml` with the plugin's name to rerun a whole suite by hand.
- Gate a CI run with `--threshold 0.8` and `npm run evals:gate -- <result> --min-mean-delta 0.2`, or the plugin's stricter floor in `.github/eval-gates.json`, and cap each effort group with `--max-cost-usd 10`; a partial run fails the job.
- Give each plugin's tool grants and `--scaffold` in `.github/evals.json`; they apply to both arms of every case.
- Authenticate eval runs as `.claude/rules/architecture/claude-workflows.md` sets.
