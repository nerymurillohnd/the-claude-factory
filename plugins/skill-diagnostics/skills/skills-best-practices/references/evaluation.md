# Evaluation

How to test whether a skill triggers on the right prompts and whether its output is better than without it, and the tools that run those tests.

## Contents

- [Two things to test](#two-things-to-test)
- [Build evals first](#build-evals-first)
- [Trigger evals](#trigger-evals)
- [Output-quality evals](#output-quality-evals)
- [Claude A and Claude B](#claude-a-and-claude-b)
- [Tools](#tools)

## Two things to test

Test two things separately: whether the skill triggers on the right prompts, and whether its output is better than without it. Both are baseline comparisons run in fresh sessions, because leftover authoring context hides gaps \[CC\]\[AS\].

## Build evals first

\[PL\]: run Claude on representative tasks without a skill, note the failures, build at least three scenarios that test them, measure the baseline, write the minimum instructions that pass, then iterate.

## Trigger evals

These test the description \[AS\].

1. Write about 20 realistic queries: 8–10 that should trigger and 8–10 that shouldn't. Vary phrasing, explicitness, detail and complexity; use real paths, personal context and typos. The best negatives are near-misses that share keywords but need something else.
2. Run each query 3 times and compute a trigger rate; pass = above 0.5 for should-trigger, below 0.5 for should-not. In Claude Code, detect a `Skill` tool call in `claude -p "<query>" --output-format json`.
3. Split about 60% train and 40% validation, with positives and negatives in both, fixed across iterations.
4. Loop: evaluate both sets, fix only train failures (broaden if positives fail, add boundaries if negatives fire), generalize instead of pasting keywords, try a different structure when stuck, stay under 1,024 characters.
5. About five iterations; pick the version with the best validation pass rate, not the last one. Confirm with 5–10 fresh queries.

## Output-quality evals

\[AS\]:

1. Start with at least three test cases in `evals/evals.json`: a realistic prompt, the expected output in words, optional input files, including one edge case. The file holds one object, `{"skill_name": "<name>", "evals": [{"id": 1, "prompt": "<what a user types>", "expected_output": "<the result in words>", "files": ["evals/files/<input>"], "assertions": ["<one checkable statement>"]}]}`; `files` and `assertions` may start empty. The baseline isn't stored there: it is the same prompt run without the skill.
2. Run each case with the skill and without it (or against a snapshot of the previous version), each in a clean context, saving outputs per case under `<skill>-workspace/iteration-N/`. Record `total_tokens` and `duration_ms`.
3. After the first run, add assertions that are specific and checkable ("valid JSON", "both axes labeled", "at least 3 recommendations"), not vague or brittle.
4. Grade each assertion PASS or FAIL with quoted evidence in `grading.json`; no benefit of the doubt; use scripts for mechanical checks.
5. Aggregate into `benchmark.json` (mean and stddev of pass rate, time and tokens, plus the delta) and weigh what the skill costs against what it buys.
6. Drop assertions that always pass in both configurations, fix those that always fail, study those that pass only with the skill, tighten instructions where results vary.
7. Have a person review outputs and record specific feedback in `feedback.json`.
8. Give the failed assertions, the feedback and the execution transcripts to an LLM with the current `SKILL.md`; ask it to generalize, keep the skill lean, explain the why and bundle repeated work. Rerun in `iteration-N+1/` until feedback is empty or gains stop.

## Claude A and Claude B

\[PL\]: refine the skill with one Claude instance (A) and test it on real tasks with a fresh instance (B). Watch B's navigation: unexpected file order, missed links, files read repeatedly (move them into `SKILL.md`), files never read (cut or signal them better), then bring the observations back to A. Collect team feedback too.

## Tools

\[CC\]:

- **Built-in runners in Claude Code.** `claude plugin eval` and the skill-creator plugin run evaluations in Claude Code \[CC\], and the open standard gives the full method \[AS\]. The Platform's sentence "There is not currently a built-in way to run these evaluations" \[PL\] doesn't hold for Claude Code, which has `claude plugin eval`.
- **`claude plugin eval`** runs each prompt with and without the plugin, grades it, and exits non-zero below a threshold, so CI can gate on it. A `tool_used: Skill` grader measures triggering. Use it for skills shipped in plugins.
- **What `claude plugin eval` loads.** It "loads the target plugin's skills, hooks, and agents", so a case can exercise a hook end to end; treat its scores as advisory outside an isolated environment when the hooks can modify the files the graders read \[CC\]. A hook script's own input and output (JSON in, JSON or nothing out) are still tested best by direct cases that pipe input into the script `default`.
- **The `skill-creator` plugin** (`/plugin install skill-creator@claude-plugins-official`) runs the same loop inside a conversation: isolated subagent runs, grading, benchmark, blind A/B between versions, description tuning and an HTML review viewer. Its `evals/evals.json` format is not interchangeable with `claude plugin eval`.
- **Baseline without the skill.** To disable a personal or project skill for the baseline run, set it to `"off"` in `skillOverrides`, which doesn't apply to plugin skills. `/skill-doctor` reports each skill's context cost and usage.
- **Seeded-defect fixture.** A seeded-defect fixture tests an audit or a review skill: plant one output-deciding defect in a multi-file skill (for example a script that rejects a value the reference table allows) and grade whether the reply reports it, in both arms \[SD\].
