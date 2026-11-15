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
- Before any eval run that spends, run the no-cost checks of `plugin-engineering:plugin-testing-and-debugging` (Evals in brief, step 4) and fix what they find: `claude plugin validate --strict`, each fixture by hand, each grader against a real or hand-written trace, the commands and templates the skill teaches, and every suite loaded with `--max-cost-usd 0` and the run's own flags.
- Then, only with the owner's approval, run a local smoke suite: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`, plus the flags `.github/evals.json` gives the plugin, which its cases need.
- Run the full suites in CI and keep local runs to the smoke run above: `.github/workflows/evals.yml` starts only for a pull request that adds a suite or changes a plugin that has one, and any other pull request skips it.
- When a plugin gets its first suite, add `plugins/<plugin>/**` to the `paths` of `evals.yml` in the same change; `npm run check:consistency` (PC-12) fails until it is there. Dispatch `evals.yml` with the plugin's name to rerun a whole suite by hand.
- Gate a CI run with `--threshold 0.8` and `npm run evals:gate -- <result> --min-mean-delta 0.2`, and cap each effort group with `--max-cost-usd 10`; a partial run fails the job. A plugin's own stricter floor (`min_mean_delta`) and cost cap (`max_cost_usd`) go in `.github/eval-gates.json`, set only with the owner's approval.
- Give each plugin's tool grants and `--scaffold` in `.github/evals.json`; they apply to both arms of every case.
- Put files only the with-plugin arm may have, such as an MCP server the plugin doesn't ship, in `plugins/<plugin>/evals/_overlay/`: `evals.yml` runs the suite on a temporary copy of the plugin with the overlay copied over it, and a local run stages the same copy first.
- Authenticate eval runs as `.claude/rules/architecture/claude-workflows.md` sets.
