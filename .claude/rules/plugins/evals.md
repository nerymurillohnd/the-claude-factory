---
paths:
  - "plugins/*/evals/**"
  - ".github/workflows/**"
---

# Plugin evals

- Write an eval case only after discussing it with the owner: every case and judge grader is a model call billed to the owner.
- Pin every case to Sonnet 5.5 with `model: claude-sonnet-5-5` in its `prompt.md` frontmatter or under `execution:` in its `case.yaml`.
- Tag each case `effort-low`, `effort-medium` or `effort-high`, and run each group with `CLAUDE_CODE_EFFORT_LEVEL=<level> claude plugin eval <plugin-dir> --tag effort-<level>`.
- Judge every `llm` and `baseline` grader with `--judge-model claude-opus-5-5`.
- Run a local smoke suite only with the owner's approval: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`.
- Run a plugin's full suite in CI once, the first time, and then only on pull requests that change that plugin.
