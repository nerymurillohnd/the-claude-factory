---
paths:
  - "plugins/*/evals/**"
  - ".github/workflows/**"
---

# Plugin evals

Every eval case and judge grader is a model call billed to the owner, so evals run only on plugins the owner chose and only when a change can move their score.

## Write

- Discuss every case with the owner before writing it; never create a case on your own.

## Models and effort

- Pin every case to Sonnet 5.5: set `model: claude-sonnet-5-5` in its `prompt.md` frontmatter or under `execution:` in its `case.yaml`, so a model rollout isn't mistaken for a plugin regression.
- Tag each case `effort-low`, `effort-medium` or `effort-high` by its complexity, and run each group with `CLAUDE_CODE_EFFORT_LEVEL=<level> claude plugin eval <plugin-dir> --tag effort-<level>`: no case field sets effort, and the variable takes precedence over every other effort source.
- Judge every `llm` and `baseline` grader with Opus 5.5: pass `--judge-model claude-opus-5-5`, because the default judge is Haiku.

## Run

- Locally, run a reduced smoke suite: `claude plugin eval plugins/<plugin> --case <case> --runs 1 --ablation none --no-publish`.
- In CI:
  1. Run a plugin's full suite once, the first time.
  2. After that, on each pull request, run the full suite only for plugins with evals that the pull request changed.
  3. Skip every plugin with evals that the pull request didn't change.
