# Eval policy: local pilot, full suite in CI

Sources: https://code.claude.com/docs/en/plugin-evals (read 2026-10-25), `claude plugin eval --help` on v2.1.310, every `plugin eval` entry of the changelog from v2.1.269 to v2.1.310. Requires Claude Code ≥ v2.1.269 (and git ≥ 2.31). Where the docs and `--help` differ, `--help` wins for flags and the changelog wins for behavior.

Contents: Who runs what · Pilot · Reading a pilot · Writing the suite · The CI template · CI audit checklist · Fork PRs · Flags worth knowing · Quick error map

## Who runs what

| | Local pilot | CI full suite |
| :- | :- | :- |
| Runs | 1 per case, one arm (`--runs 1 --ablation none`) | Case default (3), both arms, Δ reported |
| Which plugins | The one being worked on; narrow with `--case` | Only plugins that have `evals/` AND are new or edited |
| Purpose | Cases load, run and grade; rubric and tools are right | Score against `--threshold`, trigger rate, Δ vs no plugin |
| Spend | Small, announced first, user says yes | Capped by `--max-cost-usd`, approved when the workflow is added |

**New** = the plugin did not exist at the base commit. **Edited** = any file under the plugin directory changed (skills, hooks, manifest, the suite itself), ignoring `evals/results/`. Detection by `plugin.json` alone misses an edit that does not bump the manifest; [scripts/changed-eval-plugins.sh](../scripts/changed-eval-plugins.sh) uses the broader rule. A plugin with evals that nobody touched is skipped. A plugin without evals is never a target, and this skill never adds a suite unasked.

## Pilot

From the plugin root, target first, flags after:

```bash
claude plugin eval . --runs 1 --ablation none --no-publish
claude plugin eval . --case "<glob>" --runs 1 --ablation none --no-publish   # only the affected cases
```

Before running, tell the user: cases × 1 run × 1 arm = N agent runs, plus 3 judge votes per `llm`/`baseline` grader per run, plus agent-mock calls (up to 4 × `max_turns` per run) if the suite has `type: agent` mocks. Then wait for a yes. After the first pilot, estimate full cost as pilot cost × runs × 2 arms.

Gates that need a named go-ahead (they run code as the user, outside the sandbox, or call real services): `--trust-plugin`, `--scaffold`, `--allow-real-servers`, `--mocks off`. From inside an agent session stdin is not a terminal, so the first run in an untrusted directory is refused (`is not a trusted plugin directory, and this run cannot stop to ask you about it`). Either the user answers the prompt once in a terminal, or they approve `--trust-plugin` by name. Granting `Bash` forces the OS sandbox (`bubblewrap` + `socat` on Linux; WSL2 on Windows); with no backend each run is refused. The sandboxed Bash has been reported unable to write the run workspace when `TMPDIR` is under `/tmp` (anthropics/claude-code#104797, open): if every Bash-granting case fails on writes, check `TMPDIR` first. **Unverified:** whether a plugin under your home directory runs locally with Bash granted; this repository's CI copies the plugin out of `$HOME` for that reason.

Evaluating a plugin you did not write executes its code as the user: treat it as a trust decision, and do it from a throwaway config (`CLAUDE_CONFIG_DIR="$(mktemp -d)"`) with the plugin installed by `claude plugin install <plugin>@<marketplace>`, then `claude plugin eval <plugin>@<marketplace>`.

## Reading a pilot

Say what it proves and what it does not.

- It proves: the cases load (a case without a grader fails with `invalid case.yaml`), the tools granted are enough, graders return verdicts, the skill fired on the phrasing used.
- It does not prove: Δ over no plugin (no baseline arm), a stable score (one run is noisy; confirm any change at the default 3 runs), or that CI will pass.
- `tool_used: Skill` graders are `scored: false` in two-arm runs (CI) but count in a pilot, where nothing is excluded. The same suite can score differently in the two modes.
- `passed: false` under a run scoring 1.0 means an excluded grader; look at `scored`.
- Hitting `max_turns` or `timeout_seconds` is a run error. An API/rate-limit error scores 0 and exits non-zero (v2.1.295/299): check `cases[].arms.with[].error`, then re-run with `--runs 1` or a `--case` filter after the limit resets.
- Judge default is the background-task model (haiku per `--help` on v2.1.310). If `tool_used: Skill` passes but the result is marked wrong, suspect the judge: `--judge-model sonnet`, and tighten the rubric.

## Writing the suite

The facts a suite needs:

```text
evals/
├── <case>/
│   ├── prompt.md       # frontmatter: max_turns, timeout_seconds, allowed_tools, tags, runs...; body: the prompt
│   ├── case.yaml       # optional; needs schema_version: "1.1" (quoted) and name
│   └── graders/<name>.md   # frontmatter: type, weight, arm; body: rubric
└── results/            # written by runs; gitignore it
```

- Start with `claude plugin eval init` (interactive, from the plugin root) or `claude plugin eval init --bare <case>` (blank template; the only form that works in CI).
- Grader types: `regex` (JavaScript regex; `flags: i`, never `(?i)`; `match: not_contains`), `tool_used` (`tool`, `input_match`, `min`, `max`), `tool_order`, `file_exists`, `llm`, `baseline`. No custom-code graders. `target` and `focus` accept `last_message` (default), `trace`, `files` (paths only), `{ source: file, path: ... }`, `mock_calls`.
- Per case: one grader on the result, one on the steps. Prefer free graders.
- Trigger quality: at least four prompts in users' words that should fire the skill, without naming it, plus one or two near misses. Must-not-fire = `type: tool_used`, `tool: Skill`, `input_match` on the skill name, `min: 0`, `max: 0`, `arm: both`.
- Skill graders match `"skill"\s*:\s*"(?:[\w-]+:)?your-skill-name"` (namespaced form `plugin:skill` is accepted).
- Anything beyond the read-only tools (`Read, Glob, Grep, NotebookRead, Skill, AskUserQuestion, Agent, TodoWrite`, task tools) needs `--allow-tools`; otherwise the tool is removed and both arms score 0. A grader on a created file needs `Write`/`Edit`.
- Defaults: `max_turns` 10, `timeout_seconds` 300, `runs` 3. A one-shot answer needs about 5 turns; reading a repo and writing a report 25–40.
- Runs are isolated: no `CLAUDE.md`, settings, memory, other plugins, or personal MCP servers. Ship everything a case needs inside the plugin.
- An eval directory other than `evals/`: `"experimental": { "evals": "quality/evals" }` in `plugin.json`, or `--eval-dir` on both `init` and the run.

## The CI template

`../assets/evals-ci.yml` is the template of a workflow that runs the full suite in CI, only for plugins that have `evals/` and are new or edited. Use it only when the repository has no eval workflow; when it has one, audit that one with the checklist below instead.

1. Copy it to `.github/workflows/evals.yml`.
2. Point the `targets` job at the target-selection script. The template calls `bash scripts/changed-eval-plugins.sh`; set the path to where that script lives in the repository (this skill keeps it at `.claude/skills/testing-plugins/scripts/changed-eval-plugins.sh`). It takes the base and head commits, the plugins directory and the eval directory name.
3. Fill the three `TODO` values:
   - **TODO 1, models:** create the repository variables `EVAL_MODEL` and `EVAL_JUDGE_MODEL` with exact model ids, so a model rollout is not mistaken for a regression.
   - **TODO 2, cost:** set `MAX_COST_USD`, the ceiling per plugin per run; the user approves it, because it is what CI spends.
   - **TODO 3, Claude Code:** set `CLAUDE_CODE_VERSION` to an exact version, 2.1.269 or later (`plugin eval` needs it).
4. Add the secret `CLAUDE_CODE_OAUTH_TOKEN` (or switch the job to `ANTHROPIC_API_KEY`); the run step fails loudly when it is empty.
5. Keep the pinned action SHAs and `node-version-file`, and check them against their latest releases before you add the workflow. Keep `--threshold`, `--trust-plugin` and `--no-publish` unless the user decides otherwise.
6. Make sure `eval-results/` and `**/evals/results/` are git-ignored, then run the CI audit checklist below on the copy and `actionlint` on the file.

Adding the workflow spends CI money on every pull request that edits a plugin with evals: get the user's approval before you commit it, and never push it without theirs.

## CI audit checklist

Use on an existing workflow before changing it. Report each line as pass, fail or unknown, with the evidence.

1. Triggers on pull requests that touch the plugin directories (not only `plugin.json`) and offers a manual `workflow_dispatch` with a plugin input.
2. Target selection = has evals AND (new OR edited). Unedited plugins with evals are skipped. Checkout has full history (`fetch-depth: 0`), because the base commit must be present.
3. Nothing runs for plugins without evals.
4. The command is complete: `claude plugin eval <path>` target first, `--trust-plugin`, `--json <file>`, `--threshold`, pinned `--model` and `--judge-model`, `--no-publish`, `--max-cost-usd`.
5. Claude Code version is pinned (npm `@anthropic-ai/claude-code@<version>`, or `curl -fsSL https://claude.ai/install.sh | bash -s <version>`), and ≥ 2.1.269.
6. Credentials come from a secret (`CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY`); the job fails loudly when it is empty.
7. Fork PRs are handled (below).
8. Results are uploaded as an artifact; `evals/results/` is gitignored.
9. Exit codes: 0 pass; 1 below threshold, load failure, no cases, API error, or untrusted dir; 2 partial (cost ceiling hit or credential rejected); 130/143 interrupted/terminated. Δ never changes the exit code, so the threshold carries the gate.

Per-plugin tool grants and cost ceilings differ, so a config file keyed by plugin (as some repos keep) is better than one global grant. A global grant of `Bash` forces the sandbox on every plugin.

## Fork PRs

Public repos: GitHub does not give secrets to workflows triggered by `pull_request` from a fork, so the suite cannot run there. Do not switch to `pull_request_target` and check out the fork's code with secrets available: the plugin under test runs as the CI user. Instead, skip with a visible warning and let a maintainer review the code and start the run through `workflow_dispatch` ([assets/evals-ci.yml](../assets/evals-ci.yml) does this in its `fork-notice` job).

## Flags worth knowing

`--runs`, `-j/--concurrency` (1–8, shares one rate limit), `--ablation none|with-without`, `--case <glob>`, `--tag`, `--threshold` (default 1.0, so one imperfect case exits 1), `--max-cost-usd`, `--allow-tools`, `--disallow-tools` (v2.1.299; also a `disallowed_tools` case field; missing from the docs page), `--model`, `--judge-model`, `--json [path]` (must end in `.json`; quiet run), `--report`, `--output-dir`, `--eval-dir`, `--keep-temp`, `--no-publish`, `--publish-report`, `--mocks record|off`, `--scaffold`, `--no-scaffold`, `--trust-plugin`. Put the target before `--tag`, `--allow-tools`, `--disallow-tools` and `--json`: they consume the words that follow.

## Quick error map

| Message | Meaning and fix |
| :- | :- |
| `plugin eval is currently in early access` / `currently unavailable` | `claude update`, retry in a fresh session; unavailable = switched off server-side. |
| `is too old for claude plugin eval` | git < 2.31. Install a newer git. |
| `No eval cases found` | Run from the plugin root, or filters matched nothing. |
| Baseline arm shows no plugin / `ablation requested but no plugin resolved` | Add `plugins: ["../.."]` to the case (path from the case dir to the plugin dir). |
| `cannot be evaluated where sessions load it` | Name target for a plugin from a local-path marketplace: out of scope; pass `./<dir>` instead. |
| Everything scores 0 though files exist | Grader targets `files` (paths only); use `{ source: file, path: ... }`. `file_exists` ignores files that were only edited. |
| Regex over `trace` never matches | Trace is JSON per line: quotes appear as `\"`. |
| `--json output path must end in .json` | Target was placed after `--json`. |
| `Agent type '<plugin>:<agent>' not found` in the without-arm | Expected in the baseline. |
| `mock call budget exceeded` | Raise `max_turns` (budget = 4 × `max_turns`). |
