# Phase 8: Report (gate 1)

Present the audit and get the user's decision on what to act on. This phase is read-only.

## Report contents

- A plain-language summary of the repository's state.
- **Findings:** `F-1`, `F-2`, …, each with its class and its evidence.
- **Recommendations:** `R-1`, `R-2`, …, each with the findings it covers, its risk and whether it can be undone. Work that is not a deletion (a refactor, a bisect, a debugging session, a fix) is a recommendation like any other.
- **Security-sensitive items:** each with its risk and how the owner changes it. The audit never changes them.
- **Secrets in published history:** tell the owner to revoke or rotate each one first; a history rewrite alone does not remove it from clones, forks, cached views or pull requests ([GitHub: removing sensitive data][gh-sensitive]).
- **Questions for the user:** each with a recommended answer and the reason.
- The full coverage ledger.

## Gate 1

- The user approves recommendations by naming their IDs.
- Silence, a timeout, or a generic "clean it up" approves nothing.
- Warn when a partial approval leaves a deletion without the integration that makes it safe.
- "Audit only", or a refusal, ends the run with the report delivered.

## Done when

- [ ] Every finding and recommendation has its ID, and every recommendation names its findings, risk and reversibility.
- [ ] The coverage ledger is in the report.
- [ ] The user's answer names the approved IDs, or ends the run.

## Sources

Checked on 2026-11-04.

- [GitHub: removing sensitive data][gh-sensitive]: "if the sensitive data you need to remove is a secret … you need to revoke and/or rotate that secret"; after a rewrite the commits "may still be accessible … In any clones or forks of your repository … in cached views on GitHub … Through any pull requests that reference them".

[gh-sensitive]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
