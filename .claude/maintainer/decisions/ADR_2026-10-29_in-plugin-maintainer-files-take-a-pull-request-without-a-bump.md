---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# In-plugin maintainer files take a pull request without a version bump

## Scope

A change that touches only a plugin's maintainer files that must live inside the plugin: a mod's `*.test.ts(x)` and its test fixtures, and the plugin's eval suite. Any change that also touches a component, the manifest, scripts or dependencies keeps the version-bump rule.

## Context and problem statement

`claude plugin test` only finds a mod's tests under the mod's folder, and `claude plugin eval --help` (2.1.314) defines `--eval-dir` as a "Directory name (below the plugin)". Both therefore live in `plugins/<plugin>/`, and `.claude/CLAUDE.md` required a pull request and a version bump for every file there except its documentation. Users never run tests or evals; they receive them only as inert files in the plugin cache. What review and versioning should a change to them alone get?

## Decision drivers

- A version bump tells users the plugin changed; a test or eval change changes nothing they run.
- Every change inside `plugins/` still gets a review before it reaches `main`.
- The rule must stay simple enough to apply by file type.

## Considered options

- **A pull request, with no version bump or `CHANGELOG.md` entry**: chosen.
- **A pull request and a version bump, as before**: rejected, because it releases versions with no user-visible change.
- **A signed commit straight to `main`, like README-only changes**: rejected, because test and eval code still needs the review a pull request gives.

## Decision outcome

Chosen option: **A pull request with no version bump**, because it keeps review and keeps versions meaningful to users. The changed files reach users with the plugin's next version.

### Consequences

- Good, because a test-only or eval-only change no longer forces a release.
- Bad, because the version-bump check and the eval CI must recognize these files, or a test-only change fails Validate or starts a paid eval run; until they do, such a change needs a manual exception.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A change to tests or an eval suite alone passes the version-bump check | `check-version-bump` tests in `scripts/testers/scripts.test.mjs` | passed, 15/15 (commit `85b0087`) | When `check-version-bump.py` changes |
| Such a change starts no paid eval run in CI | `testing-plugins/scripts/changed-eval-plugins.sh` excludes the eval directory, `*.test.ts(x)` and a root `tsconfig.json` | changed in commit `2cec0ef` | When the eval CI changes |

## More information

Decided by Nery on 2026-10-29, after the live-sources audit `.claude/maintainer/audits/2026-10-29-plugins-and-mods-live-sources-audit.md` (F5.3, F7.2, D6). The rule is in `.claude/CLAUDE.md` → Maintainer and Plugin Scopes (commit `a736011`).