---
name: test-and-evals
description: Use right after a plugin is created and after every change to a plugin, its skills, agents, hooks, MCP or LSP servers, mods or marketplace, before the work is reported as done, and when the user asks to test, validate, check or review a plugin before publishing or releasing it, or to write, run, fix or read plugin evals (claude plugin eval, eval init, graders, mocks, CI gates). Runs the checks that cost nothing first, strict validation, loading from the folder, mod tests, an install the way users receive it and the directory and policy review, then builds an eval suite only after the user says yes to it and its cost. Not for a plugin that fails to install, load or run, which troubleshoot-and-debug diagnoses.
---

# Test plugins and run their evals

You are the user's plugin test engineer: prove that a plugin parses, loads, installs and does what it claims before it reaches people who install it. The checks that cost nothing run every time; evals spend the user's usage and run only after the user agrees.

These files were checked against Claude Code 2.1.330 and its docs. When `claude --version` is newer, read the changelog entries after it for each command you rely on, and follow the installed `--help` for flags.

## When to run it

- Right after a plugin is created, and after every change to a plugin, its components, its dependencies or its marketplace: run steps 1 to 4 below before you report the work as done, without weighing whether they are needed.
- Before a release or a publication: run every step.
- When the user asks for evals, or a step shows a behavior only an eval can prove: go to "Evals".

Load `plugin-engineering:cli-commands-guide` too if it isn't loaded yet: this skill decides what to test and in what order, and that one gives each command's exact flags, messages, JSON fields and exit codes.

## Gotchas

- `claude plugin validate` checks files and schema, never behavior, and skips some files entirely; validate each plugin folder and the marketplace, and check by hand what it never reads.
- A plugin loaded with `--plugin-dir`, and a relative-path plugin from a marketplace added from a local path, both load in place. Only an install from a git-hosted marketplace tests the cached copy users load.
- This plugin's `PostToolUse` hook validates the plugin after each `Edit` or `Write` inside it, runs its mod tests when the file is code in a plugin with mod tests, and hands you every error, warning and failed test: fix them before the next edit. Files changed through `Bash` don't fire it, so validate again after such a change.
- Every `claude plugin eval` run, judge grader, `eval init` interview and `claude -p` run is a real model call billed to the user. Never start one without the user's yes to the scope and the estimated cost.
- Never add `--trust-plugin`, `--scaffold`, `--allow-real-servers` or `--mocks off` to an eval on your own: the user's go-ahead must name the flag, because each one trusts or runs the plugin's code as the user.
- An eval run is isolated from the user's settings, `CLAUDE.md`, memory, other plugins and MCP servers: ship in the plugin everything a case depends on.

## Workflow

Copy this checklist into your reply and tick each step with its evidence.

```text
Progress:
- [ ] 1. Facts: claude --version, the surface, the plugin and marketplace folders
- [ ] 2. Validate every plugin folder and the marketplace with --strict
- [ ] 3. Check what validate never reads
- [ ] 4. Load from the folder and check every component
- [ ] 5. Mods: claude plugin test
- [ ] 6. Before a release: install the way users receive it
- [ ] 7. Before publishing: the directory and policy review
- [ ] 8. Evals, when the user agrees
```

1. Facts: run `claude --version`, note where the session runs (`CLAUDE_CODE_REMOTE`, the desktop app, a terminal) and find each plugin folder (`.claude-plugin/plugin.json`) and the marketplace root (`.claude-plugin/marketplace.json`).
2. Validate: run `claude plugin validate <plugin-dir> --strict` for every changed plugin and `claude plugin validate <marketplace-root> --strict`. Fix every error and warning, then validate again until both print none.
3. Blind spots: read [Validate and load a plugin](references/validate-and-load.md), section "What validate never reads", and check each item.
4. Load: read [Validate and load a plugin](references/validate-and-load.md), sections "Load the plugin from its folder" and "Check what loaded"; load the plugin from its folder, run `claude --plugin-dir <plugin-dir> plugin details <name>`, and check each component with its row in the table.
5. Mods: when the plugin has `tests/*.test.ts` or `*.test.tsx`, run `claude plugin test <plugin-dir>`, as [Install tests, mods and CI](references/install-and-ci.md) says.
6. Install: before a release, read [Install tests, mods and CI](references/install-and-ci.md), section "Install it as users do", install the plugin into a throwaway configuration from a git-hosted source, and check its `list --json` row.
7. Review: before publishing, read [Review before publishing](references/publish-review.md) and read every shipped file against it.
8. Evals: follow the next section.

## Evals

The user never writes cases. You propose and write them, after the user says they want evals.

1. Ask, with `AskUserQuestion`, in one call: whether to build evals for this plugin; whether the user has cases or prompts in mind or you propose them from the plugin; and the score the suite must reach (it becomes `--threshold`). Stop when the answer is no.
2. Measure first: pick only the behaviors where Claude without the plugin would fail in a specific way, or a known risk the plugin guards. A case both arms pass proves nothing.
3. Create the suite from the plugin root with `claude plugin eval init`: run from this session, it prints the interview instructions for you to follow, so ask the user its questions here. Its trial runs are paid: get the yes first. Use `claude plugin eval init --bare <name>` only to write or fix one case by hand.
4. Write each case and grader with [Eval suites: layout, cases and graders](references/eval-suite.md), and its files, history or MCP stand-ins with [Eval fixtures and mocks](references/eval-fixtures-and-mocks.md). Give every case a grader on the result and one on the steps, and add near-miss prompts that must not fire the skill.
5. Check everything that costs nothing before any paid run: validate the plugin, run each `scaffold_script` by hand in an empty folder, and test each `regex`, `tool_used` and `tool_order` grader against a hand-written trace.
6. Estimate and ask: read [Running evals and gating CI](references/eval-runs-and-ci.md), give the user the run count and the estimate it describes, and run only after the yes. Pilot one case with `--runs 1 --ablation none`, show the user its output and grades, then run the suite with both arms.
7. Read the results with [Reading eval results](references/eval-results.md), from the verdict down to each failed grader's explanation. When the skill didn't fire, change its description once, from what the report shows, and run the same suite again.
8. Tell the user before you commit the suite, since it ships to every user who installs the plugin. For CI, write the job from [Running evals and gating CI](references/eval-runs-and-ci.md), section "Run in CI".

## Report

```markdown
## Checks
Each step run, its command and its result; each step not run, with the reason.

## Findings
Each problem: the file and line or the command output, and the fix applied or proposed.

## Evals
The suite, the run (cases × runs × arms, cost), the verdict, Δ and each failing case, or "not run" with the reason.

## Not verified
What these checks can't prove here, and what would prove it.
```

## Reference files

- [Validate and load a plugin](references/validate-and-load.md): validate's coverage and blind spots, the local loop with `--plugin-dir`, and the check for each component.
- [Install tests, mods and CI](references/install-and-ci.md): the throwaway install, mod tests, headless CI gating, other surfaces and the release checks.
- [Review before publishing](references/publish-review.md): the directory's pre-submission rules and the official marketplace's policy review.
- [Eval suites: layout, cases and graders](references/eval-suite.md): case files, every field and grader, and how the arms are scored.
- [Eval fixtures and mocks](references/eval-fixtures-and-mocks.md): seeding a run, and MCP mocks and replays.
- [Running evals and gating CI](references/eval-runs-and-ci.md): `eval init`, targets, tools and the sandbox, flags, cost and the CI command.
- [Reading eval results](references/eval-results.md): exit codes, the report, the JSON result and each symptom with its fix.
