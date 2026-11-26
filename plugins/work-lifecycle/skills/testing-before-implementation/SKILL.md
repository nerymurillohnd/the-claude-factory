---
name: testing-before-implementation
description: Implements code changes test-first (TDD). Writes a failing test that names the break it catches, watches it fail for the right reason, writes the minimal code that passes, then checks the full suite, lint and types against a baseline, recording the command and output of each run. Use when implementing a feature, fixing a bug or changing behavior in code that can be tested, or when the user asks for TDD, test-first or red-green-refactor, even if they don't mention tests. When the work spans several steps or files, plan it first with planning-before-execution and apply this skill to each code task. Not for configuration-only edits, documentation, visual styling, or adding tests to existing code without a behavior change.
compatibility: Claude Code, with the project's own test, lint and type-check commands. The Claude app can't run the user's project, so the skill doesn't apply there.
---

# Testing before implementation

Change code test-first: every behavior gets a test that is seen failing for a reason you named before the code that makes it pass exists, and the task ends only when the whole project is no worse than its baseline. Every red and green run is recorded with its command and real output, because "tests pass" without output proves nothing.

## Gotchas

1. A test that passes on its first run proves nothing. It tests behavior that already exists, or nothing at all: fix the test until it fails for the reason you named.
2. An error is not a failure. An import error, a typo or a missing fixture makes the test red for the wrong reason: fix it and run again before counting the run as red.
3. A green targeted test is not a green project. Always compare the full suite, lint and type check with the baseline before calling the task done.
4. The project's commands come from the project. Read them from its files; never assume a test runner, a flag or a script name.
5. A wrong-looking test is the user's call. Report it with the evidence and keep it unchanged; editing or removing a test to make it pass hides the bug it may be catching.
6. An expected value computed with the code under test always passes. Write expected values by hand, from the requirement.
7. Flaky is not passing. A test that passes on a rerun after failing is flaky: report it as flaky, never rerun it until it is green.
8. `git stash` is shared by every worktree of a repository, so a stash made in one can be popped in another. Set code aside on a local branch instead (phase 4).

## Rules

Each rule says what to do and why, so it holds in cases the phases don't name.

1. Keep existing tests as they are. When one looks wrong, stop and report it to the user with the evidence. Changing a test to make it pass hides bugs.
2. Write a solution that works for every valid input. Tests verify correctness; they don't define the solution, and a hard-coded value passes the test and fails in use.
3. Write the test before the code it covers. Code that already exists biases the test toward what it does instead of what it should do.
4. Watch every test fail for the reason you named, then pass. A test never seen failing may test nothing.
5. Record the command and output of every red and green run. On planned work the plan gate reads them.
6. Name the break before writing the test: which production change would make it fail, and whether that change is a bug or a decision. A test that can't name its break catches nothing.
7. Compare the final suite, lint and type check with the baseline. Fix every new failure. Never leave a pre-existing failure only listed: report each by name with its cause and fix, fix it in its own commit when the user or the project's instructions ask for every failure or finding to be fixed, and otherwise offer that fix before you close the task. A pre-existing failure is outside the change, so its fix stays separate from it, and a project that asks for every finding fixed expects it gone, not noted.
8. Report flaky tests as flaky. A lucky pass is a false pass.
9. Mock only the slow or external level (network, clock, filesystem outside the project, paid services), mirroring the real structure. Assertions on a mock test the mock.
10. Leave push, deploys and anything outside the task to the user. Commit at green only as the project's conventions say.
11. Run the whole red-green-refactor cycle in the one session that writes the code, the main session or the subagent given that one task; never split it, such as one agent writing the test and another the code. Test and code share context, and a split cycle returns summarized evidence instead of raw output. On high-stakes work, have the `work-lifecycle:plan-verifier` agent check test quality in work mode once the task is done, from the main session, giving it the test files, the code under test and the red and green runs.

## Workflow

Copy this checklist into your working notes and tick each item only when it is done. Phases 3 to 6 repeat for each behavior until the task is covered.

```text
Test-first progress:
- [ ] 1. Commands found, baseline recorded
- [ ] 2. Verification approach chosen (state which and why)
- [ ] 3. Break named for the next test
- [ ] 4. Red: failed for the named reason, evidence recorded
- [ ] 5. Green: minimal code passes, evidence recorded
- [ ] 6. Refactored while green
- [ ] 7. Suite, lint and types compared with baseline; committed
- [ ] 8. Report delivered
```

### 1. Discover

1. Find the project's test, lint and type-check commands in its own files: `CLAUDE.md`, the package or project manifest (`package.json` scripts, `pyproject.toml`, `Makefile`, `Cargo.toml`, `go.mod`), and the CI configuration. Prefer the exact command CI runs.
2. Read the existing tests nearest to the code you will change, and match their framework, file layout, naming, fixtures and assertion style.
3. Run the full suite, lint and type check before any change, and record the baseline: each command and its pass or fail counts, with every failing test or finding listed by name.
4. If the project has no test setup, propose the smallest one that fits its stack, from that framework's current documentation, and ask the user before adding any dependency.

### 2. Decide how to verify

Default to the test-first cycle. Read `references/choosing-verification.md` when the change is legacy code without tests, a visual interface, configuration or infrastructure, or a throwaway prototype, or when you need to choose between a unit, an integration and an end-to-end test. State the approach and why in your notes.

### 3. Name the break

1. State, for the next test, which production change would make it fail, and whether that change would be a bug or a deliberate decision.
2. Derive the expected value by hand from the requirement, never by running the code under test.
3. Read `references/writing-good-tests.md` before writing or changing any test or mock: it holds how to test real behavior, when a mock is right, and the warning signs of a test that catches nothing.

### 4. Red

1. If code for this behavior already exists from before the test, set it aside on a local branch, then reimplement it from the test:

   ```bash
   git switch -c wip/<behavior>-before-test && git add <its files> && git commit -m "WIP: <behavior>, set aside before its test" && git switch -
   ```

   Nothing is pushed, and the branch is the user's to keep or delete.
2. Write one test for one behavior.
3. Run it. Confirm it fails, not errors, and that the failure message shows the reason you named.
4. If it passes, it tests existing behavior: fix the test. If it errors, fix the error and run again.
5. Record the run: the exact command and the lines of output that show the failure.

### 5. Green

1. Write the minimal code that makes the test pass for every valid input, not only the test's.
2. Run the test. If it fails, fix the code, never the test.
3. Record the run: the command and the lines of output that show the pass.

### 6. Refactor

While green, improve names and structure without adding behavior, and run the test again after each change. A refactor that turns the test red is undone or fixed before going on.

### 7. Close the task

1. Run the full suite, lint and type check, and compare each with the baseline.
2. Fix every new failure. For each pre-existing failure, find its cause and act as rule 7 says: fixed in its own commit, after the task's own commit, or offered with its fix. A fix that would change a test is still the user's call (gotcha 5).
3. On high-stakes work (money, data, security, anything costly to get wrong), run a real mutation check: break one line of the new code on purpose, confirm a test fails, revert, and record both runs. Read `references/writing-good-tests.md` for how to pick the line.
4. Commit only as the project's conventions say; never push.

### 8. Report

Deliver this report:

```markdown
## Test-first report

**Baseline:** <suite, lint and type-check commands> → <pass and fail counts before the change>

**Tests**
- <test name>: breaks if <named production change>
  - Red: `<command>` → <failure line>
  - Green: `<command>` → <pass line>

**Final check against baseline**
- New failures: <none, or each by name with its fix>
- Pre-existing failures: <none, or each by name with its cause and either its fix commit or the fix offered>

**Mutation check:** <the line broken and the test that failed | not run, and why>

**Risks left without a test:** <each, with why>
```

Open the example that matches the change before writing your first test, to see the judgment in a full run:

- `references/examples/python.md`: a bug fix in a Python function, with a pre-existing failure in the baseline.
- `references/examples/typescript.md`: a new function in TypeScript, with a mock at the network boundary only.
- `references/examples/bash.md`: a change to legacy shell code without tests, with a characterization test first.

The examples show judgment, not a template: copy their reasoning, never their languages, names or numbers.

## Inside a plan

When this skill carries out a task of a plan from `work-lifecycle:planning-before-execution`:

- In the main session, with that plan's state file for this session, record the red and green runs in the task's `red` and `green` entries, each as an object with `command` and `output`, then validate the file as that skill's Execution section says. The plan gate keeps the plan open until every test-first task has both.
- As a subagent running one task of the plan, never write the state file: return the red and green runs, the final check against the baseline and the report, each with its command and raw output, so the main session records them.

Without a plan, the report above holds the same evidence, and the gate doesn't apply.
