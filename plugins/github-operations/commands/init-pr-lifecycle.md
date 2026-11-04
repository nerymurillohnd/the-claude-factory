---
description: Takes a pull request at its current stage all the way to merge-ready.
---

You are authorized to use the `github-operations:auto-pr-lifecycle` skill to orchestrate an end-to-end workflow and delegate to its agents until the pull request is ready to merge.

## Start

1. Load the `github-operations:auto-pr-lifecycle` skill and follow it.
2. Identify the pull request: the one the user names, or the one for the current branch.
3. Read and analyze the pull request, then determine the stage it is in.
4. Run the workflow from that stage, delegating each step to the agent it names.

## Stage: opened, not reviewed yet

1. Launch the `github-operations:pr-lifecycle:pr-tracker` agent and require evidence for every finding.
2. Read its report and verify each finding against its evidence.
3. Continue at "Reviewed, not fixed" when verified findings remain, and at "Fixed, readiness not checked" when none remain.

## Stage: reviewed, not fixed

1. Launch the `github-operations:pr-lifecycle:pr-fixer` agent with the verified findings and the open reviews.
2. Require a detailed report: what it fixed, what it could not fix and why, where (file and line), and the evidence for each item.
3. Review its commits and its report against that evidence.
4. Show the user what was fixed and what was not, then ask whether to push.
5. Push at once when the user approves, then continue at "Opened, not reviewed yet" to track the new head.
6. Stop and ask the user how to proceed when the user declines.
7. Repeat these rounds as many times as the findings require.

## Stage: fixed, readiness not checked

1. Launch the `github-operations:pr-lifecycle:pr-finalizer` agent and require evidence for its verdict.
2. Read the verdict and verify it against its evidence.
3. Tell the user the pull request is ready and ask for the merge approval when the verdict is ready to merge.
4. Explain the current situation and what happened when it is not ready, and let the user decide.

## Done when

- Merge only with the user's approval, and only once every error is fixed, every finding is resolved, and every review thread is answered and resolved: threads opened by bots by the `github-operations:pr-lifecycle:pr-finalizer` agent, threads opened by people by their reviewer.
- Report at once anything that cannot be completed, with the reason: errors that could not be fixed, threads still open, and any other blocker.
