# Reading eval results

The exit codes, the summary table, the HTML report, the JSON result, and each common symptom with its cause and fix.

## Contents

- [Gotchas](#gotchas)
- [Exit codes](#exit-codes)
- [Summary table and report](#summary-table-and-report)
- [JSON result](#json-result)
- [Symptoms](#symptoms)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- A run that ends on an API error, such as a rate or plan usage limit, scores 0 without grading and makes the command exit non-zero, in either arm. Baseline runs count too, so every case can pass while the command fails: read `cases[].arms.with[].error` and `cases[].arms.without[].error`.
- A grader with `passed: false` under a run that scored 1.0 is one the two-arm mode leaves out of the score (`scored: false`), by design.
- Δ and problems writing or publishing the report never change the exit code.
- A run with `skippedPaidGraders` or a document with `partial: true` isn't comparable: keep it out of trends.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| `0` | every case scored at or above `--threshold`, and nothing else failed the run |
| `1` | a case scored below the threshold, a case file failed to load, no cases were found, a run couldn't start or ended on an API error, the folder isn't trusted and `--trust-plugin` wasn't passed, an option was invalid, or the `--json` result couldn't be written |
| `2` | partial: the `--max-cost-usd` ceiling was hit, or the credential was rejected before or at the first run; the result is still written with `partial: true` and the reason |
| `130` | interrupted; partial results are written |
| `143` | terminated, such as by a CI timeout |

When every case passes and the command still exits 1, a line on stderr names the cause, even under `--json`.

## Summary table and report

- The table's columns are `CASE`, `WITH`, `W/OUT`, `Δ`, `RUNS`, `COST` and `NOTES`; with one arm it shows `SCORE` and `PASS%` instead. `NOTES` holds the with-arm's highest-weight failing grader's explanation, or the run's error.
- The footer prints `Report: <path>`, and `Published: <url>` when the report was published.
- Every run with at least one case writes `results/<timestamp>/` with `aggregate-result.json` and `report.html`: under the plugin for a path target, under the current folder for a named plugin.
- `report.html` is self-contained and makes no external requests. Read it from the top: the verdict line, such as `Plugin effect: +33.3 pts vs baseline, improved 2, flat 1, regressed 0 of 3 cases`, and the tiles (suite score, ablation Δ, baseline score, cases passing, perfect runs), then each case card (its Δ, a score bar with the threshold tick, a red left edge when Δ is negative), then inside a case the with-plugin runs before the baseline runs, each failed grader expanded with its explanation and an `llm` grader's votes and evidence, and last the prompt and every grader's rubric or pattern.
- Signed in with a claude.ai subscription that has artifacts, Claude Code publishes the report as a private artifact; with an API key there is no `Published:` line and the local file is the report. `--no-publish` keeps it local. A run that a Claude Code session started stays local, its `Report:` line says `kept local`, and `--publish-report` publishes it.

## JSON result

`aggregate-result.json`, and `--json` output, carries `schemaVersion: 1`, camelCase names, and fields that are added without renaming old ones, so a script ignores the fields it doesn't know.

| Field | Meaning |
| :-- | :-- |
| `partial`, `partialReason` | `true` with `cost_ceiling`, `interrupted` or `auth_failed` when the suite didn't finish |
| `aggregates.overallScore` | the mean case score |
| `aggregates.casesPassed`, `aggregates.casesTotal` | cases at or above the threshold, and the total |
| `aggregates.meanDelta` | the mean Δ, in a two-arm run |
| `cases[].name`, `cases[].aggregates.score` | the case and its mean with-arm score |
| `cases[].aggregates.delta` | with-arm minus without-arm; omitted for one arm or arms that aren't comparable |
| `cases[].arms.with[].error` | `null`, or why a run ended abnormally, such as `timed out after 300s`; some such runs are still graded |
| `cases[].arms.with[].aborted` | `server`, `tool` and `reason` when a mock stopped the run; it scores 0 and `error` stays `null` |
| `cases[].arms.with[].skippedPaidGraders` | `true` when the cost ceiling skipped the run's judge graders |
| `cases[].arms.without[]` | the baseline runs |
| `costUsd`, `durationSeconds`, `claudeVersion` | the list-price estimate with judge calls, the wall-clock seconds, and the Claude Code version that ran |

To gate on the plugin still helping, read `aggregates.meanDelta`. Fail the job on `partial: true` too: the docs say to leave partial results out of trends, and a partial run isn't comparable.

## Symptoms

| Symptom | Cause and fix |
| :-- | :-- |
| `No eval cases found` | no `<case>/prompt.md` or `<case>/case.yaml` below the eval directory, or `--case` and `--tag` matched none: run from the plugin root, or create a suite |
| No `W/OUT` column, or `ablation requested but no plugin resolved` | no plugin was found for the case: set `plugins` to the path from the case folder up to the plugin folder, two parent-folder steps for a case directly under `evals/`. Expected when every case resumes a `context.history_file` |
| Δ near zero with the `tool_used: Skill` grader failing | usually a real finding: the skill's `description` doesn't trigger on the prompt's phrasing. Change the description once, from what the report shows, and rerun the same suite |
| `Agent type '<plugin>:<agent>' not found` | a baseline run dispatched the plugin's agent; expected. `--ablation none` skips the baseline |
| Every score is 0 though the right files were produced | the grader targets `files`, the created paths: use `{ source: file, path: <path> }`. `file_exists` also misses files the scaffold created or Claude only edited |
| A regex over the trace misses visible text | the default target is `last_message`; in the trace quotes are `\"`; write `flags: i`, never `(?i)` |
| Tools denied, MCP tools missing, Bash won't run | grant beyond the read-only set; the plugin's servers start only on opt-in and then need an `mcp__plugin_<plugin>_<server>__*` grant; for a refused Bash run read the full error in `NOTES` or `error` |
| `--json output path must end in .json` | the target came after `--json`: put it first |
| `ended on an API error and scored 0 without grading` | read each run's error after `error:` in the progress line, or in the JSON, and fix what it reports; for a usage or rate limit, rerun after the reset with `--runs 1` or `--case` |
| `mock call budget exceeded` | the run made more than 4 × `max_turns` agent-mock calls: raise `max_turns` |
| Runs time out or hit the turn cap | raise `max_turns` and `timeout_seconds` in the case, and cap spend with `--max-cost-usd` instead |
| `is too old for claude plugin eval` | the git on `PATH` is older than 2.31: install a newer one |

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Read the results](https://code.claude.com/docs/en/plugin-evals#read-the-results) when a report or JSON field is in question. It gives the report's layout and every gating field.
- Read [Troubleshooting](https://code.claude.com/docs/en/plugin-evals#troubleshooting) when a symptom is not in the table above. It gives each documented message with its cause.

## Exit

Each score, exit code and symptom is explained by a row here or by the page. Return to the step in `SKILL.md` that sent you here.
