---
status: accepted
date: 2026-11-05
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# In a cloud session, the signatures gate checks that each commit carries an SSH signature

## Scope

The `signatures` gate of `scripts/gates.mjs` (`signatureProblem`), run by `npm run gates` and the Husky pre-push hook. Local machines keep the full check.

## Context and problem statement

The gate required `%G?` = `G` for every commit since `origin/main`. A Claude Code cloud session signs commits through `gpg.ssh.program=/tmp/code-sign` with a key it does not expose: `/home/claude/.ssh/commit_signing_key.pub` is empty and `gpg.ssh.allowedSignersFile` is unset, so git prints `N` for every commit. GitHub reports the same commits as `verified: true`, `reason: valid`. With Nery's machine out of service, every push came from the cloud and needed `--no-verify`, which skipped every pre-push gate (DEBT-051). How should the gate judge signatures in a cloud session?

## Decision drivers

- The pre-push gates must run, not be skipped, on every push.
- An unsigned or badly signed commit must still fail.
- Nothing can verify a cloud signature before the push; GitHub verifies it after.

## Considered options

- **Accept `N` or `E` in a cloud session (`CLAUDE_CODE_REMOTE=true`) when the commit carries an SSH signature header; keep `G` everywhere else**: chosen.
- **Ask GitHub for each commit's verification**: rejected, because GitHub knows a commit only after the push the gate guards.
- **Keep pushing with `--no-verify`**: rejected; it skips every gate.

## Decision outcome

Chosen option: **presence of an SSH signature in a cloud session**. `signatureProblem` passes `G` everywhere; in a cloud session it also passes `N` or `E` when `git cat-file commit` shows a `gpgsig -----BEGIN SSH SIGNATURE-----` header. `B`, `U`, `X`, `Y`, `R` and an unsigned commit fail everywhere.

### Consequences

- Good, because cloud pushes run every pre-push gate again.
- Bad, because in a cloud session the gate proves a signature is present, not that it is valid; GitHub's verification after the push is the check, and a commit it shows as unverified must be reported.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Local rules unchanged | `env -u CLAUDE_CODE_REMOTE npm run gates -- --only signatures` | Failed on the cloud-signed commits on 2026-11-05 | Each change of the gate |
| Cloud sessions pass signed commits | `npm run gates -- --only signatures` in a cloud session | Passed on 2026-11-05 | Each change of the gate |
| Unsigned and badly signed commits fail | `signatures gate` tests in `scripts/testers/gates.test.mjs` | Passed on 2026-11-05 | Each push (`node-tests`) |

## More information

Ordered by Nery on 2026-11-05 ("corrige el gate de firmas"), closing DEBT-051.
