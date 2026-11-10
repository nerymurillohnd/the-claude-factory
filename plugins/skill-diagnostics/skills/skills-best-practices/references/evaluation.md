# Evaluation

What makes a skill's evals good, so an audit can judge the evals a skill has; running them is outside the audit. The criteria come from the official pages, not from any one tool's procedure.

## Contents

- [Two things to test](#two-things-to-test)
- [Where evals live](#where-evals-live)
- [Output cases](#output-cases)
- [Assertions](#assertions)
- [Trigger queries](#trigger-queries)
- [Both ways a skill is invoked](#both-ways-a-skill-is-invoked)
- [Plugin eval suites](#plugin-eval-suites)
- [What an audit can't assess](#what-an-audit-cant-assess)
- [Tools](#tools)
- [When to offer evals](#when-to-offer-evals)

## Two things to test

Test two things separately: whether the skill triggers on the right prompts, and whether its output is better than without it. Both are baseline comparisons run in fresh sessions, because leftover authoring context hides gaps \[CC\]\[AS\]. "Seeing a skill trigger tells you Claude found it, not that it did what you intended" \[CC\].

## Where evals live

- **`evals/evals.json` in the skill folder.** The open standard's format, which the `skill-creator` plugin also uses: one object, `{"skill_name": "<name>", "evals": [{"id": 1, "prompt": "...", "expected_output": "...", "files": ["evals/files/<input>"], "assertions": ["..."]}]}`; `files` and `assertions` are optional \[AS\]. The baseline isn't stored there: it is the same prompt run without the skill \[AS\].
- **A `claude plugin eval` suite.** For a plugin skill, cases live in the plugin's eval directory, `evals/` at the plugin root unless `plugin.json` sets `"experimental": { "evals": "<dir>" }`. A case is a folder with `prompt.md` or `case.yaml` and its `graders/` \[CC\]. The two formats "aren't interchangeable" and neither tool reads the other's files \[CC\].
- **Trigger query sets.** Labeled queries, `{"query": "...", "should_trigger": true}`, often split into a train file and a validation file \[AS\].
- **Not evals.** `claude plugin test` runs the `*.test.ts` files of a mod, "a plugin whose code registers event handlers"; it doesn't test skills \[CC\].

## Output cases

Owned by `TE-1`, `TE-5` and `TE-6` in [checklist.md](checklist.md).

- **Enough cases.** At least three scenarios \[PL\]; the open standard starts with two or three and grows the set after the first results \[AS\].
- **Realistic prompts.** The kind of message a user would type, with file paths, column names and personal context; "Prompts like 'process this data' are too vague to test anything useful" \[AS\].
- **Varied prompts.** Different phrasings, levels of detail and formality, some casual and some precise \[AS\].
- **An edge case.** At least one prompt tests a boundary: a malformed input, an unusual request, or a case where the skill's instructions might be ambiguous \[AS\].
- **A clear success.** `expected_output` describes in words what success looks like \[AS\].
- **Input files that exist.** Each file a case lists is in the skill, under `evals/files/` \[AS\].
- **Cases that need the skill.** Each case tests a gap Claude has without the skill: evaluations are built from "specific failures or missing context" observed without it \[PL\]. A case that passes as well without the skill doesn't show what the skill adds \[CC\]\[AS\].
- **Coverage.** Together the cases exercise what the body promises; a capability no case touches is untested \[SD\] `default`.

## Assertions

Owned by `TE-6`.

- **Checkable.** Specific, observable or countable statements: "The output file is valid JSON", "The bar chart has labeled axes", "The report includes at least 3 recommendations" \[AS\].
- **Neither vague nor brittle.** "The output is good" is too vague to grade; "uses exactly the phrase 'Total Revenue: $X'" is too brittle, since correct output with other wording fails \[AS\].
- **Objective only.** Writing style, visual design and whether output "feels right" belong to human review, not assertions \[AS\].
- **Assertions that tell something.** An assertion that always passes in both configurations, or always fails in both, says nothing about the skill \[AS\]. A static audit can flag one that obviously passes without the skill.

## Trigger queries

Owned by `TE-2`. These test the description \[AS\].

- **Size and balance.** About 20 queries: 8 to 10 that should trigger and 8 to 10 that shouldn't \[AS\].
- **Realistic.** File paths, personal context, specific details, casual language, abbreviations and occasional typos \[AS\].
- **Varied positives.** Vary phrasing, explicitness, detail and complexity. "The most useful should-trigger queries are ones where the skill would help but the connection isn't obvious from the query alone" \[AS\].
- **No trivial positives.** Agents consult skills mainly for tasks beyond what they handle alone, so a simple one-step request may not trigger even a perfectly matching skill \[AS\]; such a query tests nothing.
- **Near-miss negatives.** The most valuable negatives share keywords or concepts with the skill but need something else; an obviously unrelated query tests nothing \[AS\].
- **A fixed split.** About 60% train and 40% validation, with positives and negatives in both, fixed across iterations \[AS\].

## Both ways a skill is invoked

Owned by `TE-7`. The skills page tests a skill both ways: "Let Claude invoke it automatically by asking something that matches the description" and "invoke it directly with the skill name" \[CC\].

- Trigger queries and plugin eval prompts that test triggering are phrased "the way a user would type it rather than naming the skill" \[CC\].
- When the user may invoke the skill (`user-invocable` isn't `false`), at least one case invokes it directly with `/<name>`, so a description that never triggers doesn't hide whether the body works \[CC\] `default`. A skill with `disable-model-invocation: true` needs no trigger queries, only direct cases.

## Plugin eval suites

Owned by `TE-8` and `TE-9`. These apply to the cases of the plugin's suite that invoke the audited skill \[CC\].

- **A grader on every case.** "A case without one fails to load" \[CC\].
- **Result and steps.** "Give each case one grader on the result, such as the final message or a produced file, and one on the steps Claude took to produce it, such as `tool_used` or `tool_order`" \[CC\].
- **Stable graders.** Long output, such as a generated file, is graded with a `regex` grader over the file's contents; `llm` graders are kept for short outputs, "with rubrics written as concrete PASS and FAIL conditions" \[CC\].
- **The right target.** A grader on a produced file uses `{ source: file, path: <path> }`; `files` is only the list of created paths, and `file_exists` sees only files created during the run \[CC\].
- **Regex syntax.** Regexes are JavaScript: put case-insensitivity in `flags: i`; "inline `(?i)` isn't supported" \[CC\].
- **Must-not-invoke cases.** A `tool_used` grader on `Skill` with `min: 0` and `max: 0` needs `arm: both`, or the two-arm run excludes it from the score \[CC\].
- **A workspace that holds what the task needs.** Each run starts in an empty workspace: the prompt carries what the task needs, or `case.yaml` seeds it with a `scaffold_script` (runs only with `--scaffold`) or `add_dirs`; a file Claude must read needs a read tool in `allowed_tools`, since `@path` isn't expanded \[CC\].
- **Mocks, not real services.** A skill that calls MCP tools is evaluated against mock files under `mocks/<server>/<tool>.md`; `expect:` guards the input Claude sends \[CC\].
- **Results not committed.** The suite writes `results/`, which the docs say to add to `.gitignore` \[CC\].

## What an audit can't assess

Owned by `evals` (`TE-3`, `TE-4`): only running the evals shows them.

- Whether the skill passes its cases, with and without the skill, and what it costs in time and tokens \[AS\]\[CC\].
- Whether it works with every model it will run on \[PL\].
- How it behaves in real use: refine with one Claude instance (A) and test with a fresh one (B), watching which files B reads, misses or rereads \[PL\]; `/skill-doctor` shows how often a skill is used \[CC\].

## Tools

\[CC\]:

- **Built-in runners in Claude Code.** `claude plugin eval` and the skill-creator plugin run evaluations in Claude Code \[CC\], and the open standard gives the full method \[AS\]. The Platform's sentence "There is not currently a built-in way to run these evaluations" \[PL\] doesn't hold for Claude Code, which has `claude plugin eval`.
- **`claude plugin eval`** runs each prompt with and without the plugin, grades it, and exits non-zero below a threshold, so CI can gate on it. A `tool_used: Skill` grader measures triggering. Use it for skills shipped in plugins.
- **What `claude plugin eval` loads.** It "loads the target plugin's skills, hooks, and agents", so a case can exercise a hook end to end; treat its scores as advisory outside an isolated environment when the hooks can modify the files the graders read \[CC\].
- **The `skill-creator` plugin** (`/plugin install skill-creator@claude-plugins-official`) runs the same loop inside a conversation: isolated subagent runs, grading, benchmark, blind A/B between versions, description tuning and an HTML review viewer. Its `evals/evals.json` format is not interchangeable with `claude plugin eval`.
- **Baseline without the skill.** To disable a personal or project skill for the baseline run, set it to `"off"` in `skillOverrides`, which doesn't apply to plugin skills. `/skill-doctor` reports each skill's context cost and usage.
- **Seeded-defect fixture.** A seeded-defect fixture tests an audit or a review skill: plant one output-deciding defect in a multi-file skill (for example a script that rejects a value the reference table allows) and grade whether the reply reports it, in both arms \[SD\].

## When to offer evals

An audit judges the evals a skill has; whether a skill without evals gets them is the user's decision \[SD\] `default`.

- **When.** After the report and the recorded verdict, only when the audited skill has no evals: no `evals/evals.json` and no plugin eval case that invokes it. Never before or during the audit, which changes no file of the skill.
- **How.** One `AskUserQuestion` question, with two options: add evals (output cases, and trigger queries when the description is in question) or not now. Write the question in the user's language.
- **Yes.** Writing evals is a separate step, outside the audit: with a skill-writing skill such as `skill-creator`, which writes `evals/evals.json` and runs the loop. In Claude Code the `/skill-diagnostics:evals` workflow measures triggering and output on request, without changing the skill. Neither changes the audit's verdict; the new files are audited like any other change.
- **Where it can't ask.** `AskUserQuestion` exists only in the main conversation: subagents never have it, `claude -p` offers it only with a permission host, and `dontAsk` mode denies it \[CC\]. A forked or preloaded run never asks. In those cases, or in a chat without the tool, don't write evals: end the report with one line saying the skill has none and which tool in [Tools](#tools) would add them.
