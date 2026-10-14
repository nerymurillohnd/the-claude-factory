# Results and troubleshooting

Read this when you interpret a run, explain a score or Δ, parse the JSON, or debug an error.

## Contents

- The summary table
- `report.html`
- `aggregate-result.json`
- Reading Δ and scores
- Symptom → cause → fix

## The summary table

```text
CASE        WITH  W/OUT Δ      RUNS COST    NOTES
first-case  1.00  0.33  +0.67  6    $0.41

1 case(s) · mean Δ +0.67 · 74s · $0.41
Report: /path/to/plugin/evals/results/<timestamp>/report.html
Published: https://claude.ai/... · keep local next time with --no-publish
```

- `WITH` and `W/OUT` are the case scores with and without the plugin, and `Δ` is their difference. `COST` is a list-price estimate.
- `NOTES` shows the highest-weight failing grader's explanation, or the run's error, from the with-arm.
- With one arm, the table shows `SCORE` and `PASS%` instead.
- Every run with at least one case writes `results/<timestamp>/` with `aggregate-result.json` and `report.html`. Its location depends on the target (see [running-and-ci.md](running-and-ci.md)).

## `report.html`

- **One self-contained file** with no external requests, so it can be attached to a CI job.
- **Reading order:**
  1. The verdict line and tiles: suite score, ablation Δ, baseline score, cases passing, and perfect runs.
  2. A card per case. A negative Δ gets a red edge.
  3. The with-plugin runs, then the baseline runs. Each grader shows a chip, and failed graders open with their explanation.
  4. `llm` graders show the judge's votes and the excerpt it judged.
  5. Graders excluded from the score carry a `plugin-fired indicator` badge.
  6. The prompt and every grader's rubric, at the end.
- **Publishing:**
  - Claude Code also publishes the report as a private artifact and prints `Published: <url>`, but only when the account is signed in with a claude.ai subscription and artifacts are available.
  - API keys, cloud providers, and organizations with CMEK, HIPAA or zero data retention get no `Published:` line, and the local file is the report.
  - A run that a Claude Code session started stays local (`kept local`) unless you add `--publish-report`.
  - `--no-publish` always keeps it local.

## `aggregate-result.json`

The same document `--json` prints. It is versioned (`schemaVersion: 1`) and uses camelCase. New fields are added without renaming old ones, so ignore unknown fields.

| Field | Meaning |
| :-- | :-- |
| `partial`, `partialReason` | `true` with `cost_ceiling`, `interrupted` or `auth_failed`. Keep these out of trend charts |
| `aggregates.overallScore` | Mean case score |
| `aggregates.casesPassed`, `aggregates.casesTotal` | Cases at or above the threshold, and the total |
| `aggregates.meanDelta` | Mean Δ in two-arm mode |
| `cases[].name` | Case name |
| `cases[].aggregates.score` | Mean with-arm run score |
| `cases[].aggregates.delta` | Δ. Omitted when the case ran one arm or the arms aren't comparable |
| `cases[].arms.with[].error` | `null`, or why the run ended abnormally, such as a timeout. Some of these runs are still graded on what they produced, so an error does not mean a score of 0; since v2.1.299 a run that ended on an API error scores 0 without grading |
| `cases[].arms.with[].aborted` | Present when a mock stopped the run (`expect:`, `abort_when`, or the agent-mock budget), with server, tool and reason. Score 0, `error` is `null` |
| `cases[].arms.with[].skippedPaidGraders` | The cost ceiling skipped this run's judge graders, so its score isn't comparable |
| `cases[].arms.without` | The baseline runs |
| `costUsd`, `durationSeconds`, `claudeVersion` | Estimated cost including judges, wall-clock time, and the Claude Code version that ran |

The document also carries the suite configuration, every grader definition, and per-run grader results with explanations and evidence. Graders that didn't count have `scored: false`. Check `suite.plugins` to confirm the plugin loaded: an empty list, or a `problem` of `manifest_invalid`, `disabled_by_default` or `will_not_load`, means the with-arm ran without it. `identity_unverified` and `archive_not_probed` don't block loading.

## Reading Δ and scores

- **High score, Δ ≈ 0.** Claude passes without the plugin, so the case proves nothing about the plugin. Rewrite it around a failure Claude has without the plugin, or drop it.
- **Δ ≈ 0 and the `tool_used: Skill` indicator failing.** The skill didn't trigger on that wording. Adjust the skill's `description` and re-run the same suite. Then measure triggering as a rate across several prompts.
- **The `tool_used: Skill` indicator passes but Δ is negative.** Suspect the judge first: a small judge can fail a correct answer that is formatted differently from the rubric. Re-run with `--judge-model sonnet` and tighten the rubric so formatting doesn't decide the verdict.
- **Both arms fail.** Suspect the case: a missing tool grant, a budget that is too small, a grader on the wrong target, or a fixture. The authoring pilot prints `⚠ case … cannot pass with the granted tools` when no granted tool can create the file a grader checks.
- **Unstable across runs.** One run is noisy. Confirm changes at 3 runs or more. Ambiguous instructions in the skill also cause variance.
- **A sudden jump.** Spot-check the transcripts by hand before you trust it, especially with `llm` graders.

## Symptom → cause → fix

| Symptom | Cause | Fix |
| :-- | :-- | :-- |
| Exit 1, but every case looks good | The default `--threshold` is 1.0, or a case file failed to load (named on stderr above the table) | Set the threshold you require; fix the case file |
| A grader shows `passed: false` under a run that scored 1.0 | The grader is excluded by design (`scored: false`) | Expected. Use `arm: both` if it must count |
| No `W/OUT` column, or `ablation requested but no plugin resolved` | No plugin was found for the case, or every case resumes a `history_file` | Add `plugins: ["../.."]` with the path from the case to the plugin; for `history_file` cases, pass `--ablation with-without` |
| `Agent type '<plugin>:<agent>' not found` in baseline runs | The baseline arm has no plugin agents | Expected. Use `--ablation none` to skip the baseline |
| Everything scores 0 although the right files were made | The graders target `files` (paths), or `file_exists` on a file that already existed or was only edited | Target `{ source: file, path: … }`; for edits, use `tool_used` on `Edit` |
| A regex on the trace misses visible text | The default target is `last_message`, quotes are escaped as `\"`, or an inline `(?i)` was used | Set `target: trace`, match `\"`, use `flags: i` |
| Tools denied, MCP tools missing, Bash won't run | Missing grants; real servers not started; no sandbox backend | `--allow-tools …`; mocks or `--allow-real-servers`; install the sandbox (see [running-and-ci.md](running-and-ci.md)) |
| `--json output path must end in .json` | The target came after `--json` | Put the target first |
| `is not a trusted plugin directory, and this run cannot stop to ask you about it` | First run with no terminal, or with `--json` | Run once in a terminal and accept, or pass `--trust-plugin` for code you trust |
| `is too old for claude plugin eval` | git older than 2.31 | Install git 2.31 or later |
| `cannot be evaluated where sessions load it` | A named plugin from a local-path marketplace that no session can load now | Fix what the message names (`claude plugin marketplace list`), or target the plugin directory |
| `No eval cases found` | Wrong directory, or `--case`/`--tag` matched nothing | Run from the plugin root, check filters, or run `init` |
| `mock call budget exceeded` | Agent-mock calls passed 4 × `max_turns` | Raise `max_turns` |
| `scaffold failed` | The script exited non-zero or ran over 120 s | Run the script yourself in a temp folder |
| Runs fail partway with usage or rate-limit errors, and scores drop | The account limit was reached. The suite isn't marked partial | Check `NOTES` or `error` before you trust the drop; re-run later with fewer runs or a `--case` filter |
| Runs time out or hit the turn cap | The defaults are 10 turns and 300 s | Raise `max_turns` and `timeout_seconds` per case; use `--max-cost-usd` for cost |
| `plugin eval is currently in early access` / `unavailable` | An old build, or the command is switched off server-side | `claude update`, then try again in a fresh session |
