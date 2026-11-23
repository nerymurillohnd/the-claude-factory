# Running evals and gating CI

How to create a suite with `claude plugin eval init`, run `claude plugin eval`, grant tools, keep the cost down and gate a CI job on the result.

## Contents

- [Gotchas](#gotchas)
- [Requirements](#requirements)
- [Create a suite](#create-a-suite)
- [Choose the target](#choose-the-target)
- [Tools and the sandbox](#tools-and-the-sandbox)
- [Isolation and trust](#isolation-and-trust)
- [Flags](#flags)
- [Cost](#cost)
- [Run in CI](#run-in-ci)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- Every run, every `llm` or `baseline` grader and the `init` interview are real model calls billed to the user's plan or API account. Get the user's yes, with the estimate below, before any of them.
- `eval` and `eval init` are shell commands with no `/plugin` form.
- Put the target first: `--tag`, `--allow-tools`, `--disallow-tools` and `--json` take the words after them, so a target after them is read as their value. Write `claude plugin eval . --json results.json`, never `--json .`.
- Never add `--trust-plugin`, `--scaffold`, `--allow-real-servers` or `--mocks off` on your own: the user's go-ahead must name the flag. `--trust-plugin` asserts that the user trusts the plugin's code and suite; the other three run code as the user, outside the sandbox. A request to set up CI is the go-ahead for `--trust-plugin` there, since CI can't answer the trust prompt: say so.
- A run is isolated: no user settings, hooks, `CLAUDE.md`, memory, other plugins or the user's MCP servers. Ship in the plugin everything a case relies on.
- The default `--threshold` is `1.0`, so one imperfect case exits 1, and Δ never changes the exit code.

## Requirements

- `claude plugin eval` and `eval init` need Claude Code with the command, and git 2.31 or later when git is installed: with an older git on `PATH` the command stops before any case and exits 1; without git it runs normally. Each run turns off git hooks, credential helpers and helper programs through `GIT_CONFIG_COUNT`, which only git 2.31 reads.
- The target needs a `plugin.json` or `.claude-plugin/plugin.json`, or is a skills-directory plugin.
- Runs use the same sign-in and provider as the user's sessions. On Bedrock, Google Cloud's Agent Platform or Microsoft Foundry, run from a shell that exports the same provider variables.
- `plugin eval is currently in early access`: the build predates general availability; run `claude update` and start a new session. `plugin eval is currently unavailable`: the feature is switched off on the server, and nothing local turns it back on.

## Create a suite

- From the plugin root, the folder with `.claude-plugin/plugin.json` or the skill's `SKILL.md`, run `claude plugin eval init`. An untrusted folder first asks `Trust this plugin directory?`, and that trust carries over to later `eval` runs.
- Run from inside a Claude Code session, the command prints the interview instructions for the session to follow instead of writing a template: run it, follow what it prints, and ask the user its questions in the conversation. In a terminal it opens an interactive session that reads the plugin, asks what it should do well, proposes cases and graders, runs them once as a trial and writes one case folder per prompt.
- The interview's trial runs are paid runs, so get the user's yes before you start it.
- `--bare <name>`, or a run with no terminal, writes a blank single-case template (`prompt.md` and `graders/criteria.md`) and runs nothing: use it to write or fix one case by hand, and in CI. The name starts with a letter or digit and holds only letters, digits, `.`, `_` and `-`; names Windows can't store, such as `con` or one ending in `.`, are refused on every platform.
- `-i` requires the interview and fails without a terminal. `--eval-dir <dir>` writes below the current folder.
- Write only the cases the plugin needs: a case that both arms pass proves nothing, so rewrite or drop it.

## Choose the target

| Target | What runs |
| :-- | :-- |
| A plugin folder, such as `.` (the default when omitted) | every case under its eval directory, with that plugin loaded |
| One `prompt.md` or `case.yaml` | that case, with its enclosing plugin |
| `<name>` or `<name>@<marketplace>` of an installed plugin | its cases, read in place or from the installed copy, the way sessions load it; results under `./evals/results/` in the current folder, or `./<dir>/results/` with `--eval-dir` |
| `<name>@skills-dir` | the same, for a skills-directory plugin |

Installed and skills-directory targets add the no-plugin baseline arm, and skip the trust prompt. A named plugin from a local-path marketplace that no session can load fails with `cannot be evaluated where sessions load it`: check `claude plugin marketplace list`, or pass the folder instead.

## Tools and the sandbox

- Runs never ask for permission. Built-in tools that aren't granted (`Bash`, `Write`, `Edit`, `WebFetch`, `WebSearch`) are removed, and a requested tool that isn't granted shows as `not granted` in the progress output.
- A case's `allowed_tools` grants only read-only tools: `Read`, `Glob`, `Grep`, `NotebookRead`, `Skill`, `AskUserQuestion`, `Agent`, `TodoWrite`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `TaskStop`.
- `--allow-tools` grants for every case, with permission-rule patterns: `--allow-tools Write Edit "Bash(npm test *)"`. Neither `allowed_tools` nor a skill's `allowed-tools` can widen it.
- Grants follow graders: a grader on a created file needs `Write` or `Edit`, a `tool_used` grader on a tool needs that tool, and a build or test needs a scoped `Bash(...)` grant.
- `--disallow-tools <tools...>` keeps built-in tools from Claude in every case, even when granted, such as `--disallow-tools Agent TaskStop`.
- Eval keeps its deny rules over a plugin's permission hook, and flags the calls such a hook let through.
- A `Bash` or `PowerShell` grant runs every command in the OS sandbox: writes stay in the workspace, the home folder and Claude Code's configuration are unreadable, and the network reaches only `WebFetch(domain:…)` grants. With no sandbox backend each such run is refused and usually scores 0: on Linux install `bubblewrap` and `socat`; on Windows run under WSL2.
- On a managed machine the refusal begins `A shell tool (Bash or PowerShell) was granted but this machine cannot confine it`, and when a managed `sandbox` key is the cause it ends with `this machine's managed settings:` and the key, such as `sandbox.enabled is false`. The progress line cuts it short: read it in the summary's `NOTES` column or the run's `error` under `--json`.
- Outside shell commands there is no network sandbox: `WebFetch(domain:…)` reaches the domain directly, and hooks and real servers reach any host.

## Isolation and trust

- Each run is a `claude -p` child with a temporary home, workspace and configuration and only the plugin under test. No `.claude/`, `CLAUDE.md` or `.mcp.json` loads from above or inside the workspace, even one a scaffold wrote. Managed settings still apply, the Artifact tool is off, and the run can't read the eval directory.
- Pointing `claude plugin eval` at a plugin is the same trust decision as `claude --plugin-dir`: it loads the plugin's skills, hooks and agents and runs its suite as the user. The first run against a folder asks `Trust this plugin directory?`, unless the user already accepted the trust prompt there in an interactive session; in a git repository a yes trusts the whole repository, for interactive sessions too. With no terminal on stdin or stdout, or with `--json`, an untrusted folder is refused with exit 1: `is not a trusted plugin directory, and this run cannot stop to ask you about it`.
- `--trust-plugin` skips that prompt and implies none of `--scaffold`, `--allow-tools` or `--mocks off`.
- Isolation is not a boundary against the plugin's own code, and a passing suite is not a security review. When the plugin ships hooks someone else wrote, or the run starts real servers, treat the scores as advisory outside a container or CI runner.

## Flags

| Flag | What it does |
| :-- | :-- |
| `--runs <n>` | runs per case per arm; default the case's `runs`, else 3 |
| `-j, --concurrency <n>` | up to `n` runs at once, 1 to 8, default 1; they share one rate limit, and results keep case order |
| `--case <glob>`, `--tag <tag...>` | filter cases by name, or by any matching tag |
| `--ablation none` | the with-arm only: no Δ, and nothing left out of the score |
| `--model <model>` | the model for every case; default the case's `model`, else `ANTHROPIC_MODEL`, else Claude Code's default |
| `--judge-model <model>` | the model for `llm` and `baseline` graders |
| `--threshold <0..1>` | exit 1 when any case scores below it; default `1.0` |
| `--max-cost-usd <usd>` | a list-price ceiling checked before each run starts; started runs finish, the rest are skipped with exit 2, and a run past it skips its paid graders while free graders still score it |
| `--json [path]` | the full result as JSON on stdout or in a `.json` file, with no progress or table; another extension fails with `--json output path must end in .json` |
| `--output-dir <dir>` | where `aggregate-result.json` and `report.html` go; default `<eval dir>/results/<timestamp>/`; an empty value is an error |
| `--report <path>` | write the HTML report to that path instead of the results folder |
| `--no-publish`, `--publish-report` | keep the HTML report local, or publish it even from a run a Claude Code session started, which stays local by default |
| `--keep-temp` | the page: keep every run's sandbox folder and print its path; `--help`: keep scaffold folders |
| `--verbose` | log per-message trace events to the debug log, read with `--debug-file` |
| `--scaffold`, `--no-scaffold` | run, or explicitly skip, each case's `scaffold_script`, which runs as the user outside the sandbox |
| `--mocks record`, `--mocks off`, `--allow-real-servers` | answer MCP calls from the suite's mocks and start no real server (the default); ignore the mocks and start every real server; with `record`, also start the real servers that have no mock |
| `--eval-dir <dir>` | the eval directory below the plugin |

## Cost

- Before a paid run, give the user the agent runs (cases × runs × arms), the judge calls (3 per `llm` or `baseline` grader per run) and the agent-mock calls (up to 4 × `max_turns` per run without a replay). After a one-case pilot, estimate the full run as its `costUsd` × cases × runs × arms. The reported cost is a list-price estimate, not plan usage.
- Pilot one case first: `claude plugin eval . --case <name> --runs 1 --ablation none`. Show the user its output and grades, and revise a rubric they would score differently. Confirm any change at the default three runs, with the baseline, before trusting it.
- Prefer free graders for suites that run on every change, use `--ablation none` when Δ isn't needed, and keep `partial: true` runs and runs with `skippedPaidGraders` out of score trends.

## Run in CI

The docs' command, with every pin inside it:

```bash
claude plugin eval . --trust-plugin --json results.json --threshold 0.8 \
  --model claude-sonnet-5 --judge-model claude-haiku-4-5 --no-publish --max-cost-usd 20
```

- Resolve the model IDs live before you pin them, from the user's current model list: these two are the docs' example.
- The runner needs Claude Code and credentials in the environment, such as `ANTHROPIC_API_KEY` or the provider's variables, referenced as secrets.
- Fail the job on the command's exit code: 0 passed, 1 a case below the threshold or another failure, 2 a partial run, 130 interrupted, 143 terminated. To see why a case scored low, rerun it locally without `--json`.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Create your first eval suite](https://code.claude.com/docs/en/plugin-evals#create-your-first-eval-suite) when you start a suite. It gives the interview and the quickstart.
- Read [Run evals](https://code.claude.com/docs/en/plugin-evals#run-evals) when a target, a grant or a flag is in question. It gives the targets, the grants and every command option.
- Read [What a run can access](https://code.claude.com/docs/en/plugin-evals#security) when isolation or trust decides the answer. It gives what a run sees and the trust prompt.
- Read [Run evals in CI](https://code.claude.com/docs/en/plugin-evals#run-evals-in-ci) when you write a CI job. It gives the command, the exit codes and the credentials.
- Read [plugin eval](https://code.claude.com/docs/en/plugins/cli-reference#plugin-eval) and [plugin eval init](https://code.claude.com/docs/en/plugins/cli-reference#plugin-eval-init) when a flag's syntax is in question. They give the usage lines; `claude plugin eval --help` on the user's machine wins for flags.

## Exit

The command is ready, with the target first and each flag the user approved, and the user said yes to its cost. Return to the step in `SKILL.md` that sent you here.
