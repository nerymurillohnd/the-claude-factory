# Test a plugin with evals

Read this file before writing, running, reading or gating on `claude plugin eval`. Sources: "Test plugins with evals" (https://code.claude.com/docs/en/plugin-evals) and "Plugin commands reference", sections `plugin eval` and `plugin eval init` (https://code.claude.com/docs/en/plugins/cli-reference), as of Claude Code 2.1.325.

## Contents

- 1. What evals are for, and what they are not
- 2. Before anything runs: cost and requirements
- 3. How a run works
  - The no-plugin baseline
- 4. Create the first suite
  - Read the first finding before changing anything
- 5. Write and refine cases
  - Write a case by hand
  - prompt.md rules
- 6. Choose graders
  - Graders that give a stable signal
  - Scoring against the baseline
  - Another eval directory
- 7. Fixtures and mocks
  - Seed the workspace or the conversation
  - Mock MCP servers
  - Replay agent-mock answers
- 8. Run evals
  - Choose the target
  - Grant tools
  - Command options
- 9. Run evals in CI
- 10. Read the results
  - HTML report
  - JSON result
- 11. What a run can reach
  - Trust
  - Isolation
- 12. Eval suite reference
  - prompt.md frontmatter
  - case.yaml fields
  - Grader frontmatter
  - What a grader can look at
  - Grader types
  - Mock files
  - Regex in `expect`
- 13. Troubleshooting
- 14. Related pages

## 1. What evals are for, and what they are not

- An eval runs the plugin against test cases and scores the results. A case is a realistic prompt plus one or more graders. A grader is a pass/fail check on what Claude produced: a regex over the reply, whether a tool was called, or a rubric a second model judges.
- Use evals to measure how reliably the plugin leads Claude to the right outcome, to catch regressions when the plugin changes or a new model ships, and to see what the plugin contributes compared with no plugin.
- Do not use evals to check a plugin's files for syntax or schema errors. That is `claude plugin validate`.
- `skill-creator` runs a similar comparison for one skill with its own `evals/evals.json` format. Neither tool reads the other's case files.

## 2. Before anything runs: cost and requirements

Every eval run and every judge grader is a real model call on the user's account, counted against their plan's usage or their API bill. Tell the user this and agree the scope before the first run.

Check these requirements first:

1. Claude Code v2.1.269 or later: `claude --version`; upgrade with `claude update`.
2. Git 2.31 or later, if git is installed: `git --version`. With an older git, `claude plugin eval` stops before running any case. Without git, it runs normally.
3. A plugin directory with `plugin.json` or `.claude-plugin/plugin.json`, or a skills-directory plugin.
4. The same authentication and model provider as the user's normal sessions. On Amazon Bedrock, Google Cloud's Agent Platform or Microsoft Foundry, run the suite from a shell that exports the same provider variables, because each run inherits them.

A reported cost is a list-price estimate of the model calls.

`claude plugin eval` and `claude plugin eval init` are shell commands. They have no `/plugin` form inside a session. Run them from the shell, or have Claude run them through its Bash tool.

## 3. How a run works

- The suite lives in `evals/` inside the plugin. Each case is a subdirectory with a prompt and one or more graders.
- For each run of a case, Claude Code starts a fresh, isolated, non-interactive session with only the plugin loaded, sends the prompt, and lets Claude work until it finishes or hits the case's turn or time limit. Each grader then checks the final reply, the transcript, or a file Claude created.
- Each case runs three times by default, because one run of a non-deterministic agent tells little. A run's score is the fraction of its graders that passed, weighted if weights are set. A case's score is the mean across its runs. A case passes when its score reaches `--threshold`, which is `1.0` by default.
- Cost: roughly cases × runs agent runs with the plugin, the same number again for the baseline, plus three short judge calls per `llm` or `baseline` grader per run.

### The no-plugin baseline

A high score alone does not show the plugin helped. Each case's runs are repeated with no plugin loaded, giving two scores, `WITH` and `W/OUT`. Their difference, `Δ`, is what the plugin contributed. A case that scores 1.0 both with and without the plugin did not need the plugin. The two sets are the with-arm and the without-arm.

## 4. Create the first suite

Do this from the plugin root, the directory that holds `plugin.json` or `.claude-plugin/plugin.json`, with one skill to test and a request a user would type that should trigger it.

1. Run `claude plugin eval init`.
   - If the directory is not yet trusted, it asks `Trust this plugin directory?`; the user answers `y`.
   - An interactive session opens. Claude reads the plugin, asks what a good result looks like, proposes prompts that should and should not trigger the plugin, designs graders for each, runs them once as a trial, and writes one case directory per prompt under `evals/`, named after its prompt.
   - When Claude says the suite is ready, exit with `/exit` or Ctrl+D.
   - In an open session at the plugin root, you can run `claude plugin eval init` yourself. Run from inside a Claude Code session, the command prints the interview instructions for that session to follow instead of writing a template; follow them and ask the user the same questions in the conversation.
   - The interview, in order: Claude reads the plugin; asks what it should do well; proposes cases and graders; writes the case files; runs the cases and reviews the grades with the user to check that the graders score the way the user would.
   - Run it from the plugin's root folder, the directory that holds `.claude-plugin/plugin.json` or the skill's `SKILL.md`. To write the suite into another directory on purpose, pass `--eval-dir <dir>` (default: the manifest's `experimental.evals`, else `evals`).
   - `-i`, `--interactive` requires the interview: the command fails without a terminal instead of writing a template.
2. Run the suite: `claude plugin eval .` from the plugin root. Each case runs three times with the plugin and three without, so one case is six runs. A progress line prints as each run finishes, with its score and each grader's verdict.
3. Read the summary:

   ```text
   CASE        WITH  W/OUT Δ      RUNS COST    NOTES
   first-case  1.00  0.33  +0.67  6    $0.41

   1 case(s) · mean Δ +0.67 · 74s · $0.41
   Report: /Users/you/my-plugin/evals/results/2026-09-10T17-02-11-482Z/report.html
   Published: https://claude.ai/... · keep local next time with --no-publish
   ```

   - `WITH`: score with the plugin. `W/OUT`: score without it. A positive `Δ` means the plugin raised the score.
   - `COST`: list-price estimate. `NOTES`: the highest-weight failing grader's explanation, or the run's error, from the with-arm.
4. Open the report: the `Published:` URL, or the `Report:` path when no `Published:` line appears. It shows each grader's verdict and explanation for every run, and for `llm` graders the judge's votes and the excerpt it judged.

### Read the first finding before changing anything

The most common first finding is a `Δ` near zero with the case's `tool_used: Skill` grader failing. That means Claude is not choosing the skill on natural phrasing. The fix is the skill's `description`. Change it once, based on what the report shows about the phrasing, then run the suite again and compare.

To work on one case cheaply, run one arm once:

```bash
claude plugin eval . --case <case-name> --runs 1 --ablation none
```

One run is noisy. Confirm any change at the default three runs before trusting it. With one arm, the table shows `SCORE` and `PASS%` instead of `WITH`, `W/OUT` and `Δ`.

## 5. Write and refine cases

- A case is a directory under the eval directory that holds `prompt.md`, `case.yaml`, or both.
- Every case needs at least one grader, as `graders/<name>.md` or a `graders:` entry in `case.yaml`. A case without one fails to load.
- To group cases, nest them under a directory that is not itself a case. Everything inside a case directory, such as `graders/` and fixtures, belongs to that case.
- `evals/results/` is written by each run. Add it to `.gitignore`.

The layout `init` writes, and the one to use:

```text
my-plugin/
├── .claude-plugin/plugin.json
├── skills/...
└── evals/
    ├── first-case/
    │   ├── prompt.md          # frontmatter: case fields; body: the prompt
    │   ├── graders/
    │   │   ├── criteria.md    # frontmatter: type + options; body: rubric or pattern
    │   │   └── skill-fired.md
    │   └── case.yaml          # optional: only for context.* fields
    ├── ignores-unrelated-request/
    │   └── ...
    └── results/               # written by each run; add to .gitignore
```

### Write a case by hand

`claude plugin eval init` is the recommended path. To write one by hand, start from a blank template. With `--bare`, or when there is no terminal, the command writes a blank `prompt.md` and `graders/criteria.md` for the named case and runs nothing. The case name is then required. It must start with a letter or digit and contain only letters, digits, `.`, `_` and `-`; on every platform the command also refuses names Windows cannot store, such as `con` or a name ending in `.`.

```bash
claude plugin eval init --bare first-case
```

1. In `evals/first-case/prompt.md`, write the message Claude receives, phrased the way a user would type it, without naming the skill. Set limits and tools in the frontmatter:

   ```markdown
   ---
   max_turns: 10
   allowed_tools: [Read, Glob, Grep, Skill]
   ---

   Write me a commit message for this change: I renamed getUser to fetchUser and updated the three call sites.
   ```

   Each run starts in an empty working directory. Put what the task needs in the prompt, or set up the workspace (section 7).
2. In `evals/first-case/graders/criteria.md`, write a judge rubric as concrete PASS and FAIL conditions:

   ```markdown
   ---
   type: llm
   ---

   PASS if <what a correct response contains>.
   FAIL if <what a wrong or missing response looks like>.
   ```

3. Add `evals/first-case/graders/skill-fired.md` to check the skill produced the answer, with the skill's directory name under `skills/`:

   ```markdown
   ---
   type: tool_used
   tool: Skill
   input_match: '"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"'
   ---
   ```

   It passes when Claude invoked that skill at least once, including as `plugin-name:skill-name`.
4. Run it with `claude plugin eval .`.

### prompt.md rules

- Set `max_turns`, `timeout_seconds`, `model`, `tags` and `allowed_tools` in the frontmatter. Section 12 lists every field.
- Claude receives the body exactly as written. `@path` mentions are not expanded into attachments. If Claude must read a file, grant a tool for it in `allowed_tools`.

## 6. Choose graders

- A grader's frontmatter sets `type`, optionally `weight` (counts more toward the run's score) and `arm` (how it is scored against the baseline).
- Six types. `regex`, `tool_used`, `tool_order` and `file_exists` are computed from the transcript and files and cost nothing. `llm` and `baseline` call a judge model and add cost.
- There are no custom-code graders.
- The judge for `llm` and `baseline` is the model Claude Code uses for background tasks. Choose another with `--judge-model sonnet` or a full model ID.

### Graders that give a stable signal

An `llm` verdict can differ between runs, more so the longer the text it reads. Follow these:

- Grade long output, such as a generated file, with a `regex` grader over the file's contents. Keep `llm` graders for short output, with concrete PASS and FAIL conditions.
- Give each case one grader on the result (the final message or a produced file) and one on the steps (`tool_used` or `tool_order`). Together they show whether the answer was right and whether the plugin produced it.
- If `tool_used: Skill` passes but `Δ` is negative, suspect the judge before the plugin: a small judge can mark a correct answer wrong because of formatting. Re-run with `--judge-model sonnet` and tighten the rubric so formatting does not decide the verdict.
- To check that a build or test passed inside the run, have the prompt ask Claude to run it and write the outcome to a file, grade that file, and assert the command ran with a `tool_used` grader whose `input_match` names the command.

### Scoring against the baseline

A case normally runs in two arms. It runs the with-arm only when:

- `--ablation none` is passed: one arm, half the cost, for iterating on graders.
- The case resumes a transcript (`context.history_file`) and the target is a path such as `.`: the run prints a `single-arm (no Δ)` notice on stderr. Pass `--ablation with-without` to compare anyway.
- No plugin was found for the case when the target is a path (section 13, "The baseline arm shows no plugin").

In a two-arm run, graders that could never pass without the plugin are reported with `scored: false`: excluded from the score in both arms and shown in the with-arm as indicators only. This keeps `Δ` honest. Excluded:

- every `tool_used` grader whose `tool` is `Skill`;
- every `regex` grader with `target: mock_calls` and every `llm` grader with `focus: mock_calls`, when each mocked server in the case is one the plugin declares;
- any grader marked `arm: with-only`.

Three things change the exclusion:

- If every grader in a case is excluded, they are scored normally.
- `arm: both` scores a grader in both arms. Use it for a "must not invoke the skill" check with `min: 0` and `max: 0`.
- Under `--ablation none` nothing is excluded, so the same suite can give a different absolute score in the two modes.

### Another eval directory

If `evals/` is taken by another tool:

- In `plugin.json`: `"experimental": { "evals": "quality/evals" }`.
- On the command line: `--eval-dir quality/evals`, passed to both `claude plugin eval` and `claude plugin eval init`.

The flag wins over the manifest. Use a relative path of plain directory names. An absolute path or one with `..` is an error as a flag; as a manifest value it prints a `Warning:` line and `evals/` is used. Cases, results and `init` output all move to that directory.

## 7. Fixtures and mocks

### Seed the workspace or the conversation

Each run starts in an empty workspace. When a case needs more, add `case.yaml` beside `prompt.md` with a `context` block:

- Fixture files or a git repository: a Bash script in the case directory, named in `context.scaffold_script`. It runs as the user, outside the agent's sandbox, and only with `--scaffold`. Pass that flag only for suites the user or their organization wrote.
- An earlier conversation to continue: a `.jsonl` transcript in `context.history_file`; the prompt becomes the next user turn. With a path target, such a case runs without a baseline arm by default.
- Directories Claude can read during the run: `context.add_dirs`.

`case.yaml` also needs `schema_version: "1.1"` and `name`:

```yaml
schema_version: "1.1"
name: changelog-from-diff
tags: [smoke]
context:
  scaffold_script: fixture.sh
  add_dirs: [resources]
```

A scaffold script starts in the empty workspace with a small fixed environment: the shell's `PATH`, `HOME` set to the run's temporary home, `TMPDIR`, and a few constants such as `TERM=dumb`. Nothing else from the shell reaches it, and neither do the case's `EVAL_*` variables. If it exits non-zero or runs longer than 120 seconds, that run scores 0 with `scaffold failed`. Use it for files and git state only: project configuration it writes is not loaded.

### Mock MCP servers

A plugin whose skills call MCP tools can be evaluated without the real service.

- One Markdown file per tool: `evals/mocks/<server>/<tool>.md` for the suite, or a case's own `mocks/` for one case. `<server>` is the server's name in the plugin's MCP configuration.
- A run never starts the plugin's real servers unless asked. Claude Code registers a substitute under each server's name. Tools with a mock file answer from it and need no `--allow-tools` grant. A tool with no mock file is not available. A server with no mocks appears in the `mocked:` progress line as `plugin_<plugin>_<server>[not started: no mock]`.
- The file's body is what the tool returns. Example, `evals/mocks/tracker/create_issue.md`:

  ```markdown
  ---
  expect:
    title: string
    priority: [low, medium, high]
  ---

  Created issue #4821: {{input.title}}
  ```

- Substitutions: `{{input.<field>}}`, and `{{file:fixtures/{input.<field>}.json}}` for a fixture beside the mock.
- `expect:` guards the input. A call that violates it aborts the run with score 0 and records why, so a case can assert what the plugin asked the server to do.
- `error: true` returns the body as a tool error.
- `type: agent` makes the judge model answer as the server from instructions in the body. Agent-mock calls share one budget per run of four times the case's `max_turns`; a call past it aborts the run with score 0.
- To grade the calls themselves, point a grader at `target: mock_calls`.
- To use the real servers instead, both of which run them as the user outside the sandbox and need an `--allow-tools` grant: `--allow-real-servers` starts real servers for those without mocks and keeps mocked tools mocked; `--mocks off` ignores `mocks/` and starts every server.

### Replay agent-mock answers

A `type: agent` mock answers through `--judge-model`, so its output varies between runs and changes with the judge. After a run with no error or abort, each agent-mock answer is saved under the results directory in `mock-recordings/`. `ADOPT.txt` there lists each recording and the `.replay/<server>/` directory to copy it into, beside the mock. Later runs answer the identical call from the recording with no model call. Commit `mocks/.replay/` with the rest of `mocks/` so CI runs are repeatable.

## 8. Run evals

### Choose the target

- A plugin's root directory, such as `.`: every case in its eval directory, with that plugin loaded. This is the usual run.
- A single `prompt.md` or `case.yaml`: that case, with its enclosing plugin.
- An installed plugin by `name` or `name@marketplace`: the plugin and the cases in its eval directory, read in place or from the installed copy. Results go under `./evals/results/` in the current directory, or `./<dir>/results/` with `--eval-dir`.
- `name@skills-dir`: the same for a skills-directory plugin.
- Omitted: the current directory as a path.

Filter with `--case <glob>` by name and `--tag <tag>` by tag. Put the target before `--tag`, `--allow-tools` and `--json`: the first two take a list and `--json` takes an optional path, so a target after them is read as their value.

### Grant tools

- Runs never stop to ask for permission. Tools that need a grant not given, such as `Bash`, `Write`, `Edit`, `WebFetch` and `WebSearch`, are removed from the session.
- A run allows only the read-only tools the case lists in `allowed_tools` (`Read`, `Glob`, `Grep`, `NotebookRead`, `Skill`, `AskUserQuestion`, `Agent`, `TodoWrite`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `TaskStop`), plus what `--allow-tools` grants. The grant applies to every case in the run:

  ```bash
  claude plugin eval . --allow-tools Write Edit "Bash(npm test *)"
  ```

- A tool a case asked for and did not get shows as `not granted` in the progress output.
- Mocked MCP tools need no grant. A real plugin MCP server needs both the server started (`--allow-real-servers` or `--mocks off`) and a grant by name, such as `--allow-tools "mcp__plugin_my-plugin_github__*"`. A plugin's MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`.
- Granting `Bash` in any form runs every command under Claude Code's OS-level sandbox: writes confined to the run's workspace, home directory and Claude Code configuration unreadable, network limited to domains granted with `--allow-tools "WebFetch(domain:example.com)"`.
- On a machine with no sandbox backend, a Bash or PowerShell grant makes Claude Code refuse each run, so the case shows a run error and usually scores 0. Native Windows has no backend: run shell-granting suites under WSL2. On Linux, install `bubblewrap` and `socat` first.

### Command options

Syntax: `claude plugin eval [target] [options]`. `claude plugin eval --help` has the complete list for the installed build, including `--case`, `--tag`, `--output-dir`, `--eval-dir`, `--no-scaffold`, `--report`, `--allow-real-servers`, `--keep-temp` and `--verbose`. The main options:

- `--runs <n>`: runs per case per arm. Default: each case's `runs`, else 3.
- `-j`, `--concurrency <n>`: up to 1 to 8 runs at once. Default 1. They share the account's rate limit, so this shortens wall-clock time, not throughput. Results keep case order.
- `--model <model>`: model for the agent under test. Default: the case's `model`, else `ANTHROPIC_MODEL`, else Claude Code's default. Pin it in CI.
- `--judge-model <model>`: model for `llm` and `baseline` graders. Default: the background-task model.
- `--ablation none|with-without`: one arm, or add the no-plugin baseline. Default: decided per case.
- `--threshold <0..1>`: a case passes when its with-arm score is at least this. Default 1.0. Any case below makes the command exit 1.
- `--max-cost-usd <usd>`: ceiling on the list-price estimate, not on plan usage. Checked before each run starts; runs already started finish, so spend can pass it by those runs. If any run is left unstarted, the command exits 2 with partial results. Default: no ceiling.
- `--allow-tools <tools...>`: grants beyond the read-only set.
- `--scaffold`: run each case's `scaffold_script`. Default off.
- `--trust-plugin`: skip the first-run trust prompt. Default off. Pass it in CI.
- `--mocks record|off`: default `record` (answer from mocks, do not start real servers, save agent-mock answers). `off` ignores mocks and starts real servers.
- `--allow-real-servers`: with `--mocks record`, also start real servers that have no mock.
- `--json [path]`: print the result document to stdout, or write it to a path ending in `.json`. The run is quiet: no progress or summary.
- `--eval-dir <dir>`: the directory below the plugin that holds the cases. Default: the manifest's `experimental.evals`, else `evals`.
- `--output-dir <dir>`: where `aggregate-result.json` and `report.html` go. Default `<eval dir>/results/<timestamp>/`.
- `--no-publish`: keep the HTML report local.
- `--publish-report`: publish where it would stay local by default, such as a run a Claude Code session started.
- `--keep-temp`: keep every run's sandbox directory and print its path, to inspect what Claude produced.

## 9. Run evals in CI

Run with `--json` for archiving, fail the build on the exit code, pass `--trust-plugin`, pin both models so scores stay comparable, keep the report local, and set a cost ceiling:

```bash
claude plugin eval . \
  --trust-plugin \
  --json results.json \
  --threshold 0.8 \
  --model claude-sonnet-5 \
  --judge-model claude-haiku-4-5 \
  --no-publish \
  --max-cost-usd 20
```

The model IDs, threshold and ceiling here are the page's example values; set them with the user.

Exit codes:

- `0`: every case scored at or above `--threshold` and nothing else failed.
- `1`: a case below the threshold, a case file that failed to load, no cases found, a run that could not start, or a run that ended on an API error. Also an untrusted directory without `--trust-plugin`, an invalid option, or a `--json` result that could not be written.
- `2`: partial run: the `--max-cost-usd` ceiling was hit, or the credential was rejected before or at the first run. `results.json` is still written with `partial: true` and the reason.
- `130`: interrupted; partial results are written.
- `143`: terminated, such as by a CI timeout.

`Δ` is reported but never changes the exit code, and neither do problems writing or publishing the HTML report. To gate on `Δ`, read it from the JSON result (section 10).

To see why a case scored low, run it locally without `--json`, so per-run progress and grader lines print.

The CI runner also needs:

- a Claude Code install and credentials in the environment, such as `ANTHROPIC_API_KEY` or the cloud provider's variables;
- trust: without `--trust-plugin`, a checkout directory Claude Code does not trust needs the first-run prompt, and a run that cannot ask is refused with exit 1;
- for writing cases in CI: `claude plugin eval init` needs a terminal for its questions, so use `claude plugin eval init --bare <name>` for the blank template.

`aggregates.meanDelta` and `cases[].aggregates.delta` exist only in a two-arm run. A job that gates on `Δ` keeps the baseline arm; `--ablation none` there leaves the gate with nothing to read.

To keep costs predictable: give quick every-change suites only graders that call no judge, use `--ablation none` where `Δ` is not needed, and leave `partial: true` documents and runs with `skippedPaidGraders` out of any trend.

## 10. Read the results

Every run with at least one case writes `results/<timestamp>/` inside the eval directory, with `aggregate-result.json` and `report.html`. For a path target that is under the plugin; for a named plugin, under the current directory. The summary table, the JSON and the report render the same data.

### HTML report

`report.html` is self-contained and makes no external requests, so it can be attached to a CI job or opened from disk. Read it from the top down:

1. The verdict line and tiles: whether the plugin helped across the suite. Suite score is the mean of per-case with-plugin scores; Ablation Δ is how far that is above or below the baseline; Cases counts how many met the threshold; Perfect runs is the share of with-plugin runs where every grader passed.
2. Each case card: the case's `Δ` and with-plugin score, with a tick at the threshold. A negative `Δ` gets a red left edge.
3. Inside a case: with-plugin runs first, baseline runs after. Each run lists its graders with a pass or fail chip. A failed grader is expanded with its explanation; an `llm` grader also shows the judge's votes and the evidence it saw. This is where the reason for a low score is. Graders that do not count, such as `tool_used: Skill`, carry a `plugin-fired indicator` badge.
4. Prompt and Graders, below the runs: the case's prompt and each grader's rubric or pattern.

Publishing: signed in with a claude.ai subscription and with artifacts available, Claude Code also publishes the report as a private artifact and prints `Published: <url>`. `--no-publish` keeps it local. With API-key authentication no `Published:` line appears and the local file is the report. A run a Claude Code session started stays local and its `Report:` line says `kept local`; add `--publish-report` to publish it.

### JSON result

`aggregate-result.json` and `--json` output carry `schemaVersion: 1`. Fields are camelCase and new fields are added without renaming, so a script must ignore fields it does not recognize. The fields a gate reads:

- `partial`, `partialReason`: `true` with `cost_ceiling`, `interrupted` or `auth_failed` when the suite did not finish. Leave out of trends.
- `aggregates.overallScore`: mean case score across the suite.
- `aggregates.casesPassed`, `aggregates.casesTotal`: cases at or above `--threshold`, and the total.
- `aggregates.meanDelta`: mean `Δ` across cases, in two-arm mode.
- `cases[].name`; `cases[].aggregates.score` (mean with-arm run score); `cases[].aggregates.delta` (with minus without, omitted for one arm or arms that are not comparable).
- `cases[].arms.with[].error`: `null`, or why a run ended abnormally, such as `timed out after 300s`. Some of these runs are still graded on what they produced, so an error does not imply score 0. A run that ended on an API error scores 0 without grading.
- `cases[].arms.with[].aborted`: present when a mock stopped the run (`expect:`, `abort_when`, or the agent-mock budget), with `server`, `tool` and `reason`. The run scores 0 and `error` stays `null`.
- `cases[].arms.with[].skippedPaidGraders`: `true` when the cost ceiling skipped this run's judge graders; its score is not comparable.
- `costUsd`, `durationSeconds`, `claudeVersion`.

The document also carries the suite configuration, every grader definition, and per-run grader results with explanations and evidence.

## 11. What a run can reach

`claude plugin eval` loads the plugin's skills, hooks and agents and runs the suite on the user's machine, as the user. That is the same trust decision as `claude --plugin-dir`: evaluate only plugins the user trusts. The isolation limits what the agent under test can reach; it is not a boundary against the plugin's own code, and a passing suite says nothing about whether the plugin is safe.

### Trust

- The first run against a directory asks `Trust this plugin directory?` before loading anything, unless the trust prompt was already accepted there in an interactive `claude` session. In a git repository, yes trusts the whole repository, for interactive sessions too.
- When stdin or stdout is not a terminal, or under `--json`, the run cannot ask and is refused with exit 1. `--trust-plugin` asserts trust; use it only for a plugin the user would run on their own machine.
- A named target (an installed plugin or a skills-directory plugin) skips the prompt.
- These run only with their flag: `scaffold_script` with `--scaffold`; tools beyond the read-only set with `--allow-tools`; real MCP servers with `--allow-real-servers` or `--mocks off`. A case's `allowed_tools` and a skill's `allowed-tools` cannot widen any of them.
- When the plugin includes hooks the user did not write, or its real MCP servers are started, treat the scores as advisory unless the run was in an isolated environment such as a container or CI runner: hooks and servers run outside the sandbox and could change the files graders read.

### Isolation

Each run gets a temporary home, working directory and Claude Code configuration, and the agent runs there as a `claude -p` child with only the plugin loaded. Write cases with these in mind:

- Nothing personal or project-level loads: no user settings, hooks, `CLAUDE.md`, MCP servers, other plugins, memory or skills. No `.claude/`, `CLAUDE.md` or `.mcp.json` loads from above or inside the workspace, even one a scaffold wrote, and `add_dirs` grant read access only. Most of the shell environment is withheld; only an allowlist and `EVAL_*` variables reach the run. Ship every skill, agent, hook or MCP server a case depends on inside the plugin under test.
- Managed settings deployed to the machine still apply, so results on a managed machine can differ.
- The Artifact tool is off. A skill that publishes an artifact is graded only on what it produces before that step.
- The agent cannot read the eval directory, so it cannot see the prompt's case, its graders or sibling cases.
- No network sandbox outside shell commands: a `WebFetch(domain:…)` grant reaches that domain directly, and the plugin's hooks and real MCP servers can reach any host.

## 12. Eval suite reference

A directory is a case when it holds `prompt.md` or `case.yaml`. A case with no grader fails with an `invalid case.yaml` error naming `graders`. Every file `claude plugin eval` reads or writes:

```text
evals/
├── <case>/                        # one directory per case; nest under a non-case directory to group
│   ├── prompt.md                  # frontmatter: case and run fields; body: the prompt
│   ├── case.yaml                  # optional: context.* fields, or the whole case in one file
│   ├── graders/
│   │   └── <name>.md              # one grader per file; frontmatter: type and options; body: rubric
│   ├── mocks/                     # optional: mocks for this case only, same layout as below
│   └── <fixtures, scripts, transcripts referenced by case.yaml>
├── mocks/                         # optional: suite-wide MCP mocks
│   ├── <server>/
│   │   ├── <tool>.md              # one mocked tool; body: the tool result
│   │   ├── _server.md             # optional: one agent that answers several tools
│   │   ├── _tools.json            # optional: saved tools/list response for real descriptions and schemas
│   │   └── fixtures/              # files inserted with {{file:fixtures/...}}
│   └── .replay/<server>/          # adopted agent-mock recordings, answered without a model call
└── results/<timestamp>/           # written by each run; add results/ to .gitignore
    ├── aggregate-result.json
    ├── report.html
    └── mock-recordings/           # agent-mock answers from clean runs, with ADOPT.txt
```

### prompt.md frontmatter

An unknown key is an error.

- `schema_version`: default `"1.1"`, set automatically.
- `name`: default the directory name. `--case` globs match it and the report keys on it.
- `description`, `expected_outcome`: for humans, not used at run time.
- `tags`: default `[]`. A case runs if any tag matches `--tag`.
- `plugins`: default the nearest enclosing plugin. Plugin directories under test, relative to the case directory. Set `plugins: ["../.."]` when auto-detection misses the plugin.
- `runs`: default 3, from 1 to 50. `--runs` overrides it.
- `model`: default the child session's default. `--model` overrides it.
- `max_turns`: default 10, up to 200. Hitting it is a run error and usually lowers the score, so set it generously.
- `timeout_seconds`: default 300, up to 3600.
- `allowed_tools`: default `[]`. Read-only tools listed here are granted; anything else needs `--allow-tools`.
- `append_system_prompt`: text appended to the child session's system prompt.
- `env`: default `{}`. Keys must match `EVAL_[A-Z0-9_]*`; any other key fails the run. The run inherits only an allowlist from the shell: `PATH` and locale, proxy and certificate settings, the variables that select and authenticate the model provider, most `ANTHROPIC_*` and `CLAUDE_CODE_*` configuration, and `EVAL_*`. Pass anything else, such as a toolchain setting, as an `EVAL_*` variable.

### case.yaml fields

- Requires `schema_version: "1.1"` and `name`.
- Top level: `description`, `tags`, `plugins`, `runs`, `expected_outcome`.
- Under `execution:`: `model`, `max_turns`, `timeout_seconds`, `allowed_tools`, `append_system_prompt`, `env`, and `prompt` when the whole case lives in `case.yaml` without `prompt.md`.
- Only in `case.yaml`: `context.scaffold_script` (Bash script, runs only with `--scaffold`, minimal environment, 120-second limit, non-zero exit fails the run), `context.history_file` (a `.jsonl` transcript to resume), `context.add_dirs` (directories inside the case, read-only), `graders` (a list, each with a `name` plus the keys a grader file takes; for `llm`, the rubric goes in `criteria`).
- When both files exist, `prompt.md` frontmatter overrides matching `case.yaml` fields, the `prompt.md` body is the prompt, and `graders/*.md` are added after the graders listed in `case.yaml`.

### Grader frontmatter

The grader's name is its filename without `.md`.

- `type`: required.
- `weight`: default 1. Any positive number.
- `arm`: unset by default. `with-only` excludes it from scoring in a two-arm run; `both` scores a grader that would otherwise be excluded.

### What a grader can look at

`regex` graders take `target`, `llm` graders take `focus`, with the same values:

- `last_message`: the final response text. The default.
- `trace`: the session as JSON, one message per line. A `regex` sees every message; an `llm` judge sees the first 12 and the last 12. Quotes and newlines are JSON-escaped, so a regex matches `\"`, not `"`.
- `files`: the paths Claude created during the run, one per line. Not their contents, and not files a scaffold created or Claude only modified.
- `{ source: file, path: <path> }`: one file's contents after the run. Use it to grade what the plugin produced. PNG, JPEG, GIF and WebP are shown to an `llm` judge as images; other binaries such as `.pptx` or PDF are refused, so render them to an image or text first.
- `mock_calls`: each call to a mocked MCP tool, with its input and the mock's answer.

### Grader types

- `regex` (`pattern`, `flags`, `match`, `target`): passes when the JavaScript regex is found in the target. `match: not_contains` requires absence; `match: "count:N"` requires exactly N matches. Case-insensitivity goes in `flags: i`; inline `(?i)` is not supported.
- `tool_used` (`tool`, `input_match`, `min`, `max`): passes when the number of calls to `tool` whose JSON-encoded input matches `input_match` is between `min` (default 1) and `max` (default unlimited). For "never called", set both `min: 0` and `max: 0`.
- `tool_order` (`before`, `after`): passes when both were called and the first matching `before` call precedes the first matching `after` call. Each is a tool name or `{ tool, input_match }`.
- `file_exists` (`path`, `exists`): passes when a file Claude created matches the `path` glob, or none does with `exists: false`. Only files created during the run count.
- `llm` (`criteria`, `focus`): passes when a judge votes PASS in at least two of three votes. In the `.md` layout the file body is the criteria.
- `baseline` (`baseline_file`, `criteria`): passes when a judge finds the run satisfies the criteria at least as well as the reference transcript at `baseline_file`, a `.jsonl` in the case directory.

### Mock files

A `<tool>.md` under `mocks/<server>/` answers one tool. Its body is the result, with `{{input.<field>}}` and `{{file:fixtures/<name>}}` substitutions. Frontmatter:

- `type`: default `fixed` (returns the body). `agent` treats the body as instructions for the judge model, which acts as the server and sees earlier calls as history.
- `expect`: a map from dotted input paths to a type name (`string`, `number`, `boolean`, `array`, `object`), a `/regex/`, a literal, or a list of allowed literals. A violating call aborts the run with score 0, reported as `aborted` with server, tool and reason.
- `error`: default `false`; `fixed` only. Returns the body as a tool error.
- `abort_when`: `agent` only. Prose listing the only conditions under which the agent may abort the run.

Beside the tool files:

- `_server.md`: one `type: agent` mock for several tools, listed in its `tools:` key. A `<tool>.md` for the same tool takes precedence. An `expect:` guard here is a load error unless `tools:` lists one tool; put guards on the individual `<tool>.md`.
- `_tools.json`: a saved `tools/list` response, so mocked tools carry their real descriptions and schemas.

A case's own `mocks/` uses the same layout and overrides the suite's mocks file by file.

### Regex in `expect`

A `/regex/` in `expect:` uses a small dialect checked at load time:

- literal characters, `.`, escapes such as `\d`, classes such as `[a-z]`;
- quantifiers `*`, `+`, `?` and `{m,n}`, each on one character, escape or class;
- an optional `^` at the start and `$` at the end;
- flags `i` and `s` only.

Groups, alternation, backreferences, lookaround or other flags stop the case from loading: it scores 0 and the error names the pattern. For several exact values, write a list of literals. Each pattern checks values only up to a maximum length and a longer value counts as a violation; quantifiers can lower that length and a leading `^` raises it, so anchor with `^` and keep quantifiers few.

## 13. Troubleshooting

Match what you see, then apply the fix. Find the cause before changing a case, a grader or the plugin.

- **"plugin eval is currently in early access"**: the build predates general availability. `claude update`, then run again in a fresh session.
- **"plugin eval is currently unavailable"**: Anthropic switched the command off server-side. Nothing local turns it on; `claude update` and try later in a fresh session.
- **"is not a trusted plugin directory, and this run cannot stop to ask you about it"**: first run against an untrusted directory with no terminal or under `--json`. Run `claude plugin eval <dir>` once in a terminal and answer, or pass `--trust-plugin` if the user trusts the plugin's code and suite.
- **"is too old for claude plugin eval"**: git on `PATH` is older than 2.31, so the suite stopped with exit 1, for example `git 2.30 is too old for claude plugin eval: it ignores the environment configuration (GIT_CONFIG_COUNT, added in git 2.31) that switches off the repository's git hooks and helper programs for the run. Install git 2.31 or newer.` Claude Code turns off a repository's git hooks and helpers for each run through configuration only git 2.31+ reads, so it stops rather than run with them on. Install git 2.31 or later. Before v2.1.283 the version was not checked and an older git ran with those programs on.
- **"cannot be evaluated where sessions load it"**: the named plugin was installed from a marketplace added from a local path, and no session could load it now; exit 1. Example: `Error: formatter@my-marketplace cannot be evaluated where sessions load it: no session could load it now. Its marketplace is a folder whose catalog could not be read, or lists it no more. ...` The sentence after `no session could load it now.` names what failed. Run `claude plugin marketplace list` and fix it, such as restoring the marketplace directory or the plugin's catalog entry, or evaluate the source directory, such as `claude plugin eval ./plugins/formatter`.
- **"No eval cases found"**: no `<case>/prompt.md` or `<case>/case.yaml` under the eval directory in effect, or `--case` and `--tag` matched nothing. Run from the plugin root, or `claude plugin eval init`.
- **The baseline arm shows no plugin, or `Δ` is zero**: no `W/OUT` column, or "ablation requested but no plugin resolved", usually means no plugin was found for the case. If every case resumes a transcript, the missing column is expected. Otherwise add `plugins: ["../.."]` with the path from the case to the plugin. If the plugin loaded and `Δ` is near zero with `tool_used: Skill` failing, that is a real finding: the skill's `description` does not trigger on the prompt's phrasing. Fix the description and re-run the same suite.
- **"Agent type '...' not found" for one of the plugin's agents**: in baseline runs the plugin's agents do not exist, so `Agent type '<plugin>:<agent-name>' not found. Available agents: ...` is expected. Baseline runs are under `cases[].arms.without` in the JSON. With the plugin loaded, a case that lists `Agent` in `allowed_tools` dispatches its agents by namespaced name, such as `my-plugin:code-reviewer`. `--ablation none` skips baseline runs.
- **Everything scores zero although the right files were produced**: the graders target `files` (the list of paths) instead of contents; use `{ source: file, path: <path> }`. `file_exists` counts only files created during the run, so for a scaffolded or edited file grade its contents or use `tool_used` on `Edit`.
- **A regex over the trace does not match visible text**: the default `target` is `last_message`, not the trace; in `trace`, quotes appear as `\"`; regexes are JavaScript, so use `flags: i`, not `(?i)`.
- **Tools are denied, MCP tools are missing, or Bash will not run**: anything beyond the read-only set needs a grant such as `--allow-tools Bash Write`. Personal MCP servers never load in a run. The plugin's own servers start only when opted in, and then need `--allow-tools "mcp__plugin_<plugin>_<server>__*"`; a mocked tool needs neither.
- **The run exits 1 but the results look fine**: when every case reached the threshold and it still exits 1, a stderr line names the cause, even under `--json`, such as a case file that failed to load or a run that ended on an API error. Also, the default threshold is 1.0, so any case below perfect exits 1; set the threshold the user requires.
- **`--json output path must end in .json`**: the target came after `--json` and was read as the path. Put the target first, `claude plugin eval . --json`, or give an explicit `.json` path.
- **A grader shows `passed: false` under a run that scored 1.0**: it is excluded from the score by design in a two-arm run, with `scored: false`.
- **"ended on an API error and scored 0 without grading"**: at least one run's last request got an HTTP error, such as a rate or usage limit. It scores 0 with no grader results and the command exits non-zero whatever the scores. Find each run's error (at the end of its progress line after `error:`, or at `cases[].arms.with[].error` / `cases[].arms.without[].error` in JSON), resolve its cause, and run again. Baseline runs count too: every case can pass while the command fails; in a two-arm run the affected case's `W/OUT` and `Δ` print as `—`. Before v2.1.299 such a run was graded on what it produced.
- **Runs fail with a usage-limit or rate-limit error partway through**: they score 0 without grading and the command exits non-zero; the suite finishes and is not `partial`. Re-run after the limit resets, with `--runs 1` or a `--case` filter to stay under it.
- **"mock call budget exceeded"**: all `type: agent` mocks in a run share a budget of four times `max_turns` (40 at the default), `.replay/` answers included; the `mock budget` progress line shows it. A call past it aborts with score 0. Raise `max_turns` for a skill that calls agent mocks often.
- **Runs time out or hit the turn cap**: defaults are 10 turns and 300 seconds. Raise `max_turns` and `timeout_seconds` for tasks that need more, and use `--max-cost-usd` as the cost limit rather than tight per-run limits.

## 14. Related pages

- Create a plugin, and loading with `--plugin-dir`: https://code.claude.com/docs/en/plugins/create
- Plugin commands reference, `plugin eval` and `plugin eval init`: https://code.claude.com/docs/en/plugins/cli-reference#plugin-eval
- Troubleshooting for `<directory> is not a plugin or skill folder` from `eval init`: `messages.md`, section B5
- Manifest reference, `experimental.evals`: https://code.claude.com/docs/en/plugins/manifest-reference#fields
- Skills, how a description decides invocation: https://code.claude.com/docs/en/skills
- Sandboxing: https://code.claude.com/docs/en/sandboxing
- Publish a plugin: https://code.claude.com/docs/en/plugins/publish
- Measure plugin cost and usage: https://code.claude.com/docs/en/plugins/measure
