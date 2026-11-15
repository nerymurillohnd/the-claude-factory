# Evals audit against the official documentation

## Scope and authority

- **Authority:** "Test plugins with evals", <https://code.claude.com/docs/en/plugin-evals.md>, downloaded 2026-11-15 (735 lines), plus the official changelog for Claude Code 2.1.319 to 2.1.325 and the pages it links (github-actions, authentication). Rule: the official documentation wins over every project file, ADR and rule. Where the changelog and the page disagree, the changelog wins.
- **Installed:** Claude Code 2.1.325 (latest release; no 2.1.324 exists), equal to `CLAUDE_CODE_VERSION` in `.github/actions/setup/action.yml`. git 2.43.0 locally, 2.56.1 on the runner.
- **Covered:** 161 files that mention evals, plus every eval suite (110 files): plugin-evals, plugin-test-bench, skill-diagnostics, plugin-engineering, hook-engineering, project-maintainer, `.github/`, `scripts/`, `.claude/`. Four read-only auditors, then the owner's session verified the disputed points. No eval was run.

## Findings corrected after verification

- **`disallowed_tools` and `--disallow-tools` are valid.** The page omits them, but the changelog for 2.1.299 says: "Added `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval`". Keep them, cite the changelog, and report the gap on the page to Anthropic.
- **The judge default:** the page says "the model Claude Code uses for background tasks"; `--help` names haiku. State the page's wording; the two need not conflict.
- **`plugins` list refusal:** the testing skill says naming the plugin under test in `plugins` is refused (observed earlier on 2.1.325). The page's remedy is `plugins: ["../.."]`. Follow the page; if a probe reproduces the refusal, report it to Anthropic.
- **`--max-cost-usd 0` as a load check:** not documented. It follows from "Checked before each run starts", but must be labeled as observed, not documented.

## 1. Defects that break or falsify results

1. **CI times out.** `.github/workflows/evals.yml:96` `timeout-minutes: 60`, no `--concurrency` (default 1). hook-engineering effort-high is 5 cases × 3 runs × 2 arms = 30 serial runs at up to 2400 s each; project-maintainer medium (18 × 600 s) and plugin-engineering low (48 × 180 s) can also exceed 60 min. Doc: `-j, --concurrency` 1 to 8; exit 143 on a CI timeout. Fix: per-plugin `--concurrency`, and `timeout-minutes` sized from runs ÷ concurrency × `timeout_seconds` (GitHub maximum 360).
2. **The Δ gate measures a plugin users don't get.** `plugins/hook-engineering/evals/_overlay/.mcp.json` and the staging in `evals.yml:149-173` add the Claude Code Docs MCP to the with-plugin arm only. Doc: runs have "only your plugin loaded", Δ "is what the plugin contributed", and "Ship any skills, agents, hooks, or MCP servers a case depends on in the plugin under test". Three graders score that server's calls. Fix: ship the server in `plugins/hook-engineering/.mcp.json`, or remove the overlay, its staging, `--allow-real-servers` and the `mcp__plugin_hook-engineering_claude-code-docs__*` grant. Supersede `ADR_2026-11-15_eval-overlays-add-files-to-the-with-plugin-arm-only` and drop `.claude/rules/plugins/evals.md:21`.
3. **project-maintainer's suite cannot pass.** `.github/evals.json` grants it only `--scaffold`; doc: ungranted `Write`, `Edit`, `Bash` "are removed from the session". So `tool: Write` graders (`decision-recorded/1-adr-written`, `adr-superseded/4-new-record-written`, `debt-obsolete/1-closed-entry-written`) always fail, the `min: 0 max: 0` graders on Write, Edit and Bash pass trivially, and `debt-obsolete` tops out at exactly 0.80. The case descriptions and `decision-recorded/8-honest-report` cite a "dontAsk mode" the eval page never mentions. Fix: grant `Write Edit Bash` for project-maintainer, and grade the attempted writes, not the files: the permission-modes page (<https://code.claude.com/docs/en/permission-modes#protected-paths>) lists `.claude` as a protected directory whose writes are prompted, and a run that can't prompt refuses them even when the tool is granted.
4. **Both gate scripts fail CI on ordinary run errors.** `scripts/checkers/eval_gate.py:8-9, 71-73, 117-119` and `plugins/plugin-engineering/skills/plugin-testing-and-debugging/scripts/gate_eval_result.py:15-17, 84-85, 154-155` treat any non-null `error` as "scores 0, not comparable" (exit 2). Doc: "a non-null error doesn't imply score 0"; a `max_turns` hit "is recorded as a run error"; API-error runs already make the CLI exit 1. Fix: not comparable only for `partial`, `aborted` and `skippedPaidGraders`; report other errors as warnings. Tests: `partialReason="cost ceiling"` must be `cost_ceiling` (`scripts/testers/checkers/test_eval_gate.py:66`, `plugins/plugin-engineering/tests/test_gate_eval_result.py:156`); add `interrupted`, `auth_failed`, timeout and `aborted` cases; `test_ci_evals.py` adds exits 1, 130, 143. Also check `schemaVersion: 1` (low).
5. **Trigger-only cases give Δ by construction.** All 8 plugin-engineering cases and `evals-loading/load-lint-on-edit` have a single `tool_used: Skill` grader; doc: "if every grader in a case is in the excluded set, they're scored normally", so W/OUT is 0 and Δ is +1 regardless of quality. Doc: "Give each case one grader on the result … and one on the steps", and "use `--ablation none` where you don't need Δ". Fix: add a result grader to each, and run trigger-only suites with `--ablation none` and no delta floor. `plugin-test-bench/skills/review-evals/SKILL.md:50` ("needs only its `tool_used: Skill` grader") teaches the same defect.
6. **Turn caps below the default.** `max_turns: 4` in the 8 plugin-engineering and 3 evals-loading cases. Doc: default 10, "set it generously"; a cap hit is a run error, which item 4 turns into a failed gate. Fix: at least 10.
7. **Graders that read the prompt.** `project-maintainer/evals/decision-recorded/graders/7-users-reason.md` regexes `second service` over `trace`, which contains the user prompt; `debt-obsolete/graders/4-names-what-changed.md` judges `focus: trace`, which shows the prompt that states the answer. Fix: grade the written file or `last_message`. `decision-recorded/graders/2-not-through-the-shell.md` uses `[^"]*`, which stops at the escaped `\"` the doc warns about; use `.*?`.

## 2. Configuration that contradicts the documentation

8. **CI credentials in a GitHub environment.** `evals.yml:12, 97-98` and `.claude/skills/plugin-releases/SKILL.md:119-120` use the `claude` environment. The official guide stores credentials as repository secrets and never mentions environments. Fix: repository secret, remove `environment: claude`; update the comments and the skill.
9. **The loading suite never runs in CI.** `evals.yml` runs only `evals/`; doc: `--eval-dir` or `experimental.evals`. `.claude/rules/plugins/evals.md:17` ("Run the full suites in CI") is false for it, and the loading ADR's "by dispatch" is impossible. Fix: a CI step with `--eval-dir evals-loading --ablation none`, or an `eval_dir` dispatch input. Add `plugins/*/evals-*/results/` to `.gitignore` (today `evals-loading/results/` is not ignored, verified with `git check-ignore`).
10. **Suite discovery misses documented layouts.** `evals.yml:79-80, 120` and `scripts/validators/plugin_consistency/evals.py:51-65` see only `evals/*/prompt.md`; doc allows nested groups and `experimental.evals`. Same gap in `plugins/skill-diagnostics/skills/skills-best-practices/scripts/check-evals.py:31-33, 268-287`, which also ignores a root-level `plugin.json`. Its V-8 counts `arm: with-only` and `mock_calls` graders as scorable, and V-7 scans `llm` rubrics for `(?i)`, which the doc restricts to `regex` patterns.
11. **Paid runs are pre-approved.** `.claude/settings.json:45` `Bash(claude plugin*)` allows `claude plugin eval` without a prompt; doc: "Every eval run … is a real model call on your account". Fix: add `Bash(claude plugin eval*)` to `ask`.
12. **The credential guard is partial.** `evals.yml:134-137` blocks only `ANTHROPIC_API_KEY`; authentication precedence also ranks `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper` and the cloud-provider variables above `CLAUDE_CODE_OAUTH_TOKEN`.
13. **Effort level unverified.** `evals.yml:191` and `.claude/rules/plugins/evals.md:13` rely on `CLAUDE_CODE_EFFORT_LEVEL` reaching child runs; the doc says only "most `CLAUDE_CODE_*`" variables pass. Verify with one run or stop relying on it.
14. **Exit messages incomplete.** `evals.yml:204`, `.claude/references/evals-ci.md:59`, `plugin-engineering/.../assets/ci-evals.sh:24`, `plugin-evals/.../running-and-ci.md:269-270` and `results.md:79, 93`. Doc exit 1 also covers: no cases found, a run that couldn't start, an untrusted plugin, an invalid option, an unwritable `--json`; plus 130 and 143, and the API-error row ("score 0 without grading", baseline runs count).

## 3. Skills that teach users something the documentation contradicts

### plugin-evals (`plugins/plugin-evals/skills/plugin-evals/`)

15. `SKILL.md:14, 19` and `references/sources.md:139-141` make `--help` the authority over the page. Invert: the page (and changelog) win; `--help` only confirms a flag exists.
16. `SKILL.md:27`, `running-and-ci.md:130, 161`, `README.md:252, 355`: `init` inside a session "prints the interview at no model cost". Doc: `init` calls the model; Claude runs it and asks the questions in the conversation.
17. `running-and-ci.md:162`: `init` without a terminal writes the blank template. Doc: it needs a terminal; in CI run `init --bare <name>`.
18. `SKILL.md:38`: steps grader must be a tool other than `Skill`, and Skill counts "only when it is the only scorable grader". Doc: the walkthrough's steps grader is `tool_used: Skill`; exclusion applies only in two-arm runs, not under `--ablation none`, and an all-excluded case is scored normally.
19. `SKILL.md:41` and `review-evals/SKILL.md:62`: budgets of about 5 turns and 60–120 s. Doc: defaults 10 turns and 300 s, "set it generously"; use `--max-cost-usd` "rather than tight per-run limits".
20. `SKILL.md:43`, `case-format.md:170`, `running-and-ci.md:171, 261`: the judge must be "Sonnet-tier or larger, never the agent's model". Doc: default is the background-task model; its CI example pins `claude-haiku-4-5`; `--judge-model sonnet` is the remedy when you suspect the judge.
21. `SKILL.md:45`: `--trust-plugin` "runs code outside the sandbox". Doc: it only skips the trust prompt.
22. `SKILL.md:50`, `running-and-ci.md:172`, `review-evals/SKILL.md:94`, `plugin-engineering/.../plugin-commands.md:375`: two arms "whenever a plugin resolves". Doc: decided per case; a `context.history_file` case with a path target runs one arm.
23. `SKILL.md:53`: errors only in `arms.with[]`. Doc: also `arms.without[]`, and baseline errors fail the command while every case passes.
24. `running-and-ci.md:186` and `plugin-commands.md:392`: `--keep-temp` per `--help`. Doc: "Keep every run's sandbox directory and print its path". `plugin-commands.md:389`: `--publish-report` per `--help`; doc: publishes even where it would stay local, such as a run a session started. `running-and-ci.md:185`, `README.md:282`, `results.md:41`: publishing also requires a claude.ai subscription with artifacts available; a session-started run stays local.
25. `running-and-ci.md:197`: `not granted` meaning. Doc: a tool the case asked for that the command didn't grant.
26. `running-and-ci.md:202` and `SKILL.md:58`: Bash only. Doc: "Bash or PowerShell".
27. `running-and-ci.md:229, 234` and `SKILL.md:45`: cost = pilot × runs × arms, omitting × cases.
28. `running-and-ci.md:263`: full suite only on version bumps. Doc's CI advice: judge-free graders and `--ablation none` for every-change suites.
29. `case-format.md:123`: `env` row lacks the allowlist and `EVAL_*` passing. `case-format.md:189`: a with-arm agent dispatch needs `Agent` in `allowed_tools`. `case-format.md:173`: skill name is the directory name, not the frontmatter `name`.
30. Claims with no source on the page (cite the other official page, or remove): `case-format.md:101-103, 174-176`; `fixtures-and-mocks.md:50, 80, 98`; `running-and-ci.md:145-146, 184, 187, 194-195, 204-208, 240, 254-260`; `results.md:64, 71`; `sources.md:149-150`; `other-formats.md:162, 164, 192`; `SKILL.md:39, 46, 60`. Add the `mock budget` progress line (`fixtures-and-mocks.md:99`).
31. `sources.md:98`: snapshot dated 2026-10-14 against 2.1.299/2.1.300; re-snapshot at 2.1.325.
32. `README.md:10, 48`: minimum Claude Code 2.1.299. The page's minimum is 2.1.269; keep 2.1.299 only as this plugin's own floor (it is when `disallowed_tools` arrived), labeled as such.

### plugin-test-bench

33. `skills/test-install/SKILL.md:25` (2.1.293) vs `README.md:10, 51` (2.1.299) vs the page (2.1.269): reconcile, cite the changelog for any higher floor.
34. `skills/test-install/SKILL.md:26`: accept `plugin.json` or `.claude-plugin/plugin.json`, or a skills-directory plugin.
35. `skills/test-install/SKILL.md:78`: results of an installed-plugin target go to `./evals/results/` in the current directory, or `./<dir>/results/` with `--eval-dir`, not `<target>/<eval dir>/results/`. Lines 78 and 83 (`out/trace.jsonl`, `sealed/` mode 000) and `review-evals/SKILL.md:61` are undocumented: label as observed or remove.

### skill-diagnostics

36. `references/evaluation.md:25`: quote the page ("neither tool reads the other's case files"), add inline `graders:` in `case.yaml`; `:96`: `tool_used: Skill` is a plugin-fired indicator, unscored in two-arm runs. `references/sources.md:40`: widen the source note. `references/checklist.md:89`: drop [CC] from TE-1's case count.

### plugin-engineering

37. `skills/plugin-testing-and-debugging/SKILL.md:48`: add the all-excluded rule and the other excluded graders. `:50`: replace the `plugins` gotcha with the page's `plugins: ["../.."]` (see corrections above). `:51`: page wording, "a run error, usually scores 0". `:122` and `CHANGELOG.md:13`: label the `--max-cost-usd 0` load as observed. `:44`, `references/evals.md:66`, `references/messages.md:52`, `cli-commands-guide/references/session-commands.md:24`: "no `/plugin` form" is not on the page; cite cli-reference or drop.
38. `references/evals.md:87-90`: label `-i` and the SKILL.md root rule as from cli-reference; `:321`, `:374` (delta omitted also when arms aren't comparable), `:428`: page wording.
39. `cli-commands-guide/references/session-flags.md:31`: `claude plugin eval` loads the plugin from its target; it does not need `--plugin-dir`. `cli-commands-guide/SKILL.md:48` and `plugin-commands.md:368`: "the first two take a list and `--json` takes an optional path". `plugin-commands.md:359` (case layout), `:370` (relabel to 2.1.325), `:374` (judge default), `:377` (exit 2 when a run is left unstarted; `skippedPaidGraders`), `:385`, `:388` (`--mocks record`, `--json` quiet and `.json`), `:399-401` (exit 2 causes, 130 writes partial results, git ≥ 2.31). `:379`: keep `--disallow-tools` and `disallowed_tools`, citing the 2.1.299 changelog.
40. Bundled copy `public-marketplace-dev/references/01-plugins-core/plugin-evals.md`: add the target row `name@skills-dir`; line 129 back to "ask Claude there to run `claude plugin eval init`". Everything else matches the page.
41. `README.md:50-58` Prerequisites: add git ≥ 2.31 for evals and `bubblewrap` + `socat` on Linux for suites that grant Bash.

## 4. Project instructions and references

42. `.claude/references/evals-ci.md` and `.claude/templates/evals-ci-template.md` are outdated: native installer, a `testing-plugins` skill that doesn't exist, `EVAL_MODEL` variables, target selection; the template lacks tags, gates, `--concurrency`. Rewrite from the page and the current workflow.
43. `.claude/architecture/refactor.md:18, 293-295`: says the CLI finds cases only in `evals/` and that `evals.yml` is pending. Update.
44. `.claude/rules/architecture/github.md:35`: evals don't run in Validate; they run in `evals.yml` when `CLAUDE_EVALS` is enabled.
45. `.claude/rules/plugins/evals.md:15` and `.claude/memory/check-evals-at-no-cost-before-spending.md:8`: label the `--max-cost-usd 0` load as observed, not documented.
46. `evals.yml:40-45, 129-137`: the project's own checklist (`evals-ci.md:56-57`) requires a loud failure on an empty token and a fork notice; neither exists.

## 5. No deviation found

prompt.md and case.yaml fields and limits in every suite; grader types, `weight`, `arm`, `target`/`focus`; must-not-trigger cases (`min: 0`, `max: 0`, `arm: both`); namespaced Skill `input_match`; scaffold scripts write only files and git state; no `@path` reliance; CI flags (`--trust-plugin`, pinned `--model` and `--judge-model`, `--no-publish`, `--max-cost-usd`, `--json` path, target first); sandbox packages installed; real-server grant naming; `**/evals/results/` ignored; skill-creator's `evals/evals.json` never confused with `claude plugin eval` cases; PC-12 and PC-13.

## 6. Not verified

Real run durations and costs; whether `CLAUDE_CODE_EFFORT_LEVEL` reaches child runs; how `--allow-real-servers` treats an HTTP server; `AskUserQuestion` in a non-interactive run; writes under `.claude/` when `Write` is granted; trace key order in hook-engineering's regexes; bubblewrap under Ubuntu 24.04's AppArmor; `upload-artifact` after a job timeout. Each needs a paid run or a CI run.

## Owner decisions, 2026-11-15

- **The Claude Code docs MCP stays out of every plugin.** A plugin's `.mcp.json` renames the server's tools to `mcp__plugin_<plugin>_<server>__*`; the engineering plugins list it in their README Prerequisites with the install steps instead. Evals measure the skill as it runs in real use, with that MCP in the with-plugin arm only, against the model's default tools (WebSearch, WebFetch). The doc's "only your plugin loaded" offers no way to supply a server the user installs separately; the overlay copies it into the plugin under test, which matches the doc's "Ship any … MCP servers a case depends on in the plugin under test" for the run.
- **CI authenticates evals with the owner's subscription:** `CLAUDE_CODE_OAUTH_TOKEN` as a repository secret, no GitHub environment.
- **Every fix lands in pull request #108.**

## 7. Reports to Anthropic

- The page omits `--disallow-tools` and `disallowed_tools` (changelog 2.1.299).
- `--help` describes `--keep-temp` and the judge default differently from the page.
- `plugins: ["../.."]` versus the observed refusal to name the plugin under test, if a probe reproduces it.
- claude-code-action hides the error even in a debug rerun: it reads `process.env.ACTIONS_STEP_DEBUG`, which the runner does not export (anthropics/claude-code-action#2047 for the underlying failure).
