# Phase 7: Audit and evals

How to run the audit and the evals the requester chose in phase 6, and the final checks after them.

## Contents

- [Audit](#audit)
- [Evals](#evals)
- [Final checks](#final-checks)

## Audit

Load `skills-engineering:auditing-skills` and run its full battery, with all its agents, on the skill, and follow that skill to its end. Apply its findings as SKILL.md's Routes say for an audit's findings, then run phase 5 again. When the requester chose the evals too, run the audit first.

## Evals

### Gotchas

- Eval runs never inherit this session's context. Configure each run on purpose.
- With plugin evals, the model is set per case, and effort can't be set per case.
- With plugin evals, running one arm or both is set for the whole command.
- With plugin evals, a grader's arm setting changes only how that grader is scored.
- With plugin evals, a run removes Bash, Write, Edit, WebFetch and WebSearch unless they are granted with `--allow-tools`.
- With plugin evals, a granted Bash runs in a sandbox whose network reaches only the domains granted with `WebFetch(domain:...)`.
- With plugin evals, the plugin's MCP servers are replaced by mocks; a real server starts only with `--allow-real-servers` or `--mocks off`.
- With evals for skills, set the model and effort in each subagent you spawn.
- Every eval run, and every judge that grades one, spends the requester's usage. Never run without the requester's approval, and never take it by default.
- Ask each step's questions in their own AskUserQuestion call, after the step before it is done: each depends on what came before.

### Choose the runner by skill type

- A skill in a plugin: plugin evals.
  - Run `claude plugin eval .` from the plugin root (Claude Code 2.1.269 or later). It runs each case in an isolated session with the plugin, again with no plugin loaded, and scores the case's graders.
  - Read [Plugin evals](https://code.claude.com/docs/en/plugin-evals) for the suite layout, graders and commands.
  - Load `plugin-engineering:plugin-testing-and-debugging` and use it, when available. When it isn't, look for another specialized skill you have for plugin evals and use it. When none exists, proceed with the documentation above.
- A personal or project skill: evals for skills, the Agent Skills method.
  - Store the cases in `evals/evals.json` inside the skill directory, each with a prompt, an expected output and any input files.
  - Run each case twice, each time from a clean context: once with the skill, and once without it or with its previous version. In Claude Code, spawn one subagent per run.
  - For the baseline, set the skill to `"off"` in `skillOverrides`. This works only for personal and project skills.
  - Keep each run's outputs, timing and grading in a workspace next to the skill, under `iteration-N/<case>/with_skill/` and `without_skill/`.
  - Read [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) for the workspace, assertions, grading and aggregation.
  - Read [Evaluate and iterate on a skill](https://code.claude.com/docs/en/skills#evaluate-and-iterate-on-a-skill) for how Claude Code runs the baseline.

### Map the skill

Before any case, map the skill: its use cases, its triggers, each rule and its branches, its outputs, and the failure each section prevents.

### Define the cases

1. Stop and ask, in one call:

   ```text
   Question 1: For the evals of [name], do you have cases of your own, or should I propose them?
   Header: Eval cases
   Multiple selection: no
   Options:
   - I have cases: Share them, and I bring each to the same bar before using it.
   - Propose them: I write cases from real use and the defects they must catch.

   Question 2: How many points above Claude without the [skill | plugin] should it score? Type another number under Other.
   Header: Target
   Multiple selection: no
   Options:
   - 10 points: The [skill | plugin] scores 10 points more than the baseline.
   - 20 points: The [skill | plugin] scores 20 points more than the baseline.
   - 30 points: The [skill | plugin] scores 30 points more than the baseline.
   ```

   - I have cases: ask for them in the reply, and bring each to the bar in step 2.
   - Propose them: write them to the bar in step 2.
   - The target: keep it as the delta the results are judged against.
2. Build each case to this bar:
   - A real use case, in the words a real user would type.
   - The defect it must catch. Write it to expose a failure, never just to pass.
   - Written from two perspectives: what the skill makes Claude do, and what Claude already does well without it. A case that Claude passes either way measures nothing.
   - The official guidance:
     - [Designing test cases](https://agentskills.io/skill-creation/evaluating-skills#designing-test-cases) and [Writing assertions](https://agentskills.io/skill-creation/evaluating-skills#writing-assertions): realistic prompts, varied phrasing, edge cases, and checks that can fail.
     - [Build evaluations first](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#build-evaluations-first): at least three scenarios built from real gaps, measured against a baseline without the skill.
     - [Designing trigger eval queries](https://agentskills.io/skill-creation/optimizing-descriptions#designing-trigger-eval-queries): for cases that test whether the skill loads, with should-trigger queries and near-miss should-not-trigger queries.
     - [Write and refine cases](https://code.claude.com/docs/en/plugin-evals#write-and-refine-cases) and [Grader types](https://code.claude.com/docs/en/plugin-evals#grader-types): for a plugin skill.
     - [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests): for measurable success criteria and how to grade them.
3. Present the cases to the requester and ask:

   ```text
   Question: These are the eval cases for [name]: [each case: its prompt and the defect it must catch]. Do they work for you?
   Header: Cases
   Multiple selection: no
   Options:
   - Approve them: Go on to study them against the skill.
   - I have observations: Tell me what to change, and I correct the cases.
   ```

   - Approve them: go to the next section.
   - I have observations: correct the cases, present them again, and ask again.
4. Run none of the cases yet. Anticipate failures instead of spending the requester's usage to find them.

### Study the cases against the skill

1. Launch a subagent to study the cases against the skill. You learned things while building the skill that the skill may not say, so your own study would be biased.
   - Launch the built-in Explore subagent by its type, never a fork. A fork inherits this conversation; Explore starts without it, without the CLAUDE.md files and project rules, and without the git status.
   - Know what still reaches it: managed policy files, and a subdirectory's CLAUDE.md or path-scoped rules for the files it reads. When the skill's folders carry any of them, tell the requester the study was not fully clean.
   - Give it a brief:
     - the exact folders and files it reads, the eval cases and the skill's folder, and that it reads nothing else;
     - read each case, and answer it first from its own reasoning and knowledge, as Claude would without the skill;
     - report, for each case, what the case tests that it already knows how to do without the skill and its files, and where the skill adds what it lacks.
   - Wait for its report before you fix anything in step 3.
2. The agent studies every case from the two perspectives in Define the cases. For each case it reports where the skill is weak, where it would fail or score low, and the passage at fault.
3. Fix the skill for each gap the agent finds, before running anything. Never wait for the evals to find what this study can catch. Correct with the same two perspectives.
4. Tell the requester about each case Claude already passes without the skill, with the reason, so no usage is spent on it unless they keep it.

### The two arms

The difference between the arms is what the evals measure, so set each arm to what it stands for:

- The arm with the build runs with everything the build includes. For a plugin, that is all its skills, agents, hooks and MCP servers, with each MCP server mocked as [Mock MCP servers](https://code.claude.com/docs/en/plugin-evals#mock-mcp-servers) describes.
- The arm without the build runs with Claude's natural, default behavior: every tool and access Claude has in a user's session, such as network access and its built-in tools. Never take any of them away from this arm. A weakened baseline measures nothing.
- With plugin evals, grant with `--allow-tools` every built-in tool the cases need, so both arms keep what a user's session has.

### Run and correct

1. Propose how to run the evals, and ask, in one call. Leave out Question 2 for evals for skills, which run only in the local session:

   ```text
   Question 1: Which model should the eval runs use?
   Header: Model
   Multiple selection: no
   Options:
   - [The model the skill's users run] (Recommended): Measures the skill where it will be used.
   - [A second model]: [What it adds.]
   - [A third model, when one applies]: [What it adds.]

   Question 2: Where should the evals run?
   Header: Where
   Multiple selection: no
   Options:
   - Local smoke, full in CI (Recommended): One case runs here to check the suite, and the full suite runs in CI.
   - All local: Every case runs here.
   - All in CI: Every case runs in CI.

   Question 3: Should each case run with and without the [skill | plugin], or only with it?
   Header: Arms
   Multiple selection: no
   Options:
   - Two arms (Recommended): Measures the difference against the target of [target] points.
   - One arm: Checks only the [skill | plugin]'s own score, with no difference to compare.

   Question 4: The evals for [name] are ready: [cases] cases, [runs] runs each, plus [judge calls] judge calls, with the choices above. Run them?
   Header: Run evals
   Multiple selection: no
   Options:
   - Run them: Run the evals as chosen.
   - Don't run: Stop here. The cases and the fixes stay.
   ```

   - Model and arms: set them as chosen.
   - Where: for CI, follow [Run evals in CI](https://code.claude.com/docs/en/plugin-evals#run-evals-in-ci). Adding or changing a CI workflow, and pushing it, needs the requester's approval.
   - Run them: run the evals.
   - Don't run: stop, and report the cases and the fixes made.
2. Deliver the HTML report of every run, so the requester can see and check the results and the benchmark. Never report results only in text.
   - A plugin skill: give the requester the `report.html` path, or its `Published:` URL, as [HTML report](https://code.claude.com/docs/en/plugin-evals#html-report) describes.
   - A personal or project skill: build an HTML report from the workspace's grading and `benchmark.json`, and give the requester its path.
3. Read the results by runner, and compare the delta against the target:
   - A plugin skill: [Read the results](https://code.claude.com/docs/en/plugin-evals#read-the-results).
   - A personal or project skill: [Grading outputs](https://agentskills.io/skill-creation/evaluating-skills#grading-outputs), [Aggregating results](https://agentskills.io/skill-creation/evaluating-skills#aggregating-results) and [Reviewing results with a human](https://agentskills.io/skill-creation/evaluating-skills#reviewing-results-with-a-human).
4. Make one correction pass, following [Iterating on the skill](https://agentskills.io/skill-creation/evaluating-skills#iterating-on-the-skill).
5. Ask for approval before re-running:

   ```text
   Question: The correction pass changed [what changed]. Re-run only the [count] cases that failed or that it affected: [cases]?
   Header: Re-run
   Multiple selection: no
   Options:
   - Re-run them: Run those cases again.
   - Stop here: Keep the results as they are.
   ```

   - Re-run them: run only those cases, and deliver their HTML report. Never re-run a case the correction didn't affect that already gave the expected result.
   - Stop here: report the results as they are, with the HTML report.
6. When the results meet the target, go to Final checks. When they don't, report the gap and ask whether to make another correction pass or stop.

## Final checks

When the audit and the evals the requester chose are done, check the final skill:

1. Run every check that applies to it against the final files: the mechanical check from step 2 of phase 5, and each linter, validator or script the environment provides for skills.
2. Fix each finding, and run every check again until all of them pass.
3. Report each check with its exact command and raw output. The skill is done when every check passes.
4. Go back to phase 6 and ask again how to proceed.
