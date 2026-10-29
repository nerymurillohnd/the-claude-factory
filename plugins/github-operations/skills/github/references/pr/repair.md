# Repair loop and review threads

## Repair each finding

Work these steps in order for every finding.

1. Verify the finding applies to the current head.
2. Classify it as one of: a real branch-caused problem, a valid pre-existing problem, stale feedback, a false positive, a suspected intermittent or infrastructure problem, an external blocker, or a non-blocking improvement.
3. Inspect enough evidence to evaluate the recommended fix.
4. Apply the smallest justified change within scope.
5. Run the relevant local validation.
6. When a change is required, commit it (signed, with the repository's conventions) and push without force.
7. Refresh the remote head SHA and verify the remote branch points at the commit you pushed.
8. Reply to the review feedback with what changed and the commit that holds it, or with the evidence for making no change.
9. Observe again against the new head.

Fix real, reproducible, branch-caused problems autonomously within scope. If the same original failure survives two consecutive fixes, stop guessing: report the evidence and what you tried, set the state to `blocked`, and ask the user.

Do not silently expand into unrelated dependency upgrades, broad workflow redesign or pre-existing repository maintenance. Record those as advisory work unless an actual gate requires them. If a valid pre-existing problem blocks this PR, decide whether a minimal in-scope repair is appropriate; otherwise report the blocker.

Do not:

- Weaken tests or security controls merely to obtain green checks.
- Suppress warnings without addressing or justifying them.
- Broaden permissions without a justified need and authorization.
- Rerun failed checks repeatedly in the hope of a pass.
- Call a test flaky solely because a rerun passed.

Rerun a check only with evidence of a transient failure, or after addressing the condition that stopped it from running.

Every push invalidates head-specific observations and any earlier merge approval. Observe again against the new head, as `observe.md` says.

## Behind the base, or conflicting

Do this when the PR's mergeability is `CONFLICTING`, its merge state is `DIRTY` or `BEHIND`, or a rule requires the branch to be current.

1. Bring the base into the feature branch without rewriting its history: either merge the fetched base into the branch locally, or have GitHub update the branch (`update_pull_request_branch` with the expected head SHA, or the `gh` PR update-branch command). Never use the rebase option of that command and never rebase the branch yourself: its commits are published.
2. If the merge conflicts, resolve it locally and keep the intent of both sides. Read both versions of every conflicting hunk. If the intent of either side is unclear, abort the merge, set the state to `blocked` and ask the user. Never take one side wholesale to make the conflict disappear.
3. Run the repository's validation, commit the merge with the repository's conventions, push without force, refresh the head and observe again.
4. Record the base update in the final report.

## Review threads

1. Reply to every actionable thread addressed during this run, after the fix is pushed. For an implemented fix, explain the change and cite the commit. For a stale or false-positive finding, give the evidence instead of silently dropping it.
2. Decide whether each thread is eligible for resolution. It is eligible when:
   - Its finding is addressed by a change you pushed, or it comes from a bot and a justified no-change disposition is recorded.
   - Any required fix has been pushed and relevant validation has passed.
   - No repository policy or reviewer instruction requires leaving it open.
3. When you disagree with a human reviewer and made no change, reply with the evidence and leave the thread open for them. It is not eligible: list it in the readiness decision and in the final report.
4. Resolve the eligible threads. Resolution never substitutes for fixing the issue. Outstanding change requests and required approvals stay gates even when every thread is resolved.
5. After resolving, refresh the review state and check that no new actionable feedback appeared.
