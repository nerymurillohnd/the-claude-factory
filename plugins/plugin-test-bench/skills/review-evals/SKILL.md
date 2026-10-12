---
name: review-evals
description: Reviews a Claude Code plugin's eval suite (the cases claude plugin eval runs) before you pay for runs — checks that each case measures what the plugin adds rather than what Claude does anyway, that graders score the right thing in both the with-plugin and no-plugin arms, that triggering is measured as a rate, and that fixtures and rubrics are correct. Use when the user asks to review, check, improve or debug plugin eval cases, after claude plugin eval init drafted a suite, or when scores or deltas look wrong.
argument-hint: "[plugin folder]"
---

# Review a plugin's eval suite

Plugin: `$ARGUMENTS` (a folder; if empty, the plugin in the current directory). Its suite is in `evals/`, or in the `experimental.evals` path of its `plugin.json`.

This skill reviews cases; it doesn't write a suite from nothing. With no suite, suggest `claude plugin eval init`, which interviews the user and drafts one, then come back. Change no file until the user approves the fixes.

Format reference: <https://code.claude.com/docs/en/plugin-evals>. Read it live before stating a field, grader option or default, because the format still changes between releases.

## Steps

1. **Read the plugin**: its manifest, each skill's `description` and body, agents, hooks and README. You need to know what it promises and what Claude would do without it.
2. **Read every case in full**: `prompt.md`, `case.yaml`, each file in `graders/`, scaffold scripts, fixtures and mocks. List the cases first, then read each one with no skipping.
3. **Check each case** against the checks below. Give every finding the case, the file, what is wrong, what it does to the score, and the fix.
4. **Dry-check fixtures for free** when cases have a `scaffold_script`: ask first, because the script runs on this machine. Run it in a `mktemp -d` folder, inspect what it built, and delete the folder. A fixture that doesn't build, or doesn't contain what the prompt and graders assume, is a finding found at no cost.
5. **Report** with the template below, then offer to apply the fixes.

## Checks

### Does the case earn its place?

Each case should prove one of these, named in its `description` with the hypothesis:

| Kind | Proves |
| :-- | :-- |
| Difference | Without the plugin, Claude fails in a specific, predictable way; with it, it succeeds |
| Trigger | The skill fires on realistic requests, and stays quiet on nearby requests it shouldn't take |
| Own risk | A failure here breaks the plugin itself: an agent that doesn't get its input, a hook that doesn't fire |
| Guardrail | The plugin doesn't over-report or invent; Δ may be about 0 |

- Ask of every Difference case: would Claude, with no plugin and no project context, already get this right? Then the case measures nothing. Cases that only look hard are often easy for current models: say so and suggest a harder, realistic variant, or reclassify it as a Guardrail.
- Flag duplicate hypotheses, "test everything" cases, and cases that only re-check mechanics a unit test could prove.
- Prompts read like a user's own request: no skill name, no hint at the expected answer, everything the task needs in the prompt or the workspace (`@path` mentions are not expanded).

### Do the graders score the right thing?

- In a run with both arms, `tool_used` graders on `Skill` and graders marked `arm: with-only` don't count toward the score. A grader on the plugin's own steps that the no-plugin run should fail needs `arm: both`, or the gate never sees it. A "must not trigger" grader (`min: 0`, `max: 0`) also needs `arm: both`.
- Each case has one grader on the result (final message or produced file) and one on the steps (`tool_used`, `tool_order`).
- Prefer free graders (`regex`, `tool_used`, `tool_order`, `file_exists`). Every `llm` grader is three judge calls per run; keep it for short output that needs judgment, with concrete PASS and FAIL conditions. For a long file, grade its contents with `regex` and `target: { source: file, path: … }`.
- Grade content, not layout: a regex that requires a heading on the same line, or a fixed list format, fails correct answers.
- Common silent failures: `target: files` is the list of created paths, not their contents. `file_exists` sees only files created during the run, not ones the scaffold made or Claude edited. `trace` is JSON with escaped quotes. Regex flags go in `flags`, not `(?i)`.
- A hook's output may not show up in the trace: prove a hook fired by its effect on the reply or the tool calls.
- Every fact a rubric asserts is checked against current official docs; a wrong rubric fails a correct plugin.

### Does the run have what the case needs?

- Each run starts in an empty workspace, with a fresh home and configuration and only the plugin loaded. No `CLAUDE.md`, settings, other plugins or MCP servers, and project files a scaffold writes under `.claude/` aren't loaded. Plugin options stay at their defaults, and only `EVAL_*` and an allowlist of environment variables reach the run.
- Tools beyond the read-only set need `--allow-tools` on the command line. A case's `allowed_tools` and a skill's `allowed-tools` can't widen them. Granting `Bash` runs commands in the OS sandbox, which needs `bubblewrap` and `socat` on Linux and is unavailable on native Windows.
- Writes to protected folders such as `.claude/` and `.git` are denied in a run that can't prompt: a case that expects the plugin to write there fails in every run.
- `max_turns` (default 10) and `timeout_seconds` (default 300) fit the task. A case that only checks triggering needs few turns.

### Is triggering measured as a rate?

One prompt proves nothing about triggering. Look for several realistic phrasings that should trigger each skill and none that name it, each its own case with a `tool_used: Skill` grader, plus nearby requests that must not trigger it. Suggest a shared tag such as `trigger` so `--tag trigger` re-runs them after every description change.

## Report

```markdown
## Eval review: <plugin> — <n> cases

| Case | Kind | Verdict | Findings |
| :-- | :-- | :-- | :-- |
| <case> | <kind> | keep / fix / rewrite / remove | <count> |

### <case>
- **<file>** — <what is wrong> → <effect on the score> → **Fix:** <exact change>

### Missing
- <cases the suite needs and doesn't have: trigger rate, nearby requests, own risk>

### Next run
<the smoke-test command for the changed cases, and the number of runs it starts>
```

After a run, read the results with the user: a case with Δ about 0 that isn't a Guardrail measures nothing; a case that fails in both arms points at the grader or the task before the plugin. Never change a case after a run just to make it pass: fix the plugin, or record why the case was wrong.
