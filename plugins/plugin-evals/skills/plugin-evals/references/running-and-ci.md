# Running evals and CI

Read this when you run a suite, iterate on a case, grant tools, choose models, cap cost or set up CI. Flags change between releases: check them against the live page and the changelog, and use `claude plugin eval --help` on the machine that runs the suite only to confirm a flag exists in that build.

## Contents

- Requirements
- Choose the target
- Everyday commands
- Options
- Granting tools and the sandbox
- Trust and isolation
- Cost
- CI recipe
- Exit codes

## Requirements

- **Claude Code v2.1.269 or later** (`claude --version`, `claude update`).
- **Git.** If git is installed it must be 2.31 or later; since v2.1.283, an older git is refused before any case runs. Without git, runs work. Each run switches off git hooks, credential helpers and other programs a repository's git config can start.
- **A plugin.** Either a directory with `plugin.json` or `.claude-plugin/plugin.json`, or a skills-directory plugin.
- **The same credentials and provider your normal sessions use.** Runs, judge graders and `claude plugin eval init` call the model on that account. On Amazon Bedrock, Google Cloud's Agent Platform or Microsoft Foundry, run the suite from a shell that exports the same provider variables as your normal sessions.
- **Messages before any run** (errors reference):
  - `plugin eval is currently in early access`: the build is older than v2.1.269. Update Claude Code.
  - `plugin eval is currently unavailable`: switched off server-side. Update and try later.

## Choose the target

| Target | What runs | Results go to |
| :-- | :-- | :-- |
| `.` or a plugin directory | Every case under its eval directory, with that plugin loaded | `<plugin>/<eval dir>/results/<timestamp>/` |
| A single `prompt.md` or `case.yaml` | That case, with its enclosing plugin | the same |
| An installed plugin by name, `name` or `name@marketplace` | Its own cases, read in place or from the installed copy | `./evals/results/` in your current directory, or `./<dir>/results/` with `--eval-dir` |
| `name@skills-dir` | The same, for a skills-directory plugin | the same |
| Omitted | The current directory | — |

- **Evaluating by name.** A marketplace added from a local path loads relative-path plugins in place, from the source folder. Other marketplace installs load a copy from the cache, and files outside the plugin directory aren't in that copy. If the command says `cannot be evaluated where sessions load it`, run `claude plugin marketplace list` and fix what the message names, or pass the plugin's directory as the target instead.
- **Run from the plugin root.** Per the plugin commands reference, `init` runs from the plugin's root folder, the one that holds `.claude-plugin/plugin.json` or the skill's `SKILL.md`; pass `--eval-dir` to scaffold the suite in another directory on purpose.
- **Filters.** `--case <glob>` filters by case name. `--tag <tag…>` keeps cases that have any of the tags.
- **Put the target first.** `--tag`, `--allow-tools` and `--json` consume the words after them. So does `--disallow-tools` (changelog v2.1.299; `--help` lists it as taking a list).

## Everyday commands

```bash
claude plugin eval init                                        # authoring interview (from the plugin root)
claude plugin eval init --bare first-case                      # blank prompt.md + graders/criteria.md
claude plugin eval . --case first-case --runs 1 --ablation none  # cheap iteration on one case
claude plugin eval .                                           # full suite: 3 runs × 2 arms per case
claude plugin eval . --case first-case --runs 1 --keep-temp    # keep the run folders to read the trace
```

- **`init` with a terminal** opens an interactive session that reads the plugin, asks what good looks like, proposes cases and graders, runs them once as a trial and writes the files. Exit it with `/exit` or Ctrl+D. It calls the model on the user's account.
- **`init` from a Claude Code session.** Claude runs the command, then asks the user the same questions in that conversation. The plugin commands reference says the command prints the interview instructions for that session to follow, rather than writing a template. Follow them.
- **`init` in CI.** It needs a terminal to ask its questions, so in CI run `claude plugin eval init --bare <name>` to get the blank template. The plugin commands reference adds that without a terminal the command writes that template for `<name>`, and that `-i`, `--interactive` fails instead.

## Options

| Option | Default | Effect |
| :-- | :-- | :-- |
| `--runs <n>` | the case's `runs`, else 3 | Runs per case per arm |
| `-j`, `--concurrency <n>` | 1 | 1–8 runs at once. They share one rate limit, so this saves wall-clock time, not throughput |
| `--model <model>` | the case's `model`, else `ANTHROPIC_MODEL`, else the default | Agent under test. Pin a full model ID in CI |
| `--judge-model <model>` | the model Claude Code uses for background tasks | `llm` and `baseline` graders, and `type: agent` mocks |
| `--ablation none \| with-without` | decided per case (see [case-format.md](case-format.md)) | `none` runs one arm; `with-without` adds the no-plugin baseline |
| `--threshold <0..1>` | 1.0 | Any case below it makes the command exit 1 |
| `--max-cost-usd <usd>` | none | A ceiling on the list-price estimate, checked before each run starts. Runs already in flight finish. Paid graders on a run past the ceiling are skipped (`skippedPaidGraders`). Unstarted runs mean exit 2 with partial results |
| `--allow-tools <tools…>` | none | Grants beyond the read-only set |
| `--disallow-tools <tools…>` | none | Keeps specific built-in tools, such as `Agent`, out of eval runs. From the changelog (v2.1.299); the page omits it |
| `--scaffold` | off | Run each case's `scaffold_script`. The page also lists `--no-scaffold` among the `--help` options, without describing it |
| `--trust-plugin` | off | Skip the first-run trust prompt. It doesn't imply `--scaffold`, `--allow-tools` or `--mocks off` |
| `--mocks record \| off` | record | See [fixtures-and-mocks.md](fixtures-and-mocks.md) |
| `--allow-real-servers` | off | Start real servers that have no mock |
| `--eval-dir <dir>` | the manifest's `experimental.evals`, else `evals` | — |
| `--json [path]` | off | Print the result to stdout, or write it to a path ending in `.json`. Quiet: no progress lines or table |
| `--output-dir <dir>` | `<eval dir>/results/<timestamp>/` | Where `aggregate-result.json` and `report.html` go |
| `--no-publish` | | Keep the HTML report local. See [results.md](results.md) |
| `--publish-report` | | Publish the report even where it would stay local by default, such as a run a Claude Code session started |
| `--keep-temp` | off | Keep every run's sandbox directory and print its path, for debugging what Claude produced |

The page also lists `--report` and `--verbose` among the `--help` options, without describing them.

## Granting tools and the sandbox

- **Runs never ask for permission.** Built-in tools that need a grant you didn't give, such as `Bash`, `Write`, `Edit`, `WebFetch` and `WebSearch`, are removed from the session.
- **Read-only tools.** A case gets the read-only tools it lists in `allowed_tools`. Everything else comes from `--allow-tools`, which applies to every case in the run. Neither `allowed_tools` nor a skill's own `allowed-tools` can widen it.
- **Grant syntax** follows the permission rules (permissions page):
  - `"Bash(npm test *)"`, where the space before `*` matters: `Bash(npm test*)` also matches `npm test-all`.
  - `"WebFetch(domain:example.com)"`, which covers that domain only; `*.example.com` covers subdomains, not the apex.
  - `"mcp__plugin_<plugin>_<server>__*"` for a real plugin server, together with `--allow-real-servers` or `--mocks off`.
  - A tool a case asked for that the command didn't grant is listed in the progress output as `not granted`.
- **Any form of a Bash grant runs every command in Claude Code's OS sandbox:**
  - Writes are confined to the run's workspace.
  - The home directory and the Claude Code configuration can't be read.
  - Network reaches only domains granted with `WebFetch(domain:…)`.
  - If you grant Bash or PowerShell on a machine with no sandbox backend, each run is refused instead of running unconfined; the case shows a run error and usually scores 0. By default an interactive session would instead run commands unsandboxed (sandboxing page).
- **Platforms** (sandboxing page):
  - macOS uses the built-in Seatbelt.
  - Linux needs `bubblewrap` and `socat` (`sudo apt-get install bubblewrap socat`).
  - On Ubuntu 24.04 and later, AppArmor can stop bubblewrap from creating user namespaces. Check `sysctl kernel.apparmor_restrict_unprivileged_userns`. If it is `1`, add the `bwrap` AppArmor profile from the [sandboxing docs](https://code.claude.com/docs/en/sandboxing.md) and reload AppArmor.
  - Native Windows has no backend, so run Bash-granting suites under WSL2.
- **Unprivileged containers.** Bubblewrap can fail with `Can't mount proc on /newroot/proc`. The sandboxing page's fix is the `sandbox.enableWeakerNestedSandbox` setting. Eval runs don't load your user or project settings, so confirm how that setting reaches a run on your setup before you rely on it.
- **What the sandbox doesn't cover.** WebFetch grants reach their domain directly, and the plugin's own hooks and any real MCP servers can reach any host.

## Trust and isolation

- **First run.** The first run against a directory asks `Trust this plugin directory?`, unless you already accepted trust there in an interactive session. Inside a git repository, yes trusts the whole repository.
- **No terminal.** Without a terminal, or with `--json`, the run can't ask and is refused with exit 1. Pass `--trust-plugin` only for code you would run yourself. Named targets skip the prompt.
- **Isolation.** Each run is a `claude -p` child with a temporary home, workspace and configuration, and only the plugin loaded.
  - **Absent:** user settings, hooks, `CLAUDE.md`, memory, your MCP servers, other plugins and skills.
  - **Project config:** never read, not even what a scaffold writes.
  - **Still applies:** managed settings.
  - **Off:** the Artifact tool.
  - **Hidden:** the case definitions.
  - **Environment:** only an allowlist of variables reaches the run, plus `EVAL_*`. The allowlist covers `PATH` and locale, proxy and certificate settings, provider selection and authentication, and most `ANTHROPIC_*` and `CLAUDE_CODE_*`. To pass anything else, export it as `EVAL_*`.
- **Isolation limits the agent under test, not the plugin.** A passing suite says nothing about the plugin's safety.

## Cost

- **What runs.** Calls are roughly cases × runs with the plugin, the same again for the baseline, and 3 short judge calls per `llm` or `baseline` grader per run. Agent mocks also call the judge model.
- **What's billed.** Everything counts against the user's plan usage or API bill. The printed `COST` and `costUsd` are list-price estimates, not invoices, and on a subscription the dollar figure isn't billing.
- **Keeping it predictable:**
  - Pilot one case with `--runs 1 --ablation none`.
  - Give fast every-change suites only free graders.
  - Use `--ablation none` when Δ isn't needed.
  - Set `--max-cost-usd`.
  - Leave `partial: true` and `skippedPaidGraders` runs out of any trend.
- **Estimate before asking.** After a one-case, one-arm pilot (`--runs 1 --ablation none`), the full suite costs about the pilot's `costUsd` × cases × runs × arms (2 with the baseline), plus agent-mock calls. State it and get a yes before running.

## CI recipe

```bash
# Install a pinned Claude Code (the setup page's native installer accepts a version)
curl -fsSL https://claude.ai/install.sh | bash -s <version>
# Linux runner, only for suites that grant Bash
sudo apt-get install -y bubblewrap socat

claude plugin eval . \
  --trust-plugin \
  --json results.json \
  --threshold 0.8 \
  --model <pinned agent model id> \
  --judge-model <pinned judge model id> \
  --no-publish \
  --max-cost-usd 20
```

- **Credentials** go in the job's environment. The authentication page ranks them in this order:
  1. Cloud provider variables (`CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY` with their own credentials).
  2. `ANTHROPIC_AUTH_TOKEN`.
  3. `ANTHROPIC_API_KEY`.
  4. `apiKeyHelper`.
  5. `CLAUDE_CODE_OAUTH_TOKEN`. Generate it with `claude setup-token`; it needs a Pro, Max, Ultra, Team or Enterprise plan and counts against that plan's usage.
- **Bare mode** (`claude --bare -p`, a separate command) doesn't read `CLAUDE_CODE_OAUTH_TOKEN` (authentication page). The plugin eval page documents no `--bare` option for runs, only `init --bare`.
- **Every flag above belongs in the command, not in a list of suggestions.** Pin both models with full IDs, so a model rollout isn't mistaken for a regression, and keep `--max-cost-usd` so a runaway suite stops. `--trust-plugin` is required because CI can't answer the trust prompt. The docs' CI example pins `claude-haiku-4-5` as the judge; when you suspect the judge of failing correct answers, re-run with `--judge-model sonnet` and tighten the rubric.
- **Keep CI on the exit code**, and archive `results.json` and the report even when the job fails (for example, an upload step with `if: always()`). To see why a case scored low, rerun it locally without `--json` so the per-run grader lines print.
- **Run on every change, cheaply.** Keep the suites that run on every change cheap as [Cost](#cost) describes, rather than running the suite only on releases.

## Exit codes

| Code | Meaning |
| :-- | :-- |
| 0 | The suite passed: every case met `--threshold` and nothing else failed the run |
| 1 | A case under the threshold, a case file that failed to load, no cases found, a run that couldn't start, an untrusted directory without `--trust-plugin`, an invalid option, a `--json` result that couldn't be written, or (since v2.1.299) a run that ended on an API error, which scores 0 without grading; baseline runs count too |
| 2 | Partial: the `--max-cost-usd` ceiling was hit, or the credential was rejected at or before the first run. The JSON has `partial: true` and the reason |
| 130 | Interrupted; partial results are written |
| 143 | Terminated, for example by a CI timeout |

Δ never changes the exit code, and neither does a failure to write or publish the report.
