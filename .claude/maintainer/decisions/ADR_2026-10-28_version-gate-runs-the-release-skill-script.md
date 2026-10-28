---
status: accepted
date: 2026-10-28
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The version gate and the bump command run the release skill's Python; the `.mjs` copies are retired

## Scope

- In scope: the maintainer's version bump and bump check. Their implementation: `.claude/skills/release-and-versioning/scripts/bump-version.py` and `check-version-bump.py`; the `version-bump` gate of `scripts/gates.mjs`; the `version:bump` npm script of `package.json`; the tests of these rules in `scripts/testers/scripts.test.mjs`.
- Out of scope: the copies in `.claude/skills/plugin-renames-and-removals/scripts/`. A skill keeps its own copy of a script it runs, and that layer is tracked by DEBT-038, which needs Nery's decision.

## Context and problem statement

The repository held two implementations of the bump and the bump check: `scripts/bump-version.mjs` and `scripts/check-version-bump.mjs`, which the gate and `npm run version:bump` ran, and the release skill's `bump-version.py` and `check-version-bump.py`, which the skill documents and the pull request template names. A rule changed in one copy and not the other would make the gate and the skill disagree. DEBT-025 logged this on 2026-10-26 and waited on Nery's decision. On 2026-10-28 Nery asked for the `.mjs` copies to be retired and the debt closed.

## Decision drivers

- The gate and the command must run the code that the release skill documents.
- A rule must have one implementation in the maintainer layer.
- The maintainer's Python version is fixed by ADR_2026-10-27_python-version-is-set-per-scope.

## Considered options

- **The gate and `version:bump` run the release skill's `.py` scripts; the `.mjs` copies are deleted**: chosen.
- **Keep both copies**: rejected because the two rules drift apart silently, which is the defect DEBT-025 records.
- **The gate keeps its `.mjs` copy and the skill's `.py` scripts are deleted**: rejected because the skill, its pull request template and its tests already point at the `.py` scripts.

## Decision outcome

Chosen option: **the release skill's `.py` scripts run the gate and the command**, because the procedure the skill documents then runs the same code as the gate.

- `version-bump` in `scripts/gates.mjs` runs `python3 .claude/skills/release-and-versioning/scripts/check-version-bump.py <base>`.
- `version:bump` in `package.json` runs `python3 .claude/skills/release-and-versioning/scripts/bump-version.py`.
- `scripts/bump-version.mjs` and `scripts/check-version-bump.mjs` are deleted. The functions only they used are removed from `scripts/lib.mjs`, and `renderReadme` in `scripts/generators/catalog.mjs` is no longer exported.
- The tests in `scripts/testers/scripts.test.mjs` run the `.py` scripts by path, with `TCF_ROOT` set to their temporary copy.

### Consequences

- Good, because the maintainer layer has one implementation of each rule, and the gate checks what the release skill documents.
- Good, because the Python scripts need no dependencies and no extra install.
- Bad, because `npm run version:bump` no longer regenerates the README catalog. The `.mjs` script did; the `.py` script prints `Next: node scripts/generators/catalog.mjs`, and `npm run generate` runs it. Run `npm run generate` after every bump.
- Bad, because the `version-bump` gate needs `python3` on the machine that runs it. Local runs and the CI `policy` job already need it for the skill tests.
- Bad, because the plugin-renames skill keeps its own copies, and its copy of the check is already weaker than the release skill's (DEBT-038).

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The version rules' tests pass against the `.py` scripts | `node --test --test-name-pattern="bump" scripts/testers/scripts.test.mjs` | 2026-10-28: 8 of 8 pass | Each change to either script |
| The maintainer node tests still pass after `lib.mjs` and `catalog.mjs` lose exports | `node --test scripts/testers/*.test.mjs` | 2026-10-28: 109 of 109 pass | Each change to `scripts/` |
| The gate's command passes on the repository | `python3 .claude/skills/release-and-versioning/scripts/check-version-bump.py origin/main` | 2026-10-28: `✔ Version bumps OK (no plugin changes)`, exit 0 | Each push |
| The scripts type-check | `tsc -p scripts/tsconfig.json --noEmit` | 2026-10-28: exit 0 | Each change to `scripts/` |
| CI runs the gate with the `.py` script | The `policy` job of `validate.yml` on the push that carries this change | pending | After the push |

## More information

- Decided by Nery Samuel Murillo on 2026-10-28, in the session where DEBT-025 was closed; the instruction was to settle the debt, remove the `.mjs` copies and work on `main`.
- Logged as DEBT-025 on 2026-10-26; closed as resolved on 2026-10-28 in `.claude/maintainer/technical-debt/closed-debt.md`. The skill-layer copies are tracked by DEBT-038.
- Settled records that still name the removed `.mjs` files, and are not rewritten: ADR_2026-10-16_maintainer-operating-model, ADR_2026-10-18_breaking-changes-bump-minor-in-0x, ADR_2026-10-24_catalog-facts-are-generated-from-plugins, ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand, and `.claude/specs/2026-10-26-biome-config-corrections-and-strictness-design.md`.
