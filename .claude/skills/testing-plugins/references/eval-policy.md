# Eval policy: pilot and smoke locally, full suite in CI

Sources: https://code.claude.com/docs/en/plugin-evals (read 2026-10-26), `claude plugin eval --help` on v2.1.310, every `plugin eval` entry of the changelog from v2.1.269 to v2.1.310. Requires Claude Code ≥ v2.1.269 (and git ≥ 2.31 when git is installed). Where the docs and `--help` differ, `--help` wins for flags and the changelog wins for behavior. The docs win over this file and over this repository's rules and records.

Contents: Who runs what · Pilot · Reading a pilot · Writing the suite · Fixtures · Mock MCP servers · Reading the results · The CI template · CI audit checklist · Fork PRs · Flags worth knowing · Quick error map

## Who runs what

| | Local pilot and smoke | CI full suite |
| :- | :- | :- |
| Runs | 1 per case, one arm (`--runs 1 --ablation none`) | Case default (3), both arms, Δ reported |
| Which plugins | The one being worked on; the pilot narrows with `--case`, the smoke runs the cases tagged `smoke` | A new plugin with `evals/`, or an existing plugin with `evals/` whose components or dependencies changed; CI skips every other plugin |
| Purpose | Cases load, run and grade; rubric and tools are right | Score against `--threshold`, trigger rate, Δ vs no plugin, regressions a change causes |
| Spend | Small, announced first, user says yes | Capped by `--max-cost-usd`, approved when the workflow is added |

**New** = the plugin did not exist at the base commit. **Edited** = one of its components or dependencies changed: any file under the plugin directory except its eval directory and the documents `README.md`, `CHANGELOG.md`, `LICENSE*` and `NOTICE*` at its root. Detection by `plugin.json` alone misses an edit that does not bump the manifest; [scripts/changed-eval-plugins.sh](../scripts/changed-eval-plugins.sh) applies this rule. A change to the suite itself, or to those documents only, is checked locally with the pilot. A plugin without evals is never a target, and this skill never adds a suite unasked. Mods are plugins like any other here: their eval suites follow this file, while their `claude plugin test` suites belong to `testing-mods`.

## Pilot

From the plugin root, target first, flags after:

```bash
claude plugin eval . --runs 1 --ablation none --no-publish
claude plugin eval . --case "<glob>" --runs 1 --ablation none --no-publish   # only the affected cases
claude plugin eval . --tag smoke --runs 1 --ablation none --no-publish        # smoke: the cases tagged smoke
```

Tag the smoke cases `tags: [smoke]` in their `prompt.md` or `case.yaml`, and give them graders that call no judge (`regex`, `tool_used`, `tool_order`, `file_exists`), as the docs advise for quick every-change suites.

Add `--scaffold` when a case has a `context.scaffold_script` (see Fixtures). Before running, tell the user: cases × 1 run × 1 arm = N agent runs, plus 3 judge votes per `llm`/`baseline` grader per run, plus agent-mock calls (up to 4 × `max_turns` per run) if the suite has `type: agent` mocks. Then wait for a yes. After the first pilot, estimate full cost as pilot cost × runs × 2 arms.

Flags that run code as the user or call real services: `--trust-plugin`, `--scaffold`, `--allow-real-servers`, `--mocks off`. The docs allow `--scaffold` for "suites you or your organization wrote" and `--trust-plugin` for "a plugin whose code and suite you'd run yourself", which covers this repository's own plugins; for a plugin or suite someone else wrote, get the user's go-ahead by name. `--allow-real-servers` and `--mocks off` always need it. From inside an agent session stdin is not a terminal, so the first run in an untrusted directory is refused (`is not a trusted plugin directory, and this run cannot stop to ask you about it`): pass `--trust-plugin` for this repository's plugin, or have the user answer the prompt once in a terminal. Granting `Bash` forces the OS sandbox (`bubblewrap` + `socat` on Linux; WSL2 on Windows); with no backend each run is refused. The sandboxed Bash has been reported unable to write the run workspace when `TMPDIR` is under `/tmp` (anthropics/claude-code#104797, open): if every Bash-granting case fails on writes, check `TMPDIR` first. **Unverified:** whether a plugin under your home directory runs locally with Bash granted.

Evaluating a plugin you did not write executes its code as the user: treat it as a trust decision, and do it from a throwaway config (`CLAUDE_CONFIG_DIR="$(mktemp -d)"`) with the plugin installed by `claude plugin install <plugin>@<marketplace>`, then `claude plugin eval <plugin>@<marketplace>`.

## Reading a pilot

Say what it proves and what it does not.

- It proves: the cases load (a case without a grader fails with `invalid case.yaml`), the tools granted are enough, graders return verdicts, the skill fired on the phrasing used.
- It does not prove: Δ over no plugin (no baseline arm), a stable score (one run is noisy; confirm any change at the default 3 runs), or that CI will pass.
- Under `--ablation none` nothing is excluded from the score; in a two-arm run (CI) the graders below are `scored: false`, so the same suite can score differently in the two modes.
- `passed: false` under a run scoring 1.0 means an excluded grader; look at `scored`.
- Hitting `max_turns` or `timeout_seconds` is a run error, and such a run can still be graded on what it produced. An API/rate-limit error scores 0 without grading and exits 1: check `cases[].arms.with[].error`, then re-run with `--runs 1` or a `--case` filter after the limit resets.
- Judge default is the background-task model (haiku per `--help` on v2.1.310). If a case's `tool_used: Skill` grader passes but its Δ is negative, or the result is marked wrong, suspect the judge before the plugin: re-run with `--judge-model sonnet`, and tighten the rubric so formatting doesn't decide the verdict.
- To see why a case scored low, run it without `--json`, so the per-run progress and grader lines print.

## Writing the suite

The layout:

```text
evals/
├── <case>/
│   ├── prompt.md       # frontmatter: max_turns, timeout_seconds, allowed_tools, tags, runs, plugins...; body: the prompt
│   ├── case.yaml       # optional; needs schema_version: "1.1" (quoted) and name; adds context (see Fixtures)
│   ├── graders/<name>.md   # frontmatter: type, weight, arm; body: rubric
│   └── mocks/<server>/<tool>.md   # optional, this case only
├── mocks/<server>/<tool>.md       # optional, the whole suite; commit mocks/.replay/ too
└── results/            # written by runs; gitignore it
```

- Start with `claude plugin eval init` (interactive, from the plugin root) or `claude plugin eval init --bare <case>` (blank template; the only form that works in CI).
- Grader types: `regex` (JavaScript regex; `flags: i`, never `(?i)`; `match: not_contains`), `tool_used` (`tool`, `input_match`, `min`, `max`), `tool_order`, `file_exists`, `llm`, `baseline`. No custom-code graders. `target` and `focus` accept `last_message` (default), `trace`, `files` (paths only), `{ source: file, path: ... }`, `mock_calls`.
- **Stable signal.** An `llm` verdict varies between runs, and more the longer the text it reads. Grade long output, such as a generated file, with a `regex` grader over the file's contents. Keep `llm` graders for short outputs, with rubrics written as concrete PASS and FAIL conditions.
- **Per case: one grader on the result** (the final message or a produced file) **and one on the steps** (`tool_used` or `tool_order`): together they say whether the answer was right and whether the plugin produced it.
- **A build or test inside the run:** have the prompt ask Claude to run it and write the outcome to a file, grade that file, and assert the command ran with a `tool_used` grader whose `input_match` names the command. The command's tool needs a grant (`--allow-tools "Bash(npm test *)"`).
- **Trigger quality:** at least four prompts in users' words that should fire the skill, without naming it, plus one or two near misses. Must-not-fire = `type: tool_used`, `tool: Skill`, `input_match` on the skill name, `min: 0`, `max: 0`, `arm: both`.
- Skill graders match `"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"` (namespaced form `plugin:skill` is accepted).
- **Scored in both arms or not.** In a two-arm run these graders are excluded from the score in both arms and shown in the with-arm as pass/fail indicators: every `tool_used` grader whose `tool` is `Skill`; every `regex` grader with `target: mock_calls` and every `llm` grader with `focus: mock_calls`, when each mocked server in the case is one the plugin declares; any grader marked `arm: with-only`. If every grader of a case is in that set, they are scored normally. `arm: both` scores a grader in both arms regardless.
- **Single-arm cases** (no `W/OUT`, no Δ): every case under `--ablation none`; with a path target, a case that resumes a transcript through `context.history_file` (stderr prints a `single-arm (no Δ)` notice naming it; `--ablation with-without` compares the resumed turn anyway) and a case whose plugin Claude Code couldn't locate (fix with `plugins: ["../.."]`).
- Anything beyond the read-only tools (`Read, Glob, Grep, NotebookRead, Skill, AskUserQuestion, Agent, TodoWrite`, `TaskCreate, TaskGet, TaskList, TaskUpdate, TaskStop`) needs `--allow-tools`; otherwise the tool is removed from the session and the progress output lists it as `not granted`. The grant applies to every case in the run. A grader on a created file needs `Write`/`Edit`. With `Bash` granted, network access is limited to the domains granted with `--allow-tools "WebFetch(domain:example.com)"`.
- Defaults: `max_turns` 10, `timeout_seconds` 300 (up to 3600), `runs` 3. A one-shot answer needs about 5 turns; reading a repo and writing a report 25–40.
- Runs are isolated: no `CLAUDE.md`, settings, memory, other plugins, or personal MCP servers. Ship everything a case needs inside the plugin.
- An eval directory other than `evals/`: `"experimental": { "evals": "quality/evals" }` in `plugin.json`, or `--eval-dir` on both `init` and the run.

## Fixtures

Each run starts in an empty workspace. A `case.yaml` beside `prompt.md` adds a `context` block:

- `context.scaffold_script`: a Bash script in the case directory that writes fixture files or a git repository. It runs as the user, outside the agent's sandbox, and only with `--scaffold`; without the flag the run starts in the empty workspace, without its fixtures. It starts in the empty workspace with a fixed environment: the shell's `PATH`, `HOME` set to the run's temporary home, `TMPDIR`, and constants such as `TERM=dumb`; nothing else from the shell, and none of the case's `EVAL_*` variables. A non-zero exit or more than 120 seconds scores that run 0 with `scaffold failed`. Project configuration it writes is not loaded: use it for files and git state only.
- `context.history_file`: a `.jsonl` transcript to continue; the case's prompt becomes the next user turn (single-arm with a path target, above).
- `context.add_dirs`: fixture directories Claude can read during the run.

## Mock MCP servers

A run never starts the plugin's real MCP servers unless asked. Claude Code registers a substitute server under each server's own name (the name in the plugin's MCP configuration):

- One Markdown file per tool: `evals/mocks/<server>/<tool>.md` for the suite, or the case's own `mocks/` for one case. A tool with a mock is allowed without `--allow-tools`; a tool without one is not available to Claude. A server with no mocks shows as `plugin_<plugin>_<server>[not started: no mock]` in the case's `mocked:` progress line.
- The file's body is what the tool returns. `{{input.<field>}}` inserts a field of the call's input; `{{file:fixtures/{input.<field>}.json}}` inserts a fixture file beside the mock.
- `expect:` guards the input: a call that violates it aborts the run with score 0 and records why, so a case can assert what the plugin asked the server to do.
- `error: true` returns the body as a tool error. `type: agent` has the judge model answer as the server from the body's instructions; agent mocks share one budget per run of 4 × `max_turns`, and a call past it aborts the run with score 0.
- Grade the calls themselves with `target: mock_calls`. The docs' mock file reference lists every key and the `_server.md` and `_tools.json` files.
- **Replay.** A `type: agent` answer varies between runs and with the judge. After a run that ends without an error or abort, each agent-mock answer is saved under the results directory in `mock-recordings/`; `ADOPT.txt` there names each recording and the `.replay/<server>/` directory to copy it into, beside its mock. A copied recording answers the identical call with no model call. Commit `mocks/.replay/` with the rest of `mocks/` so CI runs are repeatable.
- Real servers instead (they run as the user, outside the run's sandbox, and their tools need a grant by full name, `--allow-tools "mcp__plugin_<plugin>_<server>__*"`): `--allow-real-servers` starts each server that has no mock and keeps the mocks; `--mocks off` ignores `mocks/` and starts every server.

## Reading the results

Every run with at least one case writes `results/<timestamp>/` inside the eval directory (under the current directory for a named-plugin target), with `aggregate-result.json` and `report.html`. A run a Claude Code session started keeps the report local (`Report: … kept local`); `--publish-report` publishes it.

- **`report.html`**, top down: the verdict line and tiles (suite score = mean with-plugin case score; Ablation Δ; cases at the threshold; perfect runs = share of with-plugin runs where every grader passed); one card per case with its Δ and score, a red left edge when Δ is negative; inside a case the with-plugin runs, then the baseline runs, each grader with a pass or fail chip, a failed one expanded with its explanation and, for `llm`, the judge's votes and evidence; excluded graders carry a `plugin-fired indicator` badge; then the prompt and every grader's rubric or pattern.
- **JSON** (`schemaVersion: 1`, camelCase, new fields added without renames, so ignore unknown fields): `partial` and `partialReason` (`cost_ceiling`, `interrupted`, `auth_failed`); `aggregates.overallScore`, `casesPassed`, `casesTotal`, `meanDelta`; `cases[].name`, `cases[].aggregates.score`, `cases[].aggregates.delta` (absent for single-arm cases); `cases[].arms.with[].error` (non-null does not imply score 0), `.aborted` (a mock stopped the run: `server`, `tool`, `reason`; score 0, `error` null), `.skippedPaidGraders` (the ceiling skipped its judge graders, so its score isn't comparable); `costUsd`, `durationSeconds`, `claudeVersion`.
- Leave `partial: true` documents and runs with `skippedPaidGraders` out of any trend.

## The CI template

`../assets/evals-ci.yml` is the template of a workflow that runs the full suite in CI, only for plugins that have `evals/` and are new or edited, and skips every other plugin. Use it only when the repository has no eval workflow; when it has one, audit that one with the checklist below instead.

1. Copy it to `.github/workflows/evals.yml`.
2. Point the `targets` job at the target-selection script. The template calls `bash scripts/changed-eval-plugins.sh`; set the path to where that script lives in the repository (this skill keeps it at `.claude/skills/testing-plugins/scripts/changed-eval-plugins.sh`). It takes the base and head commits, the plugins directory and the eval directory name.
3. Fill the three `TODO` values:
   - **TODO 1, models:** create the repository variables `EVAL_MODEL` and `EVAL_JUDGE_MODEL` with exact model ids, so a model rollout is not mistaken for a regression.
   - **TODO 2, cost:** set `MAX_COST_USD`, the ceiling per plugin per run; the user approves it, because it is what CI spends.
   - **TODO 3, Claude Code:** set `CLAUDE_CODE_VERSION` to an exact version, 2.1.269 or later (`plugin eval` needs it). The template installs it with the native installer, the method `/en/setup` recommends, which takes the version as `bash -s <version>`.
4. Add the secret `CLAUDE_CODE_OAUTH_TOKEN` (or switch the job to `ANTHROPIC_API_KEY`); the run step fails loudly when it is empty.
5. Keep the pinned action SHAs (`/en/actions/reference/security/secure-use`: pin third-party actions to a full-length commit SHA), and check them against their latest releases before you add the workflow. Keep `--threshold`, `--trust-plugin`, `--scaffold`, `--report` and `--no-publish` unless the user decides otherwise: the suites are the repository's own, which is when the docs allow `--trust-plugin` and `--scaffold`.
6. Make sure `eval-results/` and `**/evals/results/` are git-ignored and `mocks/.replay/` is not, then run the CI audit checklist below on the copy and `actionlint` on the file.

Adding the workflow spends CI money on every pull request that edits a plugin with evals: get the user's approval before you commit it, and never push it without theirs.

## CI audit checklist

Use on an existing workflow before changing it. Report each line as pass, fail or unknown, with the evidence.

1. Triggers on pull requests that touch the plugin directories (not only `plugin.json`) and offers a manual `workflow_dispatch` with a plugin input.
2. Target selection = has evals AND (new OR edited, where edited means a component or dependency changed). Every other plugin is skipped. Checkout has full history (`fetch-depth: 0`), because the base commit must be present.
3. Nothing runs for plugins without evals.
4. The command is complete: `claude plugin eval <path>` target first, `--trust-plugin`, `--json <file>`, `--threshold`, pinned `--model` and `--judge-model`, `--no-publish`, `--max-cost-usd`, `--scaffold` when any case has a `scaffold_script`, and `--allow-tools` with every tool the suites need beyond the read-only set.
5. Claude Code version is pinned (native installer `curl -fsSL https://claude.ai/install.sh | bash -s <version>`, a pinned apt or dnf package, or npm `@anthropic-ai/claude-code@<version>`; all three are documented in `/en/setup`), and ≥ 2.1.269.
6. Credentials come from a secret (`CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`); the job fails loudly when it is empty.
7. Fork PRs are handled (below).
8. The JSON result and `report.html` are uploaded as an artifact; `evals/results/` is gitignored.
9. Exit codes: 0 pass; 1 below threshold, load failure, no cases, a run that couldn't start, API error, untrusted dir, invalid option, or a `--json` file that couldn't be written; 2 partial (cost ceiling hit or credential rejected), with `partial: true` in the JSON; 130/143 interrupted/terminated. Δ and report problems never change the exit code, so the threshold carries the gate.

Per-plugin tool grants and cost ceilings differ, so a config file keyed by plugin (as some repos keep) is better than one global grant. A global grant of `Bash` forces the sandbox on every plugin.

## Fork PRs

Public repos: GitHub does not give secrets to workflows triggered by `pull_request` from a fork, so the suite cannot run there. Do not switch to `pull_request_target` and check out the fork's code with secrets available: the plugin under test runs as the CI user. Instead, skip with a visible warning and let a maintainer review the code and start the run through `workflow_dispatch` ([assets/evals-ci.yml](../assets/evals-ci.yml) does this in its `fork-notice` job).

## Flags worth knowing

`--runs`, `-j/--concurrency` (1–8, shares one rate limit), `--ablation none|with-without`, `--case <glob>`, `--tag`, `--threshold` (default 1.0, so one imperfect case exits 1), `--max-cost-usd`, `--allow-tools`, `--disallow-tools` (v2.1.299; also a `disallowed_tools` case field; missing from the docs page), `--model`, `--judge-model`, `--json [path]` (must end in `.json`; quiet run), `--report <path>`, `--output-dir`, `--eval-dir`, `--keep-temp`, `--no-publish`, `--publish-report`, `--mocks record|off`, `--allow-real-servers`, `--scaffold`, `--no-scaffold`, `--trust-plugin`, `--verbose` (trace events to the debug log; read them with `--debug-file`). Put the target before `--tag`, `--allow-tools`, `--disallow-tools` and `--json`: they consume the words that follow.

## Quick error map

| Message | Meaning and fix |
| :- | :- |
| `plugin eval is currently in early access` / `currently unavailable` | `claude update`, retry in a fresh session; unavailable = switched off server-side. |
| `is too old for claude plugin eval` | git < 2.31. Install a newer git. |
| `No eval cases found` | Run from the plugin root, or filters matched nothing. |
| Baseline arm shows no plugin / `ablation requested but no plugin resolved` | Add `plugins: ["../.."]` to the case (path from the case dir to the plugin dir). Expected when every case resumes a `history_file`. |
| `single-arm (no Δ)` on stderr | A `history_file` case with a path target; pass `--ablation with-without` to compare. |
| `scaffold failed` | The scaffold script exited non-zero or ran over 120 s; that run scores 0. |
| A case with a `scaffold_script` finds none of its fixtures | The run had no `--scaffold`, so the script never ran. |
| `not granted` in the progress output | The case asked for a tool beyond the read-only set; grant it with `--allow-tools`. |
| `[not started: no mock]` | The server has no mock files; add mocks or pass `--allow-real-servers`. |
| `cases[].arms.with[].aborted` is set | A mock's `expect:`, `abort_when` or the agent-mock budget stopped the run; read `reason`. |
| `cannot be evaluated where sessions load it` | Name target for a plugin from a local-path marketplace: out of scope; pass `./<dir>` instead. |
| Everything scores 0 though files exist | Grader targets `files` (paths only); use `{ source: file, path: ... }`. `file_exists` counts only files created during the run, not ones the scaffold created or Claude only edited. |
| Regex over `trace` never matches | Trace is JSON per line: quotes appear as `\"`. |
| `--json output path must end in .json` | Target was placed after `--json`. |
| `Agent type '<plugin>:<agent>' not found` in the without-arm | Expected in the baseline. |
| `mock call budget exceeded` | Raise `max_turns` (budget = 4 × `max_turns`). |
