# Evals CI workflow

How to audit `.github/workflows/evals.yml`, the workflow that runs the plugins' eval suites in CI.

## Sources

Read 2026-11-15, Claude Code 2.1.325:

- Claude Code docs `plugin-evals` (<https://code.claude.com/docs/en/plugin-evals>): Requirements (Claude Code 2.1.269 or later; git 2.31 or later, or `claude plugin eval` "stops before running any case"), Run evals in CI (`--trust-plugin`, `--json`, `--threshold`, pinned `--model` and `--judge-model`, `--no-publish`, `--max-cost-usd`; exit codes 0, 1, 2, 130, 143; "The with-minus-without delta is reported but never changes the exit code"), Command options (`--concurrency` 1 to 8, default 1), Use a different eval directory (`--eval-dir`), JSON result (`partial`, `partialReason`, `skippedPaidGraders`, run `error` that "doesn't imply score 0"), Grant tools (Bash needs `bubblewrap` and `socat` on Linux).
- Claude Code docs `github-actions`: credentials are repository secrets.
- Claude Code docs `authentication` → Authentication precedence: cloud-provider variables, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_API_KEY` and `apiKeyHelper` rank above `CLAUDE_CODE_OAUTH_TOKEN`.

## Audit checklist

Report each line as pass, fail or unknown, with the evidence:

1. Triggers on pull requests that touch a plugin with a suite (`paths` has `plugins/*/evals/**`, `plugins/*/evals-*/**` and each such plugin, which PC-12 checks), and offers `workflow_dispatch` with a plugin input. Fork pull requests get a visible warning, never `pull_request_target`.
2. Suites are found at any depth under `evals/` and `evals-*/`, skipping `results/`; a plugin that sets `experimental.evals` fails the job instead of being skipped.
3. The command is complete: target first, `--trust-plugin`, `--json <file>.json`, `--threshold 0.8`, pinned `--model` and `--judge-model`, `--no-publish`, `--max-cost-usd`, `--concurrency`, and the flags `.github/evals.json` gives the plugin. `evals/` runs in two arms; an `evals-*/` suite runs with `--eval-dir <dir> --ablation none`.
4. `timeout-minutes` covers the largest group: runs ÷ concurrency × the cases' `timeout_seconds`, at most 360.
5. Claude Code is pinned in `.github/actions/setup/action.yml`, 2.1.269 or later; the runner's git is 2.31 or later; `bubblewrap` and `socat` are installed.
6. `CLAUDE_CODE_OAUTH_TOKEN` comes from a repository secret, the job fails loudly when it is empty, and it fails when any credential that outranks the token is set.
7. Every exit code is read with all its documented causes, and the delta gate (`scripts/checkers/eval_gate.py`) runs only after exit 0: not comparable on `partial`, a mock `aborted` run or `skippedPaidGraders`; a run `error` is a warning.
8. The JSON result and the report are uploaded as an artifact.
9. `**/evals/results/` and `plugins/*/evals-*/results/` are git-ignored, and `mocks/.replay/` is not.
