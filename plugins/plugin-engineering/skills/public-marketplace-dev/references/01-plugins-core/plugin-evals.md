# Test plugins with evals

Write eval cases for a Claude Code plugin, run them with `claude plugin eval`, grade the results, compare them against a no-plugin baseline, and gate CI on the score.

## Contents

- [Requirements](#requirements)
- [How an eval run works](#how-an-eval-run-works)
  - [What happens in a run](#what-happens-in-a-run)
  - [How a case is scored](#how-a-case-is-scored)
  - [The no-plugin baseline](#the-no-plugin-baseline)
- [Create your first eval suite](#create-your-first-eval-suite)
- [Write and refine cases](#write-and-refine-cases)
  - [Write a case manually](#write-a-case-manually)
  - [Set run limits and tools in prompt.md](#set-run-limits-and-tools-in-promptmd)
  - [Choose and weight graders](#choose-and-weight-graders)
    - [Choose graders that give a stable signal](#choose-graders-that-give-a-stable-signal)
  - [Score against the no-plugin baseline](#score-against-the-no-plugin-baseline)
  - [Use a different eval directory](#use-a-different-eval-directory)
- [Set up fixtures and mocks](#set-up-fixtures-and-mocks)
  - [Seed the workspace or conversation](#seed-the-workspace-or-conversation)
  - [Mock MCP servers](#mock-mcp-servers)
    - [Replay agent mock answers](#replay-agent-mock-answers)
- [Run evals](#run-evals)
  - [Choose what to evaluate](#choose-what-to-evaluate)
  - [Grant tools](#grant-tools)
  - [Command options](#command-options)
  - [Run evals in CI](#run-evals-in-ci)
- [Read the results](#read-the-results)
  - [HTML report](#html-report)
  - [JSON result](#json-result)
- [What a run can access](#what-a-run-can-access)
  - [Trust the plugin directory](#trust-the-plugin-directory)
  - [How runs are isolated](#how-runs-are-isolated)
- [Eval suite reference](#eval-suite-reference)
  - [prompt.md frontmatter](#promptmd-frontmatter)
  - [case.yaml fields](#caseyaml-fields)
  - [Grader frontmatter](#grader-frontmatter)
    - [What a grader can look at](#what-a-grader-can-look-at)
    - [Grader types](#grader-types)
  - [Mock files](#mock-files)
    - [Regex patterns in expect](#regex-patterns-in-expect)
- [Troubleshooting](#troubleshooting)
  - ["plugin eval is currently in early access"](#plugin-eval-is-currently-in-early-access)
  - ["plugin eval is currently unavailable"](#plugin-eval-is-currently-unavailable)
  - ["is not a trusted plugin directory, and this run cannot stop to ask you about it"](#is-not-a-trusted-plugin-directory-and-this-run-cannot-stop-to-ask-you-about-it)
  - ["is too old for claude plugin eval"](#is-too-old-for-claude-plugin-eval)
  - ["cannot be evaluated where sessions load it"](#cannot-be-evaluated-where-sessions-load-it)
  - ["No eval cases found"](#no-eval-cases-found)
  - [The baseline arm shows no plugin, or delta is zero](#the-baseline-arm-shows-no-plugin-or-delta-is-zero)
  - ["Agent type '...' not found" for one of the plugin's agents](#agent-type--not-found-for-one-of-the-plugins-agents)
  - [Everything scores zero although the right files were produced](#everything-scores-zero-although-the-right-files-were-produced)
  - [A regex over the trace doesn't match visible text](#a-regex-over-the-trace-doesnt-match-visible-text)
  - [Tools are denied, MCP tools are missing, or Bash won't run](#tools-are-denied-mcp-tools-are-missing-or-bash-wont-run)
  - [The run exits 1 but the results look fine](#the-run-exits-1-but-the-results-look-fine)
  - [`--json output path must end in .json`](#--json-output-path-must-end-in-json)
  - [A grader shows passed: false under a run that scored 1.0](#a-grader-shows-passed-false-under-a-run-that-scored-10)
  - ["ended on an API error and scored 0 without grading"](#ended-on-an-api-error-and-scored-0-without-grading)
  - [Runs fail with a usage-limit or rate-limit error partway through](#runs-fail-with-a-usage-limit-or-rate-limit-error-partway-through)
  - ["mock call budget exceeded"](#mock-call-budget-exceeded)
  - [Runs time out or hit the turn cap](#runs-time-out-or-hit-the-turn-cap)
- [Documentation References](#documentation-references)

The `claude plugin eval` shell command runs a [plugin](https://code.claude.com/docs/en/plugins/overview.md) against a suite of test cases and scores the results. Each case is a realistic prompt plus one or more graders. A grader is a pass/fail check on what Claude produced, such as a regex over the reply, whether a particular tool was called, or a rubric that a second model judges the reply against.

The suite does not have to be written by hand. `claude plugin eval init` asks the author about the plugin, proposes the cases and graders, tries them, and writes the files. Claude can also be asked to do the same from a session that is already open.

Use evals to:

* Measure how reliably the plugin leads Claude to produce the right outcome
* Catch regressions when the plugin changes or a new model is released
* See what the plugin contributes compared with no plugin

Evals are for a working plugin whose behavior needs testing, and for gating plugin changes in CI. To iterate on one skill inside a Claude Code conversation, the [skill-creator plugin](https://code.claude.com/docs/en/skills.md#run-evals-with-skill-creator) runs a similar comparison with its own `evals/evals.json` format; neither tool reads the other's case files. To create a plugin, see [Create a plugin](https://code.claude.com/docs/en/plugins/create.md). To check a plugin's files for syntax and schema errors rather than its behavior, use [`claude plugin validate`](https://code.claude.com/docs/en/plugins/cli-reference#plugin-validate).

> **Note:** Every eval run and every judge grader is a real model call on the user's account, counted against the plan's usage or the API bill. Check the [requirements](#requirements) first. Then [create the first eval suite](#create-your-first-eval-suite), or go to [Run evals in CI](#run-evals-in-ci) when a suite already exists.

## Requirements

Plugin evals require:

* Claude Code v2.1.269 or later. Run `claude --version` to check and `claude update` to upgrade.
* Git 2.31 or later, if git is installed. Run `git --version` to check. With an older git, `claude plugin eval` [stops before running any case](#is-too-old-for-claude-plugin-eval). Without git, it runs normally.
* A plugin directory with a `plugin.json` or `.claude-plugin/plugin.json` manifest, or a [skills-directory plugin](https://code.claude.com/docs/en/plugins/loading.md#plugins-shared-through-a-repository).
* The same authentication and model provider that normal Claude Code sessions use. Eval runs, judge-scored graders, and `claude plugin eval init` call the model with those credentials, so they count against the plan's usage limits or the API bill. When the command reports a cost, the figure is a [list-price estimate](https://code.claude.com/docs/en/costs.md) of those calls. When Claude Code runs on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry, run the suite from a shell that exports the same provider variables as normal sessions, because each run inherits them from that shell as the [`env` field](#promptmd-frontmatter) describes.

## How an eval run works

An eval suite lives in a directory called `evals/` inside the plugin, laid out as [Write and refine cases](#write-and-refine-cases) shows. Each case is its own subdirectory with a [prompt](#set-run-limits-and-tools-in-promptmd) and one or more [graders](#choose-and-weight-graders). The prompt is something a person using the plugin might type, such as a request one of its skills should handle.

### What happens in a run

For each run of a case, Claude Code starts a fresh, [isolated](#how-runs-are-isolated) [non-interactive session](https://code.claude.com/docs/en/headless.md) with only the plugin under test loaded, sends the prompt, and lets Claude work until it finishes or hits the case's turn or time limit. Each grader then checks the final reply, the transcript, or a file Claude created, and passes or fails.

### How a case is scored

One run of a non-deterministic agent says little, so each case runs three times by default. A run's score is the fraction of its graders that passed, weighted when weights are set, and the case's score is the mean across its runs. A case passes when its score meets the [`--threshold`](#command-options), `1.0` by default.

In model calls, a suite makes roughly cases × runs agent runs with the plugin and the same number again for the [no-plugin baseline](#the-no-plugin-baseline), plus three short judge calls per `llm` or `baseline` grader per run.

### The no-plugin baseline

A high score alone does not show that the plugin helped, because Claude might do as well without it. To separate the two, a case's runs are repeated with no plugin loaded, which produces two scores, `WITH` and `W/OUT`. Their difference, `Δ`, is what the plugin contributed. When a case scores 1.0 both with and without the plugin, the plugin is not what made it pass.

The two sets of runs are called the with-arm and the without-arm. [Score against the no-plugin baseline](#score-against-the-no-plugin-baseline) covers which cases run the with-arm only and how graders are scored across the two arms.

## Create your first eval suite

This walkthrough writes one case for a plugin, runs it, and reads the result. Before starting, confirm:

* Claude Code v2.1.269 or later and the other [requirements](#requirements)
* A terminal open at the plugin's root directory, the one containing `plugin.json` or `.claude-plugin/plugin.json`
* One skill in the plugin to test, and a request a user would type that should trigger it

**1. Create the cases**

From the plugin root, run:

```bash theme={null}
claude plugin eval init
```

If Claude Code does not already trust this directory, it first asks `Trust this plugin directory?`; answer `y`.

An interactive Claude Code session then opens. Claude reads the plugin and asks the user what a good result looks like, proposes prompts that should and should not trigger the plugin, designs graders for each, runs them once as a trial to check they behave, and writes one case directory per prompt under `evals/`, each named after its prompt.

When Claude reports that the suite is ready, exit that session with `/exit` or Ctrl+D to return to the shell.

When a Claude Code session is already open at the plugin root, run `claude plugin eval init` from that session instead. Claude runs the command and then asks the user the same questions in that conversation.

To write a case by hand and see exactly what the files contain, follow [Write a case manually](#write-a-case-manually), then return here to run it.

**2. Run the suite**

Back in the shell at the plugin root, run every case under `evals/`:

```bash theme={null}
claude plugin eval .
```

The directory was trusted during step 1, so the run starts immediately. When the case was written by hand instead, the run first asks `Trust this plugin directory? [y/N]`; answer `y`. [What a run can access](#what-a-run-can-access) explains what that answer agrees to.

Each case runs three times with the plugin and three times without it, so one case is six runs. A progress line prints as each run finishes, with that run's score and each grader's verdict.

**3. Read the summary**

When the suite finishes, a summary table prints, followed by where the report went:

```text theme={null}
CASE        WITH  W/OUT Δ      RUNS COST    NOTES
first-case  1.00  0.33  +0.67  6    $0.41

1 case(s) · mean Δ +0.67 · 74s · $0.41
Report: /Users/you/my-plugin/evals/results/2026-09-10T17-02-11-482Z/report.html
Published: https://claude.ai/... · keep local next time with --no-publish
```

`WITH` is the case's score with the plugin loaded, `W/OUT` is the score without it, and a positive `Δ` means the plugin raised the score. `COST` is a list-price estimate of the model calls, and `NOTES` shows the highest-weight failing grader's explanation, or the run's error, from the with-arm.

**4. Open the report and iterate**

Open the `Published:` URL, or the `Report:` path when no `Published:` line appears, to see each grader's verdict and explanation for every run, and for `llm` graders the judge's votes and the excerpt it judged. The `Published:` line appears only when the account can [publish reports](#html-report).

The most common first finding is a `Δ` near zero with the case's `tool_used: Skill` grader failing, which means Claude is not choosing the skill on natural phrasing. Adjust the skill's [`description`](https://code.claude.com/docs/en/skills#frontmatter-reference), run `claude plugin eval .` again, and compare.

To iterate on one case with fewer runs, run a single arm once. A single run is noisy, so confirm any change at the default three runs before trusting it. With one arm, the table shows `SCORE` and `PASS%` columns instead of `WITH`, `W/OUT`, and `Δ`:

```bash theme={null}
claude plugin eval . --case <case-name> --runs 1 --ablation none
```

Replace `<case-name>` with one of the directory names under `evals/`.

## Write and refine cases

The cases `claude plugin eval init` writes are plain files to open, change, and add to. A case is a directory under the plugin's eval directory that contains a `prompt.md`, a `case.yaml`, or both. Give each case at least one grader, as a `graders/<name>.md` file or a `graders:` entry in `case.yaml`, because a case without one fails to load. To group cases, nest them under a directory that is not itself a case; anything inside a case directory, such as `graders/` and fixture files, belongs to that case.

This is the layout `claude plugin eval init` writes; use it for new suites. The [eval suite reference](#eval-suite-reference) has the complete tree, including mocks and results:

```text theme={null}
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

### Write a case manually

Having Claude write the cases with `claude plugin eval init` is the recommended path. To write one by hand instead, start from a blank template. The following command writes a case named `first-case` with a placeholder `prompt.md` and one placeholder grader, and runs nothing:

```bash theme={null}
claude plugin eval init --bare first-case
```

```text theme={null}
evals/first-case/
├── prompt.md            # the prompt sent to Claude, plus run limits
└── graders/
    └── criteria.md      # one grader: how to score the result
```

The body of `prompt.md` is the message Claude receives in each run; its frontmatter sets the run's limits and the tools the case may use. Open `evals/first-case/prompt.md` and replace the placeholder body with a request one of the plugin's skills should handle, phrased the way a user would type it rather than naming the skill. This example is for a skill that drafts commit messages; substitute a request for the skill under test:

```markdown theme={null}
---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Write me a commit message for this change: I renamed getUser to fetchUser and updated the three call sites.
```

Each run starts in an empty working directory, so put whatever the task needs in the prompt itself, or [set up the workspace](#seed-the-workspace-or-conversation) first.

The [full list of frontmatter fields](#promptmd-frontmatter) covers the model, timeout, tags, and environment variables.

Each file under `graders/` is one check applied after the run. Open `evals/first-case/graders/criteria.md` and replace the placeholder with a rubric for the judge model, written as concrete PASS and FAIL conditions:

```markdown theme={null}
---
type: llm
---

PASS if <what a correct response contains>.
FAIL if <what a wrong or missing response looks like>.
```

Then add a second grader that checks whether the skill is what produced the answer. Create `evals/first-case/graders/skill-fired.md`, replacing `your-skill-name` with the skill's directory name under `skills/`, which is the name Claude invokes it by:

```markdown theme={null}
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"'
---
```

This grader passes when Claude invoked that skill at least once during the run, including by its namespaced `plugin-name:skill-name` form.

[Grader types](#grader-types) lists the other checks available, such as matching a regex or confirming a file was created.

With both files saved, run the case the way the [quickstart](#create-your-first-eval-suite) does, with `claude plugin eval .` from the plugin root.

### Set run limits and tools in prompt.md

Set a case's `max_turns`, `timeout_seconds`, `model`, `tags`, and the `allowed_tools` it may use in `prompt.md` frontmatter. The [prompt.md frontmatter](#promptmd-frontmatter) reference lists every field and its default.

Claude receives the body exactly as written. `@path` mentions in it are not expanded into file attachments, so when Claude needs to read a file, grant a tool for it in `allowed_tools`.

### Choose and weight graders

A grader's frontmatter sets its `type`, and optionally a `weight` that makes it count for more of the run's score and an [`arm`](#score-against-the-no-plugin-baseline) that controls how it is scored against the baseline. Of the six types, `regex`, `tool_used`, `tool_order`, and `file_exists` are computed from the transcript and files and cost nothing, while `llm` and `baseline` call a judge model and add to the run's cost.

There are no custom-code graders.

[Grader types](#grader-types) lists each type's options and pass condition, and [What a grader can look at](#what-a-grader-can-look-at) lists the values `target` and `focus` accept.

By default, the judge for `llm` and `baseline` graders is the model Claude Code uses for background tasks. To choose the judge, pass `--judge-model sonnet` or a full model ID.

#### Choose graders that give a stable signal

An `llm` grader asks a model for a verdict, so its answer can differ between runs, and it differs more the longer the text it has to read. Follow these practices to keep a suite's scores steady enough to trust:

* For long output such as a generated file, grade it with a `regex` grader over the file's contents, which checks the whole file the same way every time. Keep `llm` graders for short outputs, with rubrics written as concrete PASS and FAIL conditions.
* Give each case one grader on the result, such as the final message or a produced file, and one on the steps Claude took to produce it, such as `tool_used` or `tool_order`. Together they show both whether the answer was right and whether the plugin produced it.
* When a case's `tool_used: Skill` grader passes but `Δ` is negative, suspect the judge before the plugin. A small judge model can mark a correct answer wrong because it is formatted differently from what the rubric describes. Re-run with `--judge-model sonnet`, and tighten the rubric so formatting does not decide the verdict.
* To check that a build or test passed inside the run, have the prompt ask Claude to run it and write the outcome to a file, grade that file, and assert the command ran with a `tool_used` grader whose `input_match` names the command.

### Score against the no-plugin baseline

When a plugin is under test, a case normally runs in two arms. The with-arm is its runs with the plugin loaded, and the without-arm is the same number of runs with no plugin at all. The summary and report show both scores and `Δ`, the with-arm score minus the without-arm score.

In these situations a case runs the with-arm only, so it gets no `W/OUT` score or `Δ`:

* **`--ablation none` is passed**: every case runs one arm, which halves the cost when the comparison is not needed, such as while iterating on graders.
* **The case resumes a transcript and the target is a path**: with a [target](#choose-what-to-evaluate) such as `.` rather than an installed plugin's name, a [`context.history_file`](#seed-the-workspace-or-conversation) case runs one arm by default, on the assumption that the recorded conversation already reflects the plugin. The run prints a `single-arm (no Δ)` notice on stderr naming these cases. To compare the resumed turn with and without the plugin, pass `--ablation with-without`.
* **No plugin was found for the case**: when the target is a path, a case whose plugin Claude Code could not locate also runs one arm by default. See [The baseline arm shows no plugin, or delta is zero](#the-baseline-arm-shows-no-plugin-or-delta-is-zero) to fix it.

In a two-arm run, some graders are reported with `scored: false`. A check like "the skill was invoked" can never pass without the plugin, so counting it would push the without-arm toward zero and inflate `Δ`. To keep the two arms comparable, Claude Code excludes such graders from the score in both arms and reports them in the with-arm as pass/fail indicators only. The excluded set includes:

* Every `tool_used` grader whose `tool` is `Skill`
* Every `regex` grader with `target: mock_calls` and every `llm` grader with `focus: mock_calls`, when each [mocked server](#mock-mcp-servers) in the case is one the plugin declares
* Any grader marked `arm: with-only`

Three settings change that exclusion:

* **Every grader excluded**: when every grader in a case is in the excluded set, they are scored normally instead, since there would be nothing left to score.
* **`arm: both`**: set `arm: both` on a grader to score it in both arms regardless. Use it for a "must not invoke the skill" check with `min: 0` and `max: 0`.
* **`--ablation none`**: under `--ablation none` nothing is excluded, so the same suite can produce a different absolute score in the two modes.

### Use a different eval directory

When `evals/` is already taken by another tool, keep the suite in a different directory. Record that directory in the plugin's `plugin.json` so every run and every collaborator uses it, or pass it on the command line for a single run:

* **In `plugin.json`**: add `"experimental": { "evals": "quality/evals" }`.
* **On the command line**: pass `--eval-dir quality/evals` to both `claude plugin eval` and `claude plugin eval init`.

When both are set, the flag's directory is used. Give a relative path of plain directory names such as `qa` or `quality/evals`. An absolute path or one containing `..` is not accepted: as a flag value it is an error, while an unusable manifest value prints a `Warning:` line and the run uses `evals/` instead. Cases, results, and `init` output all move to that directory.

## Set up fixtures and mocks

A case can need more than a prompt: files or a git repository in the workspace, an earlier conversation to continue, or answers from the MCP servers the plugin connects to. Set each of those up beside the case so runs stay repeatable.

### Seed the workspace or conversation

Each run starts in an empty workspace. When a case needs more than the prompt, add a `case.yaml` beside `prompt.md` with a `context` block:

* **Fixture files or a git repository**: write a Bash script in the case directory and name it in `context.scaffold_script`. The script runs as the invoking user, outside the agent's sandbox, and only when `--scaffold` is passed. Pass that flag only for suites the user or the user's organization wrote.
* **An earlier conversation to continue**: save the transcript as a `.jsonl` file and name it in `context.history_file`; the case's prompt becomes the next user turn. When the target is a path, such a case runs [without a baseline arm](#score-against-the-no-plugin-baseline) by default.
* **Fixture directories Claude can read during the run**: list them in `context.add_dirs`.

A `case.yaml` also needs `schema_version: "1.1"` and `name`. The [case.yaml fields](#caseyaml-fields) reference has the full list.

This `case.yaml` seeds a workspace from a script and lets Claude read fixtures from a `resources/` directory:

```yaml theme={null}
schema_version: "1.1"
name: changelog-from-diff
tags: [smoke]
context:
  scaffold_script: fixture.sh
  add_dirs: [resources]
```

A scaffold script starts in the empty workspace with a small fixed environment: the shell's `PATH`, `HOME` set to the run's temporary home directory, `TMPDIR`, and a few constants such as `TERM=dumb`. Nothing else from the shell reaches it, and neither do the case's `EVAL_*` variables. When the script exits non-zero or runs longer than 120 seconds, that run scores 0 with a `scaffold failed` error. Use the script for files and git state only, since project configuration it writes [is not loaded](#how-runs-are-isolated).

### Mock MCP servers

A plugin whose skills call MCP tools can be evaluated without the real service behind them. Put one Markdown file per tool under `evals/mocks/<server>/<tool>.md` for the whole suite, or under a case's own `mocks/` directory for one case, where `<server>` is the server's name in the plugin's [MCP configuration](https://code.claude.com/docs/en/plugins/components.md#mcp-servers).

A run never starts the plugin's real MCP servers unless asked to. Claude Code registers a substitute server under each server's own name. Tools with a mock file answer from it and are allowed without an `--allow-tools` grant, and a tool with no mock file is not available to Claude. A server with no mocks at all appears in the case's `mocked:` progress line as `plugin_<plugin>_<server>[not started: no mock]`.

The file's body is what the tool returns to Claude. This mock substitutes for a `create_issue` tool on a server named `tracker`, checks the input Claude sends, and echoes the title back. Save it as `evals/mocks/tracker/create_issue.md`:

```markdown theme={null}
---
expect:
  title: string
  priority: [low, medium, high]
---

Created issue #4821: {{input.title}}
```

A mock file's body and frontmatter accept these options:

* **Substitutions**: insert fields from the call's input with `{{input.<field>}}`, and the contents of a fixture file beside the mock with `{{file:fixtures/{input.<field>}.json}}`.
* **`expect:`**: the `expect:` block guards the input. When a call violates it, the run aborts with score 0 and records why, so a case can assert what the plugin asked the server to do.
* **`error: true`**: set `error: true` to return the body as a tool error instead.
* **`type: agent`**: set `type: agent` to have the judge model answer as the server from instructions in the body. Calls to agent mocks share one [budget per run](#mock-call-budget-exceeded) of four times the case's `max_turns`, and a call past it aborts the run with score 0.

The [mock file reference](#mock-files) lists every key and the `_server.md` and `_tools.json` files.

To grade the calls themselves, point a grader at `target: mock_calls`.

To run against the plugin's real MCP servers instead, pass one of these flags. Either way, those processes run as the invoking user, outside the run's sandbox, and their tools need an [`--allow-tools` grant](#grant-tools):

* **`--allow-real-servers`**: start the real process for each server that has no mock, and keep answering mocked tools from their files
* **`--mocks off`**: ignore `mocks/` entirely and start every server the plugin declares

#### Replay agent mock answers

A `type: agent` mock answers with a call to the [`--judge-model`](#command-options), so its output varies between runs and changes when the judge changes. When a run completes without an error or abort, Claude Code saves each answer an agent mock gave under the results directory in `mock-recordings/`.

Open `ADOPT.txt` there to see each recording and the `.replay/<server>/` directory to copy it into, beside the mock that produced it. After a recording is copied there, later runs answer the identical call from it with no model call. Commit `mocks/.replay/` with the rest of `mocks/` so CI runs are repeatable.

## Run evals

Once a suite exists, `claude plugin eval` runs it. The target argument chooses which plugin and cases run, `--allow-tools` grants any tools the cases need beyond the read-only set, and the other options control run count, models, cost, and output.

### Choose what to evaluate

Usually, run `claude plugin eval .` from the plugin root, which runs every case in the suite with the plugin in the current directory loaded. To run a single case file, or to evaluate an installed plugin rather than one under development, pass a different target:

| Target | What runs |
| :- | :- |
| A plugin's root directory, such as `.` | Every case under its eval directory, with that plugin loaded |
| A single `prompt.md` or `case.yaml` file | That case, with its enclosing plugin loaded |
| An installed plugin by name, `name` or `name@marketplace` | The plugin and the cases in its eval directory, read [in place or from the installed copy](https://code.claude.com/docs/en/plugins/loading.md#in-place-and-copied-plugins). Results are written under `./evals/results/` in your current directory, or `./<dir>/results/` with `--eval-dir` |
| Omitted | The current directory as a path |

Add `--case <glob>` to filter by case name and `--tag <tag>` to keep cases with any of the given tags.

Put the target before `--tag`, `--allow-tools`, and `--json`. The first two take a list and `--json` takes an optional path, so each of them reads a target that follows it as its own value.

### Grant tools

Runs never stop to ask for permission. Built-in tools that need a grant that was not given, such as `Bash`, `Write`, `Edit`, `WebFetch`, and `WebSearch`, are removed from the session, so Claude cannot call them at all.

A run allows only the read-only tools the case lists in `allowed_tools`, from `Read`, `Glob`, `Grep`, `NotebookRead`, `Skill`, `AskUserQuestion`, `Agent`, `TodoWrite`, and the task tools `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, and `TaskStop`, plus whatever `--allow-tools` grants. That grant applies to every case in the run. To let cases use `Bash`, `Write`, `Edit`, `WebFetch`, or `WebSearch`, grant them explicitly:

```bash theme={null}
claude plugin eval . --allow-tools Write Edit "Bash(npm test *)"
```

When a case asked for a tool that was not granted, the progress output lists it as `not granted`. Tools on a [mocked](#mock-mcp-servers) MCP server need no grant. Tools on a real plugin MCP server need both the server started, with `--allow-real-servers` or `--mocks off`, and a grant by name, such as `--allow-tools "mcp__plugin_my-plugin_github__*"`. A plugin's MCP tools are named `mcp__plugin_<plugin>_<server>__<tool>`.

When `Bash` is granted in any form, every command runs under Claude Code's [OS-level sandbox](https://code.claude.com/docs/en/sandboxing.md). Writes are confined to the run's workspace, the user's home directory and Claude Code configuration are unreadable, and network access is limited to domains granted with `--allow-tools "WebFetch(domain:example.com)"`. When Bash or PowerShell is granted on a machine with no sandbox backend, Claude Code refuses each run rather than running it unconfined, and the case shows a run error and usually scores 0. Native Windows has no backend, so run shell-granting suites under WSL2; on Linux, install `bubblewrap` and `socat` first. See the [sandboxing prerequisites](https://code.claude.com/docs/en/sandboxing.md).

### Command options

This table covers the options for run count, models, scoring, cost, tool grants, mocks, and output. Run `claude plugin eval --help` for the complete list, which also includes `--case`, `--tag`, `--eval-dir`, `--no-scaffold`, `--report`, and `--verbose`.

| Option | Default | Effect |
| :- | :- | :- |
| `--runs <n>` | Each case's `runs`, else 3 | Runs per case per arm |
| `-j`, `--concurrency <n>` | `1` | Run up to this many agent runs at once, from 1 to 8. They share your account's rate limit, so this shortens wall-clock time rather than raising throughput past that limit. Results keep case order |
| `--model <model>` | Each case's `model`, else `ANTHROPIC_MODEL` if set, else Claude Code's default | Model for the agent under test. Pin it in CI so a model rollout isn't mistaken for a plugin regression |
| `--judge-model <model>` | The model for [background tasks](#choose-and-weight-graders) | Model for `llm` and `baseline` graders |
| `--ablation <mode>` | Decided per case; see [Score against the no-plugin baseline](#score-against-the-no-plugin-baseline) | Whether to also run each case without the plugin to measure what it adds. `none` runs one arm; `with-without` adds the no-plugin baseline |
| `--threshold <0..1>` | `1.0` | A case passes when its with-arm score is at least this. Any case below it makes the command exit 1 |
| `--max-cost-usd <usd>` | No ceiling | A ceiling on the run's list-price cost estimate, not on plan usage. Checked before each run starts. Once spent, nothing further starts; runs that already started finish, so spend can pass the ceiling by those runs. If any run is left unstarted, the command exits 2 with partial results |
| `--allow-tools <tools...>` | None | Grant tools beyond the read-only set. See [Grant tools](#grant-tools) |
| `--scaffold` | Off | Run each case's [`scaffold_script`](#seed-the-workspace-or-conversation) |
| `--trust-plugin` | Off | Skip the first-run trust prompt for a plugin whose code and suite you'd run yourself. Pass it in CI so the job is never refused by or left waiting at the prompt. See [What a run can access](#what-a-run-can-access) |
| `--mocks <mode>` | `record` | `record` answers MCP tool calls from [mocks](#mock-mcp-servers), doesn't start the plugin's real servers, and saves agent-mock answers for replay. `off` ignores mocks and starts the plugin's real MCP servers |
| `--allow-real-servers` | Off | With `--mocks record`, also start the plugin's real MCP servers for servers that have no mock |
| `--json [path]` | Off | Print the [result document](#json-result) to stdout, or write it to a path ending in `.json`. The run is quiet: no progress lines or summary table |
| `--output-dir <dir>` | `<eval dir>/results/<timestamp>/` | Where `aggregate-result.json` and `report.html` go |
| `--no-publish` | | Keep the HTML report local. See [HTML report](#html-report) |
| `--publish-report` | | Publish the report even where it would stay local by default, such as a run a Claude Code session started |
| `--keep-temp` | Off | Keep every run's sandbox directory and print its path, for debugging what Claude produced |

### Run evals in CI

In the CI job, run the suite with `--json` to write the result for archiving, and fail the build on the exit code. Pass `--trust-plugin` so the job never waits at the [first-run trust prompt](#trust-the-plugin-directory), pin both models so scores are comparable over time, keep the report local, and set a cost ceiling as an upper limit:

```bash theme={null}
claude plugin eval . \
  --trust-plugin \
  --json results.json \
  --threshold 0.8 \
  --model claude-sonnet-5 \
  --judge-model claude-haiku-4-5 \
  --no-publish \
  --max-cost-usd 20
```

Read the job's exit code to see what happened:

| Exit code | Meaning |
| :- | :- |
| 0 | The suite passed: every case scored at or above `--threshold` and nothing else failed the run |
| 1 | A case scored below the threshold, a case file failed to load, no cases were found, a run couldn't be started, or a run [ended on an API error](#ended-on-an-api-error-and-scored-0-without-grading). Also returned when the plugin directory isn't trusted and `--trust-plugin` wasn't passed, an option was invalid, or the `--json` result couldn't be written |
| 2 | Partial run: the `--max-cost-usd` ceiling was hit, or your credential was rejected before or at the first run. `results.json` is still written with `partial: true` and the reason |
| 130 | Interrupted. Partial results are written |
| 143 | Terminated, such as by a CI timeout |

The with-minus-without delta is reported but never changes the exit code, and neither do problems writing or publishing the HTML report.

To see why a case scored low, run it locally without `--json` so the per-run progress and grader lines print.

A CI runner also needs these in place:

* **Install and credentials**: a Claude Code install and [credentials in the environment](https://code.claude.com/docs/en/authentication.md), such as `ANTHROPIC_API_KEY` or the cloud provider's variables.
* **Trust**: without `--trust-plugin`, a job whose checkout directory Claude Code does not already trust needs the [first-run trust prompt](#trust-the-plugin-directory), and a run that cannot ask is refused with exit 1.
* **`init` in CI**: `claude plugin eval init` needs a terminal to ask its questions. In CI, run `claude plugin eval init --bare <name>` to get the blank template.

To keep costs predictable, give quick every-change suites only graders that do not call a judge, use `--ablation none` where `Δ` is not needed, and leave `partial: true` documents and runs with `skippedPaidGraders` out of any charted trend.

## Read the results

Every run with at least one case writes a `results/<timestamp>/` directory inside the eval directory, containing `aggregate-result.json` and `report.html`. For a path target, that directory is under the plugin; for a plugin given by name, it is under the current directory, as the [target table](#choose-what-to-evaluate) shows. The summary table, the JSON, and the report all render the same result data.

### HTML report

`report.html` is a single self-contained file that makes no external requests, so it can be attached to a CI job or opened from disk. This example is the top of a report for a three-case suite run with `--threshold 0.8`; the cost shown is a list-price estimate and varies with the model and the number of cases:

![Top of an eval report: a verdict line reading "Plugin effect: +33.3 pts vs baseline, improved 2, flat 1, regressed 0 of 3 cases", five summary tiles for suite score, ablation delta, baseline score, cases passing the threshold, and perfect runs, then the first case with its delta, score bar, and one run whose two graders both show pass](https://mintcdn.com/claude-code/qq7LHDi_F0aeFHgk/images/plugin-eval-report.png?fit=max\&auto=format\&n=qq7LHDi_F0aeFHgk\&q=85\&s=106eb6e6a70a6565f891ea3a4564f87d)

> **View the image** [`assets/plugin-eval-report.png`](../../assets/plugin-eval-report.png) **to** see how an eval report lays out its verdict line, summary tiles, and per-case results.

Read the report from the top down:

* **The verdict line and tiles** answer whether the plugin helped across the whole suite. Suite score is the mean of the per-case with-plugin scores, Ablation Δ is how far that is above or below the baseline score, and Cases counts how many met the threshold. Perfect runs is the share of with-plugin runs where every grader passed.
* **Each case card** shows the case's own `Δ` and with-plugin score, with a tick on the bar at the threshold. A case whose `Δ` is negative gets a red left edge, so regressions stand out while scrolling.
* **Inside a case**, the with-plugin runs come first and the baseline runs after. Each run lists its graders with a pass or fail chip. A failed grader is already expanded with its explanation, and an `llm` grader also shows the judge's votes and the evidence it was shown; look there to find out why a run scored low. Graders that do not count toward the score, such as `tool_used: Skill`, carry a `plugin-fired indicator` badge.
* **Prompt and Graders**, below the runs, show the case's prompt and each grader's rubric or pattern, so a reader without the suite can see what was asked and what counted as good.

When the user is signed in with a claude.ai subscription and [artifacts](https://code.claude.com/docs/en/artifacts.md) are available for the account, Claude Code also publishes the report as a private artifact and prints `Published: <url>`. Pass `--no-publish` to keep it local. When no `Published:` line appears, such as with API-key authentication, the local file is the report.

A run that a Claude Code session started, such as when Claude runs the suite at the user's request, also stays local, and its `Report:` line says `kept local`. Add `--publish-report` to that command to publish it.

### JSON result

`aggregate-result.json`, and `--json` output, is a versioned document with `schemaVersion: 1` for CI scripts to parse. Field names are camelCase and new fields are added without renaming existing ones, so write any parsing script to ignore fields it does not recognize.

These are the fields a gating script usually reads. The document also carries the suite configuration, every grader definition, and per-run grader results with explanations and evidence:

| Field | Meaning |
| :- | :- |
| `partial`, `partialReason` | `true` with `cost_ceiling`, `interrupted`, or `auth_failed` when the suite didn't finish. Leave partial results out of trend charts |
| `aggregates.overallScore` | Mean case score across the suite |
| `aggregates.casesPassed`, `aggregates.casesTotal` | Cases at or above `--threshold`, and the total |
| `aggregates.meanDelta` | Mean `Δ` across cases, under the two-arm mode |
| `cases[].name` | Case name |
| `cases[].aggregates.score` | Mean with-arm run score for the case |
| `cases[].aggregates.delta` | With-arm score minus without-arm score. Omitted when the case ran one arm or the arms aren't comparable |
| `cases[].arms.with[].error` | `null`, or why a run ended abnormally, such as `timed out after 300s`. Some of these runs are still graded on what they produced, so a non-null error doesn't imply score 0. A run that [ended on an API error](#ended-on-an-api-error-and-scored-0-without-grading) scores 0 without grading |
| `cases[].arms.with[].aborted` | Present when a [mock](#mock-mcp-servers) stopped the run through `expect:`, `abort_when`, or the [agent-mock call budget](#mock-call-budget-exceeded), with `server`, `tool`, and `reason`. The run scores 0 and `error` stays `null` |
| `cases[].arms.with[].skippedPaidGraders` | `true` when the cost ceiling skipped this run's judge graders, so its score isn't comparable |
| `costUsd`, `durationSeconds`, `claudeVersion` | Estimated cost at list price including judge calls, wall-clock seconds, and the Claude Code version that ran the suite |

## What a run can access

`claude plugin eval` loads the target plugin's skills, hooks, and agents and runs its eval suite on the local machine, as the invoking user. Pointing it at a plugin is the same trust decision as `claude --plugin-dir`, so evaluate only trusted plugins.

The isolation described in this section limits what the agent under test can reach. It is not a boundary against the plugin's own code, and a passing suite says nothing about whether the plugin is safe.

### Trust the plugin directory

The first time `claude plugin eval` runs against a directory, Claude Code asks `Trust this plugin directory?` before it loads anything from it, unless the trust prompt there was already accepted in an interactive `claude` session. Inside a git repository, answering yes trusts the whole repository, for interactive sessions too. When stdin or stdout is not a terminal, or under `--json`, the run cannot ask and is refused with exit 1. Pass `--trust-plugin` to assert the trust explicitly, and only for a plugin the user would run on their own machine. A target given by name rather than as a path, meaning an installed plugin or a skills-directory plugin, skips the prompt.

Some parts of the plugin and suite run only when their flag is passed for that run:

* A case's [`scaffold_script`](#seed-the-workspace-or-conversation) with `--scaffold`
* [Tools beyond the read-only set](#grant-tools) with `--allow-tools`
* The plugin's [real MCP servers](#mock-mcp-servers) with `--allow-real-servers` or `--mocks off`

A case's `allowed_tools` and a skill's own `allowed-tools` frontmatter cannot widen any of them.

When the plugin includes hooks the user did not write, or its real MCP servers are started, treat its scores as advisory unless it ran in an isolated environment such as a container or CI runner, since hooks and servers run outside the agent's sandbox and could modify the files the graders read.

### How runs are isolated

Each run gets a temporary home directory, working directory, and Claude Code configuration, and the agent under test runs there as a `claude -p` child process with only the plugin under test loaded. Account for these consequences when writing cases:

* **Nothing personal or project-level loads.** The user's settings, hooks, `CLAUDE.md` files, MCP servers, other installed plugins, memory, and skills are absent. Project-scoped configuration is not read anywhere either: no `.claude/` directory, `CLAUDE.md`, or `.mcp.json` loads from above the workspace or inside it, even one a `scaffold_script` wrote, and `add_dirs` directories grant read access only. Most of the shell environment is withheld too; only an [allowlist](#promptmd-frontmatter) and `EVAL_*` variables reach the run. Ship any skills, agents, hooks, or MCP servers a case depends on in the plugin under test, since a [`scaffold_script`](#seed-the-workspace-or-conversation) can supply only files and git state.
* **Managed policy can still restrict a run.** Restrictions in [managed settings](https://code.claude.com/docs/en/managed-settings.md) that an administrator deployed to the machine apply inside a run, so results on a managed machine can differ from an unmanaged one by that policy.
* **The Artifact tool is off.** A skill that publishes an [artifact](https://code.claude.com/docs/en/artifacts.md) can be graded only on what it produces before that step.
* **The case definitions are hidden from the agent.** A run cannot read the eval directory, so Claude cannot see the case's prompt, its graders, or sibling cases.
* **No network sandbox outside shell commands.** Granted shell commands run under the sandbox's network rules. A `WebFetch(domain:…)` grant reaches that domain directly, and the plugin's own hooks and any real MCP servers that are started can reach any host.

## Eval suite reference

Everything an eval suite can contain lives under the plugin's eval directory, `evals/` unless [another one is configured](#use-a-different-eval-directory). A directory counts as a case when it holds a `prompt.md` or a `case.yaml`, and a case without at least one grader fails to load with an `invalid case.yaml` error that names `graders`. This tree shows every file `claude plugin eval` reads or writes in the eval directory:

```text theme={null}
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

`prompt.md` frontmatter accepts these fields. An unknown key is an error:

| Field | Default | Purpose |
| :- | :- | :- |
| `schema_version` | `"1.1"`, set for you | Case format version. Cases written as `prompt.md` get it automatically, so you rarely set it |
| `name` | The directory name | Case name. `--case` globs match it and the report keys on it |
| `description` | | For humans. Not used at run time |
| `tags` | `[]` | Labels for `--tag` filtering. A case runs if any of its tags matches |
| `plugins` | The nearest enclosing plugin | Plugin directories under test, relative to the case directory. Set `plugins: ["../.."]` when auto-detection doesn't find your plugin; see [the plugin didn't load](#the-baseline-arm-shows-no-plugin-or-delta-is-zero) |
| `runs` | `3` | Runs per arm, 1 to 50. `--runs` overrides it |
| `expected_outcome` | | For humans. Not used at run time |
| `model` | The child session's default | Model for the agent under test. `--model` overrides it |
| `max_turns` | `10` | Turn cap, up to 200. Hitting it is recorded as a run error and usually lowers the score, so set it generously |
| `timeout_seconds` | `300` | Wall-clock cap per run, up to 3600 |
| `allowed_tools` | `[]` | Tools the case wants, such as `[Read, Glob, Grep, Skill]`. Read-only tools are granted when listed here; for anything else, see [Grant tools](#grant-tools) |
| `append_system_prompt` | | Text appended to the child session's system prompt |
| `env` | `{}` | Extra environment variables for the child session. Keys must match `EVAL_[A-Z0-9_]*`; any other key fails the run. The run inherits only an allowlist from your shell: basics such as `PATH` and locale, proxy and certificate settings, the variables that select and authenticate your model provider, most `ANTHROPIC_*` and `CLAUDE_CODE_*` configuration, and `EVAL_*`. To pass the plugin anything else, such as a toolchain setting, export it as an `EVAL_*` variable |

### case.yaml fields

`case.yaml` is an alternative or companion to `prompt.md`: it describes a case in YAML and adds the fields that point at other files. It requires `schema_version: "1.1"` and `name`. The `prompt.md` fields `description`, `tags`, `plugins`, `runs`, and `expected_outcome` go at the top level; `model`, `max_turns`, `timeout_seconds`, `allowed_tools`, `append_system_prompt`, and `env` go under `execution:`. When both files exist, `prompt.md` frontmatter overrides the matching `case.yaml` fields, the `prompt.md` body is the prompt, and `graders/*.md` are added after any graders listed in `case.yaml`.

These fields exist only in `case.yaml`:

| Field | Purpose |
| :- | :- |
| `context.scaffold_script` | A Bash script in the case directory that runs in the empty workspace before Claude starts, to create fixture files or a git repository. It runs only when you pass [`--scaffold`](#seed-the-workspace-or-conversation), with a minimal environment and a 120-second limit, and a non-zero exit fails the run |
| `context.history_file` | A `.jsonl` transcript in the case directory to resume. The case's prompt becomes the next user turn |
| `context.add_dirs` | Directories inside the case directory that Claude may read during the run, granted read-only |
| `execution.prompt` | The prompt, when you keep the whole case in `case.yaml` and omit `prompt.md` |
| `graders` | A list of graders, each with a `name` plus the same keys a `graders/*.md` file takes in frontmatter. For `llm` graders, put the rubric in `criteria` |

### Grader frontmatter

Every grader file under `graders/` takes these keys in frontmatter, plus the options for its type. The grader's name is the filename without `.md`:

| Key | Default | Purpose |
| :- | :- | :- |
| `type` | required | One of the [grader types](#grader-types) |
| `weight` | `1` | Relative weight in the run's score. Any positive number |
| `arm` | unset | `with-only` excludes the grader from scoring in a [two-arm run](#score-against-the-no-plugin-baseline); `both` forces a grader Claude Code would otherwise exclude to be scored in both arms |

#### What a grader can look at

`regex` graders take a `target` and `llm` graders take a `focus`. Both accept the same values:

| Value | What the grader sees |
| :- | :- |
| `last_message` | Claude's final response text. This is the default |
| `trace` | The session as JSON, one message per line. A `regex` grader sees every message; an `llm` judge sees the first 12 and the last 12. Quotes and newlines inside it are JSON-escaped, so a regex matches `\"` rather than `"` |
| `files` | The list of paths Claude created during the run, one per line. Not their contents, and not files that a scaffold created or that Claude only modified |
| `{ source: file, path: <path> }` | The contents of one file in the workspace after the run. Use this to grade what the plugin produced. A PNG, JPEG, GIF, or WebP file is shown to an `llm` judge as an image. An `llm` judge refuses other binary files such as `.pptx` or PDF; render them to an image or write them out as text and grade that |
| `mock_calls` | Each call Claude made to a [mocked MCP tool](#mock-mcp-servers), with its input and the mock's answer |

#### Grader types

Each grader type below lists its options and when it passes:

| Type | Options | Passes when |
| :- | :- | :- |
| `regex` | `pattern`, `flags`, `match`, `target` | The JavaScript regex `pattern` is found in the target. Set `match: not_contains` to require absence or `match: "count:N"` to require exactly N matches. Put case-insensitivity in `flags: i`; inline `(?i)` isn't supported |
| `tool_used` | `tool`, `input_match`, `min`, `max` | The number of calls to `tool` whose JSON-encoded input matches the optional `input_match` regex is between `min`, default 1, and `max`, default unlimited. To assert a tool was never called, set both `min: 0` and `max: 0` |
| `tool_order` | `before`, `after` | Both tools were called and the first matching `before` call precedes the first matching `after` call. Each is a tool name or `{ tool, input_match }` |
| `file_exists` | `path`, `exists` | A file Claude created matches the `path` glob, or none does with `exists: false`. Only files created during the run count |
| `llm` | `criteria`, `focus` | A judge model votes PASS on the rubric in at least two of three votes. In the `.md` layout the file body is the criteria |
| `baseline` | `baseline_file`, `criteria` | A judge finds the run satisfies the criteria at least as well as the reference transcript at `baseline_file`, a `.jsonl` in the case directory |

### Mock files

A `<tool>.md` file under `mocks/<server>/` answers one tool. Its body is the tool result, with `{{input.<field>}}` and `{{file:fixtures/<name>}}` substitutions. Its frontmatter accepts these keys:

| Key | Default | Purpose |
| :- | :- | :- |
| `type` | `fixed` | `fixed` returns the body as written. `agent` treats the body as instructions for the [judge model](#command-options), which acts as the server for the run and sees earlier calls as history |
| `expect` | unset | A map from dotted input paths to a type name such as `string`, `number`, `boolean`, `array`, or `object`, a [`/regex/`](#regex-patterns-in-expect), a literal, or a list of allowed literals. A call that violates it aborts the run with score 0 and is reported as `aborted` with the server, tool, and reason |
| `error` | `false` | `fixed` only. Return the body as a tool error |
| `abort_when` | unset | `agent` only. Prose listing the only conditions under which the agent may abort the run |

Two optional files sit beside the tool files in a server's directory:

* **`_server.md`**: a single `type: agent` mock that answers several tools, listed in its `tools:` frontmatter key. A `<tool>.md` for the same tool takes precedence. An `expect:` guard here is a load error unless `tools:` lists a single tool, so put the guard on the individual `<tool>.md` instead
* **`_tools.json`**: a saved `tools/list` response from the real server, so mocked tools carry their real descriptions and input schemas instead of a permissive placeholder

A case's own `mocks/` directory uses the same layout and overrides the suite's mocks file by file.

#### Regex patterns in expect

A `/regex/` value in `expect:` uses a small dialect that Claude Code checks when it loads the suite:

* Literal characters, `.`, escapes such as `\d`, and character classes such as `[a-z]`
* The quantifiers `*`, `+`, `?`, and the `{m,n}` forms, each on a single character, escape, or class
* An optional `^` at the start and `$` at the end
* The flags `i` and `s` only

A pattern outside the dialect, such as one with a group, alternation, a backreference, lookaround, or another flag, stops the case from loading: the case scores 0 and its error names the pattern. To allow several exact values, write a list of literals instead of an alternation.

Each pattern checks values only up to a maximum length, and a longer value counts as a violation. Quantifiers can lower that length, and a leading `^` raises it, so anchor patterns with `^` and keep quantifiers few.

## Troubleshooting

These are the most common problems, keyed on the symptom or the exact message shown.

### "plugin eval is currently in early access"

The build predates general availability of the command. Run `claude update`, then run the command again in a fresh session.

### "plugin eval is currently unavailable"

Anthropic has switched the command off server-side. Nothing on the local machine turns it back on; run `claude update` and try again later in a fresh session.

### "is not a trusted plugin directory, and this run cannot stop to ask you about it"

This is the first run against a directory Claude Code does not trust yet, and it cannot ask because stdin or stdout is not a terminal or `--json` was passed. Run `claude plugin eval <dir>` once in a terminal and answer the prompt, or pass `--trust-plugin` when the plugin's code and suite are trusted. See [What a run can access](#what-a-run-can-access).

### "is too old for claude plugin eval"

The `git` on `PATH` is older than 2.31, so `claude plugin eval` stopped before running any case and exited 1 with a message naming the installed version:

```text theme={null}
git 2.30 is too old for claude plugin eval: it ignores the environment configuration (GIT_CONFIG_COUNT, added in git 2.31) that switches off the repository's git hooks and helper programs for the run. Install git 2.31 or newer.
```

For each run, Claude Code switches off git hooks, credential helpers, and other programs a repository's git configuration can start. It does so through environment configuration that git reads only from version 2.31. An older git ignores that configuration, so the suite stops rather than scoring runs where those programs could execute. Install git 2.31 or later and run the suite again.

Before v2.1.283, `claude plugin eval` did not check the git version, and on an older git the suite ran with those programs left on.

### "cannot be evaluated where sessions load it"

`claude plugin eval` was run in the shell with the name of a plugin installed from a marketplace [added from a local path](https://code.claude.com/docs/en/plugins/loading.md#in-place-and-copied-plugins). No session could load the plugin from that marketplace now, so the command refuses with this message and exits with code 1.

```text theme={null}
Error: formatter@my-marketplace cannot be evaluated where sessions load it: no session could load it now. Its marketplace is a folder whose catalog could not be read, or lists it no more. Check the marketplace with `claude plugin marketplace list`, or pass ./<dir> to evaluate a directory.
```

The sentence after `no session could load it now.` names what failed.

Run `claude plugin marketplace list` in the shell and fix what the message names. For example, restore the marketplace directory or put the plugin's entry back in its catalog. To evaluate the plugin's source without the marketplace, pass its directory as the target, such as `claude plugin eval ./plugins/formatter`.

### "No eval cases found"

No `<case>/prompt.md` or `<case>/case.yaml` exists beneath the eval directory in effect, or the `--case` and `--tag` filters matched no case. Run from the plugin root, or run `claude plugin eval init` to create a suite.

### The baseline arm shows no plugin, or delta is zero

When the summary has no `W/OUT` column, or a case fails with "ablation requested but no plugin resolved", the usual cause is that no plugin was found for the case. When every case resumes a transcript through `context.history_file`, the missing column is expected instead, because those cases run [one arm by default](#score-against-the-no-plugin-baseline). Otherwise, add `plugins: ["../.."]` to the case, giving the path from the case directory to the plugin directory.

When the plugin did load and `Δ` is still near zero with the `tool_used: Skill` grader failing, that is usually a real finding: the skill's `description` does not trigger on the prompt's phrasing. Adjust the description and re-run the same suite.

### "Agent type '...' not found" for one of the plugin's agents

By default each case runs both with the plugin and without it, and the runs without it are the [no-plugin baseline](#the-no-plugin-baseline). When Claude dispatches one of the plugin's agents in a baseline run, the Agent tool call fails with `Agent type '<plugin>:<agent-name>' not found. Available agents: ...`. The list names only agents that exist without the plugin, such as the [built-in subagents](https://code.claude.com/docs/en/sub-agents.md#built-in-subagents).

The error is expected, since `Δ` compares the plugin's runs against the baseline. In the JSON result, the baseline runs are under `cases[].arms.without`.

In runs with the plugin loaded, a case that lists `Agent` in `allowed_tools` can dispatch one of the plugin's agents by its namespaced name, such as `my-plugin:code-reviewer` for the `code-reviewer` agent in a plugin named `my-plugin`. To skip the baseline runs, pass `--ablation none`.

### Everything scores zero although the right files were produced

The graders target `files`, the list of created paths, when the intent was the file's contents. Use `{ source: file, path: <path> }` as the `target` or `focus`.

Separately, `file_exists` counts only files created during the run, so a file the scaffold created or that Claude only edited is invisible to it. Grade its contents, or use `tool_used` on `Edit`.

### A regex over the trace doesn't match visible text

* **Wrong target**: the default `target` is `last_message`, not the trace.
* **JSON escaping**: when the grader does target `trace`, it is JSON per line, so quotes appear as `\"`.
* **Regex syntax**: regexes use JavaScript syntax, so put `i` in `flags` rather than writing `(?i)`.

### Tools are denied, MCP tools are missing, or Bash won't run

Anything beyond the read-only set needs an explicit grant, such as `--allow-tools Bash Write`. The user's personal MCP servers never load in a run. The plugin's own servers do not start without an [opt-in](#mock-mcp-servers), and their tools then also need an `--allow-tools "mcp__plugin_<plugin>_<server>__*"` grant; a mocked tool needs neither.

### The run exits 1 but the results look fine

When every case scored at or above `--threshold` and the command still exits 1, a line on stderr names the cause, even under `--json`. For example, a case file failed to load, or runs [ended on an API error](#ended-on-an-api-error-and-scored-0-without-grading). For the other causes, see the [exit codes](#run-evals-in-ci).

The default `--threshold` is 1.0, so the command exits 1 when any case scores below perfect. Set a threshold that matches the required score.

### `--json output path must end in .json`

The target came after `--json`, so it was read as the output path. Put the target first, as in `claude plugin eval . --json`, or give `--json` an explicit `.json` path.

### A grader shows passed: false under a run that scored 1.0

That grader is excluded from the score by design in a two-arm run, and its `scored` field is `false`. See [Score against the no-plugin baseline](#score-against-the-no-plugin-baseline).

### "ended on an API error and scored 0 without grading"

This stderr warning means the API answered at least one run's last request with an HTTP error, such as a rate limit or a plan usage limit. Such a run scores 0 with no grader results, and the command exits non-zero whatever the scores and `--threshold` are.

To fix it, find each affected run's error and resolve the cause it reports, then run the suite again:

* **Without `--json`**: the error is at the end of the run's progress line, after `error:`
* **Under `--json`**: the error is in the [JSON result](#json-result), at `cases[].arms.with[].error` or `cases[].arms.without[].error`

The count includes [baseline](#the-no-plugin-baseline) runs too. Their scores never decide whether a case passes, so every case can pass while the command still fails. In a two-arm run, the affected case's `W/OUT` and `Δ` print as `—`. For a usage or rate limit, see [Runs fail with a usage-limit or rate-limit error](#runs-fail-with-a-usage-limit-or-rate-limit-error-partway-through).

Before v2.1.299, such a run was graded on what it had produced.

### Runs fail with a usage-limit or rate-limit error partway through

Runs that end with a usage-limit or rate-limit error [score 0 without grading](#ended-on-an-api-error-and-scored-0-without-grading), and the command exits non-zero. The suite still finishes and is not marked `partial`. Re-run after the limit resets, with `--runs 1` or a `--case` filter when the run must stay under the limit.

### "mock call budget exceeded"

Every `type: agent` [mock](#mock-mcp-servers) in a run draws on one call budget of four times the case's `max_turns`, which is 40 calls at the default of 10. Calls answered from `.replay/` recordings count too, and the case's `mock budget` progress line prints the budget. A call past it aborts the run with score 0 and this reason, so raise `max_turns` in the case for a skill that makes many calls to agent mocks.

### Runs time out or hit the turn cap

The defaults are 10 turns and 300 seconds. Raise `max_turns` and `timeout_seconds` in the case for tasks that need more, and use `--max-cost-usd` as the cost ceiling rather than tight per-run limits.

## Documentation References

- [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals): the source page of this file.
- [Plugins overview](https://code.claude.com/docs/en/plugins/overview.md): what a plugin is and what it contains.
- [Skills](https://code.claude.com/docs/en/skills.md): skill frontmatter, including the `description` that decides when Claude invokes a skill (what a skill-trigger case measures), and running evals with the skill-creator plugin.
- [Create a plugin](https://code.claude.com/docs/en/plugins/create.md): build the plugin under test, and load it with `--plugin-dir` during development.
- [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference.md): the `plugin eval`, `plugin eval init` and `plugin validate` command entries.
- [Plugins manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference): manifest fields, including the `experimental.evals` key.
- [Plugin loading](https://code.claude.com/docs/en/plugins/loading.md): skills-directory plugins shared through a repository, and in-place versus copied plugins.
- [Costs](https://code.claude.com/docs/en/costs.md): Claude Code costs, the page behind the list-price estimate that eval runs report.
- [Headless mode](https://code.claude.com/docs/en/headless.md): the non-interactive session each eval run uses.
- [Plugin components](https://code.claude.com/docs/en/plugins/components.md): a plugin's MCP server configuration, whose server names the mocks use.
- [Sandboxing](https://code.claude.com/docs/en/sandboxing.md): the OS-level sandbox that applies when Bash is granted to a run, and its prerequisites.
- [Authentication](https://code.claude.com/docs/en/authentication.md): credentials a CI runner needs in its environment.
- [Artifacts](https://code.claude.com/docs/en/artifacts.md): where published reports go, and why the Artifact tool is off in runs.
- [Managed settings](https://code.claude.com/docs/en/managed-settings.md): administrator policy that still applies inside a run.
- [Subagents](https://code.claude.com/docs/en/sub-agents.md): the built-in subagents available in a no-plugin baseline run.
- [Publish a plugin](https://code.claude.com/docs/en/plugins/publish.md): publish the plugin once its suite passes.
- [Measure plugin cost and usage](https://code.claude.com/docs/en/plugins/measure.md): what the plugin adds to each session's context and whether people still use it.
