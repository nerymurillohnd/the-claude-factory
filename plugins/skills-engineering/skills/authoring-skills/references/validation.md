# Validation

How to check a skill before delivering it: the mechanical checks, the reread from the model's seat, behavior and trigger tests in fresh sessions, evals, and how to report what was and wasn't verified. A skill that triggers has only been found; whether it works is shown by comparing runs with and without it.

## Contents

- Choose the checks by risk
- Mechanical checks
- The reread
- Behavior tests
- Trigger tests
- Evals
- Watch how the model uses it
- Report

## Choose the checks by risk

Run every check that applies and is runnable here; the cost of more checks should match what a defect would cost:

- **Every skill**: mechanical checks, the reread, and each use case in a fresh session.
- **Skills the model invokes on its own**: trigger tests, under the condition in [name-and-description.md](name-and-description.md).
- **Skills that take destructive or irreversible actions, write to external systems, or are distributed to third parties**: behavior tests with and without the skill, on each model its users run, and evals that can be rerun after every change.

## Mechanical checks

- **Claude Code**: `claude plugin validate` on the plugin root, or on the skills folder that holds the skill (`claude plugin validate .claude/skills`), reports frontmatter that fails to parse (v2.1.233 or later). Add `--strict` for a plugin before release.
- **Specification**: `skills-ref validate path/to/skill` checks the frontmatter and naming rules of the Agent Skills specification.
- **Uploads to claude.ai or the Skills API**: only the six spec fields; `name` and `description` within their limits, with no XML tags and no reserved words; `SKILL.md` at the root or in one folder; the archive within the upload limit in [skill-types.md](skill-types.md).
- **Links and paths**: every link in `SKILL.md` resolves to a file, spelled exactly as named; no path reaches outside the skill except through a path variable; no file goes unlinked.
- **Body size**: within the budgets in [structure.md](structure.md); every supporting file that structure.md requires a table of contents for opens with one.
- **Scripts**: each runs with `--help`, exits non-zero on bad input with a message that says what to fix, and needs only the dependencies the skill states.

## The reread

Run the reread in [writing-instructions.md](writing-instructions.md) once more over every file. Fix what you find before running anything: a run costs more than a reread.

## Behavior tests

The authoring session hides gaps: you know what the skill means, the model that loads it doesn't. Test in a fresh session every time.

1. Run each use case in a fresh session with the skill available. Check the result against the use case's success criteria, not against whether it "looks right".
2. Run the same requests in a fresh session without the skill. If the results match, the skill adds nothing for that case.
   - Personal or project skill: set it to `"off"` in `skillOverrides` for the second run.
   - Plugin skill: `skillOverrides` doesn't apply; use `claude plugin eval`, which repeats each run with no plugin loaded.
3. Run on each model the skill's users run. Smaller models may need more guidance; larger ones may be slowed by guidance they don't need.
4. When the skill changes an existing one, compare against the previous version, not against no skill.

On surfaces you can't reach from here, list the test as not run and say where it must run.

## Trigger tests

Read [name-and-description.md](name-and-description.md) for building the query set, the runs and the threshold. In a plugin, `claude plugin eval` with a grader that checks the Skill tool was used measures how often the skill triggers across those queries after each description change.

## Evals

Write evals when the skill will change over time or ships to third parties, so each change can be measured instead of judged by eye.

- Start with two or three realistic cases with their input files, from the use cases.
- Run each with and without the skill, each run in a clean context.
- Write the assertions after the first round of outputs, once you see what varies; make each objective, with the evidence a pass requires.
- Prefer a script for any assertion that can be checked mechanically.
- Drop assertions that pass both with and without the skill: they don't discriminate.
- Read the transcripts, not only the outputs: wasted steps and ignored instructions show there.
- Ask a person to review outputs where quality is a judgment.

Two formats exist, and they aren't interchangeable:

- The Agent Skills format (`evals/evals.json` in the skill folder: prompt, expected output, files, assertions), run by skill-creator or your own runner. Its guide: https://agentskills.io/skill-creation/evaluating-skills.
- `claude plugin eval` for skills in a plugin: isolated runs with and without the plugin, graders, and a non-zero exit below a threshold for CI. Its guide: https://code.claude.com/docs/en/plugin-evals.

Each eval run spends tokens on the requester's account; confirm before running a large set.

## Watch how the model uses it

In the test transcripts, look for:

- **Unexpected paths**: files read in an order you didn't plan. The structure isn't as clear as you thought.
- **Missed connections**: a file the model needed and never opened. Its pointer needs a clearer condition or a better place.
- **Overreliance**: one file read on every run. Its content may belong in the body.
- **Ignored content**: a file never read. It may be unnecessary, or its pointer is wrong.
- **Steps the model skipped or redid**: candidates for a gate, a checklist item or a script.

Fix the skill from the pattern across runs, not from one run.

## Report

Deliver with:

- what you built: the files, and what each holds;
- each design decision and its reason;
- each check: what ran, where (surface, version, model), and its result;
- each check you couldn't run, the reason, and where it must run;
- the assumptions still open, and the facts you couldn't verify.

Never report a check you didn't run as passed.
