---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The gates run from one script, `scripts/gates.mjs`, through `npm run gates` locally and in CI

## Scope

- In scope: `scripts/gates.mjs` and its tests, the `gates` and `gates:ci` scripts of the root `package.json`, the jobs of `.github/workflows/validate.yml`, `.claude/CLAUDE.md` → Before Every Push, the PR template checklist, and the rule in `scripts/check-repo.mjs` against scripts npm runs on its own.
- Out of scope: which gates CI runs (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure), the tool pins, which stay in the `env` block of `validate.yml`, and `.pre-commit-config.yaml`, which no git hook runs.

## Context and problem statement

The gates lived twice: as 21 numbered shell commands in `.claude/CLAUDE.md`, run by hand, and again as steps in `validate.yml`. The two drifted (CI did not run basedpyright, the `.mjs` type check or the plugins' Python tests, and its notes said so), the skipped-test count was read by eye, and pipelines like `git ls-files -z | xargs -0` depended on the shell's quoting, which zsh breaks. Where should the list of gates live so that local runs and CI cannot disagree?

## Decision drivers

- One source for every gate command, its arguments and its order.
- A failure is never silent: a crash, a signal, a missing tool or a skipped test fails the gate.
- No shell between the gate and the tool.
- The root `package.json` orchestrates and stays maintainer-only (ADR_2026-10-21_maintainer-only-root-package-json).

## Considered options

- **`scripts/gates.mjs`, called through `npm run gates` and `npm run gates:ci`**: chosen.
- **Keep the numbered commands in `CLAUDE.md` and the steps in `validate.yml`**: rejected because they already drifted and nothing checks they agree.
- **Inline the commands as npm scripts**: rejected because loops over plugins and test folders do not fit a one-line JSON string, and shell one-liners there bring the quoting problem back.
- **Run CI without `npm ci`**: rejected because the `tsc` gate needs `@types/node` from the lockfile; CI runs `npm ci --ignore-scripts` instead, and `check-repo.mjs` forbids the `pre`/`post` and install scripts that `npm run` would start on its own.

## Decision outcome

Chosen option: **one script with injectable gates**, because it removes the second copy of every command and makes each failure mode a tested behavior.

`gates.mjs` runs each gate with `spawnSync` and an argument list, never a shell, from the repository root. It stops at the first failure with that gate's exit code (with `--ci`, it goes on and lists every failure, then exits with the first code). A missing tool, a signal or a skipped test fails the gate: Node tests are read from a TAP copy of the report, Python tests through the `unittest` result object, and a legitimate skip goes into `ALLOWED_SKIPS` with its reason. The pins come from the `env` block of `validate.yml`, and a missing pin stops the run. Each CI job runs one group with `npm run gates:ci -- --group <group>`.

### Consequences

- Good, because a gate changes in one place, and its tests prove the runner stops, keeps going, names a missing tool and fails on skips (`scripts/tests/gates.test.mjs`, run against throwaway gates in a temporary folder).
- Good, because `npm run gates` replaces 21 manual steps.
- Bad, because the runner captures each gate's output, so a slow gate shows nothing until it ends.
- Bad, because without a shell it cannot start `npx.cmd` on Windows; the gates run on macOS and Linux only.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The runner behaves as described | `node --test scripts/tests/gates.test.mjs` | 13 of 13 passed on 2026-10-21; with the skip check disabled on purpose, its test failed | Each push |
| Every gate passes on the branch | `npm run gates` | Passed on 2026-10-21 up to `mod-test:project-maintainer`, which fails 5 of 50 on the local Claude Code 2.1.307 (pre-existing, see the handoff); the gates after it passed when run on their own | Each push |
| CI runs the same commands | `validate.yml` on the branch's first push | Pending | First push |

## More information

Nery decided this on 2026-10-21 after reviewing the proposal and a list of adjustments (fail on any skip, injectable gates in the tests, `--keep-going` for CI).
