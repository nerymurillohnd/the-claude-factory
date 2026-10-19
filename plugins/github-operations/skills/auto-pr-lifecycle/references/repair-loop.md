# Repair loop and review threads

## Repair each finding

1. Verify the finding applies to the current head.
2. Classify it as one of: a real branch-caused problem, a valid pre-existing problem, stale feedback, a false positive, a suspected intermittent or infrastructure problem, an external blocker, or a non-blocking improvement.
3. Inspect enough evidence to evaluate the recommended fix.
4. Apply the smallest justified change within scope.
5. Run the relevant local validation.
6. Reply to review feedback with what changed and why, or with the evidence for making no change.
7. Commit and push through local git when a change is required.
8. Refresh the remote head SHA.
9. Observe again against that head.

Fix real, reproducible, branch-caused problems autonomously within scope.

Do not silently expand into unrelated dependency upgrades, broad workflow redesign or pre-existing repository maintenance. Record those as advisory work unless an actual gate requires them. If a valid pre-existing problem blocks this PR, decide whether a minimal in-scope repair is appropriate; otherwise report the blocker.

Do not:

- Weaken tests or security controls merely to obtain green checks.
- Suppress warnings without addressing or justifying them.
- Broaden permissions without a justified need and authorization.
- Rerun failed checks repeatedly in the hope of a pass.
- Call a test flaky solely because a rerun passed.

Rerun a check only with evidence of a transient failure, or after addressing the condition that stopped it from running.

Every push invalidates head-specific observations and any earlier merge approval. Observe again against the new head, as the observation reference says.

## Review threads

Reply to every actionable thread addressed during this run. For an implemented fix, explain the change and cite the commit when useful. For a stale or false-positive finding, give the evidence instead of silently dropping it.

Resolve a thread only after:

- Its finding is addressed, or a justified no-change disposition is recorded.
- Any required fix has been pushed.
- Relevant validation has passed.
- No repository policy or reviewer instruction requires leaving it open.

Resolution never substitutes for fixing the issue. Outstanding change requests and required approvals stay gates even when every thread is resolved. After resolving, refresh review state and check that no new actionable feedback appeared.
